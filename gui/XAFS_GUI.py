"""
Authors    Matthew Adas, Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      madas@hawk.iit.edu, andylau@u.boisestate.edu
Version    0.0
Date       Nov 3, 2020

Please start the program within the "gui" directory, or "select file" buttons won't start the user in EXAFS.
"Select Directory" button starts the user in EXAFS/path_files/Cu
"""

# Import Basic libraries
import os,subprocess,queue,random,signal
from pathlib import Path
import numpy as np
from threading import Thread

# Import Tkiner
import tkinter as tk
from tkinter import ttk,Tk,N,W,E,S,StringVar,IntVar,DoubleVar,BooleanVar,Checkbutton,NORMAL,DISABLED,filedialog,messagebox,PhotoImage,LabelFrame,scrolledtext
from tkinter.font import Font

from psutil import cpu_count
os.environ['NUMEXPR_MAX_THREADS'] = str(cpu_count())
# import Larch
from larch.xafs import autobk, xftf
import larch
from larch.io import read_ascii

# import matplotlib for figures
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Import custom libraries
import EXAFS_Analysis

class BKG_plot:
    def __init__(self,frame,larch):
        self.mylarch = larch
        self.fig = Figure(figsize=(3.75, 3.75), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(column=2,row=1,rowspan=8,sticky="nsew",
            padx = 5,pady=5)
        self.ax = self.fig.add_subplot(111)
        # create toolbar above
        self.toolbarFrame = tk.Frame(master=frame)
        self.toolbarFrame.grid(column=2,row=0,rowspan=1,sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

    def read_file(self,file,rbkg,bkg_kw,bkg_kmax,k_min,k_max,delta_k,kweight):
        try:
            file = str(file.get())
        except ValueError:
            pass
        self.data = read_ascii(file)
        try:
            self.data.chi
        except AttributeError:
            autobk(self.data,
                rbkg=float(rbkg.get()),
                kweight=float(bkg_kw.get()),
                kmax=float(bkg_kmax.get()),
                _larch =self.mylarch)
        self.small = int(k_min.get()/delta_k.get())
        self.big = int(k_max.get()/delta_k.get())

        xftf(self.data.k, self.data.chi, kmin=float(k_min.get()), kmax=float(bkg_kmax.get()), dk=4,
        window='hanning',kweight=float(kweight.get()), group=self.data, _larch=self.mylarch)

    def draw_background(self,file,rbkg,bkg_kw,bkg_kmax,k_min,k_max,delta_k,kweight):
        self.ax.clear()
        self.kweight = kweight
        self.read_file(file,rbkg,bkg_kw,bkg_kmax,k_min,k_max,delta_k,kweight)
        self.ax.plot(self.data.energy,self.data.mu,'.-',label='Data')
        # self.ax.plot(self.data.energy[self.small:self.big],self.data.mu[self.small:self.big],'.-',label='Data')
        self.ax.plot(self.data.energy,self.data.bkg,label='Background')
        self.ax.legend()
        self.ax.set_ylabel("$\mu$ (E)")
        self.ax.set_xlabel("Energy (eV)")
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_kspace(self):
        self.ax.clear()
        self.ax.plot(self.data.k,self.data.chi*self.data.k**self.kweight.get(),'b',label='K Space')
        # self.ax.plot(self.data.k[self.small:self.big],self.data.chi[self.small:self.big]*self.data.k[self.small:self.big]**2,'b',label='K Space')
        self.ax.set_xlabel('$k$ (Å$^{-1}$)')
        self.ax.set_ylabel('$k\chi(k)$')
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_rspace(self):
        self.ax.clear()
        self.ax.plot(self.data.r,self.data.chir_mag,'b',label='R Space')
        self.ax.set_xlabel('$r$ (Å$^{-1}$)')
        self.ax.set_ylabel('$\chi(r)$')
        self.fig.tight_layout()
        self.canvas.draw()

class Analysis_Plot:
    def __init__(self,frame,larch):
        self.mylarch = larch
        self.fig = Figure(figsize=(3.5,3.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        # Create inital figure canvas
        self.canvas.get_tk_widget().grid(column=0,row=5,columnspan=3,sticky="nsew",
            padx = 5,pady=5)
        self.ax = self.fig.add_subplot(111)
        # create toolbar
        self.toolbarFrame = tk.Frame(master=frame)
        self.toolbarFrame.grid(column=0,row=6,columnspan=3,sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)
        self.params = {}

    def setup_params(self,params):
        self.params = params

    def setup_dirs(self,dir):
        self.dir = dir

    def setup_paths(self,paths):
        self.paths = paths

    def extract_and_run(self,output_folder):

        self.EXAFS_Analysis = EXAFS_Analysis.EXAFS_Analysis(self.paths,self.dir,self.params)
        self.EXAFS_Analysis.extract_data()

        self.EXAFS_Analysis.larch_init()
        self.EXAFS_Analysis.larch_score()
        self.EXAFS_Analysis.individual_fit()
        self.EXAFS_Analysis.construct_latex_table()

        self.EXAFS_Analysis.export_files(header='Test',dirs=output_folder.get())
        # Cu_10.export_igor_individual('export/Cu_10/Cu_10.ipf')
        self.EXAFS_Analysis.export_igor_individual(os.path.join(output_folder.get(),'Test.ipf'))

        return self.EXAFS_Analysis.return_str,self.EXAFS_Analysis.latex_table_str

    def plot_k_r_space(self):
        self.fig.clf()
        self.EXAFS_Analysis.plot(fig_gui=self.fig)
        self.canvas.draw()

    def plot_error(self):
        self.fig.clf()
        self.EXAFS_Analysis.plot_error(fig_gui=self.fig)
        self.canvas.draw()

class Console():
    def __init__(self,tkFrame,command):

        self.tkframe = tkFrame
        self.p = subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # Tracking the line
        self.line_start = 0
        self.alive = True
        # Create two new threads
        Thread(target=self.readFromProccessOut).start()
        Thread(target=self.readFromProccessErr).start()

        self.writeLoop()

    def writeLoop(self):
        "Used to write data from stdout and stderr to the Text widget"
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.tkframe.after(50,self.writeLoop)
        else:
            self.destroy()

    def write(self,string):
        self.tkframe.insert(tk.END, string)
        self.tkframe.see(tk.END)
        self.line_start+=len(string)

    def readFromProccessOut(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode('utf-8')
            self.outQueue.put(data)

    def readFromProccessErr(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode('utf-8')
            self.errQueue.put(data)

    def destroy(self):
        "This is the function that is automatically called when the widget is destroyed."
        self.alive=False
        # write exit() to the console in order to stop it running
        # self.p.stdin.write("exit()\n".encode('utf-8'))
        self.p.stdin.flush()

class App():
    def __init__(self):
        # Larch
        self.mylarch = larch.Interpreter()
        self.root = Tk(className='EXAFS Neo GUI')
        self.root.wm_title("Graphical User Interface for EXAFS Analysis")

        self.root.geometry("650x500")
        # self.root.minsize(550, 550)
        # self.root.maxsize(750,1125)
        # self.root.resizable(False, False)
        img = PhotoImage(file='media/icon.png')
        self.root.tk.call('wm','iconphoto',self.root._w,img)

        self.padx = 5
        self.pady = 3

        # Font
        self.entryFont = Font(family="TkFixedFont", size=10)
        self.menuFont = Font(family="TkMenuFont",size=10)
        self.labelFont = Font(family="TkTextFont", size=11)
        # Generate the mainframe
        self.mainframe = ttk.Notebook(self.root,height=40,padding="5")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # self.root.columnconfigure(0,weight=1)
        # self.root.rowconfigure(1,weight=1)
        # self.root.rowconfigure(0,weight=4)

        # Initalize variable
        self.initialize_var()
        self.initialize_tab()

        self.Build_tabs()

    def initialize_var(self):
        """
        Initalize all possible variables in the gui.

        Future additions starts here.
        """
        # Inputs
        self.data_file = StringVar(self.root,'Please choose a file')
        self.temp_data_file = StringVar(self.root,'Please choose a file')
        self.output_file = StringVar(self.root,'Please choose a file')
        self.feff_file = StringVar(self.root,'Please choose a directory')
        self.series = BooleanVar(self.root,'False')
        # Populations
        self.populations = IntVar(self.root,1000)
        self.num_gen = IntVar(self.root,100)
        self.best_sample = IntVar(self.root,20)
        self.lucky_few = IntVar(self.root,20)

        # Mutations
        self.chance_of_mutation = IntVar(self.root,20)
        self.orginal_chance_of_mutation = IntVar(self.root,20)
        self.chance_of_mutation_e0 = IntVar(self.root,20)
        self.mutation_options = IntVar(self.root,0)

        # Paths
        self.individual_path = BooleanVar(self.root,False)
        self.path_range = IntVar(self.root,20)
        temp_list = ",".join(np.char.mod('%i', np.arange(1,self.path_range.get()+1)))
        self.path_list = StringVar(self.root,temp_list)
        self.path_optimize = BooleanVar(self.root,False)

        # Larch Paths
        self.kmin = DoubleVar(self.root,2.5)
        self.kmax = DoubleVar(self.root,20)
        self.k_weight = DoubleVar(self.root,2)
        self.delta_k = DoubleVar(self.root,0.05)
        self.r_bkg = DoubleVar(self.root,1.0)
        self.bkg_kw = DoubleVar(self.root, 1.0)
        self.bkg_kmax = DoubleVar(self.root, 15)

        #Outputs
        self.print_graph = BooleanVar(self.root, False)
        self.num_output_paths = BooleanVar(self.root, True)
        self.steady_state_exit = BooleanVar(self.root, True)

        # Pertubutuions
        self.n_ini = IntVar(self.root,100)

    def initialize_tab(self):
        """
        Initialize tab for the main frame. more tabs
        """

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('TkHeadingFont','11') )

        height=1
        self.tab_Inputs = tk.Frame(self.mainframe,height=height)
        self.tab_Populations = tk.Frame(self.mainframe,height=height)
        self.tab_Paths = tk.Frame(self.mainframe,height=height)
        self.tab_Mutation = tk.Frame(self.mainframe,height=height)
        self.tab_Larch = tk.Frame(self.mainframe,height=height)
        self.tab_Bkg = tk.Frame(self.mainframe,height=height)
        self.tab_Output = tk.Frame(self.mainframe,height=height)
        self.tab_Analysis = tk.Frame(self.mainframe,height=height)
        # self.tab_About = tk.Frame(self.mainframe,height=height)

        # self.tab_Pertub = tk.Frame(self.mainframe,height=height)

        self.mainframe.add(self.tab_Inputs, text="Inputs")
        self.mainframe.add(self.tab_Populations, text="Populations")
        self.mainframe.add(self.tab_Paths, text="Paths")
        self.mainframe.add(self.tab_Mutation, text="Mutations")
        self.mainframe.add(self.tab_Larch, text="Larch")
        self.mainframe.add(self.tab_Bkg, text="Background Plots")
        self.mainframe.add(self.tab_Output, text="Outputs")
        self.mainframe.add(self.tab_Analysis, text='Analysis')
        # self.mainframe.add(self.tab_About, text='About')
        self.mainframe.grid(row=0,column=0,columnspan=4,padx=self.padx,pady=self.pady,sticky=E+W+N+S)

    def description_tabs(self,arr,tabs,sticky=(W,E),row=None):
        if row is not None:
            assert len(row) == len(arr);
        for i,inputs in enumerate(arr):
            entry = ttk.Label(tabs,text=inputs,font=self.labelFont)
            if row is not None:
                k = row[i]
            else:
                k = i
            entry.grid_configure(column=0,row=k,sticky=sticky,padx=self.padx,pady=self.pady)

    def Build_tabs(self):
        """
        Build tabs
        """
        # Building all arrays
        self.Build_global()
        self.Build_inputs_tab()
        self.Build_population_tab()
        self.Build_path_tab()
        self.Build_mutations_tab()
        self.Build_larch_tab()
        self.Build_background_tab()
        self.Build_output_tab()
        self.Build_analysis_tab()
        # self.Build_about()

        self.mainframe.grid_rowconfigure(0,weight=1)
        self.mainframe.grid_columnconfigure(0,weight=1)
        self.mainframe.grid_columnconfigure(1,weight=1)

    def Write_ini(self,filename):
        inputs = ("[Inputs] \ncsv_file = {data} \noutput_file = {out} \nfeff_file = {feff}\ncsv_series = {series}"
            .format(data=str(self.data_file.get()),
                    out=str(self.output_file.get()),
                    feff=str(self.feff_file.get()),
                    series=str(self.series.get())))

        populations = ("\n\n[Populations] \npopulation = {pop} \nnum_gen = {numgen} \nbest_sample = {best} \nlucky_few = {luck}"
            .format(pop=str(self.populations.get()),
                    numgen=str(self.num_gen.get()),
                    best=str(self.best_sample.get()),
                    luck=str(self.lucky_few.get())))

        mutations = ("\n\n[Mutations] \nchance_of_mutation = {chance} \noriginal_chance_of_mutation = {original} \nchance_of_mutation_e0 = {e0} \nmutated_options = {opt}"
            .format(chance=str(self.chance_of_mutation.get()),
                    original=str(self.orginal_chance_of_mutation.get()),
                    e0=str(self.chance_of_mutation_e0.get()),
                    opt=str(self.mutation_options.get())))

        paths = ("\n\n[Paths] \nindividual_path = {tf}  \npath_range = {range} \npath_list = {list} \npath_optimize = {optimize}"
            .format(tf=str(self.individual_path.get()),
                    range=str(self.path_range.get()),
                    list=str(self.path_list.get().replace(" ","")),
                    optimize=str(self.path_optimize.get())))

        larch_paths = ("\n\n[Larch_Paths] \nkmin = {min} \nkmax = {max} \nkweight = {weight} \ndeltak = {delk} \nrbkg = {rb} \nbkgkw = {bk} \nbkgkmax = {bmax}"
            .format(min=self.kmin.get(),
                    max=self.kmax.get(),
                    weight=self.k_weight.get(),
                    delk=self.delta_k.get(),
                    rb=self.r_bkg.get(),
                    bk=self.bkg_kw.get(),
                    bmax=self.bkg_kmax.get()))

        outputs = ("\n\n[Outputs] \nprint_graph = {pg} \nnum_output_paths = {outpath}\nsteady_state_exit = {steady}"
            .format(pg=self.print_graph.get(),
                    outpath=self.num_output_paths.get(),
                    steady=self.steady_state_exit.get()))
        with open(filename,'w') as writer:
            writer.write(str(inputs))
            writer.write(str(populations))
            writer.write(str(mutations))
            writer.write(str(paths))
            writer.write(str(larch_paths))
            writer.write(str(outputs))

    def Generate_ini(self):
        os.chdir("..") #change the working directory from gui to EXAFS
        # while proceed ==  False:
        ini_file= filedialog.asksaveasfilename(initialdir = os.getcwd(),
            title = "Choose output ini file",
            filetypes = [("ini files","*.ini")])
        if ini_file is None:
            return
        if isinstance(ini_file,tuple) == False:
            if len(ini_file) != 0:
                self.Write_ini(ini_file)
                messagebox.showinfo('','Ini file written to {fileloc}'.format(fileloc=ini_file))

        os.chdir("gui")

    def stop_term(self):
        if hasattr(self,'proc'):
            print("Stopped EXAFS")
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)

    def run_term(self):
        """
        if hasattr(self,'terminal'):
            # Need to close previous threads
            self.terminal.destroy()
        # command = ['exafs','-i','test.ini']
        self.Write_ini('test_temp.i')
        command = 'exafs -i test_temp.i'.split(' ')
        # print(command)
        self.terminal = Console(self.txtbox,command)
        """
        self.Write_ini('test_temp.i')
        self.stop_term()

        command = 'exafs -i test_temp.i'
        self.proc = subprocess.Popen(command,shell=True,preexec_fn=os.setsid)

    def Build_global(self):
        '''
        Create global generate ini
        '''

        def about_citation():
            popup = tk.Toplevel()
            popup.wm_title("About")
            msg = 'Citation:\nAnalysis of Extended X-ray Absorption Fine Structure (EXAFS) Data Using Artificial Intelligence Techniques\n J. Terry, M. Lau, J. Sun, C. Xu, B. Hendricks,\nJ. Kise, M. Lnu, S. Bagade, S. Shah, P. Makhijani,\nA. Karantha, T. Boltz, M. Oellien, M. Adas, S. Argamon, M. Long, D. Guillen\n[Submission], 2020'
            label = ttk.Label(popup, text=msg, font="TkTextFont")
            label.grid(column=0,row=0,padx=self.padx,pady=self.pady)

            license = scrolledtext.ScrolledText(popup)
            license.grid(column=0,row=1,sticky=N+S+W+E,padx=self.padx,pady=self.pady)
            with open('../LICENSE') as f:
                license.insert(tk.END,f.read())
            B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
            B1.grid(column=0,row=2,padx=self.padx,pady=self.pady)

            popup.grid_columnconfigure(0,weight=1)
            popup.grid_rowconfigure(1,weight=1)
            popup.protocol('WM_DELETE_WINDOW', popup.destroy)

        self.generate_button = tk.Button(self.root, text="Generate Input", command=self.Generate_ini)
        self.generate_button.grid(column=3,row=2,sticky=E,padx=self.padx,pady=self.pady)

        self.run_button = tk.Button(self.root,text='Run',command=self.run_term)
        self.run_button.grid(column=1,row=2,columnspan=1,sticky=E,padx=self.padx,pady=self.pady)

        self.stop_button = tk.Button(self.root,text='Stop',command=self.stop_term)
        self.stop_button.grid(column=2,row=2,columnspan=1,sticky=W,padx=self.padx,pady=self.pady)


        self.about_button = tk.Button(self.root,text='About',command=about_citation)
        self.about_button.grid(column=0,row=2,columnspan=1,sticky=W,padx=self.padx,pady=self.pady)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.root.grid_rowconfigure(0,weight=1)

        # Create a empty frame
        # self.label_frame = LabelFrame(self.root, text="Terminal", padx=5, pady=5)
        # self.label_frame.grid(column=0,row=1, columnspan=3, padx=self.padx, pady=self.pady, sticky=E+W+N+S)

        # Create the textbox
        # self.label_frame.rowconfigure(0,weight=1)
        # self.label_frame.columnconfigure(0,weight=1)
        # self.txtbox = scrolledtext.ScrolledText(self.label_frame, width=40, height=10)
        # self.txtbox.grid(row=0, column=0, sticky=E+W+N+S)

    def Build_inputs_tab(self):
        arr_input = ["Data file", "Output File", "FEFF Folder"]
        self.description_tabs(arr_input,self.tab_Inputs)

        self.tab_Inputs.grid_columnconfigure(1,weight=1)

        entry_data_file = ttk.Combobox(self.tab_Inputs, textvariable=self.temp_data_file, font=self.entryFont)
        entry_data_file.grid(column=1, row=0, sticky=(W, E),padx=self.padx,pady=self.pady)

        entry_output_file = tk.Entry(self.tab_Inputs,textvariable=self.output_file,font=self.entryFont)
        entry_output_file.grid(column=1,row=1,sticky=(W,E),padx=self.padx,pady=self.pady)

        entry_feff_folder = tk.Entry(self.tab_Inputs,textvariable=self.feff_file,font=self.entryFont)
        entry_feff_folder.grid(column=1,row=2,sticky=(W,E),padx=self.padx,pady=self.pady)

        def select_data_file():
            os.chdir("..") #change the working directory from gui to EXAFS
            file_name =  filedialog.askopenfilenames(initialdir = os.getcwd(), title = "Choose xmu/csv", filetypes = (("xmu files", "*.xmu"),("csv files","*.csv"),("all files","*.*")))
            if not file_name:
                self.data_file.set('Please choose file/s')
                self.temp_data_file.set('Please choose file/s')
            else:
                if isinstance(file_name,tuple):
                    if len(file_name)==1:
                        self.data_file.set(str(file_name[0]))
                        self.temp_data_file.set(str(file_name[0]))
                    else:
                        file_list = list(self.root.splitlist(file_name))
                        separator = ' '
                        self.data_file.set(separator.join(file_list))
                        entry_data_file['value'] = file_list
                        self.series.set(True)
            os.chdir("gui")

        def select_output_file():
            os.chdir("..") #change the working directory from gui to EXAFS
            file_name =  filedialog.asksaveasfilename(initialdir = os.getcwd(), title = "Choose data_file", filetypes = (("csv files","*.csv"),("all files","*.*")))
            if not file_name:
                self.output_file.set('Please choose a file')
            else:
                self.output_file.set(file_name)
            os.chdir("gui")

        def select_feff_folder():
            os.chdir("..") #change the working directory from gui to EXAFS
            folder_name = filedialog.askdirectory(initialdir = os.getcwd(), title = "Select folder")
            if not folder_name:
                self.feff_file.set('Please choose a directory')
            else:
                folder_name = os.path.join(folder_name,'feff')
                self.feff_file.set(folder_name)
            # print(self.feff_file.get())
            os.chdir("gui")

        button_data_file = ttk.Button(self.tab_Inputs, text="Choose",
                command=select_data_file, style='my.TButton')
        button_data_file.grid(column=3, row=0, sticky=W,padx=self.padx,pady=self.pady)

        button_output_file = ttk.Button(self.tab_Inputs,text="Choose",
                command=select_output_file, style='my.TButton')
        button_output_file.grid(column=3, row=1, sticky=W,padx=self.padx,pady=self.pady)

        button_feff_folder = ttk.Button(self.tab_Inputs,text="Choose",
                command=select_feff_folder, style='my.TButton')
        button_feff_folder.grid(column=3, row=2, sticky=W,padx=self.padx,pady=self.pady)

    def Build_population_tab(self):
        arr_pop = ["Population", "Number of Generations", "Best Individuals(%)", "Lucky Survivor(%)"]
        self.description_tabs(arr_pop,self.tab_Populations)

        self.tab_Populations.grid_columnconfigure(1,weight=1)

        entry_population = tk.Entry(self.tab_Populations, textvariable=self.populations, font=self.entryFont)
        entry_population.grid(column=1, row=0, sticky=(W, E),padx=self.padx)

        entry_num_gen = tk.Entry(self.tab_Populations, textvariable=self.num_gen, font=self.entryFont)
        entry_num_gen.grid(column=1, row=1, sticky=(W, E),padx=self.padx)

        entry_best_sample = tk.Entry(self.tab_Populations, textvariable=self.best_sample, font=self.entryFont)
        entry_best_sample.grid(column=1, row=2, sticky=(W, E),padx=self.padx)

        entry_lucky_few = tk.Entry(self.tab_Populations, textvariable=self.lucky_few, font=self.entryFont)
        entry_lucky_few.grid(column=1, row=3, sticky=(W, E),padx=self.padx)

    def Build_path_tab(self):
        arr_paths = ["Individual Path", "Path Range", "Path List", "Path Optimize"]
        self.description_tabs(arr_paths,self.tab_Paths)

        def checkbox_individual_paths():
            if self.individual_path.get() == True:
                entry_path_range.config(state='disabled')
                entry_path_list.config(state='normal')

            else:
                entry_path_range.config(state='normal')
                entry_path_list.config(state='disabled')

        def path_range_cb(var, indx, mode):
            if self.individual_path.get()==False:
                if self.path_range_call.get() == '':
                    int_test = 0
                else:
                    int_test = int(float(self.path_range_call.get()))
                self.path_range_call.set(int_test)
                self.path_range.set(int_test)

                custom_path_list = ",".join(np.char.mod('%i', np.arange(1,self.path_range.get()+1)))
                self.path_list_call.set(custom_path_list)
                self.path_list.set(custom_path_list)

        def path_list_cb(var, indx, mode):
            if self.individual_path.get()== True:
                self.path_list.set(self.path_list_call.get())
                counts = 0
                test_list = self.path_list.get().split(",")
                for i in range(len(test_list)):
                    if test_list[i] != '':
                        counts += 1
                self.path_range_call.set(counts)

        entry_individual_paths = ttk.Checkbutton(self.tab_Paths,
            variable = self.individual_path,command = checkbox_individual_paths)
        entry_individual_paths.grid(column=1,row=0,sticky=(W),padx=self.padx)

        self.path_range_call = StringVar(self.tab_Paths,str(self.path_range.get()))
        self.path_range_call.trace_add("write",path_range_cb)
        entry_path_range = ttk.Entry(self.tab_Paths, width=7,
                textvariable=self.path_range_call, font=self.entryFont)
        entry_path_range.grid(column=1, row=1, sticky=(W),padx=self.padx)

        self.path_list_call = StringVar(self.tab_Paths,self.path_list.get())
        self.path_list_call.trace_add('write',path_list_cb)
        entry_path_list = ttk.Entry(self.tab_Paths,
                textvariable=self.path_list_call, font=self.entryFont)
        entry_path_list.grid(column=1, row=2, sticky=(W, E),padx=self.padx)
        entry_path_list.config(state='disabled')

        entry_path_optimize = ttk.Checkbutton(self.tab_Paths,
            variable = self.path_optimize)
        entry_path_optimize.grid(column=1,row=3,sticky=(W),padx=self.padx)

    def Build_mutations_tab(self):
        arr_muts = ["Mutation Chance (%)", "Original chance of mutation (%)", "E0 Mutation Chance (%)", "Mutation Options (%)"]
        self.description_tabs(arr_muts,self.tab_Mutation)

        mut_list = list(range(101))
        # self.tab_Inputs.grid_columnconfigure(1,weight=1)

        entry_chance_of_mutation = ttk.Combobox(self.tab_Mutation, width=7, values=mut_list,textvariable=self.chance_of_mutation, font=self.entryFont)
        entry_chance_of_mutation.grid(column=1, row=0, sticky=(W, E),padx=self.padx)

        entry_chance_of_mutation = ttk.Combobox(self.tab_Mutation, width=7, values=mut_list,textvariable=self.orginal_chance_of_mutation, font=self.entryFont)
        entry_chance_of_mutation.grid(column=1, row=1, sticky=(W, E),padx=self.padx)

        entry_chance_of_mutation = ttk.Combobox(self.tab_Mutation, width=7, values=mut_list,textvariable=self.chance_of_mutation_e0, font=self.entryFont)
        entry_chance_of_mutation.grid(column=1, row=2, sticky=(W, E),padx=self.padx)

        mut_list = list(range(3))
        entry_chance_of_mutation = ttk.Combobox(self.tab_Mutation, width=7, values=mut_list,textvariable=self.mutation_options, font=self.entryFont)
        entry_chance_of_mutation.grid(column=1, row=3, sticky=(W, E),padx=self.padx)

    def Build_larch_tab(self):

        arr_larch = ["Kmin", "Kmax", "Kweight", "Delta k", "R Bkg", "Bkg Kw", "Bkg Kmax"]
        self.description_tabs(arr_larch,self.tab_Larch)

        entry_kmin = ttk.Entry(self.tab_Larch, textvariable=self.kmin, font=self.entryFont)
        entry_kmin.grid(column=1, row=0, sticky=(W, E),padx=self.padx)

        entry_kmax = ttk.Entry(self.tab_Larch, textvariable=self.kmax, font=self.entryFont)
        entry_kmax.grid(column=1, row=1, sticky=(W, E),padx=self.padx)

        entry_k_weight = ttk.Entry(self.tab_Larch, textvariable=self.k_weight, font=self.entryFont)
        entry_k_weight.grid(column=1, row=2, sticky=(W, E),padx=self.padx)

        entry_delta_k = ttk.Entry(self.tab_Larch, textvariable=self.delta_k, font=self.entryFont)
        entry_delta_k.grid(column=1, row=3, sticky=(W, E),padx=self.padx)

        entry_r_bkg = ttk.Entry(self.tab_Larch, textvariable=self.r_bkg, font=self.entryFont)
        entry_r_bkg.grid(column=1, row=4, sticky=(W, E),padx=self.padx)

        entry_bkg_kw = ttk.Entry(self.tab_Larch, textvariable=self.bkg_kw, font=self.entryFont)
        entry_bkg_kw.grid(column=1, row=5, sticky=(W, E),padx=self.padx)

        entry_bkg_kmax = ttk.Entry(self.tab_Larch, textvariable=self.bkg_kmax, font=self.entryFont)
        entry_bkg_kmax.grid(column=1, row=6, sticky=(W, E),padx=self.padx)

    def Build_background_tab(self):

        def button_bkg_draw():
            bkg_plot.draw_background(self.temp_data_file,self.r_bkg,self.bkg_kw,self.bkg_kmax,self.kmin,self.kmax,self.delta_k,self.k_weight)

        arr_bkg = ["R Bkg", "K min","K max","Bkg Kw", "Bkg Kmax"]
        self.description_tabs(arr_bkg,self.tab_Bkg,sticky=(W,E,N))
        # self.tab_Bkg.grid_rowconfigure(3,weight=1)
        # self.tab_Bkg.grid_rowconfigure(4,weight=1)
        # self.tab_Bkg.grid_rowconfigure(5,weight=1)
        # self.tab_Bkg.grid_rowconfigure(6,weight=1)
        self.tab_Bkg.rowconfigure(8,weight=1)
        self.tab_Bkg.columnconfigure(2,weight=1)

        entry_r_bkg = ttk.Entry(self.tab_Bkg, textvariable=self.r_bkg, font=self.entryFont)
        entry_r_bkg.grid(column=1, row=0, sticky=(W,E,N),padx=self.padx,pady=self.pady)

        entry_k_min = ttk.Entry(self.tab_Bkg, textvariable=self.kmin, font=self.entryFont)
        entry_k_min.grid(column=1, row=1, sticky=(W,E,N),padx=self.padx,pady=self.pady)

        entry_k_max = ttk.Entry(self.tab_Bkg, textvariable=self.kmax, font=self.entryFont)
        entry_k_max.grid(column=1, row=2, sticky=(W,E,N),padx=self.padx,pady=self.pady)

        entry_bkg_kw = ttk.Entry(self.tab_Bkg, textvariable=self.bkg_kw, font=self.entryFont)
        entry_bkg_kw.grid(column=1, row=3, sticky=(W,E,N),padx=self.padx,pady=self.pady)

        entry_bkg_kmax = ttk.Entry(self.tab_Bkg, textvariable=self.bkg_kmax, font=self.entryFont)
        entry_bkg_kmax.grid(column=1, row=4, sticky=(W,E,N),padx=self.padx,pady=self.pady)

        bkg_plot = BKG_plot(self.tab_Bkg,self.mylarch)

        button_bkg_mu = ttk.Button(self.tab_Bkg, text="Plot Background and Mu",
            command=button_bkg_draw)
        button_bkg_mu.grid(column=0, row=5,columnspan=2,sticky=W+E,padx=self.padx,pady=self.pady)

        button_kspace = ttk.Button(self.tab_Bkg, text="K space",
            command=bkg_plot.draw_kspace)
        button_kspace.grid(column=0, row=6,columnspan=2,sticky=W+E,padx=self.padx,pady=self.pady)

        button_rspace = ttk.Button(self.tab_Bkg, text="R space",
            command=bkg_plot.draw_rspace)
        button_rspace.grid(column=0, row=7,columnspan=2,sticky=W+E,padx=self.padx,pady=self.pady)

    def Build_output_tab(self):

        pop_min = IntVar(self.tab_Output,100)
        pop_max = IntVar(self.tab_Output,5001)
        gen_min = IntVar(self.tab_Output,20)
        gen_max = IntVar(self.tab_Output,501)
        mut_min = IntVar(self.tab_Output,20)
        mut_max = IntVar(self.tab_Output,101)

        pertub_check = IntVar(self.tab_Output,0)
        def generate_multi_ini():
            os.chdir("..")
            pop_range = np.arange(pop_min.get(),pop_max.get(),100)
            gen_range = np.arange(gen_min.get(),gen_max.get(),5)
            mut_range = np.arange(mut_min.get(),mut_max.get(),10)
            # exit()
            multi_folder = filedialog.askdirectory(initialdir = os.getcwd(),title = 'Select folder')
            if not multi_folder:
                return
            else:
                print(multi_folder)
                og_pop = self.populations.get()
                og_gen = self.num_gen.get()
                og_mut = self.chance_of_mutation.get()
                og_out_file = self.output_file.get()

                for i in range(self.n_ini.get()):

                    pop_select = np.random.choice(pop_range)
                    gen_select = np.random.choice(gen_range)
                    mut_select = np.random.choice(mut_range)
                    base_file = os.path.splitext(og_out_file)[0]
                    self.output_file.set(os.path.join(base_file +"_"+str(i).zfill(3) +".ini"))
                    self.populations.set(pop_select)
                    self.num_gen.set(gen_select)
                    self.chance_of_mutation.set(mut_select)
                    self.Write_ini(multi_folder + "/file_" + str(i).zfill(3)+'.i')
                self.populations.set(og_pop)
                self.num_gen.set(og_gen)
                self.chance_of_mutation.set(og_mut)
                self.output_file.set(og_out_file)
            os.chdir("gui")

        def checkbox_multi():
            widget_lists=[
                entry_n_ini,
                entry_pertub_pop_min,
                entry_pertub_pop_max,
                entry_pertub_gen_min,
                entry_pertub_gen_max,
                entry_pertub_mut_min,
                entry_pertub_mut_max,
                button_gen_nini]
            if pertub_check.get() == 0:
                for i in widget_lists:
                    i.config(state='disabled')
            elif pertub_check.get() == 1:
                for i in widget_lists:
                    i.config(state='normal')

        arr_out = ["Print graph", "Steady state exit"]
        self.description_tabs(arr_out,self.tab_Output)

        checkbutton_print_graph = ttk.Checkbutton(self.tab_Output, var=self.print_graph)
        checkbutton_print_graph.grid(column=1, row=0,sticky=W+E,padx=self.padx)

        checkbutton_steady_state= ttk.Checkbutton(self.tab_Output, var=self.steady_state_exit)
        checkbutton_steady_state.grid(column=1, row=1,sticky=W+E,padx=self.padx)

        # Create separators
        separator = ttk.Separator(self.tab_Output, orient='horizontal')
        separator.grid(column=0, row=2,columnspan=4,sticky=W+E,padx=self.padx)
        self.tab_Output.columnconfigure(3,weight=1)


        arr_out = ["Create Multiple Input Files","Number of Ini Files","Pertubutions-Population(min,max)", "Pertubutions-Generation(min,max)","Pertubutions-Mutation(min,max)"]
        self.description_tabs(arr_out,self.tab_Output,row=[3,5,6,7,8])
        # Create New pertubutuions

        checkbutton_pertub= ttk.Checkbutton(self.tab_Output, var=pertub_check,command=checkbox_multi)
        checkbutton_pertub.grid(column=1, row=3,sticky=W+E,padx=self.padx)


        pertub_list = list(range(1,101))

        text ='Each entry allows user to control perturbation percentage of the desire variables.'
        entry = ttk.Label(self.tab_Output,text=text,font=self.labelFont)
        entry.grid_configure(column=0,row=4,columnspan=3,sticky=W+E,padx=self.padx,pady=self.pady)


        entry_n_ini = tk.Entry(self.tab_Output,textvariable=self.n_ini,font=self.entryFont)
        entry_n_ini.grid(column=1, row=5,columnspan=2,sticky=(W, E),padx=self.padx)

        entry_n_ini.config(state='disabled')

        width = 5
        # --------------
        entry_pertub_pop_min= ttk.Entry(self.tab_Output, width=width,textvariable=pop_min, font=self.entryFont)
        entry_pertub_pop_min.grid(column=1, row=6, sticky=(W, E),padx=self.padx)

        entry_pertub_pop_max= ttk.Entry(self.tab_Output, width=width,textvariable=pop_max, font=self.entryFont)
        entry_pertub_pop_max.grid(column=2, row=6, sticky=(W, E),padx=self.padx)

        entry_pertub_pop_min.config(state='disabled')
        entry_pertub_pop_max.config(state='disabled')

        # --------------
        entry_pertub_gen_min= ttk.Entry(self.tab_Output, width=width,textvariable=gen_min, font=self.entryFont)
        entry_pertub_gen_min.grid(column=1, row=7, sticky=(W, E),padx=self.padx)

        entry_pertub_gen_max= ttk.Entry(self.tab_Output, width=width,textvariable=gen_max, font=self.entryFont)
        entry_pertub_gen_max.grid(column=2, row=7, sticky=(W, E),padx=self.padx)

        entry_pertub_gen_min.config(state='disabled')
        entry_pertub_gen_max.config(state='disabled')

        # --------------
        entry_pertub_mut_min= ttk.Entry(self.tab_Output, width=width,textvariable=mut_min, font=self.entryFont)
        entry_pertub_mut_min.grid(column=1, row=8, sticky=(W, E),padx=self.padx)

        entry_pertub_mut_max= ttk.Entry(self.tab_Output, width=width,textvariable=mut_max, font=self.entryFont)
        entry_pertub_mut_max.grid(column=2, row=8, sticky=(W, E),padx=self.padx)

        entry_pertub_mut_min.config(state='disabled')
        entry_pertub_mut_max.config(state='disabled')

        # --------------

        button_gen_nini = tk.Button(self.tab_Output,text="Generate Input Files",command=generate_multi_ini)
        button_gen_nini.grid(column=0, row=9,columnspan=3,sticky=W+E,padx=self.padx,pady=self.pady)

        button_gen_nini.config(state='disabled')

    def Build_analysis_tab(self):

        def select_analysis_folder():
            os.chdir("..") #change the working directory from gui to EXAFS
            folder_name = filedialog.askdirectory(initialdir = os.getcwd(), title = "Select folder")
            if not folder_name:
                analysis_folder.set('Please choose a directory')
            else:
                # folder_name = os.path.join(folder_name,'feff')
                analysis_folder.set(folder_name)
            # print(self.feff_file.get())
            os.chdir("gui")
        def run_analysis():
            params = {}
            # params['base'] = Path(os.getcwd()).parent
            params['base'] = ''
            params['Kmin'] = self.kmin.get()
            params['Kmax'] = self.kmax.get()
            params['kweight'] = self.k_weight.get()
            params['deltak'] = self.delta_k.get()
            params['rbkg'] = self.r_bkg.get()
            params['bkgkw'] = self.bkg_kw.get()
            params['bkgkmax'] = self.bkg_kmax.get()
            params['front'] = self.feff_file.get()
            params['CSV'] = self.data_file.get()
            params['optimize'] = self.path_optimize.get()
            params['series_index'] = series_index.get()
            params['series'] = self.series.get()
            # set up the params
            self.txtbox.insert(tk.END,"Running Analysis...\n")
            analysis_plot.setup_params(params)

            paths = self.path_list.get()
            analysis_plot.setup_paths(list(map(int,list(paths.split(",")))))

            analysis_plot.setup_dirs(analysis_folder.get())
            arr_str,latex_str = analysis_plot.extract_and_run(analysis_folder)

            self.txtbox.insert(tk.END,arr_str)
            self.txtbox.insert(tk.END,"-------------\n")
            self.txtbox.insert(tk.END,latex_str)
            self.txtbox.insert(tk.END,"\n-------------\n")
            self.txtbox.insert(tk.END,"Done")

        analysis_folder = StringVar(self.tab_Analysis,'Please choose a directory')
        series_index = IntVar(self.tab_Analysis,0)
        self.tab_Analysis.columnconfigure(1,weight=1)
        self.tab_Analysis.rowconfigure(5,weight=1)

        arr_out = ["Select folder"]
        self.description_tabs(arr_out,self.tab_Analysis)

        entry_analysis_folder = tk.Entry(self.tab_Analysis,textvariable=analysis_folder,font=self.entryFont)
        entry_analysis_folder.grid(column=1,row=0,sticky=(W,E),padx=self.padx,pady=self.pady)

        button_analysis_folder = ttk.Button(self.tab_Analysis,text="Choose",
                command=select_analysis_folder, style='my.TButton')
        button_analysis_folder.grid(column=2, row=0, sticky=W,padx=self.padx,pady=self.pady)

        separator = ttk.Separator(self.tab_Analysis, orient='horizontal')
        separator.grid(column=0, row=1,columnspan=4,sticky=W+E,padx=self.padx)

        analysis_plot = Analysis_Plot(self.tab_Analysis,self.mylarch)

        button_Run_Analysis = ttk.Button(self.tab_Analysis,text="Run Analysis",
                command=run_analysis, style='my.TButton')
        button_Run_Analysis.grid(column=0, row=2,columnspan=3, sticky=W+E,padx=self.padx,pady=self.pady)

        button_plot_error = ttk.Button(self.tab_Analysis,text="Plot K & R Space",
                command=analysis_plot.plot_k_r_space, style='my.TButton')
        button_plot_error.grid(column=0, row=3,columnspan=3, sticky=W+E,padx=self.padx,pady=self.pady)

        button_plot_error = ttk.Button(self.tab_Analysis,text="Plot Error",
                command=analysis_plot.plot_error, style='my.TButton')
        button_plot_error.grid(column=0, row=4,columnspan=3, sticky=W+E,padx=self.padx,pady=self.pady)

    def On_closing(self):
        """
        on closing function
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if hasattr(self,'terminal'):
                self.root.quit()
                self.terminal.destroy()
            else:
                self.root.quit()

    def Run(self):
        """
        Run the code
        """
        self.root.protocol('WM_DELETE_WINDOW', self.On_closing)
        self.root.mainloop()

root = App()
root.Run()
