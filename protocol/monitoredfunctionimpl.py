#!/usr/bin/env python
# -*-coding: utf-8-*- 

""" This module implements the MonitoredFunction interface. """

import numpy
from monitoredfunction import MonitoredFunction
import pdb


class MonitoredFunctionImpl(MonitoredFunction):
    """ Implements the monitored function. """

    def __init__(self, dimension=0, error=0.01, margin=1.10):
        """ @param error is the error permitted.
        @param margin is the relaxation for errors.
        """
        self.dimension = dimension
        self.error = error
        self.margin = margin
        self.threshold = None

    def getDimension(self):
        """ returns the dimension of vector.
        Hardcoded for now.
        """
        return self.dimension

    def isMonochromatic(self, estimate, drift):
        """ checks if the ball is monochromatic, by checking
        the condition given.
        @param estimate is the estimate vector.
        @param drift is the drift vector
        @param thres is the threshold, and in particular the
        sqrt(thres)
        @return True if the ball is Monochromatic and False otherwise.
        """
        #return sum(estimate) >= 50.0 and sum(drift) >= 50.0
        self.center_vec = self._compute_center(estimate, drift)
        self.sorted_vec = sorted(self.center_vec)
        self.rad_ball = self._compute_rad(estimate, drift)
        self.r2 = 0.0
        self.dim = len(self.sorted_vec)
        for i in range(int(self.dim/2), self.dim):
            if self.sorted_vec[i] < self.threshold:
                self.r2 += (self.threshold - self.sorted_vec[i])**2
            else:
                break
        return self.rad_ball < numpy.sqrt(self.r2)

    def _compute_center(self, estimate, drift, depth=7, buckets=2000):
        """ computes the center of the ball.
        It is ((estimate + drift)^2)/2.2
        @param estimate is the estimate vector.
        @param drift is the drift vector.
        @return is a vector, lengthed depth, and consisted of centers.
        """
        c = []
        index = 0
        # for every raw in the vectors, compute the sum between them,
        # multiply the result by itself, divide it by 2 and 
        # add it to c vector
        for i in range(depth):
            squares = 0
            elem = 0
            for j in range(buckets):
                elem += (estimate[index] + drift[index])/2
                squares += elem * elem
                index += 1
            c.append(numpy.sqrt(squares))
        return c

    def _compute_rad(self, estimate, drift, depth=7, buckets=2000):
        """ computes the rad of the ball. Rad is a simple value.
        @param estimate is the estimate vector
        @param drift is the drift vector.
        @return is the rad.
        """
        # Implementation algorithm explanation:
        # we have our sketches in one-dimensional vector.
        # Instead of having [[a,b,c],[a,b,c],...,[a,b,c]],
        # we have [a,b,c, a,b,c, ..., a,b,c].
        # In order to implement the 
        # rad = sqrt(sum(power((est[i][1...buck] - drift[i][1...buck])/2))),
        # we do it by multiplying ixj (=bucketsxdepth) but increasing
        # the global index ixj times.
        rad = 0.0
        index = 0
        sum_of_squares = 0
        for i in range(depth):
            for j in range(buckets):
                diff = (estimate[index] - drift[index])/2
                square = diff * diff
                sum_of_squares += square
                index += 1
        rad = numpy.sqrt(sum_of_squares)
        return rad

    def set_threshold(self, est):
        """ initializes and sets threshold.
        @param est is a vector.
        """
        # at first, create a help vector of same length as est
        help_vec = [0] * len(est)
        # and call _compute_rad()
        self.thres = self._compute_rad(est, help_vec)
        self.threshold = self.margin * self.thres

    def get_threshold(self):
        """ @return the threshold. """
        return self.threshold
