
"""
Author: Miu Lun Lau
Date: Mar 18, 2021
Progress
1. Points the FEFF file [Done]
2. Read the FEFF file and adjust the print parameters [Done]
3. Find the FEFF8L exectuable in anaconda [Done]
4. Create new files based on directory [Done]
5. Make new directory based on the feff file and execute the file [Done]
6. Compute the number of scattering files [Done]
"""

import os,sys
import platform
import pathlib
from subprocess import Popen, PIPE
import shutil
import fnmatch
import argparse

# Import Larch instead
import larch.xafs as xafs
# FEFF file_score
def read_feff_file(file,replace=True):
    # Read the file
    try:
        pathlib.Path(file).is_file()
    except FileNotFoundError:
        print("File Not right!")
    with open(file, 'r') as reader:
        file_arr = []
        for i,line in enumerate(reader.readlines()):
            file_arr.append(line.rstrip())
            if 'CONTROL' in line:
                control_ind = i
            elif 'PRINT' in line:
                print_ind = i

    file_arr[control_ind] =  'CONTROL   1      1     0     1     1      1'
    file_arr[print_ind] = 'PRINT     3      3     0     3     1      3'
    if replace:
        with open(file, 'w') as f:
            for i,line in enumerate(file_arr):
                f.write(file_arr[i] + '\n')

def calculate_nfeff(dest_path):
    """
    Calculate number of feff
    """
    num_feff_file = 0
    dest_path = pathlib.Path(dest_path)
    # check if it dirs
    if dest_path.is_dir():
        for i in dest_path.iterdir():
            # convert to pathlib
            file = pathlib.Path(i).name
            # matches the feff files
            if fnmatch.fnmatch(file,'feff????.dat'):
                num_feff_file +=1
    print('Number of FEFF file contains: {}'.format(num_feff_file))
    return num_feff_file

def find_feff8l_larch(file,copy2fold=False):
    folder_path = pathlib.Path(file)
    if copy2fold:
        try:
            folder_path.with_suffix('').mkdir()
        except FileExistsError:
            print('Folder already_exists')

        # copy feff file into new folder
        src_file_path = pathlib.Path.cwd().joinpath(folder_path)
        dest_file_path = pathlib.Path.cwd().joinpath(folder_path.with_suffix('').joinpath('feff.inp'))
        shutil.copy(src_file_path,dest_file_path)
        return dest_file_path

    else:
        # No copying to new folder.
        src_file_path = pathlib.Path.cwd().joinpath(folder_path)
        return src_file_path


def call_feff8l_inp_larch(dest_path):
    print(dest_path)
    print(dest_path.parent)
    xafs.feff8l(folder=dest_path.parent,feffinp=dest_path)


def create_feff_folder(file):
    read_feff_file(file)
    dest_file_path = find_feff8l_larch(file)
    call_feff8l_inp_larch(dest_file_path)
    calculate_nfeff(dest_file_path.parent)


# Example FEFF file
if __name__ == "__main__":
    # feff_file = 'test_feff/feff2.inp'

    len_arg = len(sys.argv)
    if (len_arg !=2):
        print("Invalid number of arguments")
        print("python feff_folder_larch.py <feff.inp>")
        sys.exit()
    feff_file = sys.argv[1]
    if pathlib.Path(feff_file).is_file():
        create_feff_folder(feff_file)
    else:
        print("FEFF file doesn't exists")
        sys.exit()
# else:
