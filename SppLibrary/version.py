import sys

VERSION = '0.95'
RELEASE = 'beta'
TIMESTAMP = '20140807-120000'


def get_version(sep=' '):
    if RELEASE == 'beta':
        return VERSION
    return VERSION + sep + RELEASE


def get_full_version(who=''):
    sys_version = sys.version.split()[0]
    version = '%s %s (%s %s on %s)' \
        % (who, get_version(), _get_interpreter(), sys_version, sys.platform)
    return version.strip()


def _get_interpreter():
    if sys.platform.startswith('java'):
        return 'Jython'
    if sys.platform == 'cli':
        return 'IronPython'
    if 'PyPy' in sys.version:
        return 'PyPy'
    return 'Python'
