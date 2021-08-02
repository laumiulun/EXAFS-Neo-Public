"""
Authors    Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      andylau@u.boisestate.edu, jterry@agni.phys.iit.edu, minlong@boisestate.edu
Version    0.2.0
Date       July 4, 2021

Class definitions for background plots in tkinter
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import larch
from larch.io import read_ascii
from larch.xafs import autobk, xftf

class BKG_plot:
    """
    Class for Background plots, the plots utilizes matplotlib to include the toolbar,
    this calculates the background for preallocations.
    """
    def __init__(self,frame,larch):
        self.mylarch = larch
        self.fig = Figure(figsize=(3.75, 3.75), dpi=100)
        self.frame = frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().grid(column=2,row=1,rowspan=8,sticky="nsew",
            padx = 5,pady=5)
        self.ax = self.fig.add_subplot(111)
        # create toolbar above
        self.toolbarFrame = tk.Frame(master=self.frame)
        self.toolbarFrame.grid(column=2,row=0,rowspan=1,sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

    def inital_parameters(self,file,rbkg,bkg_kw,bkg_kmax,k_min,k_max,delta_k,kweight):
        """
        Initalize the parameters
        """
        self.file = file
        self.rbkg = rbkg
        self.bkg_kw = bkg_kw
        self.bkg_kmax = bkg_kmax
        self.kmin = k_min
        self.kmax = k_max
        self.delta_k = delta_k
        self.kweight = kweight

        self.small = int(k_min.get()/delta_k.get())
        self.big = int(k_max.get()/delta_k.get())

        try:
            str(self.file.get())
        except ValueError:
            pass
        self.data = read_ascii(str(self.file.get()))
        print(self.data)
    def bg_autobk(self):
        """
        calculate the background
        TODO:
        # Recalculate autobk if rbkg changes.

        """
        try:
            self.data.chi
        except AttributeError:
            autobk(self.data,
                rbkg=float(self.rbkg.get()),
                kweight=float(self.bkg_kw.get()),
                kmax=float(self.bkg_kmax.get()),
                _larch =self.mylarch)

    def update_parameters(self):
        """
        # Update parameters from the orginal script
        """
        self.kmin_val = float(self.kmin.get())
        self.kmax_val = float(self.kmax.get())
        self.bkg_kmax_val = float(self.bkg_kmax.get())
        self.kweight_val = float(self.kweight.get())


    def draw_background(self,visual=True,main=True):
        #
        # TODO:
        #  1. only change background when related to bkg (bkgkw, rbkg, bkgmax) is getting change.
        #  2. auto update plots based on changes to the val, might be difficult since
        #  3. If there no energy and mu:
        self.bg_autobk()
        try:
            self.data.energy
        except AttributeError:
            pass
            if main:
                print("No background detected.")
        else:
            if visual:
                self.ax.clear()
                # self.kweight = kweight
                self.ax.plot(self.data.energy,self.data.mu,'b.-',label='Data')
                # self.ax.plot(self.data.energy[self.small:self.big],self.data.mu[self.small:self.big],'.-',label='Data')
                self.ax.plot(self.data.energy,self.data.bkg,'r',label='Background')
                self.ax.legend()
                self.ax.set_ylabel("$\mu$ (E)")
                self.ax.set_xlabel("Energy (eV)")
                self.fig.tight_layout()
                self.canvas.draw()


    def draw_kspace(self,visual=True):
        # # TODO:
        # If any of these parameters changes, we need to replot.
        self.draw_background(visual=False,main=False)
        # self.draw_kspace()
        self.update_parameters()
        if visual:
            self.ax.clear()
            self.ax.plot(self.data.k,self.data.chi*self.data.k**self.kweight_val,'b',label='K Space')
            # self.ax.plot(self.data.k[self.small:self.big],self.data.chi[self.small:self.big]*self.data.k[self.small:self.big]**2,'b',label='K Space')
            self.ax.set_xlabel('$k$ (Å$^{-1}$)')
            self.ax.set_ylabel('$k\chi(k)$')
            self.fig.tight_layout()
            self.canvas.draw()

    def draw_rspace(self):
        # # TODO:
        # If any of these parameters changes, we need to replot.
        self.draw_background(visual=False,main=False)
        self.draw_kspace(visual=False)

        self.update_parameters()
        xftf(self.data.k, self.data.chi, kmin=self.kmin_val, kmax=self.kmax_val, dk=4,
        window='hanning',kweight=self.kweight_val, group=self.data, _larch=self.mylarch)

        self.ax.clear()
        self.ax.plot(self.data.r,self.data.chir_mag,'b',label='R Space')
        self.ax.set_xlabel('$r$ (Å$^{-1}$)')
        self.ax.set_ylabel('$\chi(r)$')
        self.fig.tight_layout()
        self.canvas.draw()
