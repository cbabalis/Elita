#!/usr/bin/env python
# -*-coding: utf-8-*-

from copy import deepcopy
import pdb  # DEBUGGING


class VectorOps:
    """ This class contains static methods implementing some arithmetic
    operations on lists (vectors).
    """

    def __init__(self):
        pass

    @classmethod
    def addTo(cls, target, operand):
        """ adds operand to target. """
        # make sure lists have the same length
        if not cls.have_same_length(target, operand):
            target, operand = cls.init_empty_vector(target, operand)
        result = [targ + op for targ, op in zip(target, operand)]
        return result

    @classmethod
    def subFrom(cls, target, operand):
        """ substracts operand from target. """
        if not cls.have_same_length(target, operand):
            target, operand = cls.init_empty_vector(target, operand)
        cls.result = [targ - op for targ, op in zip(target, operand)]
        return cls.result

    @classmethod
    def mult(cls, a, b):
        """ returns a * b. """
        cls.ret = deepcopy(a)
        cls.ret = cls.multBy(cls.ret, b)
        return cls.ret

    @classmethod
    def multBy(cls, target, operand):
        """ multiplies the elements of a vector with a number.. """
        cls.result = [item * operand for item in target]
        return cls.result

    @classmethod
    def cpy(cls, dest=[], src=[]):
        """ Copies the elements of src to the elements of dst"""
        # assign an empty list but same length to dest vector
        dest = [0] * len(src)
        assert cls.have_same_length(dest, src), 'different length'
        dest = deepcopy(src)
        return dest

    @classmethod
    def multAndAddTo(cls, target, factor, operand):
        """ Adds target = factor * operand. """
        if not cls.have_same_length(target, operand):
            target, operand = cls.init_empty_vector(target, operand)
        target = [elem * factor for elem in operand]
        return target

    @classmethod
    def multAndAdd(cls, target, factor, operand):
        """return target + factor * operand. """
        cls.clone = deepcopy(target)
        cls.multAndAddTo(cls.clone, factor, operand)
        return cls.clone

    @classmethod
    def have_same_length(cls, a=[], b=[]):
        """ checks for equal lengths of two lists (vectors) """
        if len(a) == len(b):
            return True
        else:
            return False

    @classmethod
    def init_empty_vector(cls, a, b):
        """ in case a vector (usually last statistics vector) is empty,
        full it with zeros.
        """
        if len(a) > len(b):
            b = [0] * len(a)
        elif len(a) < len(b):
            a = [0] * len(b)
        return (a, b)

if __name__ == '__main__':
    pass
