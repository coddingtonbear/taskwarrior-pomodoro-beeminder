package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os/exec"
	"os/user"
	"strconv"
	"strings"
	"time"

	"github.com/howeyc/gopass"
	"github.com/lunixbochs/go-keychain"
	"github.com/ryanuber/go-glob"
	"gopkg.in/alecthomas/kingpin.v2"
	"gopkg.in/ini.v1"
)

var (
	autoincrement       = kingpin.Command("autoincrement", "Auto-increment a beeminder goal")
	autoincrementTaskID = autoincrement.Arg("taskId", "Task ID to increment").String()

	incrementGoal         = kingpin.Command("increment_goal", "Increment a beeminder goal")
	incrementGoalUsername = incrementGoal.Arg("username", "Username to use").String()
	incrementGoalGoal     = incrementGoal.Arg("goal", "Goal name to increment").String()
	incrementGoalTaskID   = incrementGoal.Flag("taskId", "Task ID to increment").String()

	storeAuthToken         = kingpin.Command("store_auth_token", "Store password information")
	storeAuthTokenUsername = storeAuthToken.Arg("username", "Username to store a password for").String()

	config  = kingpin.Flag("config", "Configuration file to use").Short('c').Default("~/.taskwarrior-pomodoro-beeminder.cfg").String()
	taskBin = kingpin.Flag("task-bin", "Path to taskwarrior binary").Default("/usr/local/bin/task").String()
	taskRc  = kingpin.Flag("taskrc", "Path to taskrc file").Default("~/.taskrc").String()
)

type taskData struct {
	UUID        string   `json:"uuid"`
	Description string   `json:"description"`
	Project     string   `json:"project"`
	Tags        []string `json:"tags"`
}

type goalData struct {
	username string
	goal     string
}

func main() {
	kingpin.UsageTemplate(kingpin.CompactUsageTemplate).Version("1.0").Author("Adam Coddington")
	commandName := kingpin.Parse()

	*config = expandUser(*config)
	*taskBin = expandUser(*taskBin)
	*taskRc = expandUser(*taskRc)

	cfg, err := ini.Load(*config)
	if err != nil {
		log.Fatalf("Unable to open configuration file at %s\n", *config)
	}

	switch commandName {
	case "autoincrement":
		doAutoincrement(cfg)
	case "increment_goal":
		doIncrementGoal(cfg)
	case "store_auth_token":
		doStoreAuthToken(cfg)
	default:
		fmt.Println("Please specify a command.")
	}
}

func doAutoincrement(cfg *ini.File) {
	task := getTaskData(*autoincrementTaskID)

	matchingGoals := getMatchingGoals(cfg, task)

	for _, goal := range matchingGoals {
		incrementBeeminderGoal(
			goal.username,
			goal.goal,
			task.Description,
		)
	}
}

func doIncrementGoal(cfg *ini.File) {
	taskDescription := ""

	if *incrementGoalTaskID != "" {
		taskDescription = getTaskData(*incrementGoalTaskID).Description
	}

	incrementBeeminderGoal(
		*incrementGoalUsername,
		*incrementGoalGoal,
		taskDescription,
	)
}

func doStoreAuthToken(cfg *ini.File) {
	fmt.Println(
		"Taskwarrior-Pomodoro-Beeminder needs your Beeminder " +
			"Personal Authentication Token to interact with your Beeminder " +
			"account.  You can find yours by going to " +
			"https://www.beeminder.com/api/v1/auth_token.json.",
	)
	fmt.Printf("Auth Token: ")
	pass, err := gopass.GetPasswd()
	if err == nil {
		keychain.Add(
			"taskwarrior-pomodoro-beeminder",
			*storeAuthTokenUsername,
			string(pass[:]),
		)
	}
}

func expandUser(path string) string {
	usr, _ := user.Current()
	dir := usr.HomeDir

	return strings.Replace(path, "~/", dir+"/", 1)
}

func getTaskData(id string) *taskData {
	output, err := exec.Command(
		*taskBin,
		"rc:"+*taskRc,
		"rc.json.array=off",
		id,
		"export",
	).Output()
	if err != nil {
		log.Fatal(err)
	}

	taskData := taskData{}
	merr := json.Unmarshal(output, &taskData)
	if merr != nil {
		fmt.Println("error:", merr)
	}

	return &taskData
}

func incrementBeeminderGoal(username string, goal string, message string) {
	token, err := keychain.Find(
		"taskwarrior-pomodoro-beeminder",
		*storeAuthTokenUsername,
	)
	if err != nil {
		log.Fatalf(
			"Unable to find stored authentication token for %s",
			username,
		)
	}

	fullURL := "https://www.beeminder.com/api/v1/users/" + username +
		"/goals/" + goal + "/datapoints.json?auth_token=" + token

	resp, err := http.PostForm(
		fullURL,
		url.Values{
			"timestamp": {strconv.FormatInt(int64(time.Now().Unix()), 10)},
			"value":     {"1"},
			"comment":   {message},
		},
	)
	if err == nil {
		if resp.StatusCode != 200 {
			log.Fatal(resp)
		} else {
			fmt.Println(resp)
		}
	} else {
		log.Fatal(err)
	}
}

func stringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

func taskMatchesConstraints(task *taskData, constraints []*ini.Key) bool {
	for _, constraint := range constraints {
		if constraint.Name() == "tags" {
			for _, expectedTag := range strings.Split(constraint.Value(), ",") {
				if !stringInSlice(expectedTag, task.Tags) {
					return false
				}
			}
		} else if constraint.Name() == "project" {
			if !glob.Glob(constraint.Value(), task.Project) {
				return false
			}
		}
	}
	return true
}

func getMatchingGoals(cfg *ini.File, task *taskData) []goalData {
	var goals []goalData

	defaultUsername := ""
	defaultSection, err := cfg.GetSection("")
	if err == nil {
		if defaultSection.HasKey("username") {
			defaultUsername = defaultSection.Key("username").Value()
		}
	}

	for _, section := range cfg.Sections() {
		if section.Name() == "DEFAULT" {
			continue
		}
		if taskMatchesConstraints(task, section.Keys()) {
			usernameKey, err := section.GetKey("username")
			username := defaultUsername
			if err == nil {
				username = usernameKey.Value()
			}
			goalName := section.Name()
			if section.HasKey("goal") {
				goalNameKey, err := section.GetKey("goal")
				if err == nil {
					goalName = goalNameKey.Value()
				}
			}

			goals = append(
				goals,
				goalData{
					username,
					goalName,
				},
			)
		}
	}

	return goals
}
