"""
Authors    Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      andylau@u.boisestate.edu, jterry@agni.phys.iit.edu, minlong@boisestate.edu
Version    0.2.0
Date       Sep 1, 2021

Larch Objects for contains all data
"""
import numpy as np

class Larch_Obj:
    def __init__(self,params):
        """
        Initalze the objects from the params
        """
        self.params = params
        self.base = params['base']
        self.kmin = params['Kmin']
        self.kmax = params['Kmax']
        self.kweight = params['kweight']
        self.deltak = params['deltak']
        self.rbkg = params['rbkg']
        self.bkgkw = params['bkgkw']
        self.bkgkmax = params['bkgkmax']
        self.front = params['front']
        self.csv = params['CSV']
        self.optimize = params['optimize']
        self.series_index = params['series_index']
        self.series = params['series']

        self.big = int(self.kmax/self.deltak)
        self.small = int(self.kmin/self.deltak)
        self.mid = int(self.big-self.small + 1 )
        self.intervalK = (np.linspace(self.small,self.big,self.mid)).tolist()
