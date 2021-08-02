import copy
import numpy as np

class Pathrange_limits():
    # class hidden variable
    _tol = 1e-13

    def __init__(self,_path_,custom_range=None):

        self._path_ = _path_
        self.offset_val = 3

        if custom_range is None:

            self.rangeS02 = (np.arange(0.05,0.96,0.01))
            self.rangeS02 = np.insert(self.rangeS02,0,0)
            self.rangeE0 = (np.arange(-1,1.01,0.01))
            self.rangeSigma2 = (np.arange(0.001,0.016,0.001))
            self.rangeDeltaR = (np.arange(-0.1,0.11,0.01))

            self.S02_min = np.min(self.rangeS02)
            self.S02_max = np.max(self.rangeS02)
            self.S02_dt = 0.01

            self.Sigma2_min = np.min(self.rangeSigma2)
            self.Sigma2_max = np.max(self.rangeSigma2)
            self.Sigma2_dt = 0.001

            self.deltaR_min = np.min(self.rangeDeltaR)
            self.deltaR_max = np.max(self.rangeDeltaR)
            self.deltaR_dt = 0.01

        else:
            self.S02_min = custom_range[1]
            self.S02_max = custom_range[2]
            self.S02_dt = custom_range[3]

            self.Sigma2_min = custom_range[4]
            self.Sigma2_max = custom_range[5]
            self.Sigma2_dt = custom_range[6]

            self.deltaR_min = custom_range[7]
            self.deltaR_max = custom_range[8]
            self.deltaR_dt = custom_range[9]
            # -----
            self.rangeS02 = (np.arange(self.S02_min,self.S02_max,self.S02_dt))
            self.rangeE0 = (np.arange(-1,1.01,0.01))
            self.rangeSigma2 = (np.arange(self.Sigma2_min,self.Sigma2_max,self.Sigma2_dt))
            self.rangeDeltaR = (np.arange(self.deltaR_min,self.deltaR_max,self.deltaR_dt))


        self.glob_rangeS02 = copy.deepcopy(self.rangeS02)
        self.glob_rangeE0 = copy.deepcopy(self.rangeE0)
        self.glob_rangeSigma2 = copy.deepcopy(self.rangeSigma2)
        self.glob_rangeDeltaR = copy.deepcopy(self.rangeDeltaR)

    def get_lim(self):
        lim_s02 = self.get_lim_S02()
        lim_sigma2 = self.get_lim_Sigma2()
        lim_deltaR = self.get_lim_DeltaR()
        return (self._path_,lim_s02,lim_sigma2,lim_deltaR)

    def get_lim_S02(self):
        return (self.S02_min,self.S02_max,self.S02_dt)

    def get_lim_Sigma2(self):
        return (self.Sigma2_min,self.Sigma2_max,self.Sigma2_dt)

    def get_lim_DeltaR(self):
        return (self.deltaR_min,self.deltaR_max,self.deltaR_dt)

    # Get the range for each specific parameter
    def get_path(self):
        return self._path_

    def getrange_S02(self):
        return self.rangeS02

    def getrange_E0(self):
        return self.rangeE0

    def getrange_Sigma2(self):
        return self.rangeSigma2

    def getrange_DeltaR(self):
        return self.rangeDeltaR

    def getrange(self):
        return (self.getrange_S02(),self.getrange_E0(),self.getrange_Sigma2(),self.getrange_DeltaR())

    # Modify parameters of each objects
    def mod_range(self,glob_arr,val):
        index = next(i for i, _ in enumerate(glob_arr) if np.isclose(_, val, self._tol))
        lower = index - self.offset_val
        upper = index + self.offset_val

        if lower < 0:
            lower = 0
        if upper >= len(glob_arr):
            upper = len(glob_arr)-1

        return glob_arr[lower:upper+1]

    # Mod each parameters based on value
    def mod_s02(self,val):
        self.rangeS02 = self.mod_range(self.glob_rangeS02,val)

    def mod_e0(self,val):
        self.rangeE0 = self.mod_range(self.glob_rangeE0,val)

    def mod_sigma2(self,val):
        self.rangeSigma2 = self.mod_range(self.glob_rangeSigma2,val)

    def mod_deltaR(self,val):
        self.rangeDeltaR = self.mod_range(self.glob_rangeDeltaR,val)
