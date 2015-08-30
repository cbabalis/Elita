#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module implements probabilistic random number generators. """

import random


class Prng:
    """ Prng stands for Probabilistic Random Number Generators."""

    HL = 31 # number of bits for shifting
    MOD = 2**31 - 1 # 2^31 - 1: biggest number

    def __init__(self):
        pass

    def createRandomArray(self, rows, columns):
        """ generates a dictionary (rows x columns) and fills it with
        random numbers.
        @param rows is the rows of the array
        @param columns is the columns of the array
        @return a dictionary with random numbers.
        """
        # initialize dictionary
        rand_array = {}
        # fill it with random numbers
        for i in range(rows):
            rand_array[i] = self.genHashAssistantNums(columns)
        return rand_array

    def genHashAssistantNums(self, depth):
        """ generates assistant numbers for hash functions.
        It generates <depth>-long a's and b's for hash function a*x + b
        @param depth is the depth.
        @return a list ofh random numbers.
        """
        # return a list of length(depth) with numbers in range(MOD)
        return random.sample(xrange(Prng.MOD), depth)

    def hash31(self, a, b, item):
        """ hash item.
        @return a hash of x using a and b MOD(2^31-1).
        May need to do another mod afterwards, or drop high bits
        depending on d, number of bad guys.
        @param a is assistant number for hash function
        @param b is assistant number for hash function
        @param item is the item
        @return a hash value
        """
        # if item is not an integer, then return False
        if type(item) is not int: return -1
        # 2^31-1 = 2147483647
        self.result = (a * item) + b
        # msbit and lsbit have special treatment (TODO Why?)
        self.result = ((self.result >> Prng.HL ) + self.result) & Prng.MOD
        return self.result

    def fourwise(self, a, b, c, d, x):
        """ @return 4-wise independent values. """
        result = self.hash31(self.hash31(self.hash31(x, a, b), x, c), x, d)
        return result

