# Import Library
from .import_lib import *
from .input_arg import *
from .helper import *

if timeing_mode:
    t1 = timecall()

from psutil import cpu_count
# Set the number of threads
import os,copy,random,logging
os.environ['NUMEXPR_MAX_THREADS'] = str(cpu_count())
import operator
import sys, csv
import datetime,time
from operator import itemgetter
import numpy as np
import larch
import pathlib
larch_version = larch.__version__.split('.')
if int(larch_version[2]) >= 55:
    # Old versions
    from larch.io import read_ascii
    from larch.xafs import autobk
    from larch.xafs import feffdat
    from larch.xafs import xftf
else:
    # Old versions
    from larch_plugins.io import read_ascii
    from larch_plugins.xafs import autobk
    from larch_plugins.xafs import feffdat
    from larch_plugins.xafs import xftf
from larch import Interpreter
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.integrate import simps
import subprocess
from .pathrange_file import *
# from multiprocessing import Pool
# import multiprocessing as mp
# import ray
# from multiprocessing import Pool as ProcessPool
# from multiprocessing.dummy import Pool as ThreadPool  ### this uses threads



if timeing_mode:
    initial_elapsed = timecall()- t1
    print('Inital import function took %.2f second' %initial_elapsed)
