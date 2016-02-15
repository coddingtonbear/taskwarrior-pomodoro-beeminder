Taskwarrior Pomodoro Beeminder Incrementer
==========================================

Usage:

1. Store your Beeminder Personal Authentication Token using:

```
taskwarrior-pomodoro-beeminder store_auth_token <username>
```

2. Configure [Taskwarrior Pomodoro](https://github.com/coddingtonbear/taskwarrior-pomodoro) to
   increment your Beeminder goal by entering the following into your ``~/.taskrc``:

```
pomodoro.postCompletionCommand=/usr/local/bin/taskwarrior-pomodoro-beeminder increment_goal <username> <goal slug>
```
