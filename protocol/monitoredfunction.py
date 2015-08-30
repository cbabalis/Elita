#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module represents an interface which must be implemented. """

class MonitoredFunction:
    """ Implements the monitored function interface. """

    def getDimension(self):
        """ Dimension of the vector space.
        @return the dimension
        """
        raise NotImplementedError

    def isMonochromatic(self, estimate, drift):
        """ Implements the main function for the threshold monitoring.

        If the ball defined by estimate and drift vectors is wholly
        within the safe zone, then return True.
        else, return False

        @param estimate the estimate (i.e. global estimate)
        @param drift the drift vector of a node
        @return true if the ball with diameter defined by estimate and
        drift is wholly within the safe zone, false elsewhere.
        """
        raise NotImplementedError
