from fnmatch import fnmatch
import os

from six.moves import configparser


class ConfigManager(object):
    def __init__(self, path=None):
        self.config = configparser.SafeConfigParser()

        expanded = os.path.expanduser(path)
        if path and os.path.isfile(expanded):
            self.config.read([expanded])

    def __getattr__(self, attr):
        return getattr(self.config, attr)

    def _task_matches_constraints(self, task, constraints):
        for n, v in constraints.items():
            if n == 'tags':
                for tag in v.split(','):
                    if tag not in task.get('tags', []):
                        return False
            elif n == 'project':
                if not fnmatch(task.get('project', ''), v):
                    return False

        return True

    def find_matching_goals(self, task):
        matching_goals = set()

        sections = self.sections()
        for section in sections:
            section_data = dict(self.items(section))

            if self._task_matches_constraints(task, section_data):
                matching_goals.add(
                    (
                        section_data['username'],
                        # Default to section name for goal name.
                        section_data.get('goal', section),
                    )
                )

        return matching_goals
