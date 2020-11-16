import numpy as np
"""
Author: Andy Lau

"""
class PathObject:
    """
        Paths Objects of a specific paths
    """
    # def __init__(self,rangeS02,e0,rangeSigma2,rangeDeltaR,path):
    #
    #     self.s02 = np.random.choice(rangeS02)
    #     self.e0 = e0
    #     self.sigma2 = np.random.choice(rangeSigma2)
    #     self.deltaR = np.random.choice(rangeDeltaR)
    #     self.path = path
    def __init__(self,pathrange_obj,e0):
        # printpathrange_obj.getrange_S02())
        self.s02 = np.random.choice(pathrange_obj.getrange_S02())
        self.e0 = e0
        self.sigma2 = np.random.choice(pathrange_obj.getrange_Sigma2())
        self.deltaR = np.random.choice(pathrange_obj.getrange_DeltaR())
        self.path = pathrange_obj.get_path()

    def verbose(self):
        print(self.s02,self.e0,self.sigma2,self.deltaR,",",self.path)

    def get(self):
        return [self.s02, self.e0, self.sigma2,self.deltaR]

    def get_s02(self):
        return self.s02

    def get_e0(self):
        return self.e0

    def get_sigma2(self):
        return self.sigma2

    def get_deltaR(self):
        return self.deltaR
    # -----------------
    def set(self,s02,sigma2,deltaR):
        self.set_s02(s02)
        # self.set_e0(s02)
        self.set_sigma2(sigma2)
        self.set_deltaR(deltaR)
    def set_s02(self,s02):
        self.s02 = s02

    def set_e0(self,e0):
        self.e0 = e0

    def set_sigma2(self,sigma2):
        self.sigma2 = sigma2

    def set_deltaR(self,deltaR):
        self.deltaR = deltaR
