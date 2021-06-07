# Generate range limits for PY giving the
import copy
import numpy as np


class Pathrange_limits():
    # class hidden variable
    _tol = 1e-13

    def __init__(self,
                path):

        self.path = path
        self.offset_val = 3
        self.rangeS02 = (np.arange(0.05,0.96,0.01))
        self.rangeE0 = (np.arange(-1,1.01,0.01))
        # self.rangeE0_large = (np.linspace(-600, 600, 1201) * 0.01)  # <- Larger range B
        self.rangeSigma2 = (np.arange(0.001,0.016,0.001)) # <- should be separate
        self.rangeDeltaR = (np.arange(-0.1,0.11,0.01))
        self.rangeS02 = np.insert(self.rangeS02,0,0)

        self.glob_rangeS02 = copy.deepcopy(self.rangeS02)
        self.glob_rangeE0 = copy.deepcopy(self.rangeE0)
        self.glob_rangeSigma2 = copy.deepcopy(self.rangeSigma2)
        self.glob_rangeDeltaR = copy.deepcopy(self.rangeDeltaR)

    # Get the range for each specific parameter
    def get_path(self):
        return self.path

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

    # Mod each parameters
    def mod_s02(self,val):
        self.rangeS02 = self.mod_range(self.glob_rangeS02,val)

    def mod_e0(self,val):
        self.rangeE0 = self.mod_range(self.glob_rangeE0,val)

    def mod_sigma2(self,val):
        self.rangeSigma2 = self.mod_range(self.glob_rangeSigma2,val)

    def mod_deltaR(self,val):
        self.rangeDeltaR = self.mod_range(self.glob_rangeDeltaR,val)
