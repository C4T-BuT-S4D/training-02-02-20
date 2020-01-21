package main

import (
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"net/http"
)

func (ks *KTFServer) statusHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "OK"})
	}
}

func (ks *KTFServer) registerHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		user := new(User)
		if err := c.ShouldBindJSON(user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		if err := ks.DataController.AddUser(user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, user)
	}
}

func (ks *KTFServer) loginHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		data := new(LoginForm)
		if err := c.ShouldBindJSON(data); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, err := ks.DataController.GetUser(data.Username)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		if user.Password != data.Password {
			c.JSON(http.StatusBadRequest, gin.H{"error": ErrInvalidCreds.Error()})
			return
		}

		ks.DataController.SetSession(data.Username, c)
		c.JSON(http.StatusOK, gin.H{"status": "OK"})
	}
}

func (ks *KTFServer) logoutHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.SetCookie("session", "", 0, "/", "", false, true)
		c.JSON(http.StatusOK, gin.H{"status": "OK"})
	}
}

func (ks *KTFServer) meHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		user, _ := c.Get("user")
		c.JSON(http.StatusOK, user)
	}
}

func (ks *KTFServer) userProfileHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		userForm := new(GetUserForm)
		if err := c.ShouldBindUri(userForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, err := ks.DataController.GetUserProfile(userForm)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, user)
	}
}

func (ks *KTFServer) createTaskHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		task := new(Task)
		if err := c.ShouldBindJSON(task); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		tmpID, _ := uuid.NewRandom()
		task.ID = tmpID.String()

		user, _ := c.Get("user")
		username := user.(*User).Username
		task.Author = username

		if err := ks.DataController.AddTask(task, username); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, task)
	}
}

func (ks *KTFServer) getTaskHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		taskForm := new(GetTaskForm)
		if err := c.ShouldBindUri(taskForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, _ := c.Get("user")
		task, err := ks.DataController.GetTaskSafe(taskForm, user.(*User).Username)
		if err != nil {
			status := http.StatusBadRequest
			if err == ErrTaskNotFound {
				status = http.StatusNotFound
			}
			c.JSON(status, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, task)
	}
}

func (ks *KTFServer) listTasksHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		listingForm := new(TaskListingForm)
		if err := c.ShouldBindQuery(listingForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		taskList, err := ks.DataController.ListTasks(listingForm)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, taskList)
	}
}

func (ks *KTFServer) submitTaskHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		getForm := new(GetTaskForm)
		if err := c.ShouldBindUri(getForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		submitForm := new(TaskSubmitForm)
		if err := c.ShouldBindJSON(submitForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, _ := c.Get("user")
		score, err := ks.DataController.SubmitTask(getForm, submitForm, user.(*User).Username)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "OK", "score": score})
	}
}

func (ks *KTFServer) userRankingHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		rankingForm := new(UserRankingForm)
		if err := c.ShouldBindQuery(rankingForm); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		data, err := ks.DataController.GetUserRankings(rankingForm)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, data)
	}
}
