import json
import logging
import os
import subprocess

from . import DEFAULTS


logger = logging.getLogger(__name__)


def get_task_data(task_id, task_path=None, task_config=None):
    if task_path is None:
        task_path = DEFAULTS['task_bin']
    if task_config is None:
        task_config = DEFAULTS['task_config']

    try:
        output = subprocess.check_output(
            [
                task_path,
                'rc:{path}'.format(path=os.path.expanduser(task_config)),
                task_id,
                'export',
            ]
        )
        return json.loads(output)
    except Exception as e:
        logger.exception(
            'Error encountered while fetching task data for %s: %s',
            task_id,
            str(e)
        )
        return {}
