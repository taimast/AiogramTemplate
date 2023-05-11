import argparse
import os
from enum import StrEnum


class Action(StrEnum):
    DEPLOY = 'deploy'
    REDEPLOY = 'redeploy'
    UPDATE = 'update'
    PULL = 'pull'

    RESTART_DOCKER = 'restart_docker'
    STOP_DOCKER = 'stop_docker'
    START_DOCKER = 'start_docker'
    BUILD_DOCKER = 'build_docker'
    SETUP_DOCKER = 'setup_docker'
    REBUILD_DOCKER = 'rebuild_docker'


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--token',
        '-t',
        required=False,
        help="Github token",
        default=os.environ.get('GITHUB_TOKEN')
    )
    parser.add_argument(
        '--repo',
        '-r',
        required=True,
        help="Github repo name"
    )
    parser.add_argument(
        '--ip',
        '-i',
        required=True,
        help="Server IP"
    )
    parser.add_argument(
        '--username',
        '-u',
        required=False,
        help="Server username",
        default='root'
    )
    parser.add_argument(
        '--action',
        '-a',
        required=False,
        help="Action to perform",
        default=Action.DEPLOY.value,
        choices=[action.value for action in Action]
    )
    args = parser.parse_args()
    return args
