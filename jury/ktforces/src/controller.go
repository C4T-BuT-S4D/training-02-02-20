package main

import (
	"bytes"
	"encoding/json"
	"errors"
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
		PoolSize:     20,
		MinIdleConns: 5,
	})

	dc.SessionStorage = NewSessionStorage()

	_, err := dc.Client.Ping().Result()
	if err != nil {
		logrus.Fatal("Error connecting to redis: ", err)
	}
	logrus.Info("Successfully connected to redis")

	return &dc
}

func (dc *DataController) TrySetUser(user *User) (err error) {
	buf := new(bytes.Buffer)
	encoder := json.NewEncoder(buf)
	err = encoder.Encode(user)
	if err != nil {
		return
	}

	key := "user:" + user.Username
	cmd := dc.SetNX(key, buf.Bytes(), 0)
	ok, err := cmd.Result()
	if err != nil {
		return
	}
	if !ok {
		return ErrUserExists
	}
	return nil
}

func (dc *DataController) TryGetUser(username string) (fullUser *User, err error) {
	pipe := dc.TxPipeline()
	key := "user:" + username
	userExists := pipe.Exists(key)
	userData := pipe.Get(key)
	_, _ = pipe.Exec()

	exists, err := userExists.Result()
	if err != nil {
		return
	}
	if exists == 0 {
		return nil, ErrInvalidCreds
	}

	data, err := userData.Result()
	if err != nil {
		return
	}

	buf := bytes.NewBuffer([]byte(data))
	decoder := json.NewDecoder(buf)

	fullUser = new(User)
	if err = decoder.Decode(fullUser); err != nil {
		return
	}
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
	pipe.RPush(allTasksKey, task.ID)
	pipe.RPush(userTasksKey, task.ID)

	if task.Public {
		publicKey := "tasks:public"
		pipe.RPush(publicKey, task.ID)
		userPublicKey := "tasks:public:user:" + username
		pipe.RPush(userPublicKey, task.ID)
	}

	if _, err = pipe.Exec(); err != nil {
		return
	}
	return
}

func (dc *DataController) tryGetTask(taskID string) (task *Task, err error) {
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

func (dc *DataController) TryGetTaskSafe(taskID, username string) (task *Task, err error) {
	task, err = dc.tryGetTask(taskID)
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
	if limit > 50 {
		limit = 50
	}
	pipe := dc.TxPipeline()
	cntCmd := pipe.LLen(key)
	resCmd := pipe.LRange(key, offset, offset+limit-1)

	if _, err = pipe.Exec(); err != nil {
		return
	}

	result = new(TaskListing)
	if result.Count, err = cntCmd.Result(); err != nil {
		return
	}
	tasksData, err := resCmd.Result()
	if err != nil {
		return
	}

	result.TaskIDs = tasksData
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
	score, err = dc.ZIncrBy(scoreboardKey, 1.0, username).Result()
	return
}

func (dc *DataController) TrySubmitTask(getForm *GetTaskForm, submitForm *TaskSubmitForm, username string) (score float64, err error) {
	task, err := dc.tryGetTask(getForm.ID)
	if err != nil {
		return
	}
	if task.Flag != submitForm.Flag {
		return 0, ErrInvalidFlag
	}
	score, err = dc.addSubmission(task, username)
	return
}
