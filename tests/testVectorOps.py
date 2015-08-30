#!/usr/bin/env python

""" Unit test for vectoroperations.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from vec_ops import VectorOps
import unittest

class TestOperations(unittest.TestCase):
    
    def setUp(self):
        """ initial set up for testing """
        # initialize two lists of equal length
        self.target = [1, 1, 1, 1, 1]
        self.operand = [1, 1, 1, 1, 1]

    def testAddTo(self):
        """ tests the addTo(self, a, b) method and prints the result.
        Final results should be [2,2,2,2,2].
        """
        self.true_result = [2, 2, 2, 2, 2]
        self.test_result = VectorOps.addTo(self.target, self.operand)
        self.assertEqual(self.true_result, self.test_result)

    def testSubFrom(self):
        """ tests the subFrom(self, a, b) method """
        self.true_result = [0, 0, 0, 0, 0]
        self.test_result = VectorOps.subFrom(self.target, self.operand)
        self.assertEqual(self.true_result, self.test_result)

    def testMultBy(self):
        """ tests the multBy(self, a b) method """
        self.true_result = [1, 1, 1, 1, 1]
        self.test_result = VectorOps.multBy(self.target, self.operand)
        self.assertEquals(self.true_result, self.test_result)

    def testCpy(self):
        """ tests if new vector has some value inside it. """
        self.cpy_vector = []
        self.cpy_vector = VectorOps.cpy(self.cpy_vector, self.target)
        self.assertTrue(self.cpy_vector)

    def testDeepCpy(self):
        """ tests if new vector is really different """
        self.cpy_vector = []
        self.cpy_vector = VectorOps.cpy(self.cpy_vector, self.target)
        # change the target vector a little
        self.target = [1, 2, 1, 1, 1]
        self.assertIsNot(self.cpy_vector, self.target)


if __name__ == '__main__':
    unittest.main()

