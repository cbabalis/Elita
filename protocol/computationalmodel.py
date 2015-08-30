#!/usr/bin/env python
# -*-coding: utf-8-*-


import abc  # TODO Remove it if not necessary at all

class ComputationalModel(object):
    """ describes the computational model. """

    def __init__(self):
        self.create_vectors()

    def create_vectors(self):
        """ Creates the vectors necessary for computational model. """
        self.localStatistics = []
        self.lastStatistics = []
        self.globalV = []
        self.estimate = []
        self.delta = []
        self.drift = []
        self.slack = []  # only for coordBased model
