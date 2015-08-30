#!/usr/bin/env python
# -*-coding: utf-8-*-

""" Unit test for coordclass.py. """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/simulation/coordbasedsim')
from coordclass import CoordClass
from nodecoordclass import NodeClass
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from sources import Sources
from SimPy.Simulation import *

import unittest

import pdb


class TestCoordClass(unittest.TestCase):
    
    def setUp(self):
        """ initial setup"""
        self.net = Network()
        self.nc1 = NodeClass('simple_node_1', 0.1, 'coordbased', \
                            Sources(), self.net)
        self.nc2 = NodeClass('simple_node_2', 0.1, 'coordbased', \
                            Sources(), self.net)
        self.cc = CoordClass('coord', 0.1, 'coordbased', Sources(), self.net)
        self.li = [self.nc1, self.nc2, self.cc]
        self.nc1.node.protocol.initProtocol(self.li)
        self.nc2.node.protocol.initProtocol(self.li)
        self.cc.node.protocol.initProtocol(self.li)
        self.net.NodeList = self.li


    def testRun(self):
        """ tests the run method. """
        self.cc.run()
        pass

    def testIncomingMsgs(self):
        """ tests the incomingMsgs method. """
        # wrong test
        initialize()
        activate(self.cc, self.cc.incomingMsgs())
        simulate(until=10)
        self.assertTrue(self.cc.busy_cpu)

    def test_sim(self):
        """ tests a real simple small simulation. """
        initialize()
        for node in self.li:
            activate(node, node.run())
            activate(node, node.incomingMsgs())
        self.net.run()
        simulate(until=10)
        self.assertTrue(self.cc.node.protocol.NodeList)


if __name__ == '__main__':
    unittest.main()
