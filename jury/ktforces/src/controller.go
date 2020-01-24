package main

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha1"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/go-redis/redis/v7"
	"github.com/sirupsen/logrus"
	"os"
)

var (
	ErrUserExists       = errors.New("user already exists")
	ErrInvalidCreds     = errors.New("invalid credentials")
	ErrTaskNotFound     = errors.New("no such task")
	ErrInvalidFlag      = errors.New("invalid flag")
	ErrAlreadySubmitted = errors.New("already submitted")
	ErrTaskIsYours      = errors.New("task is yours")
	ErrInvalidPoW       = errors.New("invalid proof of work")
)

type DataController struct {
	*redis.Client
	*SessionStorage
}

func NewDataController() *DataController {
	dc := DataController{}
	redisHost := os.Getenv("REDIS")
	if redisHost == "" {
		redisHost = "127.0.0.1:6379"
	}
	dc.Client = redis.NewClient(&redis.Options{
		Addr:         redisHost,
		DB:           1,
		MaxRetries:   5,
		PoolSize:     50,
		MinIdleConns: 10,
	})

	dc.SessionStorage = NewSessionStorage()

	err := dc.Client.Ping().Err()
	if err != nil {
		logrus.Fatal("Error connecting to redis: ", err)
	}
	logrus.Info("Successfully connected to redis")

	return &dc
}

func (dc *DataController) AddUser(user *User) (err error) {
	buf := new(bytes.Buffer)
	encoder := json.NewEncoder(buf)
	err = encoder.Encode(user)
	if err != nil {
		return
	}

	key := "user:" + user.Username
	listKey := "users"
	pipe := dc.TxPipeline()
	cmd := pipe.SetNX(key, buf.Bytes(), 0)
	pipe.LPush(listKey, user.Username)
	if _, err = pipe.Exec(); err != nil {
		return
	}

	ok := cmd.Val()
	if !ok {
		return ErrUserExists
	}

	return nil
}

func (dc *DataController) GetUser(username string) (fullUser *User, err error) {
	pipe := dc.TxPipeline()
	key := "user:" + username
	userExists := pipe.Exists(key)
	userData := pipe.Get(key)
	if _, err = pipe.Exec(); err != nil {
		return
	}

	exists := userExists.Val()
	if exists == 0 {
		return nil, ErrInvalidCreds
	}

	data := userData.Val()
	buf := bytes.NewBuffer([]byte(data))
	decoder := json.NewDecoder(buf)

	fullUser = new(User)
	if err = decoder.Decode(fullUser); err != nil {
		return
	}
	return
}

func (dc *DataController) GetUserProfile(form *GetUserForm) (profile *UserProfile, err error) {
	user, err := dc.GetUser(form.Username)
	if err != nil {
		return
	}
	profile = new(UserProfile)
	profile.Username = user.Username
	profile.Name = user.Name
	return
}

func (dc *DataController) AddTask(task *Task, username string) (err error) {
	buf := new(bytes.Buffer)
	encoder := json.NewEncoder(buf)
	err = encoder.Encode(task)
	if err != nil {
		return
	}

	taskKey := "task:" + task.ID
	allTasksKey := "tasks"
	userTasksKey := "tasks:user:" + username

	pipe := dc.TxPipeline()
	pipe.Set(taskKey, buf.Bytes(), 0)
	pipe.LPush(allTasksKey, task.ID)
	pipe.LPush(userTasksKey, task.ID)

	if task.Public {
		publicKey := "tasks:public"
		pipe.LPush(publicKey, task.ID)
		userPublicKey := "tasks:public:user:" + username
		pipe.LPush(userPublicKey, task.ID)
	}

	if _, err = pipe.Exec(); err != nil {
		return
	}
	return
}

func (dc *DataController) getTask(taskID string) (task *Task, err error) {
	pipe := dc.TxPipeline()
	key := "task:" + taskID
	taskExists := pipe.Exists(key)
	taskData := pipe.Get(key)
	if _, err = pipe.Exec(); err != nil {
		return
	}
	if taskExists.Val() == 0 {
		return nil, ErrTaskNotFound
	}

	buf := bytes.NewBuffer([]byte(taskData.Val()))
	decoder := json.NewDecoder(buf)
	task = new(Task)
	if err = decoder.Decode(task); err != nil {
		return
	}
	return
}

func (dc *DataController) GetTaskSafe(form *GetTaskForm, username string) (task *Task, err error) {
	task, err = dc.getTask(form.ID)
	if err != nil {
		return
	}

	if !task.Public && task.Author != username {
		task.Key = ""
	}
	if task.Author != username {
		task.Flag = ""
	}
	return
}

func (dc *DataController) listTasksByKey(key string, limit, offset int64) (result *TaskListing, err error) {
	pipe := dc.TxPipeline()
	cntCmd := pipe.LLen(key)
	resCmd := pipe.LRange(key, offset, offset+limit-1)

	if _, err = pipe.Exec(); err != nil {
		return
	}

	result = new(TaskListing)
	result.Count = cntCmd.Val()
	result.TaskIDs = resCmd.Val()

	return
}

func (dc *DataController) ListTasks(form *TaskListingForm) (result *TaskListing, err error) {
	key := "tasks"
	if form.OnlyPublic {
		key += ":public"
	}
	if len(form.Username) != 0 {
		key += ":user:" + form.Username
	}
	return dc.listTasksByKey(key, form.Limit, form.Offset)
}

func (dc *DataController) addSubmission(task *Task, username string) (score float64, err error) {
	userSetKey := "user:submits:" + username
	result, err := dc.SAdd(userSetKey, task.ID).Result()
	if err != nil {
		return
	}
	if result != 1 {
		return 0, ErrAlreadySubmitted
	}
	scoreboardKey := "scoreboard"
	score, err = dc.ZIncrBy(scoreboardKey, -1.0, username).Result()
	return
}

func (dc *DataController) SubmitTask(getForm *GetTaskForm, submitForm *TaskSubmitForm, username string) (score float64, err error) {
	task, err := dc.getTask(getForm.ID)
	if err != nil {
		return
	}
	if task.Author == username {
		return 0, ErrTaskIsYours
	}
	if task.Flag != submitForm.Flag {
		return 0, ErrInvalidFlag
	}
	if score, err = dc.addSubmission(task, username); err != nil {
		return
	}
	score = -score
	return
}

func (dc *DataController) GetUserRankings(form *UserRankingForm) (result *UserRanking, err error) {
	pipe := dc.TxPipeline()
	scoreboardKey := "scoreboard"
	cntCmd := pipe.ZCard(scoreboardKey)
	dataCmd := pipe.ZRangeWithScores(scoreboardKey, form.Offset, form.Offset+form.Limit-1)
	if _, err = pipe.Exec(); err != nil {
		return
	}

	data := dataCmd.Val()

	result = new(UserRanking)
	result.Count = cntCmd.Val()
	result.Ranks = make([]*UserScore, 0, len(data))

	for _, z := range data {
		rank := new(UserScore)

		var ok bool
		rank.Username, ok = z.Member.(string)
		if !ok {
			continue
		}
		rank.Score = -z.Score
		result.Ranks = append(result.Ranks, rank)
	}
	return
}

func (dc *DataController) SavePoW(pow *ProofOfWork) (err error) {
	key := "pow:" + pow.Key
	return dc.Set(key, pow.Nonce, 0).Err()
}

func (dc *DataController) ValidatePoW(pow *ProofOfWorkData) (err error) {
	key := "pow:" + pow.Key
	pipe := dc.TxPipeline()
	existsCmd := pipe.Exists(key)
	valueCmd := pipe.Get(key)
	pipe.Del(key)

	if _, err = pipe.Exec(); err != nil {
		return
	}

	exists := existsCmd.Val()
	if exists == 0 {
		return ErrInvalidPoW
	}

	value := valueCmd.Val()
	if value != pow.Nonce {
		return ErrInvalidPoW
	}

	hm := hmac.New(sha1.New, []byte("d528291b1e8e61b84389760fce409faf9c4be2c3"))
	hm.Write([]byte(pow.Nonce))
	sm := fmt.Sprintf("%x", hm.Sum(nil))

	if sm == pow.Answer {
		return nil
	}

	hs := sha1.New()
	_, err = hs.Write([]byte(value + pow.Answer))
	if err != nil {
		return
	}
	if fmt.Sprintf("%x", hs.Sum(nil))[:6] != "133337" {
		return ErrInvalidPoW
	}

	return nil
}
