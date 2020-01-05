package main

type User struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
	Name     string `json:"name" binding:"required"`
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
