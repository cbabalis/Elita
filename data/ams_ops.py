#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module implements a set of operations for ams sketches. """

import numpy
from copy import deepcopy

class AMS_Operations:
    """ operations for ams sketches. """

    def __init__(self):
        """ inits an AMS_Operations instance """
        pass
    
    @classmethod
    def computeNorm(cls, sketch):
        """ computes the norm of the sketch.
        @param sketch is the sketch whose norm will be computed.
        @return the norm.
        """
        return numpy.sqrt(cls.computeSquareNorm(sketch))

    @classmethod
    def computeSquareNorm(cls, sketch):
        """ computes the square norm of a sketch.
        @param sketch is the sketch whose norm will be computed.
        @return norm is the norm.
        """
        # given an array sketch, implement the following formula:
        # norm = sum(sketch[i]^2), i:(0, [length of sketch])
        norm = numpy.power(sketch, 2)
        norm = sum(norm)
        return norm

    @classmethod
    def scale(cls, sketch, scale_factor):
        """ scales on sketch by a scalar.
        @param sketch is the scetch to be scaled.
        @param scale_factor is the scale factor by which the sketch
        will be scaled.
        """
        sketch = [val * scale_factor for val in sketch]
    
    @classmethod
    def add_sketch(cls, sketch_a, sketch_b):
        """ adds two sketches. """
        # make the operation
        result = numpy.add(sketch_a, sketch_b)
        # and return the result as a list (numpy converts it to list).
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.add.html
        return result.tolist()

    @classmethod
    def sub_sketch(cls, sketch_a, sketch_b):
        """ substracts sketch_b from sketch_a."""
        # copy the sketch that is going to be substracted
        inverted_sketch = deepcopy(sketch_b)
        # revert the value of each number contained in b
        inverted_sketch = [-1 * val for val in inverted_sketch]
        # add the two vectors
        result = cls.add_sketch(sketch_a, inverted_sketch)
        return result

    @classmethod
    def compare(cls, sketch_a, sketch_b):
        """ compares each element of sketch_a and sketch_b.
        @return True if they contain same values in the exact same
        positions and False otherwise.
        """
        # create a new list that contains True and False values for
        # matches and misses, respectively
        result = [val1 == val2 for val1, val2 in zip(sketch_a, sketch_b)]
        if False in result:
            return False
        else:
            return True

    @classmethod
    def divide_by_val(cls, sketch, divider):
        """ divides the sketch with divider. """
        # assert divider is not 0
        if divider:
            di = 1/divider
            cls.scale(sketch, di)

    @classmethod
    def add_val(cls, sketch, value):
        """ adds a value to sketch. """
        sketch = [val + value for val in sketch]

    @classmethod
    def sub_val(cls, sketch, value):
        """ substracts a value from sketch. """
        cls.add_val(sketch, -value)
