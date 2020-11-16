from .input_arg import *
from .helper import *
# ------------------------------------
# Andy Lau
# 4/22/2019
# goal : Parsed the ini into each specific documents.
#-------------------------------------
# print(file_dict)
Inputs_dict = file_dict['Inputs']
Populations_dict = file_dict['Populations']
Mutations_dict = file_dict['Mutations']
Paths_dict = file_dict['Paths']
Larch_dict = file_dict['Larch_Paths']
Outputs_dict = file_dict['Outputs']

# Input
csv_file = Inputs_dict['csv_file']
output_file = Inputs_dict['output_file']
feff_file = Inputs_dict['feff_file']

try:
	csv_series = str_to_bool(Inputs_dict['csv_series'])
	if csv_series == True:
		# print(csv_file)
		csv_file = list(Inputs_dict['csv_file'].split(","))
		# print(type(csv_file))
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
individual_path = str_to_bool(Paths_dict['individual_path'])
pathrange = int(Paths_dict['path_range'])
path_list = list(Paths_dict['path_list'].split(","))
try:
	path_optimize = str_to_bool(Paths_dict['path_optimize'])
except KeyError:
	path_optimize = False

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
try:
	steady_state = str_to_bool(Outputs_dict['steady_state'])
except KeyError:
	steady_state = False
