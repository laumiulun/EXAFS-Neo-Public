from .input_arg import *
from .helper import *
"""
Author: Andy Lau
Last Updated: 1/19/2021

Changes:

2/8/2021: Andy:
	- Function defintion for arr to be in 2D

1/20/2021: Andy:
	- Function definition for optional parameters.
	- Changes to allows for multiple inputs folder.

"""

def split_path_arr(arr_str,num_compounds):
	"""
	Read the path list
	"""
	starter = []
	end = []
	k = 0
	split_str = []
	for i in arr_str:
		if i == '[':
			starter.append(k)
		elif i == ']':
			end.append(k)
		k = k + 1

	assert(len(starter) == len(end)),'Bracket setup not right.'
	if num_compounds > 1:
		assert(num_compounds == len(starter)),'Number of compounds not matched.'
		assert(num_compounds == len(end)),'Number of compounds not matched.'

	# check if both are zeros, therefore the array is one 1 dimensions
	if len(starter) == 0 and len(end) == 0:
	# print("1D array only")
		split_str = list(arr_str.split(","))
	else:
	# # print("2D array")
		for i in range(len(starter)):
			split_str.append(arr_str[starter[i]+1:end[i]].split(","))

	return split_str

def optional_var(dict,name_var,alt_var,type_var):
	"""
	Detections of optional variables exists within input files, and
		put in corresponding default inputs parameters.

	"""
	# boolean needs special attentions
	if type_var == bool:
		if name_var in dict:
			return_var = str_to_bool(dict[name_var])
		else:
			return_var = alt_var
	else:
		if name_var in dict:
			return_var = type_var(dict[name_var])
		else:
			return_var = type_var(alt_var)
	return return_var

Inputs_dict = file_dict['Inputs']
Populations_dict = file_dict['Populations']
Mutations_dict = file_dict['Mutations']
Paths_dict = file_dict['Paths']
Larch_dict = file_dict['Larch_Paths']
Outputs_dict = file_dict['Outputs']

# Inputs
num_compounds = optional_var(Inputs_dict,'num_compounds',1,int)
csv_file = Inputs_dict['csv_file']
output_file = Inputs_dict['output_file']

# Compounds
if num_compounds > 1:
	try:
		feff_file = list(Inputs_dict['feff_file'].split(","))
	except:
		print("Feff folder is not correct")
else:
	feff_file = Inputs_dict['feff_file']

try:
	csv_series = str_to_bool(Inputs_dict['csv_series'])
	if csv_series == True:
		csv_file = list(Inputs_dict['csv_file'].split(","))
except KeyError:
	csv_series = False

# population
size_population = int(Populations_dict['population'])
number_of_generation = int(Populations_dict['num_gen'])
best_sample = int(Populations_dict['best_sample'])
lucky_few = int(Populations_dict['lucky_few'])

# Mutations
chance_of_mutation = int(Mutations_dict['chance_of_mutation'])
original_chance_of_mutation = int(Mutations_dict['original_chance_of_mutation'])
chance_of_mutation_e0 = int(Mutations_dict['chance_of_mutation_e0'])
mutated_options = int(Mutations_dict['mutated_options'])

# Paths
if num_compounds > 1:
	individual_path = True
else:
	individual_path = str_to_bool(Paths_dict['individual_path'])
	pathrange = int(Paths_dict['path_range'])

try:
	optimize_only = str_to_bool(Paths_dict['optimize_only'])
except KeyError:
	optimize_only = False

try:
	path_optimize = str_to_bool(Paths_dict['path_optimize'])
except KeyError:
	path_optimize = False

try:
	path_optimize_percent = float(Paths_dict['path_optimize_percent'])
except KeyError:
	path_optimize_percent = 0.01

path_list = split_path_arr(Paths_dict['path_list'],num_compounds)
path_optimize = optional_var(Paths_dict,'path_optimize',False,bool)
path_optimize_percent = optional_var(Paths_dict,'path_optimize_percent',0.01,float)

# Larch Paths
Kmin = float(Larch_dict['kmin'])
Kmax = float(Larch_dict['kmax'])
KWEIGHT = float(Larch_dict['kweight'])
deltak = float(Larch_dict['deltak'])
rbkg = float(Larch_dict['rbkg'])
bkgkw = float(Larch_dict['bkgkw'])
bkgkmax = float(Larch_dict['bkgkmax'])

# Output
printgraph = str_to_bool(Outputs_dict['print_graph'])
num_output_paths = str_to_bool(Outputs_dict['num_output_paths'])
steady_state = optional_var(Outputs_dict,'steady_state_exit',False,bool)
