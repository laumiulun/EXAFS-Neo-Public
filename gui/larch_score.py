"""
Authors    Miu Lun(Andy) Lau*, Jeffrey Terry, Min Long
Email      andylau@u.boisestate.edu, jterry@agni.phys.iit.edu, minlong@boisestate.edu
Version    0.2.0
Date       Sep 1, 2021

This modules is used for modeling the score for each dataset
"""

# Import Library


from pathlib import Path
import csv
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import datetime
from larch.xafs import autobk,xftf,feffdat
from larch.io import read_ascii
from operator import itemgetter
import numpy as np
import operator
from larch import Interpreter
from larch.xafs import xftf
import random
import larch
import os
os.environ['NUMEXPR_MAX_THREADS'] = '16'
# from larch_plugins.xafs import feffdat
# from larch_plugins.xafs import xftf
# from larch_plugins.io import read_ascii
# from larch_plugins.xafs import autobk
# mpl.use('Agg')

global mylarch
global base


mylarch = Interpreter()
base = Path(os.getcwd()).parent.parent


# Larch has two types of files, from Larch which is the chik, and the experimential files
def larch_init(CSV_sub, params):
    """Initalize Larch

    Args:
        CSV_sub (str): path to the csv/xmu files
        params (dicts): dictionary containing the parameters

    Returns:
        _type_: _description_
    """

    global intervalK
    global best
    global KMIN
    global KMAX
    global KWEIGHT
    global g

    Kmin = params['Kmin']
    Kmax = params['Kmax']
    deltak = params['deltak']

    BIG = int(Kmax/deltak)
    SMALL = int(Kmin/deltak)
    MID = int(BIG-SMALL+1)
    RBKG = params['rbkg']
    KWEIGHT = params['kweight']

    KMIN = Kmin
    KMAX = Kmax

    BKGKW = params['bkgkw']  # cu = 1 hfal2 = 2.0
    BKGKMAX = params['bkgkmax']  # cu = 25, hfal2 = 15
    base = params['base']
    CSV_PATH = os.path.join(base, CSV_sub)
    g = read_ascii(CSV_PATH)
    best = read_ascii(CSV_PATH)
    sumgroup = read_ascii(CSV_PATH)

    # back ground subtraction using autobk
    # data kweight
    try:
        g.chi
    except AttributeError:
        autobk(g, rbkg=RBKG, kweight=BKGKW, kmax=BKGKMAX, _larch=mylarch)
        autobk(best, rbkg=RBKG, _larch=mylarch)
        autobk(sumgroup, rbkg=RBKG, _larch=mylarch)

    intervalK = (np.linspace(SMALL, BIG, MID)).tolist()

    '''chang'''
    xftf(g.k, g.chi, kmin=KMIN, kmax=KMAX, dk=4, window='hanning',
         kweight=KWEIGHT, group=g, _larch=mylarch)
    xftf(best.k, best.chi, kmin=KMIN, kmax=KMAX, dk=4, window='hanning',
         kweight=KWEIGHT, group=best, _larch=mylarch)
    xftf(sumgroup.k, sumgroup.chi, kmin=KMIN, kmax=KMAX, dk=4, window='hanning',
         kweight=KWEIGHT, group=sumgroup, _larch=mylarch)
    '''chang end'''

    exp = g.chi
    params['SMALL'] = SMALL
    params['BIG'] = BIG
    params['intervalK'] = intervalK
    return exp, g, params, mylarch


def flatten_2d_list(array: list):
    """Flatten 2d list based on

    (unit test: done)

    Args:
        array (list): list of paths

    Returns:
        list: flatten list of array based on compound or not
    """
    arr = []
    iscompound = False
    # check if list is multidimensional
    for i in range(len(array)):
        if isinstance(array[i], list) == True:
            iscompound = True
    if iscompound == True:
        for i in range(len(array)):
            for j in range(len(array[i])):
                arr.append(array[i][j])
    else:
        arr = array
    return arr


def fittness_score(CSV_loc, data, paths, plot=False):
    """Fitness score

    Args:
        CSV_loc (str): CSV file
        data (_type_): _description_
        paths (list): list of scattering paths number
        plot (bool, optional): plotting options. Defaults to False.

    Returns:
        _type_: _description_
    """
    exp = larch_init(CSV_loc)
    loss = fitness_individual(exp, data, paths, plot=False)
    return loss


# Action to calculate fitness
def fitness_individual(exp, arr, full_paths, params, plot=False, export=False, fig_gui=None):
    """
    Fittness for individual scattering paths

    Args:
        exp(larch_object): experience data for larch object
        arr(arr): array for best fit
        full_paths(list): path list
        params(dicts): dictionary for params calculations
        plot(bool, optional): plot for individual paths. Defaults to False.
        export(bool, optional): if return array for each paths. Defaults to False.
        fig_gui(_type_, optional): plot in fig instead. Defaults to None.

    Returns:
        _type_: _description_
    """

    global intervalK
    global best
    loss = 0
    yTotal = [0]*(401)
    offset = 5
    global best

    num_comp = len(params['front'])
    base = Path(os.getcwd()).parent.parent

    compounds_list = params['front']
    if num_comp > 1:
        front = [os.path.join(base, i) for i in compounds_list]
    else:
        front = os.path.join(base, params['front'][0])

    end = '.dat'
    Kmax = params['Kmax']
    SMALL = params['SMALL']
    BIG = params['BIG']
    export_paths = np.zeros((2*len(flatten_2d_list(full_paths)), 401))
    if plot:
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(7, 6))
    if fig_gui != None:
        ax = fig_gui.add_subplot(111)

    iterator = 0

    for i in range(num_comp):
        if num_comp > 1:
            paths = full_paths[i]
        else:
            paths = full_paths

        print(paths)

        print(paths)
        for j in range(len(paths)):
            if num_comp > 1:
                filename = front[i] + str(paths[j]).zfill(4) + end
            else:
                filename = front + str(paths[j]).zfill(4) + end
            path = feffdat.feffpath(filename, s02=str(arr[j, 0]), e0=str(
                arr[j, 1]), sigma2=str(arr[j, 2]), deltar=str(arr[j, 3]), _larch=mylarch)
            feffdat.path2chi(path, _larch=mylarch)

            if plot:
                ax.plot(path.k, path.chi*path.k**2.0 +
                        offset*(iterator+1), label='Path:')
                ax.set_xlabel("k ($\AA^{-1}$)")
                ax.set_ylabel("k$^{2}$ ($\chi(k)\AA^{-1}$)")
                ax.set_ylim(-10, len(paths)*offset+offset)
                ax.set_xlim(0, Kmax+1)

            if fig_gui != None:
                ax.plot(path.k, path.chi*path.k**2.0 +
                        offset*(iterator+1), label='Path')
                ax.set_xlabel("k ($\AA^{-1}$)")
                ax.set_ylabel("k$^{2}$ ($\chi(k)\AA^{-1}$)")
                ax.set_ylim(-10, len(paths)*offset+offset)
                ax.set_xlim(0, Kmax+1)

            if export:
                export_paths[2*iterator, :] = path.k
                export_paths[2*iterator+1, :] = (path.chi*path.k**2.0)

            y = path.chi

            for k in intervalK:
                yTotal[int(k)] += y[int(k)]

            iterator = iterator + 1
    best.chi = yTotal
    best.k = path.k
    xftf(best.k, best.chi, kmin=KMIN, kmax=KMAX, dk=4, window='hanning',
         kweight=KWEIGHT, group=best)

    offset = 0
    if plot == True or fig_gui != None:
        ax.plot(g.k, g.chi*g.k**2+offset, 'r--', label='Data')
        ax.plot(path.k[SMALL:BIG], yTotal[SMALL:BIG] *
                path.k[SMALL:BIG]**2+offset, 'b--', label="GA")
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

    for j in intervalK:
        # loss = loss + (yTotal[int(j)]*g.k[int(j)]**2 - exp[int(j)]*g.k[int(j)]**2)**2
        loss = loss + (yTotal[int(j)]*g.k[int(j)]**2 -
                       exp[int(j)]*g.k[int(j)]**2)**2

    return path, yTotal, best, loss, export_paths


def cal_row_generations(i, k, npaths, pop_size):
    """Calculate row generations

    Args:
        i (_type_): _description_
        k (_type_): _description_
        npaths (_type_): _description_
        pop_size (_type_): _description_

    Returns:
        _type_: _description_
    """
    start = i*npaths + k*pop_size*npaths
    end = start + npaths
    return start, end


def fitness(exp, arr, full_paths, params, return_r=True,verbose=False) -> tuple:
    """Fitness of a full scattering paths

    Args:
        exp (larch_object): experience data for larch object
        arr (array): array for best fit
        full_paths (list): full scattering paths
        params (dicts): dictionary for params calculations
        return_r (bool, optional): if return r space. Defaults to True.
        verbose (bool,optional): Verbose the result. Defaults to False.

    Returns:
        _type_: _description_
    """

    base = params['base']
    compounds_list = params['front']
    num_comp = len(params['front'])

    if num_comp > 1:
        front = [os.path.join(base, i) for i in compounds_list]
    else:
        front = os.path.join(base, params['front'][0])
    end = '.dat'

    loss = 0
    yTotal = [0]*(401)
    offset = 2
    global best

    Kmin = params['Kmin']
    Kmax = params['Kmax']
    SMALL = params['SMALL']
    BIG = params['BIG']
    Kweight = params['kweight']
    arr_r = []
    array_str = "---------------------\n"
    if verbose:
        print(f"Number of Components: {num_comp}")
    for i in range(num_comp):
        if num_comp > 1:
            paths = full_paths[i]
        else:
            paths = full_paths
        for j in range(len(paths)):
            if num_comp > 1:
                filename = front[i] + str(paths[j]).zfill(4) + end
            else:
                filename = front + str(paths[j]).zfill(4) + end
            # print(j*num_comp+1)
            # print(i,j)
            # print(i*num_paths + j)
            k = 20*i + j
            # print(k)
            # print(filename)
            path = feffdat.feffpath(filename, s02=str(arr[k, 0]), e0=str(
                arr[k, 1]), sigma2=str(arr[k, 2]), deltar=str(arr[k, 3]), _larch=mylarch)
            feffdat.path2chi(path, larch=mylarch)
            if verbose:
                print("Path", paths[j], path.s02, path.e0,
                    path.sigma2, path.reff+arr[j, 3])
            temp = [float(path.s02), float(path.e0), float(path.sigma2), float(
                path.reff+arr[j, 3]), float(path.degen), float(path.nleg), (path.geom)]
            arr_r.append(temp)
            y = path.chi
            for k in intervalK:
                yTotal[int(k)] += y[int(k)]

    best.chi = yTotal
    best.k = path.k
    xftf(best.k, best.chi, kmin=Kmin, kmax=Kmax, dk=4, window='hanning',
         kweight=Kweight, group=best, _larch=mylarch)

    for j in intervalK:
        loss = loss + (yTotal[int(j)]*g.k[int(j)]**2 -
                       exp[int(j)]*g.k[int(j)]**2)**2

    if return_r == True:
        return path, yTotal, best, loss, arr_r, array_str
    else:
        return path, yTotal, best, loss


def construct_bestfit_mat(gk, gchi, pathk, yTotal, SMALL, BIG):
    """Construct best fit matrix

    Args:
        gk (_type_): _description_
        gchi (_type_): _description_
        pathk (_type_): _description_
        yTotal (_type_): _description_
        SMALL (_type_): _description_
        BIG (_type_): _description_

    Returns:
        _type_: _description_
    """
    exp_data = np.vstack((gk, gchi*gk**2)).T
    fit_data = np.vstack(
        (pathk[SMALL:BIG], yTotal[SMALL:BIG]*pathk[SMALL:BIG]**2)).T

    return exp_data, fit_data


# Writes bestfit
def write_dat_csv(writer, data):
    """Write data csv

    Args:
        writer (file writer): file writer
        data (array): data array
    """
    for i in range(len(data)):
        writer.writerow((data[i, :]))


def write_bestFit_csv(gk, gchi, pathk, yTotal, SMALL, BIG, name='bestFit.csv', header_base='Sample'):
    """ Write out bestFit csv for plotting in Igor Format

    Args:
        gk(_type_): gk
        gchi(_type_): _description_
        pathk(_type_): _description_
        yTotal(_type_): _description_
        SMALL(_type_): _description_
        BIG(_type_): _description_
        name(str, optional): _description_. Defaults to 'bestFit.csv'.
        header_base(str, optional): _description_. Defaults to 'Sample'.
    """

    with open(name, mode='w', newline='', encoding='utf-8') as write_file:

        exp_data, fit_data = construct_bestfit_mat(
            gk, gchi, pathk, yTotal, SMALL, BIG)
        writer = csv.writer(write_file, delimiter=',')
        writer.writerow(['data_' + header_base + '.k',
                        'data_' + header_base+'.chi2'])
        write_dat_csv(writer, exp_data)
        writer.writerow('')
        writer.writerow(['fit_' + header_base + '.k',
                        'fit_' + header_base+'.chi2'])
        write_dat_csv(writer, fit_data)


def write_individual_csv(gk, gchi, pathk, yTotal, SMALL, BIG, export_path, paths, name='Individual.csv', header_base='Sample'):
    """_summary_

    Args:
        gk (_type_): _description_
        gchi (_type_): _description_
        pathk (_type_): _description_
        yTotal (_type_): _description_
        SMALL (_type_): _description_
        BIG (_type_): _description_
        export_path (_type_): _description_
        paths (_type_): _description_
        name (str, optional): _description_. Defaults to 'Individual.csv'.
        header_base (str, optional): _description_. Defaults to 'Sample'.
    """
    with open(name, mode='w', newline='', encoding='utf-8') as write_file:

        exp_data, fit_data = construct_bestfit_mat(
            gk, gchi, pathk, yTotal, SMALL, BIG)
        writer = csv.writer(write_file, delimiter=',')
        writer.writerow(['data_' + header_base + '.k',
                        'data_' + header_base+'.chi2'])
        write_dat_csv(writer, exp_data)
        writer.writerow('')
        writer.writerow(['fit_' + header_base + '.k',
                        'fit_' + header_base+'.chi2'])
        write_dat_csv(writer, fit_data)

        # print(paths)
        full_paths = flatten_2d_list(paths)
        for i in range(int(export_path.shape[0]/2)):
            path_header = ['path_' + str(full_paths[i]) + '_' + header_base +
                           '.k', 'path_'+str(full_paths[i])+'_' + header_base+'.chi2']
            writer.writerow(path_header)
            write_dat_csv(writer, export_path[(2*i, 2*i+1), :].T)
            writer.writerow('')


def write_result_n_err(full_mat_var, err, name='bestfit_err.csv', header_base='Sample'):
    """Write Result and Error

    Args:
        full_mat_var (_type_): _description_
        err (_type_): _description_
        name (str, optional): _description_. Defaults to 'bestfit_err.csv'.
        header_base (str, optional): _description_. Defaults to 'Sample'.
    """

    average = full_mat_var

    assert len(average) == len(err)
    out_mat = np.vstack((average, err)).T

    with open(name, mode='w', newline='', encoding='utf-8') as write_file:
        writer = csv.writer(write_file, delimiter=',')
        writer.writerow(['BestFit_' + header_base, 'Err_' + header_base])
        write_dat_csv(writer, out_mat)


def generate_labels(path_list):
    """_summary_

    Args:
        path_list(_type_): _description_

    Returns:
        _type_: _description_
    """
    label = []
    s02_label = []
    sigma2_label = []
    deltaR_label = []
    # path_list = np.arange(20)
    for i in range(len(path_list)):
        label.append('s02_' + str(path_list[i]))
        if i == 0:
            label.append('e0')

        s02_label.append('s02_' + str(path_list[i]))
    #     label.append('e0_' + str(path_list[i]))
        label.append('sigma_' + str(path_list[i]))
        sigma2_label.append('sigma_' + str(path_list[i]))

        label.append('deltaR_' + str(path_list[i]))
        deltaR_label.append('deltaR_' + str(path_list[i]))

    return label, s02_label, sigma2_label, deltaR_label


# construct full error matrix
def construct_full_err(err):
    """Construct full err matrix

    Args:
        err (_type_): _description_

    Returns:
        _type_: _description_
    """
    e0 = err[1]
    # print(e0)

    err_temp = np.delete(err, 1)
    err_temp = err_temp.reshape((-1, 3))
    # print(err_temp)
    e0_arr = np.ones((err_temp.shape[0]))*e0
    err_temp = np.insert(err_temp, 1, e0_arr, axis=1)
    # print(err_temp)
    return err_temp


# Convert to certain precisions
def convert_to_str(val, prec) -> str:
    """convert to string of certain percision

    Args:
        val (float): float value
        prec (int): number of precision

    Returns:
        str: precision string
    """
    prec_val = '{:.' + str(prec) + 'f}'
    return prec_val.format(round(val, prec))


def convert_label(select_bestfit_r):
    """_summary_

    Args:
        select_bestfit_r (_type_): _description_

    Returns:
        _type_: _description_
    """
    temp_label = ''
    for j in range(len(select_bestfit_r)):
        temp_label += select_bestfit_r[j][0]
        temp_label += '-'
    temp_label = temp_label[:-1]
    return temp_label


def cal_err_prec(val_arr):
    """_summary_

    Args:
        val_arr (_type_): _description_

    Returns:
        _type_: _description_
    """
    prec_arr = []
    for i in range(len(val_arr)):
        dist = abs(int(np.log10(abs(val_arr[i])))-1)
        prec_arr.append(dist)
    return prec_arr


def temp_round_deltaR(val):
    """_summary_

    Args:
        val (_type_): _description_

    Returns:
        _type_: _description_
    """
    if val < 1e-6:
        val = 0.001
    else:
        val = np.round(val, 3)
    return val



def latex_table(paths, best_Fit_r, err_full):
    """convert to latex table output

    Args:
        paths (_type_): list of paths (unflatten)
        best_Fit_r (_type_): reduced best fit result with scattering params
        err_full (_type_): full error matrix

    """
    nleg_arr = []
    label_arr = []
    full_paths = flatten_2d_list(paths)

    for i in range(len(full_paths)):
        # print(i)
        label_arr.append(convert_label(best_Fit_r[i][6]))
        nleg_arr.append(str(int(best_Fit_r[i][5])))
    latex_table_str = ""
    latex_table_str += (R"""\floatsetup[table]{capposition = top}
        \begin{table}[]
            \centering
                \footnotesize
                    \caption{test}
                        \begin{tabular}{cccccccc}
                            \hline
                        \vspace{0.05 in }
                            Path \# & $N$ & $S_0^2$ & $\Delta$E$_0$ (eV) & $\sigma^{2}$ (\AA$^2$) & R (\AA)& Legs & Labels\\
                            \hline""")

    for i in range(len(full_paths)):
        prec_arr = cal_err_prec(err_full[i, :4])
        latex_table_str += ("                        " + str(full_paths[i]) + " & " +
                            str(int(best_Fit_r[i][4])) + " & " +
                            convert_to_str(best_Fit_r[i][0], prec_arr[0]) + r"$\pm$" + convert_to_str(err_full[i, 0], prec_arr[0]) + " & " +
                            convert_to_str(best_Fit_r[i][1], prec_arr[1]) + r"$\pm$" + convert_to_str(err_full[i, 1], prec_arr[1]) + " & " +
                            str(np.round(best_Fit_r[i][2], 4)) + r"$\pm$" + str(np.round(err_full[i, 2], 4)) + " & " +
                            str(np.round(best_Fit_r[i][3], 3)) + r"$\pm$" + str(temp_round_deltaR(err_full[i, 3])) + " &  " +
                            str(int(best_Fit_r[i][5])) + " & " + label_arr[i] + r"\\")

    latex_table_str += (r"""                        \hline
                        \end{tabular}
                        \label{Label}


\end{table}""")
    # return

    return nleg_arr, label_arr, latex_table_str
