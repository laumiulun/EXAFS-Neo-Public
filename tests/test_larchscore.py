"""
Unit test for larch score
"""
import sys
import larch
from larch.xafs import autobk,xftf

import os
import unittest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.append('gui/')
import larch_score


class Test_Larchscore(unittest.TestCase):

    # Create a different global interpetor for larch

    mylarch = larch.Interpreter()
    params = {}
    params['base'] = Path(os.getcwd())
    params['Kmin'] = 2.5
    params['Kmax'] = 12.5
    params['kweight'] = 2.0
    params['deltak'] = 0.05
    params['rbkg'] = 1.0
    params['bkgkw'] = 2.0
    params['bkgkmax'] = 15.0
    params['front'] = ["tests/cu_test_files/cu_paths/path_75/feff"]
    params['CSV'] = "tests/cu_test_files/cu_paths/cu_10k.xmu"
    params['optimize'] = 'False'
    params['series_index'] = 0
    params['series'] = False
    dirs = 'tests/cu_test_files/cu_results_2/'


    print(params['base'])

    def test_generate_label_single(self):
        """
        Test Labels with one label
        """
        data = [1]
        result_label = ['s02_1', 'e0', 'sigma_1', 'deltaR_1']
        result_s02_label = []
        result = larch_score.generate_labels(data)
        self.assertEqual(result[0], result_label)
        self.assertEqual(result[1], ['s02_1'])
        self.assertEqual(result[2], ['sigma_1'])
        self.assertEqual(result[3], ['deltaR_1'])

    def test_generate_label_compound(self):
        """
        Test labels with multiple paths
        """
        data = [1, 2]
        result_label = ['s02_1', 'e0', 'sigma_1',
                        'deltaR_1', 's02_2', 'sigma_2', 'deltaR_2']
        result_s02_label = []
        result = larch_score.generate_labels(data)
        self.assertEqual(result[0], result_label)
        self.assertEqual(result[1], ['s02_1', 's02_2'])
        self.assertEqual(result[2], ['sigma_1', 'sigma_2'])
        self.assertEqual(result[3], ['deltaR_1', 'deltaR_2'])


    def test_flatten_2d_list_single(self):
        x = [1,2,3,4,5]
        result = larch_score.flatten_2d_list(x)
        self.assertEqual(result, [1,2,3,4,5])

    def test_flatten_2d_list_compound(self):
        x = [[1,2,3],[1,2,3]]
        result = larch_score.flatten_2d_list(x)
        self.assertEqual(result, [1,2,3,1,2,3])

    def test_larch_init_params(self):
        """
        Check larch spacing and the resulting output
        """

        result = larch_score.larch_init(self.params['CSV'],Test_Larchscore.params)

        params = result[2]

        self.assertEqual(params['SMALL'], int(self.params['Kmin']/self.params['deltak']))
        self.assertEqual(params['BIG'], int(self.params['Kmax']/self.params['deltak']))

    def test_larch_init_exp(self):
        """
        Check Larch Xftf
        """
        # get the exp, which should be g.chi
        result = larch_score.larch_init(self.params['CSV'],Test_Larchscore.params)
        exp = result[0]

        # compared againast manually test
        file_path = os.path.join(Test_Larchscore.params['base'], Test_Larchscore.params['CSV'])
        g = larch.io.read_ascii(file_path)

        autobk(g,rbkg=Test_Larchscore.params['rbkg'],
               kweight=Test_Larchscore.params['bkgkw'],
               kmax=Test_Larchscore.params['bkgkmax'])
        xftf(g.k,g.chi,kmin=Test_Larchscore.params['Kmin'],
             kmax=Test_Larchscore.params['Kmax'],
             dk=4,window='hanning',
             kweight=Test_Larchscore.params['kweight'],
             group=g)

        # self.assertTrue(np.allclose(exp, g.chi))
        self.assertTrue((exp == g.chi).all())
    # def test_latex_table(self):
    #     """Test Latex table
    #     """

    #     # larch_score.latex_table()
    #     return 0
    # def test_fitness(self):

