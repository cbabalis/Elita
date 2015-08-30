#!/usr/bin/env python

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/data')
from ams import *
import unittest
import pdb
from copy import deepcopy
import random


class testAMS(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for testing """
        self.bucks = 20
        self.depth = 7
        self.ams = AMS_Sketch(self.bucks, self.depth)

    def testCreateHelpArray(self):
        """ test the create help array function.
        Two tests are included. The first checks if the help array
        exists. The second if the functions created are four-wise
        independent.
        """
        self.rand_arr = self.ams.createHelpArray()
        # first of all, check that the rand_arr exists
        self.assertTrue(self.rand_arr)
        # now, check that the rand_arr funcs are independent
        self.assertNotEqual(self.rand_arr[0], self.rand_arr[1])
        self.assertNotEqual(self.rand_arr[2], self.rand_arr[3])

    def testUpdate(self):
        """ tests the update function of the AMS sketch. """
        # hold the old sketch somewhere
        self.old_sketch = deepcopy(self.ams.sketch)
        # update the sketch
        self.ams.update(2, 4)
        self.assertNotEqual(self.old_sketch, self.ams.sketch)
    
    def test_compute_hash_value(self):
        """ tests the hash value for permitted values. """
        # run several times so as to be sure
        for i in range(10):
            self.counter = random.randint(0, self.depth-1)
            self.h = self.ams._compute_hash_value(5, self.counter)
            self.assertLessEqual(self.h, self.bucks)
            self.assertGreaterEqual(self.h, 0)

    def testIsCompatible(self):
        """ tests the compatibility function between two sketches. """
        # create a compatible sketch (of the same dimensions)
        self.another_sketch = AMS_Sketch(self.bucks, self.depth)
        # but let it also have different items
        self.another_sketch.update(1,1)
        # test the isCompatible function
        self.is_comp = self.ams.isCompatible(self.another_sketch)
        self.assertTrue(self.ams.sketch, self.another_sketch)

    def testIsNotCompatible(self):
        """ tests the isCompatible() with a not compatible sketch
        (expext it to be False).
        """
        self.another_sketch = AMS_Sketch(self.bucks+1, self.depth)
        self.is_comp = self.ams.isCompatible(self.another_sketch)
        self.assertFalse(self.is_comp)

    def testItemCount(self):
        """ tests if the count of an item is being returned. """
        self.item = 8   # random item
        for i in range(10):
            self.ams.update(self.item, 1)
        self.count = self.ams.itemCount(self.item)
        pdb.set_trace()
        self.assertEqual(self.count, 10)


if __name__ == '__main__':
    unittest.main()

