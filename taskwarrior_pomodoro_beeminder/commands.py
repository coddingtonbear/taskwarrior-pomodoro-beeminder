from __future__ import print_function

import argparse
import getpass

from . import beeminder, DEFAULTS
from .utils import get_task_data


COMMANDS = {}


def command(fn):
    COMMANDS[fn.__name__] = fn
    return fn


@command
def autoincrement(config, args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--task-bin',
        default=DEFAULTS['task_bin'],
    )
    parser.add_argument(
        '--taskrc',
        default=DEFAULTS['taskrc'],
    )
    parser.add_argument('task_id', nargs='?')
    args = parser.parse_args(args)

    if args.task_id:
        task_data = get_task_data(
            args.task_id,
            task_path=args.task_bin,
            task_config=args.taskrc,
        )
    else:
        task_data = {}

    matching_targets = config.find_matching_goals(task_data)

    message = task_data.get('description', '')
    for username, goal in matching_targets:
        beeminder.increment_goal(username, goal, message)


@command
def increment_goal(config, args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--task-bin',
        default=DEFAULTS['task_bin'],
    )
    parser.add_argument(
        '--taskrc',
        default=DEFAULTS['taskrc'],
    )
    parser.add_argument('username')
    parser.add_argument('goal')

    if args.task_id:
        task_data = get_task_data(
            args.task_id,
            task_path=args.task_bin,
            task_config=args.taskrc,
        )
    else:
        task_data = {}

    message = task_data.get('description', '')
    beeminder.increment_goal(args.username, args.goal, message)


@command
def store_auth_token(config, args):
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    args = parser.parse_args(args)

    password = ''
    while not password:
        print(
            "Taskwarrior-Pomodoro-Beeminder needs your Beeminder "
            "Personal Authentication Token to interact with your Beeminder "
            "account.  You can find yours by going to "
            "https://www.beeminder.com/api/v1/auth_token.json."
        )
        password = getpass.getpass(
            "Personal Authentication Token for {username}: ".format(
                username=args.username,
            )
        )

    keyring.set_password(
        KEYRING_SYSTEM_NAME,
        args.username,
        password
    )
