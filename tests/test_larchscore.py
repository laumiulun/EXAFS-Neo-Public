"""
Unit test for larch score
"""
import sys,os
import unittest
sys.path.append('gui')
import larch_score

# python -m unittest discover -s tests -v

class TestCase(unittest.TestCase):
    def test_generate_label_1(self):
        """
        Test Labels with one label
        """
        data = [1]
        result_label= ['s02_1','e0','sigma_1','deltaR_1']
        result_s02_label = []
        result = larch_score.generate_labels(data)
        self.assertEqual(result[0],result_label)
        self.assertEqual(result[1],['s02_1'])
        self.assertEqual(result[2],['sigma_1'])
        self.assertEqual(result[3],['deltaR_1'])

    def test_generate_label_2(self):
        """
        Test labels with multiple paths
        """
        data = [1,2]
        result_label= ['s02_1','e0','sigma_1','deltaR_1','s02_2','sigma_2','deltaR_2']
        result_s02_label = []
        result = larch_score.generate_labels(data)
        self.assertEqual(result[0],result_label)
        self.assertEqual(result[1],['s02_1','s02_2'])
        self.assertEqual(result[2],['sigma_1','sigma_2'])
        self.assertEqual(result[3],['deltaR_1','deltaR_2'])


    def test_larch_init(self):
        """
        test larch init
        """
        
        return 0

    # def test_larch_init(self):
    #     """
    #     Test larch init
    #     """
    #
