import argparse
import sys

from .commands import COMMANDS


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('subcommand', choices=COMMANDS.keys())

    args, extra = parser.parse_known_args(args)

    COMMANDS[args.subcommand](extra)
