# Parser for Inputs files

import os
import configparser
from .helper import bcolors

def CheckKey(dict, key_list):
    for i in range(len(key_list)):
        try:
            dict[key_list[i]]
        except KeyError:
            raise KeyError(str(key_list[i]) + ' is missing')
            # break
def CheckOptionalKey(dict,optional_key_list):
	optional_key = []
	for i in range(len(optional_key_list)):
		try:
			dict[optional_key_list[i]]
		except KeyError:
			optional_key.append(optional_key_list[i])

	return optional_key
# config the parser to the right order:
def read_input_file(input_file,verbose=False):
    config = configparser.ConfigParser()
    config.read(input_file)
    config = config._sections

    # read into each dict
    file_min = ['Inputs','Populations','Mutations','Paths','Larch_Paths','Outputs']
    CheckKey(config,file_min)

    Inputs_dict = config['Inputs']
    Populations_dict = config['Populations']
    Mutations_dict = config['Mutations']
    Paths_dict = config['Paths']
    Larch_dict = config['Larch_Paths']
    Outputs_dict = config['Outputs']

    # Checking for minimum inputs
    input_min = ['csv_file','output_file','feff_file']
    CheckKey(Inputs_dict,input_min)

    population_min = ['population','num_gen','best_sample','lucky_few']
    CheckKey(Populations_dict,population_min)

    mutation_min = ['chance_of_mutation','original_chance_of_mutation','chance_of_mutation_e0','mutated_options']
    CheckKey(Mutations_dict,mutation_min)

    path_min = ['path_range','path_list','individual_path']
    path_optional = ['path_optimize','optimize_percent']
    CheckKey(Paths_dict,path_min)
    path_missing = CheckOptionalKey(Paths_dict,path_optional)

    larch_min = ['kmin','kmax','kweight','deltak','rbkg','bkgkw','bkgkmax']
    CheckKey(Larch_dict,larch_min)

    output_min =['print_graph','num_output_paths']
    output_optional = ['steady_state_exit']
    CheckKey(Outputs_dict,output_min)
    output_missing = CheckOptionalKey(Outputs_dict,output_optional)
    # Adjust values

    # Pack all of them into a single dicts
    file_dict = {}
    file_dict['Inputs'] = Inputs_dict
    file_dict['Populations'] = Populations_dict
    file_dict['Mutations'] = Mutations_dict
    file_dict['Paths'] = Paths_dict
    file_dict['Larch_Paths'] = Larch_dict
    file_dict['Outputs'] = Outputs_dict

    if verbose == True:
        print_input_file(file_dict)

    return file_dict

def print_input_file(file_dict):
    for key,value in file_dict.items():
        print("[" +bcolors.BOLD + str(key)+ bcolors.ENDC +"]")
        for inner_key,inner_value in value.items():
            print('---'  +  inner_key + ": " +inner_value)


## Need to run some sample:
# if __name__ == '__main__':
#
#     checkKey()
