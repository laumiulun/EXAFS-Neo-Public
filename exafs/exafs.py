from .helper import *
from .import_lib import *
from .ini_parser import *
from larch import Interpreter
from .pathObj import PathObject
from .individual import Individual
from .pathrange import Pathrange_limits
# from .run_verbose import *


class EXAFS_GA:

    def initialize_params(self, verbose=False):
        """Initalize Params

        Args:
            verbose (bool, optional): Verbosity. Defaults to False.
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
        self.intervalK = np.linspace(self.small, self.big, self.mid)

        self.path_optimize = path_optimize
        self.path_optimize_percent = path_optimize_percent
        self.path_optimize_only = optimize_only
        self.ind_options = individual_path
        self.ncomp = num_compounds
        self.printgraph = printgraph
        if self.printgraph:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111)
        self.pathrange_file = pathrange_file
        self.debug_mode = debug_mode

    def initialize_variable(self, firstpass=False):
        """Initalize the variables

        Args:
            firstpass (bool, optional): check if it first pass, for multi file optimization. Defaults to False.
        """
        self.genNum = 0
        self.nChild = 3
        self.globBestFit = [0, np.inf]
        self.currBestFit = [0, np.inf]
        self.bestDiff = np.inf
        self.bestBest = np.inf
        self.diffCounter = 0

        self.pathDictionary = {}

        self.bestChir_magTotal = [0]*(326)
        self.bestYTotal = [0]*(401)
        # Typical INI parameters
        if self.ind_options == True:
            if firstpass == True:
                self.path_lists = path_list
        else:
            self.path_lists = list(range(1, pathrange+1))
            for i in range(len(self.path_lists)):
                self.path_lists[i] = str(self.path_lists[i])

        # Calcualte total number of paths
        if self.ncomp > 1:
            self.npaths = 0
            for i in range(self.ncomp):
                self.npaths += len(self.path_lists[i])
        else:
            self.npaths = len(self.path_lists)

        self.npops = size_population
        self.ngen = number_of_generation
        self.steady_state = steady_state

        # Mutation Parameters
        self.mut_opt = mutated_options
        self.mut_chance = chance_of_mutation
        self.mut_chance_e0 = chance_of_mutation_e0
        self.sel_opt = selection_options
        self.cro_opt = crossover_options

        # Crosover Parameters
        self.n_bestsam = int(best_sample*self.npops*(0.01))
        self.n_lucksam = int(lucky_few*self.npops*(0.01))

        # Time related
        self.time = False
        self.tt = 0

        # CSV-Series check
        self.csv_percent = 0.2

        # reset e0
        self.secondhalf = False
        self.bestE0 = 0

    def initialize_logger(self):
        """Initialize logger
        """
        # Initialize logger
        self.logger = logging.getLogger('')

        # Delete handler
        self.logger.handlers = []
        file_handler = logging.FileHandler(
            self.log_path, mode='a+', encoding='utf-8')
        stdout_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)

        self.logger.setLevel(logging.INFO)
        self.logger.info(banner())

    def initialize_file_path(self, i=0, firstpass=False, path_optimize=False):
        """
        Initalize file paths for each of the file first
        """
        self.csv_series = csv_series
        self.base = os.getcwd()
        # self.front = os.path.join(self.base,feff_file)
        if self.ncomp > 1:
            self.front = []
            for i in range(self.ncomp):
                self.front.append(os.path.join(self.base, feff_file[i]))
        else:
            self.front = os.path.join(self.base, feff_file)

        if self.csv_series == True:
            self.data_path = os.path.join(self.base, csv_file[i])
            self.output_path = os.path.splitext(os.path.join(self.base, output_file))[
                0] + "_" + str(i) + ".csv"
            self.log_path = os.path.splitext(
                copy.deepcopy(self.output_path))[0] + ".log"

        else:
            self.data_path = os.path.join(self.base, csv_file)
            self.output_path = os.path.join(self.base, output_file)
            self.log_path = os.path.splitext(
                copy.deepcopy(self.output_path))[0] + ".log"
        if path_optimize:
            self.output_path = os.path.splitext(os.path.join(self.base, output_file))[
                0] + "_optimized.csv"

        self.end = '.dat'
        self.check_output_file(self.output_path)
        if not firstpass:
            self.check_if_exists(self.log_path)

        self.sabcor_file = sabcor_file
        self.sabcor_executable(firstpass=firstpass)

    def sabcor_executable(self, firstpass=True):
        """
        Call the sabcor executable from the submodules

        The sabcor exectuable is as follow:

        sabcor <file.test> <inp>

        if input file is <file.test>, output is <file_sac.test>

        """

        # TODO: need to check if sabcor has been compiled
        if self.sabcor_file is not None:
            # self.sabcor_file = os.path.join(self.base,sabcor_file)
            sabcor_exec = os.path.join(self.base, 'contrib/sabcor/bin/sabcor')
            sabcor_full_file = os.path.join(self.base, self.sabcor_file)
            # call sabcor
            command = [sabcor_exec, self.data_path, sabcor_full_file]
            p = subprocess.call(command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
            if p == 0:
                # self.logger.info('Sabcor Finished')
                self.data_path = os.path.splitext(
                    self.data_path)[0] + "_sac.csv"

    def check_if_exists(self, path_file):
        """
        Check if the directory exists
        """
        if os.path.exists(path_file):
            os.remove(path_file)
        # Make Directory when its missing
        path = pathlib.Path(path_file)
        path.parent.mkdir(parents=True, exist_ok=True)

    def check_output_file(self, file):
        """
        check if the output file for each file, assumes equality.
        """
        file_base = os.path.splitext(file)[0]
        self.check_if_exists(file)
        self.file = file

        self.file_initial = open(self.output_path, "a+")
        self.file_initial.write(
            "Gen,TPS,FITTNESS,CO_Score,Mut_Score,CURRFIT,CURRIND,BESTFIT,BESTIND\n")  # writing header
        self.file_initial.close()

        # Not using right now
        """
        # file_score = os.path.splitext(file)[0] + '_score.csv'
        # self.check_if_exists(file_score)
        # self.file_score = file_score
        """
        file_data = os.path.splitext(file)[0] + '_data.csv'
        self.check_if_exists(file_data)
        self.file_data = file_data

        # Not using right now
        file_gen = os.path.splitext(file)[0] + '_generations.csv'
        self.check_if_exists(file_gen)
        self.file_gen = file_gen

    def initialize_range(self, i=0, BestIndi=None):
        """
        Initalize range

        To Do list:
            Initalize range will be difference for each paths depend if the run are
            in series, therefore the ranges will self-adjust
        """

        if i == 0:
            self.pathrange_Dict = []
            if self.pathrange_file == None:
                for i in range(self.npaths):
                    self.pathrange_Dict.append(Pathrange_limits(i))

            else:
                # Read the path range file
                pathrange_file = read_pathrange_file(
                    self.pathrange_file, self.npaths)
                for i in range(self.npaths):
                    path_range_obj = Pathrange_limits(i, pathrange_file[i, :])
                    self.pathrange_Dict.append(path_range_obj)

            self.rangeE0 = (np.linspace(-100, 100, 201) *
                            0.01)  # <- e0, for everything
            # <- Larger range B
            self.rangeE0_large = (np.linspace(-600, 600, 1201) * 0.01)
        else:
            for k in range(self.npaths):
                path_bestfit = BestIndi.get_path(k)
                self.pathrange_Dict[k].mod_s02(path_bestfit[0])
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

        # Check if using k space, else autobk
        try:
            self.g.k
            self.g.chi
        except AttributeError:
            autobk(self.g, rbkg=rbkg, kweight=bkgkw,
                   kmax=bkgkmax, _larch=self.mylarch)
            autobk(self.best, rbkg=rbkg, _larch=self.mylarch)
            autobk(self.sumgroup, rbkg=rbkg, _larch=self.mylarch)

    def initialize_paths(self):
        """
        Initalized Paths for each scattering
        """
        self.e0 = np.random.choice(self.rangeE0)
        if self.ncomp == 1:
            for i, paths in enumerate(self.path):
                self.pathDictionary[paths] = pathObject(self.rangeS02,
                                                        self.e0,
                                                        self.rangeSigma2,
                                                        self.rangeDeltaR)
        # else:

        #     for i,paths in enumerate(path_list):
    def loadPaths(self):
        """
        Load paths:
            Initialize paths in various files.

        """
        self.pathname = []
        if self.ncomp > 1:
            if self.ind_options == True:
                for i in range(self.ncomp):
                    comp_path = len(self.path_lists[i])
                    for j in range(comp_path):

                        filename = self.front[i] + \
                            str(self.path_lists[i][j]).zfill(4) + self.end

                        pathName = "Comp" + \
                            str(i) + "Path" + self.path_lists[i][j]
                        self.pathname.append(pathName)
                        self.pathDictionary.update(
                            {pathName: feffdat.feffpath(filename, _larch=self.mylarch)})
        else:
            if self.ind_options == True:
                for i in range(self.npaths):
                    filename = self.front + \
                        str(self.path_lists[i]).zfill(4) + self.end
                    pathName = "Path" + self.path_lists[i]
                    self.pathname.append(pathName)
                    self.pathDictionary.update(
                        {pathName: feffdat.feffpath(filename, _larch=self.mylarch)})
            else:
                for i in range(1, self.npaths+1):
                    filename = self.front + str(i).zfill(4) + self.end
                    pathName = f"Path{i}"
                    self.pathname.append(pathName)
                    self.pathDictionary.update(
                        {pathName: feffdat.feffpath(filename, _larch=self.mylarch)})

    def generateIndividual(self, e0=None):
        """
        Generate Individuals using a random choice
        """
        if self.secondhalf == False:
            e0 = np.random.choice(self.rangeE0)

        ind = Individual(self.npaths, self.pathDictionary,
                         self.pathrange_Dict, self.path_lists, e0, self.pathname)
        return ind

    def generateFirstGen(self):
        """
        Generated Initial Generation
        """
        self.Populations = []
        for i in range(self.npops):
            self.Populations.append(self.generateIndividual())

        self.eval_Population()
        # self.bestDiff = 0

        self.globBestFit = self.currBestFit

    # @profile
    def fitness(self, indObj, return_tot=False):
        """
        Evaluate fitness of a individual
        """
        # t1 = time.time()
        loss = 0
        yTotal = [0] * (401)
        for i in range(self.npaths):
            path = self.pathDictionary.get(self.pathname[i])
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
            loss = loss + (yTotal[int(j)] * self.g.k[int(j)] ** self.Kweight -
                           self.exp[int(j)] * self.g.k[int(j)] ** self.Kweight) ** 2
        if return_tot:
            return loss, yTotal
        else:
            return loss

    def eval_Population(self, replace=True, sorting=True):
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

        for i, individual in enumerate(self.Populations):

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
        if sorting:
            self.sorted_population = sorted(
                populationPerf.items(), key=operator.itemgetter(1), reverse=False)
        if replace:
            self.currBestFit = list(self.sorted_population[0])
        return score

    def next_generation(self, detect_limits=False):
        self.st = time.time()
        self.logger.info(
            "---------------------------------------------------------")
        self.logger.info(datetime.datetime.fromtimestamp(
            self.st).strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.info(f"{bcolors.BOLD}Gen: {bcolors.ENDC}{self.genNum+1}")

        self.genNum += 1

        # Evaluate Fittness
        score = self.eval_Population()

        self.bestDiff = abs(self.globBestFit[1]-self.currBestFit[1])
        if self.currBestFit[1] < self.globBestFit[1]:
            self.globBestFit = self.currBestFit

        # elif self.genNum == 1:
        #     self.globBestFit = self.currBestFit

        # detecting if limits is hit on the bestfit

        self.logger.info(
            f"Best Fit: {bcolors.BOLD}{self.sorted_population[0][1].round(3)}{bcolors.ENDC}")
        self.logger.info(
            "2nd Fit: " + str(self.sorted_population[1][1].round(3)))
        self.logger.info(
            "3rd Fit: " + str(self.sorted_population[2][1].round(3)))
        self.logger.info(
            "4th Fit: " + str(self.sorted_population[3][1].round(3)))
        self.logger.info(
            "Last Fit: " + str(self.sorted_population[-1][1].round(3)))

        with np.printoptions(precision=3, suppress=True):
            self.logger.info(
                "Different from last best fit: " + str(self.bestDiff))
            self.logger.info(bcolors.BOLD + "Best fit: " +
                             bcolors.OKBLUE + str(self.currBestFit[1]) + bcolors.ENDC)
            CurrchiR = str(
                self.currBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "Best fit ChiR: " +
                             bcolors.OKBLUE + str(CurrchiR) + bcolors.ENDC)
            self.logger.info("Best fit combination:\n" +
                             str(np.asarray(self.sorted_population[0][0].get())))
            self.logger.info(bcolors.BOLD + "History Best: " +
                             bcolors.OKBLUE + str(self.globBestFit[1]) + bcolors.ENDC)
            GlobchiR = str(
                self.globBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "History Best ChiR: " +
                             bcolors.OKBLUE + str(GlobchiR) + bcolors.ENDC)
            self.logger.info("History Best Indi:\n" +
                             str(np.asarray(self.globBestFit[0].get())))

        nextBreeders = self.selectFromPopulation()

        # self.createChildren()
        if self.debug_mode:
            self.eval_Population(replace=False)
            self.crossover_score = self.sorted_population[0][1]
        else:
            self.crossover_score = 0
        self.mutatePopulation()
        if self.debug_mode:
            self.eval_Population(replace=False)
            self.mutation_score = self.sorted_population[0][1]
        else:
            self.mutation_score = 0
        self.et = timecall()
        self.tdiff = self.et - self.st
        self.tt = self.tt + self.tdiff
        self.report_after_generation()

    def report_after_generation(self):

        self.logger.info(
            f"Best Fit: {bcolors.BOLD}{self.sorted_population[0][1].round(3)}{bcolors.ENDC}")
        self.logger.info(
            "2nd Fit: " + str(self.sorted_population[1][1].round(3)))
        self.logger.info(
            "3rd Fit: " + str(self.sorted_population[2][1].round(3)))
        self.logger.info(
            "4th Fit: " + str(self.sorted_population[3][1].round(3)))
        self.logger.info(
            "Last Fit: " + str(self.sorted_population[-1][1].round(3)))
        # sys.exit()
        with np.printoptions(precision=3, suppress=True):
            # print(self.intervalK)
            self.logger.info(
                "Different from last best fit: " + str(self.bestDiff))
            self.logger.info(bcolors.BOLD + "Best fit: " +
                             bcolors.OKBLUE + str(self.currBestFit[1]) + bcolors.ENDC)
            CurrchiR = str(
                self.currBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "Best fit ChiR: " +
                             bcolors.OKBLUE + str(CurrchiR) + bcolors.ENDC)
            self.logger.info("Best fit combination:\n" +
                             str(np.asarray(self.sorted_population[0][0].get())))
            self.logger.info(bcolors.BOLD + "History Best: " +
                             bcolors.OKBLUE + str(self.globBestFit[1]) + bcolors.ENDC)
            GlobchiR = str(
                self.globBestFit[1]/(len(self.intervalK)-3*self.npaths+1))
            self.logger.info(bcolors.BOLD + "History Best ChiR: " +
                             bcolors.OKBLUE + str(GlobchiR) + bcolors.ENDC)
            self.logger.info("History Best Indi:\n" +
                             str(np.asarray(self.globBestFit[0].get())))

        self.logger.info("Number of Breeders: " + str(len(self.parents)))
        self.logger.info("DiffCounter: " + str(self.diffCounter))
        self.logger.info("Diff %: " + str(self.diffCounter / self.genNum))
        self.logger.info("Mutation Chance: " + str(self.mut_chance))
        if self.mut_opt == 2:
            self.logger.info("Mutation Percentage" +
                             str(np.round(self.nmutate_success/self.nmutate, 4)))
        self.logger.info("Time: " + str(round(self.tdiff, 5)) + "s")
        if self.printgraph:
            # total = self.globBestFit[0].verbose_yTotal(self.intervalK)
            self.verbose_graph()

    def verbose_graph(self, end=False):
        """_summary_

        Args:
            end (bool, optional): _description_. Defaults to False.
        """
        total = self.globBestFit[0].verbose_yTotal(self.intervalK)
        k_xlabel = "k ($\AA^{-1}$)"
        k_ylabel = "k$^{" + str(int(self.Kweight)) + \
            "}$ ($\chi(k)\AA^{-" + str(int(self.Kweight)) + "}$)"

        r_xlabel = "R ($\AA$)"
        r_ylabel = "$ ($\chi(R)\AA^{-" + str(int(self.Kweight)-1) + "}$)"

        title = 'Generation: ' + str(self.genNum)
        if end == True:
            fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(10, 5))
            # grab a random path for the x
            path = self.pathDictionary.get(self.pathname[0])
            self.best.k = path.k
            self.best.chi = total
            xftf(self.best.k, self.best.chi, kmin=self.Kmin, kmax=self.Kmax,
                 dk=4, window='hanning', kweight=self.Kweight, group=self.best)
            ax[0].plot(self.g.k, self.g.chi*self.g.k **
                       self.Kweight, 'b', label='Experiments')
            ax[0].plot(self.g.k[self.small:self.big], total[self.small:self.big] *
                       self.g.k[self.small:self.big]**self.Kweight, 'r', label='Machine Learning')
            ax[0].set_title('K Space')
            ax[0].set_xlabel(k_xlabel)
            ax[0].set_ylabel(k_ylabel)
            ax[0].legend()

            ax[1].plot(self.g.r, self.g.chir_mag, 'b', label='Experiments')
            ax[1].plot(self.best.r, self.best.chir_mag,
                       'r', label='Machine Learning')
            ax[1].set_title('R Space')
            ax[1].set_xlabel(r_xlabel)
            ax[1].set_xlabel(r_ylabel)
            ax[1].legend()
            plt.show()
        else:
            self.ax.plot(self.g.k, self.g.chi*self.g.k **
                         self.Kweight, 'b', label='Experiments')
            self.ax.plot(self.g.k[self.small:self.big], total[self.small:self.big] *
                         self.g.k[self.small:self.big]**self.Kweight, 'r', label='Machine Learning')
            self.ax.legend()
            self.ax.set_xlabel(k_xlabel)
            self.ax.set_ylabel(k_ylabel)
            self.ax.set_title(title)

            plt.show(block=False)
            plt.pause(0.001)
            plt.cla()

    def detect_and_adjust_limits(self):
        """
        On development
        """
        best_Fit = self.globBestFit[0].get()

        for i in range(len(self.pathrange_Dict)):
            temp_range = self.pathrange_Dict[i].getrange()

            self.logger.info(best_Fit[i, 0])

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
            # Rechenberg mutation
            if self.genNum > 20:
                if self.bestDiff < 0.1:
                    self.diffCounter += 1
                else:
                    self.diffCounter -= 1
                if (abs(self.diffCounter) / float(self.genNum)) > 0.2:
                    self.mut_chance += 2.5
                    self.mut_chance = abs(self.mut_chance)
                elif (abs(self.diffCounter) / float(self.genNum)) < 0.2:
                    self.mut_chance -= 2.5
                    self.mut_chance = abs(self.mut_chance)
            # Mutation
        for i in range(self.npops):
            if random.random()*100 < self.mut_chance:
                self.nmutate += 1
                self.Populations[i] = self.mutateIndi(i)

        if self.secondhalf == False:
            if random.random() * 100 < self.mut_chance_e0:
                e0 = random.choice(self.rangeE0)
                self.logger.info("Mutate e0 to: " + str(np.round(e0, 3)))
                for individual in self.Populations:
                    individual.set_e0(e0)

        self.logger.info("Mutate Times: " + str(self.nmutate))

    def mutateIndi(self, indi):
        """
        Generate new individual during mutation operator
        """
        if self.mut_opt == 0:
            # Create a new individual with Rechenberg
            newIndi = self.generateIndividual(self.bestE0)
        # Random pertubutions
        if self.mut_opt == 1:
            # Random Pertubutions
            self.Populations[indi].mutate_paths(self.mut_chance)
            newIndi = self.Populations[indi]
            # Mutate every gene in the Individuals
        if self.mut_opt == 2:
            # initalize_variable:
            self.nmutate_success = 0
            og_indi = copy.deepcopy(self.Populations[indi])
            og_score = self.fitness(og_indi)
            mut_indi = copy.deepcopy(self.Populations[indi])
            mut_indi.mutate_paths(self.mut_chance)
            mut_score = self.fitness(mut_indi)

            T = - self.bestDiff/np.log(1-(self.genNum/self.ngen))
            if mut_score < og_score:
                self.nmutate_success = self.nmutate_success + 1
                newIndi = mut_indi
            elif np.exp(-(mut_score-og_score)/T) > np.random.uniform():
                self.nmutate_success = self.nmutate_success + 1
                newIndi = mut_indi
            else:
                newIndi = og_indi
        if self.mut_opt == 3:
            def delta_fun(t, delta_val):
                rnd = np.random.random()
                return delta_val*(1-rnd**(1-(t/self.ngen))**5)

            og_indi = copy.deepcopy(self.Populations[indi])
            og_data = og_indi.get_var()
            for i, path in enumerate(og_data):
                print(i, path)
                arr = np.random.randint(2, size=3)
                for j in range(len(arr)):
                    new_path = []
                    val = path[j]
                    if arr[j] == 0:
                        UP = self.pathrange_Dict[i].get_lim()[j+1][1]
                        del_val = delta_fun(self.genNum, UP-val)
                        val = val + del_val
                    if arr[j] == 1:
                        LB = self.pathrange_Dict[i].get_lim()[j+1][0]
                        del_val = delta_fun(self.genNum, val-LB)
                    new_path.append(val)
                self.Populations[indi].set_path(
                    i, new_path[0], new_path[1], new_path[2])
        if self.mut_opt == 4:
            newIndi = self.generateIndividual(self.bestE0)
        return newIndi

    def selectFromPopulation(self):
        self.parents = []
        # choose the top samples
        if self.sel_opt == 0:
            for i in range(self.n_bestsam):
                self.parents.append(self.sorted_population[i][0])

        self.createChildren()

    def crossover(self, individual1, individual2):
        """
        Uniform Cross-Over, 50% percentage chance
        """
        if self.cro_opt == 0:
            child = self.generateIndividual(self.bestE0)
            if np.random.randint(0, 1) == True:
                child.set_e0(individual1.get_e0())
            else:
                child.set_e0(individual2.get_e0())

            for i in range(self.npaths):
                individual1_path = individual1.get_path(i)
                individual2_path = individual2.get_path(i)

                temp_path = []
                for j in range(4):
                    if np.random.randint(0, 2) == True:
                        temp_path.append(individual1_path[j])
                    else:
                        temp_path.append(individual2_path[j])

                child.set_path(i, temp_path[0], temp_path[2], temp_path[3])
        elif self.cro_opt == 1:
            # AND Arithmetric
            child = self.generateIndividual(self.bestE0)
            if np.random.randint(0, 1) == True:
                child.set_e0(individual1.get_e0())
            else:
                child.set_e0(individual2.get_e0())

            for i in range(self.npaths):
                individual1_path = individual1.get_path(i)
                individual2_path = individual2.get_path(i)

                temp_path = []
                for j in range(4):
                    ind_1 = np.random.randint(0, 2)
                    ind_2 = np.random.randint(0, 2)
                    if np.logical_and(ind_1, ind_2):
                        temp_path.append(individual1_path[j])
                    else:
                        temp_path.append(individual2_path[j])

                child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        elif self.cro_opt == 2:
            # AND Arithmetric
            child = self.generateIndividual(self.bestE0)
            if np.random.randint(0, 1) == True:
                child.set_e0(individual1.get_e0())
            else:
                child.set_e0(individual2.get_e0())

            for i in range(self.npaths):
                individual1_path = individual1.get_path(i)
                individual2_path = individual2.get_path(i)

                temp_path = []
                for j in range(4):
                    ind_1 = np.random.randint(0, 2)
                    ind_2 = np.random.randint(0, 2)
                    if np.logical_or(ind_1, ind_2):
                        temp_path.append(individual1_path[j])
                    else:
                        temp_path.append(individual2_path[j])

                child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        return child

    @staticmethod
    def flatten_path(path_lists):
        """Flatten the paths

        Args:
            path_lists (list): Path lists

        Returns:
            list: Flattened path list
        """
        flatlist=[]
        for sublist in path_lists:
            for element in sublist:
                flatlist.append(element)
        return flatlist

    @staticmethod
    def get_sum_path(path_lists,ncomp):
        """Get the sum of each components

        Args:
            path_lists (list): Path lists
            ncomp (int): Number of components

        Returns:
            list: List of sum of each components
        """
        sum_path = []
        if ncomp > 1:
            for i in range(ncomp):
                sum_path.append(len(path_lists[i]))
        return sum_path

    @staticmethod
    def path_optimization_multicomp(path_lists,new_path_ind,ncomp):
        """Path optimizations for multiple components

        Args:
            path_lists (lists): Path lists
            new_path_ind (lists): Optimize path index
            ncomp (int): Number of components

        Returns:
            (list): Optimized path lists
        """
        flat_path = EXAFS_GA.flatten_path(path_lists)
        cumsum_path = np.cumsum(EXAFS_GA.get_sum_path(path_lists,ncomp))

        new_path_list = []
        temp_path = []

        k = 0
        for i,path in enumerate(flat_path):
            if i in new_path_ind:
                temp_path.append(path)
            if i+1 == cumsum_path[k]:
                new_path_list.append(temp_path)
                k +=1
                temp_path = []

        return new_path_list

    def paths_optimization_process(self):
        if timeing_mode:
            t0 = timecall()
        self.logger.info("-------------------")
        self.logger.info("Paths Optimization")
        self.logger.info("-------------------")

        arr = np.asarray(self.globBestFit[0].get())
        total = 0
        # Contribution of each path
        contrib = []

        for i, (key, value) in enumerate(self.pathDictionary.items()):

            path = feffdat.feffpath(value.filename, s02=str(arr[i, 0]), e0=str(arr[i, 1]),
                                    sigma2=str(arr[i, 2]), deltar=str(arr[i, 3]), _larch=self.mylarch)
            feffdat.path2chi(path, _larch=self.mylarch)

            xftf(path.k, path.chi*path.k**self.Kweight, kmin=self.Kmin, kmax=self.Kmax, dk=4,
                 window='hanning', kweight=self.Kweight, group=path, _larch=self.mylarch)

            area = simps(path.chir_mag, path.r)
            total += area
            contrib.append(area)

        print(contrib)
        contrib_p = [i/total for i in contrib]
        new_path_ind = (np.argwhere(np.array(contrib_p) >=
                        self.path_optimize_percent)).flatten()

        if timeing_mode:
            t1 = timecall() - t0
            self.logger.info('Path Optimization took %.2f second' % t1)

        if self.ncomp > 1:
            new_path = EXAFS_GA.path_optimization_multicomp(self.path_lists,new_path_ind,self.ncomp)
        else:
            new_path = []
            for i in new_path_ind:
                if i in new_path_ind:
                    new_path.append(self.path_lists[i])

        self.path_lists = new_path
        self.ind_options = True

        self.logger.info(f"New Paths: {self.path_lists}")
        self.logger.info(f"Percentage: {str(contrib_p)}")

    def createChildren(self):
        """
        Generate Children

        Todo.
            Need to separate this into multiple functions
        """
        self.nextPopulation = []
        # --- append the breeder to there first ---
        # Rank selection
        if self.sel_opt == 0:
            for i in range(len(self.parents)):
                self.nextPopulation.append(self.parents[i])
            # --- use the breeder to crossover
            for i in range(abs(self.npops-self.n_bestsam)-self.n_lucksam):
                par_ind = np.random.choice(
                    len(self.parents), size=2, replace=False)
                child = self.crossover(
                    self.parents[par_ind[0]], self.parents[par_ind[1]])
                self.nextPopulation.append(child)

            for i in range(self.n_lucksam):
                self.nextPopulation.append(
                    self.generateIndividual(self.bestE0))
            # Shuffle the populations
            random.shuffle(self.nextPopulation)
        # Roulette Wheel Selection
        elif self.sel_opt == 1:
            totalFitness = 0
            fitness_arr = []
            for i in range(self.npops):
                totalFitness += self.sorted_population[i][1]
                fitness_arr.append(self.sorted_population[i][1])

            cum_prob = np.array(fitness_arr)/totalFitness
            print(np.sum(cum_prob))
            print(totalFitness)
            print(cum_prob)
            # sys.exit()
        self.Populations = self.nextPopulation

    def findE0(self, mess=None):
        """
        Optimize E0 in the middle of the generations
        """
        if mess == None:
            self.logger.info(
                "Finished First Half of Generation, Optimizing E0...")
        else:
            self.logger.info(mess)

        listOfX = []
        listOfY = []
        CurrInd = copy.deepcopy(self.globBestFit[0])
        CurrScore = copy.deepcopy(self.globBestFit[1])
        CurrE0 = CurrInd.get_e0()
        for i in self.rangeE0_large:
            CurrInd.set_e0(i)
            fitScore = self.fitness(CurrInd)
            if fitScore < CurrScore:
                CurrE0 = i
                CurrScore = fitScore
            # listOfX.append(i)
            # listOfY.append(fit)
        self.logger.info("Continue With E0= " + str(round(CurrE0, 3)))
        newE0 = CurrE0
        self.bestE0 = newE0
        # print(self.bestE0)
        self.mut_chance_e0 = 0
        self.globBestFit[0].set_e0(newE0)
        self.globBestFit[1] = CurrScore

        for i in self.Populations:
            i.set_e0(self.bestE0)

        self.output_generations()

    def run_verbose_start(self):
        """
        Visualize the verbose start place
        """
        if self.debug_mode:
            self.logger.info(f"{bcolors.BOLD}DEBUG-MODE{bcolors.ENDC}")
        self.logger.info("------------Inputs File Stats--------------")
        self.logger.info(
            f"{bcolors.BOLD}Data File{bcolors.ENDC}: {self.data_path}")
        self.logger.info(
            f"{bcolors.BOLD}Feff File{bcolors.ENDC}: {self.front}")
        self.logger.info(
            f"{bcolors.BOLD}Output File{bcolors.ENDC}: {self.output_path}")
        self.logger.info(
            f"{bcolors.BOLD}Log File{bcolors.ENDC}: {self.log_path}")
        self.logger.info(
            f"{bcolors.BOLD}Paths Range File{bcolors.ENDC}: {self.pathrange_file}")
        self.logger.info(
            f"{bcolors.BOLD}CSV series{bcolors.ENDC}: {self.csv_series}")
        self.logger.info("--------------Populations------------------")
        # self.logger.info(f"{bcolors.BOLD}Population{bcolors.ENDC}:")
        self.logger.info(
            f"{bcolors.BOLD}Population{bcolors.ENDC}: {self.npops}")
        self.logger.info(f"{bcolors.BOLD}Num Gen{bcolors.ENDC}: {self.ngen}")
        self.logger.info(
            f"{bcolors.BOLD}Best Individuals{bcolors.ENDC}: {best_sample}")
        self.logger.info(
            f"{bcolors.BOLD}Lucky Survior{bcolors.ENDC}: {lucky_few}")
        self.logger.info("-----------------Paths---------------------")
        self.logger.info(
            f"{bcolors.BOLD}Individual Path{bcolors.ENDC}: {self.ind_options}")
        self.logger.info(
            f"{bcolors.BOLD}Num Path{bcolors.ENDC}: {self.npaths}")
        self.logger.info(f"{bcolors.BOLD}Paths {bcolors.ENDC}: {self.path_lists}")
        self.logger.info(
            f"{bcolors.BOLD}Path Optimize{bcolors.ENDC}: {self.path_optimize}")
        self.logger.info(
            f"{bcolors.BOLD}Path Optimize Percent{bcolors.ENDC}: {self.path_optimize_percent}")
        self.logger.info(
            f"{bcolors.BOLD}Path Optimize Only{bcolors.ENDC}: {self.path_optimize_only}")
        self.logger.info("----------------Mutations------------------")
        self.logger.info(
            f"{bcolors.BOLD}Mutations{bcolors.ENDC}: {self.mut_chance}")
        self.logger.info(
            f"{bcolors.BOLD}E0 Mutations{bcolors.ENDC}: {self.mut_chance_e0}")
        self.logger.info(
            f"{bcolors.BOLD}Mutation Options{bcolors.ENDC}: {self.mut_opt}")
        self.logger.info(
            f"{bcolors.BOLD}Selection Options{bcolors.ENDC}: {self.sel_opt}")
        # self.logger.info(f"{bcolors.BOLD}Selection Options{bcolors.ENDC}: {self.cro_opt}")
        self.logger.info("---------------Larch Paths-----------------")
        self.logger.info(f"{bcolors.BOLD}Kmin{bcolors.ENDC}: {self.Kmin}")
        self.logger.info(f"{bcolors.BOLD}Kmax{bcolors.ENDC}: {self.Kmax}")
        self.logger.info(
            f"{bcolors.BOLD}Kweight{bcolors.ENDC}: {self.Kweight}")
        self.logger.info(f"{bcolors.BOLD}Delta k{bcolors.ENDC}: {self.deltak}")
        self.logger.info(f"{bcolors.BOLD}R BKG{bcolors.ENDC}: {self.rbkg}")
        self.logger.info(f"{bcolors.BOLD}BKG Kw{bcolors.ENDC}: {self.bkgkw}")
        self.logger.info(
            f"{bcolors.BOLD}BKG Kmax{bcolors.ENDC}: {self.bkgkmax}")
        self.logger.info("-------------------------------------------")
        # self.logger.info(f"{bcolors.BOLD}Print Out{bcolors.END}: {self.printgraph})
        # print(f"{bcolors.BOLD}Printout{bcolors.ENDC}: {self.printgraph}")
        self.logger.info(
            f"{bcolors.BOLD}Steady State{bcolors.ENDC}: {self.steady_state}")
        self.logger.info(
            f"{bcolors.BOLD}Print Graph{bcolors.ENDC}: {self.printgraph}")
        # self.logger.info(f"{bcolors.BOLD}Output Paths{bcolors.ENDC}: {num_output_paths}")
        self.logger.info("-------------------------------------------")

    def run_verbose_end(self):
        """
        Verbose end
        """
        self.logger.info("-----------Output Stats---------------")
        self.logger.info(
            f"{bcolors.BOLD}Total Time(s){bcolors.ENDC}: {round(self.tt,4)}")
        self.logger.info(f"{bcolors.BOLD}File{bcolors.ENDC}: {self.data_path}")
        self.logger.info(
            f"{bcolors.BOLD}Path{bcolors.ENDC}: {self.path_lists}")
        self.logger.info(
            f"{bcolors.BOLD}Final Fittness Score{bcolors.ENDC}: {self.globBestFit[1]}")
        self.logger.info("-------------------------------------------")
        if self.printgraph:
            self.verbose_graph()

    def run(self, detect_limits=False):
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
            if i > int(0.5*self.ngen)-1:
                self.secondhalf = True

            exit = self.check_steady_state()
            if exit == True:
                break

        self.findE0(
            mess='Finished Second Half of Generations, Optimizing E0...')
        self.run_verbose_end()

    def output_generations(self):
        """
        Output generations result into two files

        """
        try:
            f1 = open(self.file, "a")
            f1.write(str(self.genNum) + "," + str(self.tdiff) + "," +
                     str(self.currBestFit[1]) + "," + str(self.crossover_score) + "," +
                     str(self.mutation_score) + "\n")
            # f1.write(str(self.genNum) + "," + str(self.tdiff) + "," +
            #     str(self.crossover_score)+ "," + str(self.mutation_score) + "," +
            #     str(self.currBestFit[1]) + "," + str(self.currBestFit[0].get()) +"," +
            #     str(self.globBestFit[1]) + "," + str(self.globBestFit[0].get()) +"\n")
        finally:
            f1.close()
        try:
            f2 = open(self.file_data, "a")
            write = csv.writer(f2)
            bestFit = self.globBestFit[0].get()
            # print(bestFit)
            for i in range(self.npaths):
                write.writerow(
                    (bestFit[i][0], bestFit[i][1], bestFit[i][2], bestFit[i][3]))
            f2.write("#################################\n")
        finally:
            f2.close()

        # file_npz = os.path.splitext(self.file)[0] + "/generations_" + str(self.genNum) + ".npz"
        # file_fit = os.path.splitext(self.file)[0] + "/fits_" + str(self.genNum) + ".csv"
        # npz_list = []
        # fit_list = []
        # for i in range(self.npops):
        #     npz_list.append(np.array(self.sorted_population[i][0].get()))
        #     fit_list.append(self.sorted_population[i][1])
        #
        # fit_list = np.array(fit_list)
        # # for i in range(self.npops):
        # np.savez(file_npz,*npz_list)
        # np.savetxt(file_fit,fit_list,delimiter=',')
        #

    def __init__(self):
        """
        Steps to Initalize EXAFS
        """
        # initialize params
        self.initialize_params()
        # initalize variables
        self.initialize_variable(firstpass=True)
        # initialze file paths
        self.initialize_file_path()
        # initalize logger
        self.initialize_logger()
        # initialize range
        self.initialize_range()
        # initalize group
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
        if self.path_optimize_only:
            self.paths_optimization_process()

        if self.path_optimize:
            self.paths_optimization_process()

            # variables
            self.initialize_variable()
            # initialze file paths
            self.initialize_file_path(path_optimize=True)
            # initalize logger
            self.initialize_logger()
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
            for i in range(1, len(csv_file)):
                self.total_bestFit = self.globBestFit
                # variables
                self.initialize_variable()
                # initialze file paths
                self.initialize_file_path(i)
                # initialize range
                self.initialize_range(i, self.total_bestFit[0])
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
                self.run(detect_limits=True)


def main():

    EXAFS_GA()
