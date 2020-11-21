from .pathObj import PathObject

class Individual(PathObject):
    def __init__(self,npaths,pathrange_Dict,e0):
        self.npaths = npaths
        self.Population = []
        for pathrange in pathrange_Dict:
            self.Population.append(PathObject(pathrange,e0))

    def get(self):
        Population = []
        for i in range(self.npaths):
            Population.append(self.Population[i].get())
        return Population

    def get_e0(self):
        return self.Population[0].get_e0()

    def get_path(self,i):
        return self.Population[i].get()

    def verbose(self):
        """
        Print out the Populations
        """
        for i in range(self.npaths):
            self.Population[i].verbose()

    def set_path(self,i,s02,sigma2,deltaR):
        self.Population[i].set(s02,sigma2,deltaR)

    def set_e0(self,e0):
        """
        set e0 to a value
        """
        for i in range(self.npaths):
            self.Population[i].set_e0(e0)
