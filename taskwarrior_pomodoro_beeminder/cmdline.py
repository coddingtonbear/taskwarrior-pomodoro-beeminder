import argparse
import sys

from .commands import COMMANDS
from .config import ConfigManager


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', dest='config',
        default='~/.taskwarrior-pomodoro-beeminder.cfg',
    )
    parser.add_argument('subcommand', choices=COMMANDS.keys())

    args, extra = parser.parse_known_args(args)

    config = ConfigManager(args.config)
    COMMANDS[args.subcommand](config, extra)
