"""
Authors    Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      andylau@u.boisestate.edu, jterry@agni.phys.iit.edu, minlong@boisestate.edu
Version    0.2.0
Date       July 4, 2021

EXAFS Analysis Wrapper Functions, contains Latex, Igor Pro
"""

import sys,glob,re,os
import numpy as np
import matplotlib.pyplot as plt
import larch_score
from larch.xafs import autobk, xftf
from scipy.integrate import simps
import re
import fnmatch

def sort_fold_list(dirs):
    fold_list = list_dirs(dirs)
    fold_list.sort(key=natural_keys)
    return fold_list

## Human Sort
def list_dirs(path):
    return [os.path.basename(x) for x in filter(
        os.path.isdir, glob.glob(os.path.join(path, '*')))]

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/generate_label200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def calculate_occurances(folder_name: str,paths,limits=20.0):
    """Calculate Occurances plot

    Args:
        folder_name (str): Folder name
        paths (list): path list
        limits (float, optional): limit parameters. Defaults to 20.
    """
    def compute_log_files(folder,og_paths):
        # calculate the number of log for each path optimizaiton
        files = []
        for r, d, f in os.walk(folder):
            f.sort(key = natural_keys)
            for file in f:
                # if re.search('test_\d+_data.csv',file):
                if fnmatch.fnmatch(file,'*.log'):
                    files.append(os.path.join(r, file))

        occ_list = np.zeros(len(og_paths))
        # print(og_paths)
        for i in range(len(files)):
            with open(files[i]) as f:
                for line in f:
                    if 'New Paths:' in line:
                        temp_str = []
                        list_str = line[12:-2].split(',')
                        # print(list_str)
                        for i in range(len(list_str)):
                            # temp_str.append(list_str[i][1:-1])
                            temp_str.append(int(list_str[i].replace("'","")))
                        # print(temp_str)
                        for i,cur_path in enumerate(temp_str):
                            for j,og_path in enumerate(og_paths):
                                # print(i,cur_path)
                                if cur_path == og_path:
                                    occ_list[j] +=1

        return occ_list,len(files)
    occ_list,nfiles = compute_log_files(folder_name,paths)
    j2 = np.argwhere(occ_list/nfiles > limits)
    # print(repr(j2.flatten()+1))
    return occ_list

def plot_occ_list(folder_name: str,limits:int,paths,fig_gui=None):
    """Plot Occurances list

    Args:
        folder_name (str): folder name
        limits (float): limit parameters, default is 20
        paths (list): _description_
        fig_gui (fig, optional): _description_. Defaults to None.
    """
    occ_list = calculate_occurances(folder_name,paths,limits)
    if fig_gui == None:
        plt.figure(figsize=(8,5))
        plt.xticks(paths);
        plt.bar(paths,occ_list)
    else:
        ax = fig_gui.add_subplot(111)
        # ax.xticks
        ax.set_xticks(paths)
        # ax.set_xticklabels(self.label,rotation=70)
        ax.bar(paths,occ_list)
        fig_gui.tight_layout()


class EXAFS_Analysis:
    """
    Set up analysis of EXAFS dataset

    Inputs:
        paths (list): list containing paths numbers
        dirs (str): str pointing the files locations
        params (dics): dicts contain all parameters
    """
    def __init__(self,paths,dirs,params):
        self.paths = paths
        # Generate Label for plotting
        self.flat_paths = larch_score.flatten_2d_list(self.paths)
        self.label = larch_score.generate_labels(self.flat_paths)[0]
        self.params = params
        self.dirs = dirs
        self.num_paths = len(self.flat_paths)
        self.num_params = 3*self.num_paths + 1
        self.return_str = ""
        if 'optimize' not in params:
            self.params['optimize'] = False

        if 'series' not in params:
            self.series = False
        else:
            self.series = self.params['series']
            self.series_index = self.params['series_index']

    def read_optimize_paths(self,files_opt):
        """
        Read optimize paths

        Args:
            files_opt (file): optimized paths
        """
        optimize_path = []
        for i in range(len(files_opt)):
            # print(files_opt[i])
            with open(files_opt[i]) as fp:
                for j, line in enumerate(fp):
                    if j == 1:
                        # clean up the newline symbol
                        clean = line.replace("]\n","")
                        clean = clean.replace("[","")
                        clean_arr = np.fromstring(clean,dtype = int,sep="  ")

                        optimize_path.append(clean_arr)
                        # print(line)

        # print(optimize_path)
        self.optimize_path = optimize_path

    def read_result_files(self,folder,series=False,series_index=None,verbose=False):
        """
        read result files (helper function)

        Inputs:
            folder (str): str pointing the files locations
        """
        num_path = self.num_paths
        full_mat = []
        files = []
        folder = self.dirs

        if self.params['optimize'] == True:
            files_opt = []
            files_opt_data = []


        if os.path.isdir(folder) == True:
            self.params['individual'] = False

            # self.return_str += str(folder + "\n")
            search_string = '*_*_' + str(series_index) + '_data.csv'

            f = os.listdir(folder)
            f.sort(key = natural_keys)
            for file in f:
                # various checks in place
                # print(file,fnmatch.fnmatch(file,'*_data.csv'))
                if series == False:
                    if fnmatch.fnmatch(file,'*_data.csv'):
                        files.append(os.path.join(folder, file))
                elif series == True:
                    if fnmatch.fnmatch(file,search_string):
                        files.append(os.path.join(folder, file))
                elif self.params['optimize'] == True:
                    if re.search('test_\d+_optimized.csv',file):
                        files_opt.append(os.path.join(folder, file))
                    if re.search('test_\d+_optimized_data.csv',file):
                        files_opt_data.append(os.path.join(folder, file))
        else:
            self.params['individual'] = True
            files.append(folder)
        if verbose:
            print(folder)
        files.sort(key=natural_keys)
        if self.params['optimize'] == True:
            files_opt.sort(key=natural_keys)
            files_opt_data.sort(key=natural_keys)
            self.read_optimize_paths(files_opt)
        # loop through all the files:
        # 1.
        for i in range(len(files)):
            file = files[i]
            try:
                # check if the paths exists first
                os.path.exists(file)
                # read the resulting csv
                gen_csv = np.genfromtxt(file,delimiter=',')
                gen_csv_unflatten = gen_csv.reshape((-1,4*num_path))

                gen_csv_best_unflatten = gen_csv[-num_path::].reshape((-1,4*num_path))

                if self.params['individual']:
                    full_mat = gen_csv_unflatten
                    best_full_mat = gen_csv_best_unflatten
                else:
                    if i == 0:
                        full_mat = gen_csv_unflatten
                        best_full_mat = gen_csv_best_unflatten
                    best_full_mat = np.vstack((best_full_mat,gen_csv_best_unflatten))
                    full_mat = np.vstack((full_mat,gen_csv_unflatten))
            except OSError:
                print(" " + str(i) + " Missing")
                pass

        return full_mat,best_full_mat

    def extract_data(self,data=None,verbose=True):
        """ Extract the data
        Args:
            data (list, optional): if inputted data instead. Defaults to None.
            verbose (bool, optional): verbosity. Defaults to True.
        """
        if data == None:
            full_mat,bestfit_full_mat = self.read_result_files(self.dirs,self.series,self.series_index,verbose=verbose)
        bestFit,err = self.construct_bestfit_err_mat(full_mat,bestfit_full_mat,self.paths)

        if self.params['individual']:
            best_Fit = bestfit_full_mat.reshape(-1,4).round(6)
        else:
            # best_Fit = np.mean(full_mat,axis=0).reshape(-1,4).round(6)
            # best_Fit = full_mat[-1]
            best_Fit = bestfit_full_mat.reshape(-1,4).round(6)
        if verbose:
            print(f"Individual Path: {self.params['individual']}")
            print(best_Fit)
        self.bestFit = bestFit
        self.err = err
        self.bestFit_mat = best_Fit

    def larch_init(self):
        """
        Initialize larch helper function in the background
        """
        csv_path = os.path.join(self.params['base'],self.params['CSV'])
        exp,g,params,mylarch = larch_score.larch_init(csv_path,self.params)

        self.g = g
        self.exp = exp
        self.small = params['SMALL']
        self.big = params['BIG']
        self.intervalK = params['intervalK']
        self.kweight = params['kweight']
        self.mylarch = mylarch

    def larch_score(self,verbose=True):
        """
        Calculate fitness score based on Chi and ChiR

        Args:
            verbose (bool, optional): if verbose output. Defaults to True.
        """

        path,yTotal,best,loss,best_Fit_r,arr= larch_score.fitness(self.exp,self.bestFit_mat,self.paths,self.params,return_r=True,verbose=verbose)
        self.return_str += arr

        chir2 = (loss/(len(self.intervalK)-self.num_params)).round(6)

        if verbose:
            print(f"Fitness Score (Chi2): {np.round(loss,6)}")
            print(f"Fitness Score (ChiR2): {np.round(chir2,6)}")

        self.path = path
        self.yTotal = yTotal
        self.best = best
        self.loss = loss
        self.chir2 = chir2
        self.best_Fit_r = best_Fit_r


    def plot(self,title='Temp',fig_gui=None,show=False):
        """
        Plot the K and R Space

        Args:
            title (str, optional): Title of the plot. Defaults to 'Test'.
            fig_gui (pyplot, optional): Matplotlib gui for passing in. Defaults to None.
            show (bool, optional): if showing. Defaults to False.
        """

        SMALL = self.small
        BIG = self.big

        self.best.k = self.path.k
        self.best.chi = self.yTotal
        xftf(self.best.k,self.best.chi,kmin=self.params['Kmin'],kmax=self.params['Kmax'],dk=4,window='hanning',kweight=self.kweight,group=self.best)

        if fig_gui == None:
            fig, ax = plt.subplots(1, 2,figsize=(15,5))

            ax[0].plot(self.g.k, self.g.chi*self.g.k**self.kweight,'b--',label="Experiment Data")
            ax[0].plot(self.path.k[SMALL:BIG], self.yTotal[SMALL:BIG]*self.path.k[SMALL:BIG]**self.kweight,'r-',label="Genetic Algorithm")
            ax[0].set_xlim((0,self.params['Kmax']))
            ax[0].legend()
            ax[0].set_title(title + " K Space")

            ax[1].plot(self.g.r,self.g.chir_mag,'b--',label='Experiment Data')
            ax[1].plot(self.best.r,self.best.chir_mag,'r-',label='Genetic Algorithm')
            ax[1].set_title(title + " R Space")
            ax[1].legend()
        else:
            ax = fig_gui.add_subplot(121)

            ax.plot(self.g.k, self.g.chi*self.g.k**self.kweight,'b--',label="Experiment Data")
            ax.plot(self.path.k[SMALL:BIG], self.yTotal[SMALL:BIG]*self.path.k[SMALL:BIG]**self.kweight,'r-',label="Genetic Algorithm")
            ax.legend()
            ax.set_title(title + " K Space")

            ax = fig_gui.add_subplot(122)

            ax.plot(self.g.r,self.g.chir_mag,'b--',label='Experiment Data')
            ax.plot(self.best.r,self.best.chir_mag,'r-',label='Genetic Algorithm')
            ax.set_title(title + " R Space")
            ax.legend()
            fig_gui.tight_layout()


    def construct_latex_table(self,print_table=False):
        """
        Construct latex table

        Args:
            print_table (bool, optional): print the table. Defaults to False.


        Todo:
            Change this from printout to files instead.
        """

        err_full = larch_score.construct_full_err(self.err)
        print(self.best_Fit_r)
        nleg_arr,label_arr,latex_table_str =larch_score.latex_table(self.paths,self.best_Fit_r,err_full)

        self.nleg_arr = nleg_arr
        self.label_arr = label_arr
        self.latex_table_str = latex_table_str
        if print_table:
            print(self.latex_table_str)

    def individual_fit(self,plot=False,fig_gui=None):
        """
        Perform fitness calculation separately for each paths for r space

        Args:
            plot (bool, optional): plotting. Defaults to False.
            fig_gui (_type_, optional): supplement gui for plotting in other windows. Defaults to None.
        """

        # path,yTotal,best,loss,export_paths=larch_score.fitness_individual(self.exp,self.best_Fit,self.paths,self.params,export=True,plot=True)
        path,yTotal,best,loss,export_paths = larch_score.fitness_individual(self.exp,self.bestFit_mat,self.paths,self.params,export=True,plot=plot,fig_gui=fig_gui)
        self.ind_export_paths = export_paths

    def write_latex_csv(self,file_name=''):
        """
        Write latex table to csv file

        Args:
            file_name (str, optional): filename for csv. Defaults to ''.
        """

        # check if attributes exists first.
        if hasattr('self','latex_table_str'):
            print('Attribute Exists')
        else:
            self.construct_latex_table()
        if file_name !=None:
            with open(file_name,mode='w',newline='',encoding='utf-8') as write_file:
                write_file.write(self.latex_table_str)

    def get_data(self):
        """
        Get the data for plotting

        Returns:
            tuple: (data_x, data_y, model_x, model_y),error_full
        """
        SMALL = self.small
        BIG = self.big
        data_x = self.g.k[SMALL:BIG]
        data_y = self.g.chi[SMALL:BIG]*self.g.k[SMALL:BIG]**self.kweight
        model_x = self.path.k[SMALL:BIG]
        model_y = self.yTotal[SMALL:BIG]*self.path.k[SMALL:BIG]**self.kweight

        error_full = larch_score.construct_full_err(self.err)
        return (data_x,data_y,model_x,model_y),error_full


    def export_files(self,header='test',dirs='',igor_true = False):
        """Export files to their corresponding spots:

        Args:
            header (str, optional): header file. Defaults to 'test'.
            dirs (str, optional): path location for files. Defaults to ''.
            igor_true (bool, optional): if igor plotting. Defaults to False.

        Todo:
            Removed one of the files since it is plotted directly using latex
            function

        """

        file_name_k = os.path.join(dirs,'bestFit_' + header + '.csv')
        file_name_best = os.path.join(dirs,header + '_bestFit_err.csv')
        file_name_ind = os.path.join(dirs,'Individual_Fit_' + header + '.csv')
        file_name_latex = os.path.join(dirs,'Latex_' + header + '.txt')

        SMALL = self.small
        BIG = self.big
        self.header = header
        larch_score.write_bestFit_csv(self.g.k,self.g.chi,self.path.k,self.yTotal,SMALL,BIG,name=file_name_k,header_base=header)
        # larch_score.write_result_n_err(full_mat_var,err,name=file_name_best,header_base=header)
        larch_score.write_individual_csv(self.g.k,self.g.chi,self.path.k,self.yTotal,SMALL,BIG,self.ind_export_paths,self.paths,name=file_name_ind,header_base=header)

        self.write_latex_csv(file_name_latex)
        if igor_true == True:
            self.export_igor_individual()

    def construct_bestfit_err_mat(self,full_mat,bestfit_full_mat,paths,plot=False):
        """
        Construct the average best fit matrix using the sum of the files, and
        generate the corresponding labels using the paths provided.

        (Helper function)

        """
        full_mat_var = np.delete(full_mat, np.s_[5::4],axis=1)
        bestfit_full_mat_var = np.delete(bestfit_full_mat,np.s_[5::4],axis=1)
        full_mat_var_cov = np.cov(full_mat_var.T)
        full_mat_diag = np.diag(full_mat_var_cov)
        err = np.sqrt(full_mat_diag)

        label = larch_score.generate_labels(paths)[0]

        # bestFit = np.mean(bestfit_full_mat_var,axis=0)
        bestFit = np.mean(full_mat_var,axis=0)
        self.label = label
        self.full_mat_diag = full_mat_diag
        if plot:
            plt.figure(figsize=(8,5))
            plt.xticks(np.arange(len(full_mat_diag)),label,rotation=70);
            plt.bar(np.arange(len(full_mat_diag)),np.sqrt(full_mat_diag))

        return bestFit,err

    def plot_error(self,fig_gui=None):
        if fig_gui == None:
            plt.figure(figsize=(8,5))
            # plt.xticks(np.arange(len(self.full_mat_diag)),self.label,rotation=70);
            plt.bar(np.arange(len(self.full_mat_diag)),np.sqrt(self.full_mat_diag))
        else:
            ax = fig_gui.add_subplot(111)
            # ax.xticks
            ax.set_xticks(np.arange(len(self.full_mat_diag)))
            # ax.set_xticklabels(self.label,rotation=70)
            ax.bar(np.arange(len(self.full_mat_diag)),np.sqrt(self.full_mat_diag))
            fig_gui.tight_layout()


    def paths_optimizations(self,number=0.01,verbose=False):
        r"""
        Paths optimizations using simpsons area calculation.
        The calculation are used to perform

        Inputs:
            number (float): cut off percentage for paths_optimizations, the vals
                is typically set at 1%
        """
        total = 0
        total_area = 0
        contrib = []
        contrib_area = []
        # print(self.num_paths)
        for i in range(self.num_paths):
            self.best.k = self.ind_export_paths[2*i,:]
            self.best.chi = self.ind_export_paths[2*i+1,:]

            xftf(self.best.k, self.best.chi, kmin=self.params['Kmin'], kmax=self.params['Kmax'], dk=4,
            window='hanning',kweight=self.params['kweight'], group=self.best, _larch=self.mylarch)

            total += np.linalg.norm(self.best.chir_mag)
            contrib.append(np.linalg.norm(self.best.chir_mag))
            contrib_area.append(simps(self.best.chir_mag,self.best.r))
            total_area += simps(self.best.chir_mag,self.best.r)
        contrib_p = [i / total for i in contrib]
        contrib_ap = [i/total_area for i in contrib_area]
        if verbose:
            print("Paths, Contrib Percentage (2-Norm), Contrib Percentage (Area)")
            for i in range(len(self.paths)):
                print(i+1,contrib_p[i].round(3),contrib_ap[i].round(3))
        #print(total)
        new_path = (np.argwhere(np.array(contrib_ap) >= number)).flatten()+1
        print("New Paths:")
        print(new_path)
        plt.bar(np.arange(self.num_paths),height= contrib_ap)
        plt.xticks(np.arange(self.num_paths),self.flat_paths)

    def export_igor_individual(self,file_paths='export_ind.ipf'):
        """ Export files in igor plotting for individuals, must be ran after
        the individual methods

        Args:
            file_paths (str, optional): location for igor plot script. Defaults to 'export_ind.ipf'.
        """
        # Displace all data
        f = open(file_paths,"w")
        f.write('•Display data_' + self.header + '_chi2 vs data_' + \
            self.header + '_k;')
        f.write('\n')
        f.write('•AppendToGraph fit_' + self.header + '_chi2 vs fit_' +\
            self.header + '_k;' )
        f.write('\n')
        full_paths = larch_score.flatten_2d_list(self.paths)
        for i in range(len(full_paths)):
            f.write('•AppendToGraph path_' + str(full_paths[i]) + '_'+ self.header+ \
                '_chi2 vs path_' + str(full_paths[i]) +'_'+ self.header + '_k;' )
            f.write('\n')

        f.write('•SetAxis bottom *,11');f.write('\n')

        ## Offset
        # offset first two is designated number
        # Todo:
            # Need to redesign this later!

        if len(full_paths) < 3:
            if len(full_paths) == 1:
                f.write('•ModifyGraph offset(path_' + str(full_paths[0])+ '_'+self.header + '_chi2)={0,5}');f.write('\n')
            elif len(full_paths) == 2:
                        f.write('•ModifyGraph offset(path_' + str(full_paths[0])+ '_'+self.header + '_chi2)={0,5}');f.write('\n')
                        f.write('•ModifyGraph offset(path_' + str(full_paths[1]) + '_' + self.header + '_chi2)={0,10}');f.write('\n')
        else:
            f.write('•ModifyGraph offset(path_' + str(full_paths[0])+ '_'+self.header + '_chi2)={0,5}');f.write('\n')
            f.write('•ModifyGraph offset(path_' + str(full_paths[1]) + '_' + self.header + '_chi2)={0,10}');f.write('\n')
            f.write('•ModifyGraph offset(path_' + str(full_paths[2]) + '_' + self.header + '_chi2)={0,12.5}');f.write('\n')

        # offset the rest
        for i in range(len(full_paths)-3):
            curr_paths = str(full_paths[i+3])
            f.write('•ModifyGraph offset(path_' + curr_paths + '_' +self.header + '_chi2)={0,' + str(15 + i) + '}' )
            f.write('\n')
        f.write(r'•Label left "k\\S2\\M \u03c7(k) (Å\\S-2\\M)";DelayUpdate');f.write('\n')
        f.write(r'•Label bottom "k (Å\\S-1\\M)"');f.write('\n')
        f.write('•ModifyGraph lsize(fit_' + self.header  + '_chi2)=2');f.write('\n')
        for i in range(len(full_paths)):
            f.write('•ModifyGraph lsize(path_' + str(full_paths[i]) + '_' + self.header + '_chi2)=2')
            f.write('\n')
        ## Legend
        # \r  - new line
        self.adjust_color(f)
        self.create_legend(f)
        f.write('•ModifyGraph mode(data_' + self.header  + '_chi2)=3');f.write('\n')

    def create_legend(self,f):
        """
        Create legend for igor
        """
        legend_header = r'•Legend/C/N=text0/J "Test\rk\\S2\\M\u03c7(k)\rTest_Detail\r\r\\s('
        legend_1 = 'data_' + self.header + r"_chi2) Data\r\\s(fit_" + self.header + r'_chi2) Fit";'
        legend = legend_header + legend_1
        f.write(legend); f.write('\n')
        full_paths = larch_score.flatten_2d_list(self.paths)
        for i in range(len(full_paths)):
            if int(self.nleg_arr[i]) > 2:
                addition = ' MS '
            else:
                addition = ' '
            paths_arr = str(full_paths[i]) + '_' + self.header + '_chi2) Path ' + str(full_paths[i]) + addition + self.label_arr[i] + r'";DelayUpdate'
            f.write('•AppendText/N=text0 "\\s(path_'+ paths_arr)
            f.write('\n')
    # Adjust the color using jet reverse color bar
    def adjust_color(self,f,color_map=plt.cm.jet_r):
        r"""
        adjust color for legend

        Input:
            f (str): files output name and locations
            color_map (cmp): matplotlib.cm.cmap objects, default to
                plt.cm.jet_r
        """
        full_paths = larch_score.flatten_2d_list(self.paths)
        x = np.linspace(0,1,len(full_paths))
        color = [color_map(i) for i in x]
        test = 65535
        for i in range(len(color)):
            color[i] = (int(test*color[i][0]),int(test*color[i][1]),int(test*color[i][2]))
        # Change to X and Y for data
        f.write('•ModifyGraph rgb(fit_' + self.header + '_chi2)=(0,0,0)');f.write('\n')
        for i in range(len(color)):
            f.write('•ModifyGraph rgb(path_' + str(full_paths[i]) + '_' + self.header + '_chi2)=' + str(color[i]))
            f.write('\n')

    @staticmethod
    def jet_r(x):

        return plt.cm.jet_r(x)


    def stacks_plot(self):
        """Generate stack plot
        """
        # print(self.num_paths)
        # get the array size first:
        self.best.k = self.ind_export_paths[0,:]
        self.best.chi = self.ind_export_paths[1,:]
        xftf(self.best.k, self.best.chi, kmin=self.params['Kmin'], kmax=self.params['Kmax'], dk=4,
        window='hanning',kweight=self.params['kweight'], group=self.best, _larch=self.mylarch)
        y_arr = np.zeros((self.num_paths,len(self.best.r)))
        y_tot = np.zeros(len(self.best.r))
        # grab all the data
        for i in range(self.num_paths):
            self.best.k = self.ind_export_paths[2*i,:]
            self.best.chi = self.ind_export_paths[2*i+1,:]

            xftf(self.best.k, self.best.chi, kmin=self.params['Kmin'], kmax=self.params['Kmax'], dk=4,
            window='hanning',kweight=self.params['kweight'], group=self.best, _larch=self.mylarch)
            y_arr[i,:] = -self.best.chir_mag
            y_tot += self.best.chir_mag
            # print(len(self.best.chir_mag))
        x = self.best.r


        plt.rc('font',size=11)
        rc = {"font.family" : "serif",
            "mathtext.fontset" : "stix"}
        plt.rcParams.update(rc)
        plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]

        figsize = (10,7)
        linewidth = 1.0
        edgecolor = 'black'
        capsize = 5
        spacing = 0.2
        color = 'royalblue'
        label_fontsize=14

        fig,ax = plt.subplots(ncols=1,nrows=1,figsize=figsize)
        ax.set_xlabel('R, uncorrected ($\AA$)')
        ax.set_ylabel('|$\chi$(R)| ($\AA^{3}$)')

        ax.plot(x,y_tot,'k',linestyle='solid',linewidth=linewidth,label='Fits')
        ax.stackplot(x,y_arr,labels=np.arange(1,self.num_paths+1))

        # ax.set_xlim([1,9])
        ax.yaxis.grid(True,linestyle='--',which='major',color='grey',alpha=0.25)
        ax.xaxis.grid(True,linestyle='--',which='major',color='grey',alpha=0.25)
        ax.tick_params(which='both',direction='in')

        ax.legend(loc='lower right',fontsize=label_fontsize)#,labelcolor='black')
        plt.tight_layout()

