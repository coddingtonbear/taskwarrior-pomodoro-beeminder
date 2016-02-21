Taskwarrior Pomodoro Beeminder Incrementer
==========================================

Simple Usage
------------

1. Store your Beeminder Personal Authentication Token using:

   ```
   taskwarrior-pomodoro-beeminder store_auth_token <YOUR BEEMINDER USERNAME>
   ```

2. Configure [Taskwarrior Pomodoro](https://github.com/coddingtonbear/taskwarrior-pomodoro) to
   increment your Beeminder goal by entering the following into your ``~/.taskrc``:

   ```
   pomodoro.postCompletionCommand=/usr/local/bin/taskwarrior-pomodoro-beeminder increment_goal <YOUR BEEMINDER USERNAME> <YOUR BEEMINDER GOAL SLUG>
   ```


Configurable Usage
------------------

1. Store your Beeminder Personal Authentication Token using:

   ```
   taskwarrior-pomodoro-beeminder store_auth_token <YOUR BEEMINDER USERNAME>
   ```

2. Create a file in your home directory named ``.taskwarrior-pomodoro-beeminder.cfg`` with contents something like the following:

   ```
   # These settings will apply to all below sections
   [DEFAULT]
   username=<YOUR BEEMINDER USERNAME>
   
   # Each section configures the application to post to a specific goal when
   # a task matches its constraints.  If you do not specify a goal slug,
   # we'll assume that the goal slug in Beeminder matches the section name.
   
   # For incrementing a specific goal for only tasks having specified tags:
   # Note that tags are comma-separated, and *all* tags listed must be present
   # on the given task.  If you would like to increment a given goal when either
   # of two tags are present, just create a new section.
   [some-arbitrary-name]
   goal=<YOUR BEEMINDER GOAL SLUG>
   tags=<TAG ONE>,<TAG TWO>
   
   # For incrementing a specific goal for only tasks having a specified project:
   # Note that you can use globbing; for example, if you wanted to increment this
   # goal only when a task's project starts with "work", you could enter "work*"
   [some-other-arbitrary-name]
   goal=<YOUR BEEMINDER GOAL SLUG>
   project=<YOUR PROJECT NAME>
   ```

3. Configure [Taskwarrior Pomodoro](https://github.com/coddingtonbear/taskwarrior-pomodoro) to
   increment the relevant Beeminder goals by entering the following into your ``~/.taskrc``:

   ```
   pomodoro.postCompletionCommand=/usr/local/bin/taskwarrior-pomodoro-beeminder autoincrement
   ```

Example Config
--------------

This is my ``~/.taskwarrior-pomodoro-beeminder.cfg`` that you can use as an example.

```
[DEFAULT]
username=coddingtonbear

[pomodoros]

[pomodoros-mig]
tags=MIG

[pomodoros-mig-coursera]
goal=pomodoros-mig
project=coursera*

[pomodoros-opensource]
tags=Opensource

[pomodoros-work]
tags=Work
```
