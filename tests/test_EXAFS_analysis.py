"""
Unit test for larch score
"""
import sys
import larch
import os
import unittest
import numpy as np
from pathlib import Path
sys.path.append('gui')
import EXAFS_Analysis


class TestCase(unittest.TestCase):

    mylarch = larch.Interpreter()
    params = {}
    params['base'] = Path(os.getcwd())
    params['Kmin'] = 3.0
    params['Kmax'] = 17.0
    params['kweight'] = 2.0
    params['deltak'] = 0.05
    params['rbkg'] = 1.2
    params['bkgkw'] = 1.0
    params['bkgkmax'] = 25.0
    params['front'] = ["tests/cu_test_files/cu_paths/path_75/feff"]
    params['CSV'] = "tests/cu_test_files/cu_paths/cu_10k.xmu"
    params['optimize'] = 'False'
    params['series_index'] = 0
    params['series'] = False
    dirs = 'tests/cu_test_files/cu_results/'

    print(params['base'])

    paths = [1,2,3,5,6,10,14,16,28,30,36,40,42]
    Test_Result = EXAFS_Analysis.EXAFS_Analysis(paths,dirs,params)

    # def test_construct_full_err(self):


    #     return 0
    # def test_larch_init(self):
    #     """
    #     test larch init
    #     """

    #     return 0

    def test_larch_extract_data_shape(self):
        """
        Test larch extract to have the correct matrix shape
        """
        TestCase.Test_Result.extract_data(verbose=False)
        result_shape = TestCase.Test_Result.bestFit_mat.shape
        self.assertEqual(result_shape[0], 13)
        self.assertEqual(result_shape[1], 4)

    def test_larch_extract_data_info(self):
        """
        Test larch extract to have the right data
        """
        TestCase.Test_Result.extract_data(verbose=False)
        test_result = TestCase.Test_Result.bestFit_mat
        real_result = np.array(
            [[ 0.721429,  0.414286,  0.003   , -0.018571],
            [ 0.641429,  0.414286,  0.009429, -0.03    ],
            [ 0.455714,  0.414286,  0.007   , -0.01    ],
            [ 0.797143,  0.414286,  0.007143,  0.005714],
            [ 0.527143,  0.414286,  0.008286,  0.017143],
            [ 0.678571,  0.414286,  0.009143,  0.044286],
            [ 0.425714,  0.414286,  0.008571, -0.05    ],
            [ 0.562857,  0.414286,  0.008857,  0.025714],
            [ 0.632857,  0.414286,  0.01    , -0.02    ],
            [ 0.351429,  0.414286,  0.009143, -0.041429],
            [ 0.332857,  0.414286,  0.008429,  0.011429],
            [ 0.535714,  0.414286,  0.007571, -0.004286],
            [ 0.67    ,  0.414286,  0.007286, -0.044286]]
        )
        self.assertTrue(np.allclose(test_result, real_result))
        # self.assertTrue((test_result == real_result).all())

    def test_chi(self):
        """
        Test larch score data
        """
        TestCase.Test_Result.extract_data(verbose=False)
        TestCase.Test_Result.larch_init()
        TestCase.Test_Result.larch_score(verbose=False)

        Chi2 = TestCase.Test_Result.loss
        Chir2 = TestCase.Test_Result.chir2

        self.assertAlmostEqual(Chi2,184.01516426369412)
        self.assertAlmostEqual(Chir2,0.763548)


    def test_bestFit_r(self):
        """Test best fit R data value
        """
        TestCase.Test_Result.extract_data(verbose=False)
        TestCase.Test_Result.larch_init()
        TestCase.Test_Result.larch_score(verbose=False)

        best_Fit_r = TestCase.Test_Result.best_Fit_r

        self.assertEqual(len(best_Fit_r), 13)
        best_Fit_r_1 = best_Fit_r[0]
        # S02
        self.assertEqual(best_Fit_r_1[0],0.721429)
        self.assertEqual(best_Fit_r_1[1],0.414286)
        self.assertEqual(best_Fit_r_1[2],0.003)
        self.assertEqual(best_Fit_r_1[3],2.534129)
        self.assertEqual(best_Fit_r_1[4],12.0)
        self.assertEqual(best_Fit_r_1[5],2.0)
        self.assertIsInstance(best_Fit_r_1[6], list)

    # def test_larch_init(self):
    #     """
    #     Test larch init
    #     """
    #
