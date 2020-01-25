package main

type User struct {
	Username string  `json:"username" binding:"required,min=5,max=255"`
	Password string  `json:"password,omitempty" binding:"required"`
	Name     string  `json:"name" binding:"required"`
	Score    float64 `json:"score" binding:"isdefault"`
}

type GetUserForm struct {
	Username string `json:"username" form:"username" uri:"username" binding:"required"`
}

type LoginForm struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type Task struct {
	ID         string `json:"id" binding:"isdefault"`
	Name       string `json:"name" binding:"required"`
	Data       string `json:"data" binding:"required,base64"`
	Key        string `json:"key" binding:"required,base64"`
	Encryption string `json:"encryption" binding:"required,base64"`
	Public     bool   `json:"public"`
	Flag       string `json:"flag"`
	Author     string `json:"author" binding:"isdefault"`
}

type GetTaskForm struct {
	ID string `uri:"id" binding:"required,uuid4"`
}

type TaskListing struct {
	Count   int64    `json:"count"`
	TaskIDs []string `json:"task_ids"`
}

type TaskListingForm struct {
	Username   string `form:"username"`
	Limit      int64  `form:"limit" binding:"min=1,max=50"`
	Offset     int64  `form:"offset" binding:"min=0"`
	OnlyPublic bool   `form:"only_public"`
}

type TaskSubmitForm struct {
	Flag string `json:"flag" binding:"required"`
}

type UserRankingForm struct {
	Limit  int64 `form:"limit" binding:"min=1,max=50"`
	Offset int64 `form:"offset" binding:"min=0"`
}

type UserScore struct {
	Username string  `json:"username"`
	Score    float64 `json:"score"`
}

type UserRanking struct {
	Count int64        `json:"count"`
	Ranks []*UserScore `json:"ranks"`
}

type ProofOfWork struct {
	Key   string `json:"key"`
	Nonce string `json:"nonce"`
}

type ProofOfWorkData struct {
	Key    string `json:"key" binding:"required,uuid4"`
	Nonce  string `json:"nonce" binding:"required,uuid4"`
	Answer string `json:"answer" binding:"required"`
}

type CreateTaskForm struct {
	Task    *Task            `json:"task" binding:"required"`
	PoWData *ProofOfWorkData `json:"pow" binding:"required"`
}
