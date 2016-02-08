from __future__ import print_function

import argparse
import getpass
import keyring
import time

import requests

from . import DEFAULTS
from .utils import get_task_data


KEYRING_SYSTEM_NAME = "taskwarrior-pomodoro-beeminder"
COMMANDS = {}


def command(fn):
    COMMANDS[fn.__name__] = fn
    return fn


@command
def increment_goal(args):
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

    auth_token = keyring.get_password(KEYRING_SYSTEM_NAME, args.username)
    if not auth_token:
        raise RuntimeError(
            "No auth token is currently stored for username {username}; "
            "store an auth token for {username} using the 'store_auth_token' "
            "subcommand before attempting to increment this goal.".format(
                username=args.username,
            )
        )

    result = requests.post(
        'https://www.beeminder.com/api/v1/users/{username}'
        '/goals/{goal}/datapoints.json?auth_token={token}'.format(
            username=args.username,
            goal=args.goal,
            token=auth_token,
        ),
        data={
            'timestamp': int(time.time()),
            'value': 1,
            'comment': task_data.get('description', ''),
        },
    )
    result.raise_for_status()


@command
def store_auth_token(args):
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
