"""
Authors    Matthew Adas, Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      madas@hawk.iit.edu, andylau@u.boisestate.edu
Version    0.2.0
Date       July 4, 2021

Constains misc functions for GUI
"""
import platform,re,sys,os

def get_platform():
    os_name = platform.system()
    return os_name

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def check_sabcor_folder(ostype):
    # check sabcor folder if it initialize
    if ostype == "Windows":
            print("Window doesn't have sabcor capabilites, continue without sabcor")
    else:
        if not os.listdir('../contrib/sabcor'):
            print("Please Initialize \"Sabcor\" as submodules")
            exit()
        else:
            
            if os.path.exists('../contrib/sabcor/sabcor'):
                print("Please make the sabcor exectuable first in '../contrib/sabcor' directory")
            else:
                sys.path.insert(1,'../contrib/sabcor')
                from sabcor import check_executable

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    os_name = get_platform()
    print(os_name)
