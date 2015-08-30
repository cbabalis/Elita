#!/usr/bin/env python
# -*-coding: utf-8-*-

""" Unit test for monitoredfunctionimpl.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from monitoredfunctionimpl import *
import numpy
import unittest
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/data')
from ams import *


class TestMonitoredFunctionImpl(unittest.TestCase):
    
    def setUp(self):
        """ initial setup"""
        self.mf = MonitoredFunctionImpl()
        self.est = AMS_Sketch()
        self.drift = AMS_Sketch()
