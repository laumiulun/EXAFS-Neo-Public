import numpy as np
import random
"""
Author: Andy Lau

"""
class PathObject:
    """
    Scattering Paths of each
    """

    def __init__(self,pathrange_obj,e0):
        self.pathrange = pathrange_obj
        self.s02 = np.random.choice(self.pathrange.getrange_S02())
        self.e0 = e0
        self.sigma2 = np.random.choice(self.pathrange.getrange_Sigma2())
        self.deltaR = np.random.choice(self.pathrange.getrange_DeltaR())
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

    def mutate_s02(self,chance):
        if random.random()*100 < chance:
            self.s02 = np.random.choice(self.pathrange.getrange_S02())

    def mutate_sigma2(self,chance):
        if random.random()*100 < chance:
            self.sigma2 = np.random.choice(self.pathrange.getrange_Sigma2())

    def mutate_deltaR(self,chance):
        if random.random()*100 < chance:
            self.deltaR = np.random.choice(self.pathrange.getrange_DeltaR())

    def mutate(self,chance):
        """
        Mutated each of the parameters
        """
        self.mutate_s02(chance)
        self.mutate_sigma2(chance)
        self.mutate_deltaR(chance)
