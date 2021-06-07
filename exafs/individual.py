from .pathObj import PathObject
from larch_plugins.xafs import feffdat
"""
Construct individuals for the GA
"""
class Individual(PathObject):
    def __init__(self,npaths,pathDictionary,pathrange_Dict,pathlists,e0,pathName):
        """
        Definition:
            npaths = number of paths
            pathDictionary = <dict> path name, and their corresponding paths.dat
            pathrange_Dict = <list> pathrange_limits
            path_lists = the paths lists (can be 2D depends number of feff)
            e0 = qunatum e0 of the individuals
            pathname = the paths identifier
        """
        self.npaths = npaths
        self.path_lists = pathlists
        self.pathname = pathName
        self.Population = []
        self.pathrange_Dict = pathrange_Dict
        self.pathDictionary = pathDictionary

        for pathrange in self.pathrange_Dict:
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

    def mutate_paths(self,chance):
        for path in self.Population:
            path.mutate(chance)

    def verbose_yTotal(self,intervalK):
        yTotal = [0]*(401)
        for i in range(self.npaths):

            path = self.pathDictionary.get(self.pathname[i])
            Individual = self.get()
            path.e0 = Individual[i][1]
            path.s02 = Individual[i][0]
            path.sigma2 = Individual[i][2]
            path.deltar = Individual[i][3]
            feffdat.path2chi(path)
            y = path.chi
            for k in intervalK:
                yTotal[int(k)] += y[int(k)]

        return yTotal
