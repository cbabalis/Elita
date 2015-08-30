#!/usr/bin/env python

""" Unit test for ReadInput.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/userinterface')
from ReadInput import ReadInput
import unittest

class BadInput(unittest.TestCase):
    
    def setUp(self):
        self.ri = ReadInput()
    
    def testBadPath(self):
        """ tests the case the user inputs a wrong path """
        self.wrong_path = 'some fantastic, not true path'
        self.path = self.ri.askPath(self.wrong_path)
        self.assertNotEqual(self.wrong_path, self.path)

    def testGoodPath(self):
        """ tests the case the user inputs a correct path """
        self.correct_path = '/home/blaxeep/Workspace/diploma/trunk/test.txt'
        self.path = self.ri.askPath(self.correct_path)
        self.assertEqual(self.correct_path, self.path)
    
    def testExtractData(self):
        """ extractData should return exactly the data in raw form """
        self.path = '/home/blaxeep/Workspace/diploma/trunk/test.txt'
        self.data = {'n1':['2', '3', '4'], 'n2':['1','1','1']}
        self.test = self.ri.extractData(self.path)
        self.assertEqual(self.data, self.test)

if __name__ == '__main__':
    unittest.main()
