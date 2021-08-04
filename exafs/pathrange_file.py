"""
Author: Andy Lau
Last Updated: 3/23/2021

Changes:

Input Range selected by user in a input files

# Format:
Paths,(S02_LOW,S02,HIGH,DELTA_S02),(SIGMA2_LOW,SIGMA2_High,DELTA_SIGMA2),(DELTAR_LOW,DELTAR_High,DELTA_DELTAR)

 User can create their own inputs files which corresponds to the
"""
import numpy as np

def raise_error(msg='Error'):
    raise Exception(msg)

def check_range(val_low,val_high,delta_val):
    if np.abs(val_high - val_low)/delta_val < 1:
        raise_error('Delta Spacing too high')
    try:
        range = np.arange(val_low,val_high,delta_val)
    except:
        pass
    return range

def read_pathrange_file(file,num_path):
    # Read in the custom input files
    raw_data = np.genfromtxt(file,delimiter=",")
    raw_npath = raw_data.shape[0]
    if num_path != raw_npath:
        raise_error("Mismatch in number of paths")

    if raw_data.shape[1] != 10:
        raise_error("Number of Columns not right")
    for i in range(num_path):
        check_range(raw_data[i][1],raw_data[i][2],raw_data[i][3])
        check_range(raw_data[i][4],raw_data[i][5],raw_data[i][6])
        check_range(raw_data[i][7],raw_data[i][8],raw_data[i][9])

    return raw_data

if __name__ == "__main__":
    file = 'test/test_custom_input.txt';
    read_pathrange_file(file,5);
