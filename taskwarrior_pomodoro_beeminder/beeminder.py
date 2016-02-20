import time

import keyring
import requests


KEYRING_SYSTEM_NAME = "taskwarrior-pomodoro-beeminder"


def increment_goal(username, goal_slug, message=''):
    auth_token = keyring.get_password(KEYRING_SYSTEM_NAME, username)
    if not auth_token:
        raise RuntimeError(
            "No auth token is currently stored for username {username}; "
            "store an auth token for {username} using the 'store_auth_token' "
            "subcommand before attempting to increment this goal.".format(
                username=username,
            )
        )

    result = requests.post(
        'https://www.beeminder.com/api/v1/users/{username}'
        '/goals/{goal}/datapoints.json?auth_token={token}'.format(
            username=username,
            goal=goal_slug,
            token=auth_token,
        ),
        data={
            'timestamp': int(time.time()),
            'value': 1,
            'comment': message,
        },
    )
    result.raise_for_status()
