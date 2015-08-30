#!/usr/bin/env python
# -*-coding: utf-8-*- 


""" Unit test for prng.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/data')
from prng import Prng
import unittest


class TestPrng(unittest.TestCase):
    """ tests for Prng.py"""

    def setUp(self):
        """ initial setup for testing. """
        self.prng = Prng()


    def testCreateRandomArray(self):
        """ tests createRandomArray(self, rows, columns).
        Check if the returned item:
        (a) exists
        (b) has the same dimensions as given
        (c) is full of numbers (and not zeros, for example).
        """
        self.arr = self.prng.createRandomArray(8, 10)
        self.assertTrue(self.arr)
        # check if rows are ok
        self.assertEqual(len(self.arr), 8)
        # then check if columns are ok, too
        self.assertEqual([len(v) for k, v in self.arr.iteritems()][0], 10)
        for k, v in self.arr.iteritems():
            self.assertTrue(v)

    def testGenHashAssistantNums(self):
        """ tests if method returns a list full of random numbers
        and of length(depth).
        """
        self.row = self.prng.genHashAssistantNums(8)
        self.assertTrue(self.row)
        self.assertEqual(len(self.row), 8)

    def testHash31(self):
        """ tests if an item is hashed. """
        self.number = 7798
        self.result = self.prng.hash31(12344, 3456, self.number)
        self.assertTrue(self.result)

    def testBadArgumentHash31(self):
        """ tests if hash31 can hash a non-numerical item. """
        self.number = 'this is not a number'
        self.result = self.prng.hash31(12344, 3456, self.number)
        self.assertEqual(self.result, -1)

    def testFourwise(self):
        """ tests if fourwise works. """
        self.result = self.prng.fourwise(213,45,6546,2342,43)
        self.assertTrue(self.result)


if __name__ == '__main__':
    unittest.main()
