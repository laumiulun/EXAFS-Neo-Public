from .helper import *
from .import_lib import *
from .ini_parser import *
from larch import Interpreter
from .pathObj import PathObject
from .individual import Individual
from .pathrange import Pathrange_limits
# from .run_verbose import *



class EXAFS_GA:

    def initialize_params(self,verbose = False):
        """
        Initialize Parameters
        """

        self.Kmin = Kmin
        self.Kmax = Kmax
        self.Kweight = KWEIGHT
        self.deltak = deltak

        self.rbkg = rbkg
        self.bkgkw = bkgkw
        self.bkgkmax = bkgkmax

        self.small = int(self.Kmin/self.deltak)
        self.big = int(self.Kmax/self.deltak)
        self.mid = int(self.big - self.small + 1)
        self.intervalK = np.linspace(self.small,self.big,self.mid)

        self.path_optimize = path_optimize
        self.ind_options = individual_path
        self.printgraph = printgraph


    def initialize_variable(self,firstpass=False):
        """
        Initalize variables
        """
        self.genNum = 0
        self.nChild = 3
        self.globBestFit = [0,99999]
        self.currBestFit = [0,99999]
        self.bestDiff = 9999
        self.bestBest = 999999999
        self.diffCounter = 0

        self.pathDictionary = {}
        # self.MetaDictionary = {}
        # Not used
        # self.sortedFourier = 0
        # self.bestFitIndi = (())
        self.bestChir_magTotal = [0]*(326)
        self.bestYTotal = [0]*(401)
        # Typical INI parameters
        if self.ind_options == True:
            if firstpass==True:
                self.path_lists = path_list
        else:
            self.path_lists = list(range(1,pathrange+1))
            for i in range(len(self.path_lists)):
                self.path_lists[i] = str(self.path_lists[i])


        self.npaths = len(self.path_lists)
        self.npops = size_population
        self.ngen = number_of_generation
        self.steady_state = steady_state

        # Mutation Parameters
        self.mut_opt = mutated_options
        self.mut_chance = chance_of_mutation
        self.mut_chance_e0 = chance_of_mutation_e0

        # Crosover Parameters
        self.n_bestsam = int(best_sample*self.npops*(0.01))
        self.n_lucksam = int(lucky_few*self.npops*(0.01))

        # Time related
        self.time = False
        self.tt = 0

        # CSV-Series check
        self.csv_percent = 0.2

    def initialize_file_path(self,i=0,firstpass=False):
        """
        Initalize file paths for each of the file first
        """
        self.csv_series = csv_series
        self.base = os.getcwd()
        self.front = os.path.join(self.base,feff_file)

        if self.csv_series == True:
            self.data_path = os.path.join(self.base,csv_file[i])
            self.output_path = os.path.splitext(os.path.join(self.base,output_file))[0] + "_" + str(i) + ".csv"
            self.log_path = os.path.splitext(copy.deepcopy(self.output_path))[0] + ".log"

        else:
            self.data_path = os.path.join(self.base,csv_file)
            self.output_path = os.path.join(self.base,output_file)
            self.log_path = os.path.splitext(copy.deepcopy(self.output_path))[0] + ".log"

        self.end ='.dat'
        self.check_output_file(self.output_path)
        if not firstpass:
            self.check_if_exists(self.log_path)
        # Initialize logger
        self.logger = logging.getLogger('')
        # Delete handler
        self.logger.handlers=[]
        file_handler = logging.FileHandler(self.log_path,mode='a+',encoding='utf-8')
        stdout_handler = logging.StreamHandler(sys.stdout)

        formatter= logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)


        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)

        self.logger.setLevel(logging.INFO)
        self.logger.info(banner())
        # print(self.logger.root.handlers)
        # print(output_file)


    def check_if_exists(self,path_file):
        """
        Check if the directory exists
        """
        if os.path.exists(path_file):
            os.remove(path_file)
        # Make Directory when its missing
        path = pathlib.Path(path_file)
        path.parent.mkdir(parents=True, exist_ok=True)

    def check_output_file(self,file):
        """
        check if the output file for each of the file
        """
        file_base= os.path.splitext(file)[0]
        self.check_if_exists(file)
        self.file = file

        self.file_initial = open(self.output_path,"a+")
        self.file_initial.write("Gen,TPS,FITTNESS,CURRFIT,CURRIND,BESTFIT,BESTIND\n")  # writing header
        self.file_initial.close()

        # Not using right now
        # file_score = os.path.splitext(file)[0] + '_score.csv'
        # self.check_if_exists(file_score)
        # self.file_score = file_score

        file_data = os.path.splitext(file)[0] + '_data.csv'
        self.check_if_exists(file_data)
        self.file_data = file_data

        # Not using right now
        # file_gen = os.path.splitext(file)[0] + '_generations.csv'
        # self.check_if_exists(file_gen)

    def initialize_range(self,i=0,BestIndi=None):
        """
        Initalize range

        To Do list:
            Initalize range will be difference for each paths depend if the run are
            in series, therefore the ranges will self-adjust
        """

        # print(self.path_lists)
        # print("Initialize Range")
        if i == 0:
            self.pathrange_Dict = []
            for i in self.path_lists:
                self.pathrange_Dict.append(Pathrange_limits(i))

            # self.dt_S02 = [0.01,2]
            # self.dt_Sigma2 = [0.001,3]

            # self.dt_DeltaR = [0.01,2]
            # sys.exit()
            # self.rangeS02 = (np.linspace(5, 95, 91) * 0.01)  # <- should be separate
            self.rangeE0 = (np.linspace(-100, 100, 201) * 0.01) # <- e0, for everything
            self.rangeE0_large = (np.linspace(-600, 600, 1201) * 0.01)  # <- Larger range B

        else:
            for k in range(self.npaths):
                path_bestfit = BestIndi.get_path(k)
                self.pathrange_Dict[k].mod_s02(path_bestfit[0])
                # self.pathrange_Dict[k].mod_e0(path_bestfit[1])
                self.pathrange_Dict[k].mod_sigma2(path_bestfit[2])
                self.pathrange_Dict[k].mod_deltaR(path_bestfit[3])


    def initialize_group(self):
        """
        initalize larch group
        """
        # Create 3 empty group
        self.mylarch = Interpreter()
        self.g = read_ascii(self.data_path)
        self.best = read_ascii(self.data_path)
        self.sumgroup = read_ascii(self.data_path)

        # Check if
        try:
            self.g.chi
        except AttributeError:
            autobk(self.g, rbkg=rbkg, kweight=bkgkw, kmax=bkgkmax, _larch=self.mylarch)
            autobk(self.best, rbkg=rbkg, _larch=self.mylarch)
            autobk(self.sumgroup, rbkg=rbkg, _larch=self.mylarch)

    def initialize_paths(self):
        """
        Initalize paths
        """
        self.e0 = np.random.choice(self.rangeE0)
        for i,paths in enumerate(path_list):
            self.pathDictionary[paths] = pathObject(self.rangeS02,
                                                    self.e0,
                                                    self.rangeSigma2,
                                                    self.rangeDeltaR)

    def loadPaths(self):
        if self.ind_options == True:
            for i in range(self.npaths):
                filename = self.front + str(self.path_lists[i]).zfill(4) + self.end
                pathName = "Path" + self.path_lists[i]
                self.pathDictionary.update({pathName: feffdat.feffpath(filename, _larch=self.mylarch)})
        else:
            # print(paths)
            for i in range(1, self.npaths+1):
                filename = self.front + str(i).zfill(4) + self.end
                # pathName = 'Path'+ str(i)
                pathName = f"Path{i}"
                self.pathDictionary.update({pathName: feffdat.feffpath(filename, _larch=self.mylarch)})

    def generateIndividual(self):
        e0 = np.random.choice(self.rangeE0)
        ind = Individual(self.npaths,self.pathrange_Dict,e0)
        return ind

    def generateFirstGen(self):
        self.Populations=[]
        for i in range(self.npops):
            # e0 = np.random.choice(self.rangeE0)
            self.Populations.append(self.generateIndividual())

    # @profile
    def fitness(self,indObj):
        """
        Evaluate fitness of a individual
        """
        # from larch_plugins.xafs import feffdat
        # t1 = time.time()
        loss = 0
        yTotal = [0] * (401)
        # print(self.path_lists)
        for i in range(self.npaths):
            # pathName = f"Path{paths[i]}"
            pathName = 'Path' + self.path_lists[i]
            path = self.pathDictionary.get(pathName)
            Individual = indObj.get()
            path.e0 = Individual[i][1]
            path.s02 = Individual[i][0]
            path.sigma2 = Individual[i][2]
            path.deltar = Individual[i][3]
            feffdat.path2chi(path, _larch=self.mylarch)
            y = path.chi
            for k in self.intervalK:
                yTotal[int(k)] += y[int(k)]
        # compute loss function
        for j in self.intervalK:
            # kweight
            loss = loss + (yTotal[int(j)] * self.g.k[int(j)] ** self.Kweight - self.exp[int(j)] * self.g.k[int(j)] ** self.Kweight) ** 2
        return loss

    def eval_Population(self):
        """
        Evalulate populations
        """

        # fittness_pool = Pool(os.cpu_count())
        # result = fittness_pool.map(self.fitness,self.Populations)

        # output = mp.Queue()
        # processes = [mp.Process(target=self.fitness, args=(, self.output)) for x in range(4)]
        # pool = mp.Pool(processes=4)
        #
        # results  = [pool.apply(self.fitness,args=(x)) for x in self.Populations]
        #
        # print(result)

        # ray.init()
        # print(type(self.Populations))
        # score = []
        score = []
        populationPerf = {}

        for i,individual in enumerate(self.Populations):
            # print(i)
            # print(i,individual)
            # t1 = time.time()
            # print(individual)

            temp_score = self.fitness(individual)
            score.append(temp_score)

            populationPerf[individual] = temp_score

            # self.time == True:
            # t2 = time.time()
            # print(t2-t1)
            # Average
            # print(individualTuple)
        # pool = ThreadPool(processes=2)
        # pool.map(self.fitness,range(self.npops))
        # pool.close()
        # pool.join()
        # print(score)
        # score
        # self.pop
        # print(populationPerf.items())
        # print(operator.itemgetter(1))
        self.sorted_population = sorted(populationPerf.items(), key=operator.itemgetter(1), reverse=False)

        # print(self.sorted_population)
        # print(self.bestFit)
        self.currBestFit = list(self.sorted_population[0])

        return score

    def next_generation(self,detect_limits=False):
        self.st = time.time()
        # ray.init()
        self.logger.info("---------------------------------------------------------")
        self.logger.info(datetime.datetime.fromtimestamp(self.st).strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.info(f"{bcolors.BOLD}Gen: {bcolors.ENDC}{self.genNum+1}")

        self.genNum += 1

        # Evaluate Fittness
        score = self.eval_Population()

        self.bestDiff = abs(self.globBestFit[1]-self.currBestFit[1])
        # print(self.bestDiff)
        if self.currBestFit[1] < self.globBestFit[1]:
            self.globBestFit = self.currBestFit

        # detecting if limits is hit on the bestfit
        # if detect_limits:
            # self.detect_and_adjust_limits()
        # Rechenberg mutation
        if self.genNum > 20:
            if self.bestDiff < 0.1:
                self.diffCounter += 1
            else:
                self.diffCounter -= 1
            if (abs(self.diffCounter)/ float(self.genNum)) > 0.2:
                self.mut_chance += 2.5
                self.mut_chance = abs(self.mut_chance)
            elif (abs(self.diffCounter) / float(self.genNum)) < 0.2:
                self.mut_chance -= 2.5
                self.mut_chance = abs(self.mut_chance)
            # elif self.mut_chance > 100:
                # self.mut_chance -= 20
        self.logger.info(f"Best Fit: {bcolors.BOLD}{self.sorted_population[0][1].round(3)}{bcolors.ENDC}")
        self.logger.info("2nd Fit: " + str(self.sorted_population[1][1].round(3)))
        self.logger.info("3rd Fit: " + str(self.sorted_population[2][1].round(3)))
        self.logger.info("4th Fit: " + str(self.sorted_population[3][1].round(3)))
        self.logger.info("Last Fit: " + str(self.sorted_population[-1][1].round(3)))
        # sys.exit()
        with np.printoptions(precision=3, suppress=True):
            # print(self.intervalK)
            self.logger.info("Different from last best fit: " +str(self.bestDiff))
            self.logger.info(bcolors.BOLD + "Best fit: " + bcolors.OKBLUE + str(self.currBestFit[1]) + bcolors.ENDC)
            CurrchiR = str(self.currBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "Best fit ChiR: " + bcolors.OKBLUE + str(CurrchiR) + bcolors.ENDC)
            self.logger.info("Best fit combination:\n" + str(np.asarray(self.sorted_population[0][0].get())))
            self.logger.info(bcolors.BOLD + "History Best: " + bcolors.OKBLUE + str(self.globBestFit[1]) +bcolors.ENDC)
            GlobchiR = str(self.globBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "History Best ChiR: " + bcolors.OKBLUE + str(GlobchiR) + bcolors.ENDC)
            self.logger.info("History Best Indi:\n" + str(np.asarray(self.globBestFit[0].get())))

        # Temp locations for calculating plots
        # if self.printgraph:
        #
        #     plt.ion()
        #     plt.plot()
        # for i in range(100):
        #     x = range(i)
        #     y = range(i)
            # plt.gca().cla() # optionally clear axes
        #     plt.plot(x, y)
        #     plt.title(str(i))
        #     plt.draw()
        #     plt.pause(0.1)
        #
        # plt.show(block=True)
        # change

        nextBreeders = self.selectFromPopulation()
        self.logger.info("Number of Breeders: " + str(len(self.parents)))
        # print(self.parents)
        self.createChildren()
        self.logger.info("DiffCounter: " + str(self.diffCounter))
        self.logger.info("Diff %:" + str(self.diffCounter / self.genNum))
        self.logger.info("Mutation Chance: " + str(self.mut_chance))
        self.mutatePopulation()

        self.et = timecall()
        self.tdiff = self.et - self.st
        self.tt = self.tt + self.tdiff
        self.logger.info("Time: "+ str(round(self.tdiff,5))+ "s")

    def detect_and_adjust_limits(self):
        best_Fit = self.globBestFit[0].get()

        for i in range(len(self.pathrange_Dict)):
            temp_range = self.pathrange_Dict[i].getrange()

            self.logger.info(best_Fit[i,0])

            # if temp_range[0] == bestFit[i]
        exit()

    def check_steady_state(self):
        if self.diffCounter > int(0.2 * number_of_generation):
            self.logger.info("---------------------")
            self.logger.info("Steady State Detected")
            self.logger.info("---------------------")
            return True
        else:
            return False

    def mutatePopulation(self):
        """
        # Mutation operators
        # 0 = original: generated a new versions:
        # 1 = mutated every genes in the total populations
        # 2 = mutated genes inside population based on secondary probability

        # TODO:
            options 2 and 3 needs to reimplmented
        """
        self.nmutate = 0

        if self.mut_opt == 0:
            for i in range(self.npops):
                if random.random()*100 < self.mut_chance:
                    self.nmutate += 1
                    self.Populations[i] = self.mutateIndi()

        if random.random() * 100 < self.mut_chance_e0:
            e0 = random.choice(self.rangeE0)
            self.logger.info("Mutate e0 to: " + str(e0))
            for individual in self.Populations:
                individual.set_e0(e0)
        self.logger.info("Mutate Times: " + str(self.nmutate))
        """
        if mutated_options == 1:
            for i in range(len(population)):
                for j in range(len(population[i])):
                    if random.random() * 100 < chance_of_mutation:
                        mutateTime += 1
                        if j == 0:
                            mutate_val = random.choice(rangeA)
                            population[i][j] == mutate_val
                        if j == 2:
                            mutate_val = random.choice(rangeC)
                            population[i][j] == mutate_val
                        if j == 3:
                            mutate_val = random.choice(rangeD)
                            population[i][j] == mutate_val

        if mutated_options == 2:
            for i in range(len(population)):
                if random.random() * 100 < chance_of_mutation:
                    for j in range(len(population[i])):
                        if random.random() * 100 < chance_gene_mut:
                            mutateTime += 1
                            if j == 0:
                                mutate_val = random.choice(rangeA)
                                population[i][j] == mutate_val
                            if j == 2:
                                mutate_val = random.choice(rangeC)
                                population[i][j] == mutate_val
                            if j == 3:
                                mutate_val = random.choice(rangeD)
                                population[i][j] == mutate_val
        """

    def mutateIndi(self):
        """
        Generate new individual during mutation operator
        """
        mutatIndi = self.generateIndividual()
        return mutatIndi

    def selectFromPopulation(self):
        self.parents = []
        # choose the top samples
        for i in range(self.n_bestsam):
            self.parents.append(self.sorted_population[i][0])

    def crossover(self,individual1, individual2):
        """
        Uniform Cross-Over, 50% percentage chance
        """
        child = self.generateIndividual()
        if np.random.randint(0,1) ==True:
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())

        for i in range(self.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            temp_path = []
            for j in range(4):
                if np.random.randint(0,2) == True:
                    temp_path.append(individual1_path[j])
                else:
                    temp_path.append(individual2_path[j])

            child.set_path(i,temp_path[0],temp_path[2],temp_path[3])
        return child


    def paths_optimization_process(self):
        if timeing_mode:
            t0 = timecall()
        self.logger.info("-------------------")
        self.logger.info("Paths Optimization")
        self.logger.info("-------------------")

        arr = np.asarray(self.globBestFit[0].get())
        total = 0
        contrib = []
        for i, (key, value) in enumerate(self.pathDictionary.items()):
            # print(index, key, value)

            path = feffdat.feffpath(value.filename, s02=str(arr[i, 0]), e0=str(arr[i, 1]),
                                    sigma2=str(arr[i, 2]), deltar=str(arr[i, 3]), _larch=self.mylarch)
            feffdat.path2chi(path, _larch=self.mylarch)

            xftf(path.k,path.chi*path.k**2,kmin=self.Kmin,kmax=self.Kmax,dk=4,
                window='hanning',kweight=self.Kweight,group=path,_larch = self.mylarch)

            area = simps(path.chir_mag,path.r)
            total += area
            contrib.append(area)
        contrib_p = [i/total for i in contrib]
        new_path = (np.argwhere(np.array(contrib_p)>=0.01)).flatten()

        self.logger.info(f"New Paths: {new_path+1}")
        if timeing_mode:
            t1 = timecall() - t0
            self.logger.info('Path Optimization took %.2f second' % t1)

        # self.path_lists = list(new_path+1)
        new_path_lists = []
        for i in range(len(new_path)):
            new_path_lists.append(str(new_path[i]+1))

        self.path_lists = new_path_lists
        self.ind_options = True
        # self.npaths = len(self.path_lists)


    def createChildren(self):
        """
        Generate Children
        """
        self.nextPopulation = []
        # --- append the breeder ---
        for i in range(len(self.parents)):
            self.nextPopulation.append(self.parents[i])
        # print(len(self.nextPopulation))
        # --- use the breeder to crossover
        for i in range(abs(self.npops-self.n_bestsam)-self.n_lucksam):
            par_ind = np.random.choice(len(self.parents),size=2,replace=False)
            child = self.crossover(self.parents[par_ind[0]],self.parents[par_ind[1]])
            self.nextPopulation.append(child)
        # print(len(self.nextPopulation))

        for i in range(self.n_lucksam):
            self.nextPopulation.append(self.generateIndividual())

        random.shuffle(self.nextPopulation)
        self.Populations = self.nextPopulation

    def findE0(self,mess=None):
        """
        Optimize E0 in the middle of the generations

        To Do:
        chi2(E0) vs E0
        """
        if mess == None:
            self.logger.info("Finished First Half of Generation, Optimizing E0...")
        else :
            self.logger.info(mess)
        lowestX = 99999
        lowestY = 99999
        listOfX = []
        listOfY = []
        # print(type(self.globBestFit[0]))
        # print(self.globBestFit[0].get_e0())
        bestFitlist = copy.deepcopy(self.globBestFit[0])
        # print(self.globBestFit[0].get_e0())

        for i in self.rangeE0_large:
            bestFitlist.set_e0(i)
            fit = self.fitness(bestFitlist)
            if fit < lowestY:
                lowestY = fit
                lowestX = i
            listOfX.append(i)
            listOfY.append(fit)
        self.logger.info("Continue With E0= " + str(round(lowestX,3)))
        newE0 = lowestX
        self.mut_chance_e0 = 0
        self.globBestFit[0].set_e0(newE0)
        self.globBestFit[1] = lowestY


    def run_verbose_start(self):
        """
        Visualize the verbose start place
        """
        self.logger.info("------------Inputs File Stats--------------")
        self.logger.info(f"{bcolors.BOLD}Data File{bcolors.ENDC}: {self.data_path}")
        self.logger.info(f"{bcolors.BOLD}Output File{bcolors.ENDC}: {self.output_path}")
        self.logger.info(f"{bcolors.BOLD}Log File{bcolors.ENDC}: {self.log_path}")
        self.logger.info(f"{bcolors.BOLD}CSV series{bcolors.ENDC}: {self.csv_series}")
        self.logger.info("--------------Populations------------------")
        # self.logger.info(f"{bcolors.BOLD}Population{bcolors.ENDC}:")
        self.logger.info(f"{bcolors.BOLD}Population{bcolors.ENDC}: {self.npops}")
        self.logger.info(f"{bcolors.BOLD}Num Gen{bcolors.ENDC}: {self.ngen}")
        self.logger.info(f"{bcolors.BOLD}Best Individuals{bcolors.ENDC}: {best_sample}")
        self.logger.info(f"{bcolors.BOLD}Lucky Survior{bcolors.ENDC}: {lucky_few}")
        self.logger.info("-----------------Paths---------------------")
        self.logger.info(f"{bcolors.BOLD}Individual Path{bcolors.ENDC}: {self.ind_options}")
        self.logger.info(f"{bcolors.BOLD}Population{bcolors.ENDC}: {self.npops}")
        self.logger.info(f"{bcolors.BOLD}Num Path{bcolors.ENDC}: {self.npaths}")
        self.logger.info(f"{bcolors.BOLD}Path{bcolors.ENDC}: {list(map(int,self.path_lists))}")
        self.logger.info(f"{bcolors.BOLD}Path Optimize{bcolors.ENDC}: {self.path_optimize}")
        self.logger.info("----------------Mutations------------------")
        self.logger.info(f"{bcolors.BOLD}Mutations{bcolors.ENDC}: {self.mut_chance}")
        self.logger.info(f"{bcolors.BOLD}E0 Mutations{bcolors.ENDC}: {self.mut_chance_e0}")
        self.logger.info(f"{bcolors.BOLD}Mutation Options{bcolors.ENDC}: {self.mut_opt}")
        self.logger.info("---------------Larch Paths-----------------")
        self.logger.info(f"{bcolors.BOLD}Kmin{bcolors.ENDC}: {self.Kmin}")
        self.logger.info(f"{bcolors.BOLD}Kmax{bcolors.ENDC}: {self.Kmax}")
        self.logger.info(f"{bcolors.BOLD}Kweight{bcolors.ENDC}: {self.Kweight}")
        self.logger.info(f"{bcolors.BOLD}Delta k{bcolors.ENDC}: {self.deltak}")
        self.logger.info(f"{bcolors.BOLD}R BKG{bcolors.ENDC}: {self.rbkg}")
        self.logger.info(f"{bcolors.BOLD}BKG Kw{bcolors.ENDC}: {self.bkgkw}")
        self.logger.info(f"{bcolors.BOLD}BKG Kmax{bcolors.ENDC}: {self.bkgkmax}")
        self.logger.info("-------------------------------------------")
        # self.logger.info(f"{bcolors.BOLD}Print Out{bcolors.END}: {self.printgraph})
        # print(f"{bcolors.BOLD}Printout{bcolors.ENDC}: {self.printgraph}")
        self.logger.info(f"{bcolors.BOLD}Steady State{bcolors.ENDC}: {steady_state}")
        self.logger.info(f"{bcolors.BOLD}Output Paths{bcolors.ENDC}: {num_output_paths}")
        self.logger.info("-------------------------------------------")

        # self.logger.info("-------------------------------------------")


    def run_verbose_end(self):
        """
        Verbose end
        """
        self.logger.info("-----------Output Stats---------------")
        self.logger.info(f"{bcolors.BOLD}Total Time(s){bcolors.ENDC}: {round(self.tt,4)}")
        self.logger.info(f"{bcolors.BOLD}File{bcolors.ENDC}: {self.data_path}")
        # print(f"{bcolors.BOLD}{bcolors.ENDC}: {self.npops}")
        # print(f"{bcolors.BOLD}Num Gen{bcolors.ENDC}: {self.ngen}")
        # print(f"{bcolors.BOLD}Num Path{bcolors.ENDC}: {self.npaths}")

        self.logger.info(f"{bcolors.BOLD}Path{bcolors.ENDC}: {self.path_lists}")
        self.logger.info(f"{bcolors.BOLD}Final Fittness Score{bcolors.ENDC}: {self.globBestFit[1]}")

        self.logger.info("-------------------------------------------")

    def run(self,detect_limits=False):
        """
        Run the actual code
        """
        self.run_verbose_start()
        self.historic = []
        self.historic.append(self.Populations)
        for i in range(self.ngen):
            temp_gen = self.next_generation(detect_limits=detect_limits)
            self.output_generations()
            # print(0.5*self.ngen)
            if i == int(0.5*self.ngen)-1:
                self.findE0()
            exit = self.check_steady_state()
            if exit == True:
                break

        self.findE0(mess='Finished Second Half of Generations, Optimizing E0...')
        self.run_verbose_end()
    def output_generations(self):
        """
        Output generations result into two files
        """
        try:
            f1 = open(self.file,"a")
        # f1.write(str(self.genNum) + "," + str(self.tdiff) + "," + str(self.currBestFit[1]) + "," + str(self.currBestFit[0].get()) + "," +
            # str(self.globBestFit[1]) + "," + str(self.globBestFit[0].get()) + "\n")
            f1.write(str(self.genNum) + "," + str(self.tdiff) + "," +
                str(self.currBestFit[1]) + "," + str(self.currBestFit[0].get()) +"," +
                str(self.globBestFit[1]) + "," + str(self.globBestFit[0].get()) +"\n")
        finally:
            f1.close()
        try:
            f2 = open(self.file_data,"a")
            write = csv.writer(f2)
            bestFit = self.globBestFit[0].get()
            # print(bestFit)
            for i in range(self.npaths):
                write.writerow((bestFit[i][0], bestFit[i][1], bestFit[i][2], bestFit[i][3]))
            f2.write("#################################\n")
        finally:
            f2.close()

    def __init__(self):
        """
        Steps to Initalize EXAFS
            EXAFS
        """
        # initialize params
        self.initialize_params()
        # variables
        self.initialize_variable(firstpass=True)
        # initialze file paths
        self.initialize_file_path()
        # initialize range
        self.initialize_range()
        self.initialize_group()

        # #  Initalize uses the following:
        # Initalization Step:
        #
        # For automatic range selection between different series, this requries
        # the following
        #
        # Intialize ranges:
        #
        # Secondary, calculate the percentages of each chances
        xftf(self.g.k, self.g.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
         kweight=self.Kweight, group=self.g, _larch=self.mylarch)
        xftf(self.best.k, self.best.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
         kweight=self.Kweight, group=self.best, _larch=self.mylarch)
        xftf(self.sumgroup.k, self.sumgroup.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
         kweight=self.Kweight, group=self.sumgroup, _larch=self.mylarch)

        self.exp = self.g.chi
        self.loadPaths()

        self.generateFirstGen()

        self.run()
        if self.path_optimize:
            self.paths_optimization_process()

            # variables
            self.initialize_variable()
            # initialze file paths
            self.initialize_file_path(firstpass=True)
            # initialize range
            self.initialize_range()

            self.initialize_group()

            xftf(self.g.k, self.g.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
             kweight=self.Kweight, group=self.g, _larch=self.mylarch)
            xftf(self.best.k, self.best.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
             kweight=self.Kweight, group=self.best, _larch=self.mylarch)
            xftf(self.sumgroup.k, self.sumgroup.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
             kweight=self.Kweight, group=self.sumgroup, _larch=self.mylarch)

            self.exp = self.g.chi

            self.loadPaths()
            self.generateFirstGen()

            self.run()

        if self.csv_series == True:
            for i in range(1,len(csv_file)):
                self.total_bestFit = self.globBestFit
                # variables
                self.initialize_variable()
                # initialze file paths
                self.initialize_file_path(i)
                # initialize range
                self.initialize_range(i,self.total_bestFit[0])
                self.initialize_group()

                xftf(self.g.k, self.g.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
                 kweight=self.Kweight, group=self.g, _larch=self.mylarch)
                xftf(self.best.k, self.best.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
                 kweight=self.Kweight, group=self.best, _larch=self.mylarch)
                xftf(self.sumgroup.k, self.sumgroup.chi, kmin=self.Kmin, kmax=self.Kmax, dk=4, window='hanning',
                 kweight=self.Kweight, group=self.sumgroup, _larch=self.mylarch)

                self.exp = self.g.chi
                # print(self.path_lists)
                # print("Load Path")
                self.loadPaths()
                #
                self.generateFirstGen()
                self.run(detect_limits=True)

def main():
    # from .helper import *
    # from .input_arg import *
    # from .import_lib import *
    # from .parser import read_input_file
    # from .ini_parser import *
    # from .initialization import loadPaths
    # from .exafs import *

    EXAFS_GA()
