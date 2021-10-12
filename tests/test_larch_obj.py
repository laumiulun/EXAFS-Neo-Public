"""
Unit test for initalizations
"""
import sys,os
import unittest
sys.path.append('gui')
from larch_obj import Larch_Obj

# python -m unittest discover -s tests -v

class TestCase(unittest.TestCase):
    def test_initalization(self):
        """
        Test initalizations
        """
        params = {}
        params['base'] = 'test'
        params['Kmin'] = 2.5
        params['Kmax'] = 12.5
        params['kweight'] = 2
        params['deltak'] = 0.05
        params['rbkg'] = 1.0
        params['bkgkw'] = 2.0
        params['bkgkmax'] = 15
        params['front'] = ['test/feff']
        params['CSV'] = "test.xmu"
        params['optimize'] = 'False'
        params['series_index'] = 0
        params['series'] = False
        test_obj  = Larch_Obj(params)

        self.assertEqual(test_obj.big,250)
        self.assertEqual(test_obj.small,50)
        self.assertEqual(test_obj.mid,201)
