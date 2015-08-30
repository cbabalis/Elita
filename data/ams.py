#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module implements an AMS-sketch and its methods."""

import numpy
from prng import Prng
from ams_ops import AMS_Operations
import pdb


class AMS_Sketch:
    """ Implements an AMS-Sketch. """

    def __init__(self, buckets=2000, depth=7):
        """ 'Constructor' for ams sketch.
        @param buckets the buckets for sketch
        @param depth number of vectors.
        """
        self.depth = depth
        self.buckets = buckets
        # following two lines are from imports (from the same package)
        #self.operations = AMS_Operations(self.buckets, self.depth)
        self.operation = AMS_Operations()
        self.rand_gen = Prng()
        self.count = 0
        # create the sketch
        #self.sketch = [[0 for i in range(self.buckets)] \
        #                  for j in range(self.depth)]
        self.sketch = [0 for i in range(self.buckets * self.depth)]
        self.rand_array = self.createHelpArray()


    def createHelpArray(self):
        """ creates and returns an array full of random numbers.

        Creates an array which contains random numbers that are used
        for the production of pairwise independent hash functions.
        @return the array.
        """
        # first, be sure that everything that is needed, exists
        assert self.buckets and self.depth and self.rand_gen
        # create an array of (buckets x depth) length full of random
        # integer numbers uniformly distributed in the range 0...2^31-1
        self.rand_array = self.rand_gen.\
                            createRandomArray(self.buckets, self.depth)
        return self.rand_array

    def update(self, item, freq=1):
        """ This method updates the sketch.
        @param item is the new item that came.
        @param freq is the frequency
        """
        # work exactly the same way as in itemCount(item). Only last
        # method changes.
        self.offset = 0
        for i in range(self.depth):
            self.hash_value = self._compute_hash_value(item, i)
            self.mult = self._compute_mult_factor(item, i)
            self._update_sketch(self.mult, self.offset, self.hash_value, freq)
            self.offset += self.buckets

    def _update_sketch(self, mult, offset, hash_value, freq):
        """ This method updates the sketch array. """
        if (mult & 1) == 1:
            self.sketch[offset + hash_value] += freq
        else:
            self.sketch[offset + hash_value] -= freq

    def isCompatible(self, sketch):
        """ compares the self.sketch with the argument sketch about
        compatibility issues.

        This method checks if the two sketches have the same dimensions
        and the same help arrays and return true if sketches have the 
        same dimensions and help arrays and false otherwise.
        @param sketch is a sketch.
        @return boolean True if they are comparable or False otherwise.
        """
        # check if all parameters of two sketches are the same.
        # If they are, return True (that means that sketches can be
        # added, substracted, etc).
        if not sketch: return False
        if self.buckets != sketch.buckets or \
            self.depth != sketch.depth or \
            self.rand_array != sketch.rand_array:
            return False
        return True

    def itemCount(self, item):
        """ returns the count of an item.
        @param item is the item for which count is asked.
        @return the count.
        """
        self.offset = 0
        self.estimates = [0] * self.depth
        for i in range(self.depth):
            # compute the hash value
            self.hash_value = self._compute_hash_value(item, i)
            # compute the mult factor (+/-1)
            self.mult = self._compute_mult_factor(item, i)
            # place the hash_value to the appropriate position
            self._get_estimate(self.hash_value, self.mult, \
                               self.offset, self.estimates, i)
            self.offset += self.buckets
        # return the final estimate for item
        self.count = self._compute_final_estimate(self.estimates)
        return self.count

    def _compute_hash_value(self, item, counter):
        """ private method that computes the hash value. """
        self.hash_value = self.rand_gen.hash31(\
            self.rand_array[0][counter], self.rand_array[1][counter],\
            item) % self.buckets
        return self.hash_value

    def _compute_mult_factor(self, item, counter):
        """ private method that computes the mult factor. """
        self.mult = self.rand_gen.fourwise(\
            self.rand_array[0][counter], self.rand_array[1][counter], \
            self.rand_array[2][counter], self.rand_array[3][counter], \
            item)
        return self.mult

    def _get_estimate(self, hash_value, mult, offset, estimates, counter):
        """ computes an estimate of the item. """
        assert type(estimates) is list, "estimate not a list! (in ams.py)"
        if mult & 1 == 1:
            estimates[counter] += self.sketch[offset + hash_value]
        else:
            estimates[counter] -= self.sketch[offset + hash_value]

    def _compute_final_estimate(self, estimates):
        """ computes the final count (by the help of estimates) for
        a particular item.
        @param estimates the estimates for an item.
        @return the count.
        """
        # initialize count to -1 (it's an error value)
        self.count = -1
        # in the degenerated case depth==1: return the single estimate
        if self.depth == 1:
            self.count = estimates[0]
        else:
            # else, compute and return median. Full documentation is 
            # found here: 
            # http://docs.scipy.org/doc/numpy/reference/generated/numpy.median.html
            self.count = numpy.median(estimates)
        # make count integer before return it
        return int(self.count)

    def estimateF2(self, sketch):
        """ estimates F2 moment of the vector (sum of squares).
        @param sketch is the sketch.
        @return the estimate F2.
        """
        estimates = self._mult_by_pos(sketch, sketch)
        self.result = self._compute_final_estimate(estimates)
        return self.result

    def _mult_by_pos(self, sketch_a, sketch_b):
        """ This method computes the following formula:
        r = sum(sketch_a[i] * sketch_b[i]), i in (1,...,N)
        @param sketch_a is the first sketch (array)
        @param sketch_b is the second sketch (array)
        @return the inner product of (sketch_a, sketch_b)
        """
        self.result = [a * b for a, b in zip(sketch_a, sketch_b)]
        return self.result

    def computeInnerProd(self, sketch):
        """ computes inner product.
        @param sketch is a sketch.
        @return inner product
        """
        # first of all, check if sketch is ok
        self.isCompatible(sketch)
        self.estimates = self._mult_by_pos(self.sketch, sketch)
        self.result = self._compute_final_estimate(self.estimates)
        return self.result

    def setZero(self, sketch):
        """ sets a whole sketch to contain zero values.
        @param sketch is the sketch.
        """
        assert type(self.sketch) is list, "not a list argument! setZero"
        self.sketch = [0] * len(self.sketch)

