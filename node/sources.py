#!/usr/bin/env python
#! -*- codinng: utf-8 -*-

from SimPy.Simulation import *

class Sources:
    """ This class represents the resources of the node."""

    def __init__(self, cpu=1, available_channels=1, up_speed=2, down_speed=3):
        """ Initializes the sources object. """
        self.cpu = Resource(name='cpu', capacity=cpu, qType=PriorityQ)
        self.av_channels = Resource(name='available_channels', \
                                    capacity=available_channels, \
                                    qType=PriorityQ)
        self.up_speed = Resource(name='up', capacity=up_speed, qType=PriorityQ)
        self.down_speed = Resource(name='down', \
                                    capacity=down_speed, \
                                    qType=PriorityQ)

    def _set_cpu(self, cpu):
        """ Sets a new value to cpu. """
        self.cpu.capacity = cpu

    def _get_cpu(self):
        """ Gets the cpu value. """
        return self.cpu.capacity

    def _set_channels(self, available_channels):
        """ Sets number of available channels."""
        self.av_channels.capacity = available_channels

    def _get_channels(self):
        """ Gets number of available channels."""
        return self.av_channels.capacity

    def _set_up_speed(self, up_speed):
        """ Sets speed to up channel."""
        self.up_speed.capacity = up_speed

    def _get_up_speed(self):
        """ Gets value of up channel speed."""
        return self.up_speed.capacity

    def _set_down_speed(self, down_speed):
        """ Sets value of speed to down channel. """
        self.down_speed.capacity = down_speed

    def _get_down_speed(self):
        """ Gets value of speed to down channel. """
        return self.down_speed.capacity

