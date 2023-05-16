import time
from .__init__ import __version__


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def timecall():
    return time.time()


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError  # evil ValueError that doesn't tell you what the wrong value was


def norm(val):
    return np.linalg.norm(val)


def banner():
    banner_str = ('''
            EXAFS_GA ver %s
 _______________________________________
|    _______  __    _    _____ ____     |
|   | ____\ \/ /   / \  |  ___/ ___|    |
|   |  _|  \  /   / _ \ | |_  \___ \\    |
|   | |___ /  \  / ___ \|  _|  ___) |   |
|   |_____/_/\_\/_/   \_\_|   |____/    |
|_______________________________________|
    ''' % __version__)

    return banner_str
