from .parser import *
import argparse, os, sys
parser = argparse.ArgumentParser()

parser.add_argument('-i','--input',help="Submit input file to EXAFS")
parser.add_argument("-v","--verbose",help="output verbosity",action="store_true")
parser.add_argument("-s","--show_input",help = "show input file",action="store_true")
parser.add_argument("-t",help = "Timeing mode",action="store_true")
parser.add_argument("-d",help = "Debug mode",action="store_true")

args = parser.parse_args()
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

if args.input!=None:
    file_path = os.path.join(os.getcwd(),args.input)
    file_dict = read_input_file(file_path)

# Read input file
if args.show_input==True and args.input != None:
    read_input_file(file_path,verbose=True)

debug_mode = args.d
timeing_mode = args.t
