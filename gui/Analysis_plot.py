"""
Authors    Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      andylau@u.boisestate.edu, jterry@agni.phys.iit.edu, minlong@boisestate.edu
Version    0.2.0
Date       July 4, 2021

EXAFS Analysis Wrapper Functions, contains Latex, Igor Pro
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import EXAFS_Analysis
import os
# from EXAFS_Analysis import calculate_occurances,plot_occ_list


class Analysis_Plot:
    def __init__(self,frame,larch):
        self.mylarch = larch
        self.fig = Figure(figsize=(3.5,3.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        # Create inital figure canvas
        self.canvas.get_tk_widget().grid(column=0,row=10,columnspan=4,sticky="nsew",
            padx = 5,pady=5)
        self.ax = self.fig.add_subplot(111)
        # create toolbar
        self.toolbarFrame = tk.Frame(master=frame)
        self.toolbarFrame.grid(column=0,row=11,columnspan=4,sticky="nsew")
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
        self.EXAFS_Analysis.export_igor_individual(os.path.join(output_folder.get(),'Test.ipf'))

        return self.EXAFS_Analysis.return_str,self.EXAFS_Analysis.latex_table_str

    def plot_k_r_space(self):
        self.fig.clf()
        self.EXAFS_Analysis.plot(fig_gui=self.fig)
        self.canvas.draw()

    def plot_individual(self):
        self.fig.clf()
        self.EXAFS_Analysis.individual_fit(fig_gui=self.fig)
        self.canvas.draw()

    def plot_error(self):
        self.fig.clf()
        self.EXAFS_Analysis.plot_error(fig_gui=self.fig)
        self.canvas.draw()

    def plot_occurances(self,folder,limits,paths):
        self.fig.clf()
        path_list = paths.split(',')
        paths = [int(path) for path in path_list]

        EXAFS_Analysis.plot_occ_list(folder,limits,paths,fig_gui=self.fig)
        # self.EXAFS_Analysis.plot_occ_list(fig_gui=self.fig)
        self.canvas.draw()
