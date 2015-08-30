#!/usr/bin/env python
# -*-coding: utf-8-*-

""" Unit test for coordprotocol.py. """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from decentralizedProtocol import NodeProtocol
from coordprotocol import CoordinatorProcess
from signals import *
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from node import NodeClass, Node
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation/coordbasedsim')
from coordclass import CoordClass

import unittest


class TestCoordProtocol(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for testing """
        # define network first
        self.net = Network()
        self.n1 = NodeClass(1, 0.1, 'coordbased', 'sources', self.net)
        self.n2 = NodeClass(2, 0.1, 'coordbased', 'sources', self.net)
        self.coordclass = CoordClass('coord', 0.1, 'coordbased', 'sources', self.net)
        self.coord = self.coordclass.node
        self.coord.protocol = CoordinatorProcess('coord', self.net)
        self.NodeList = [self.n1, self.n2, self.coordclass]
        # create a list with the nodes and the coordinator
        self.nl = [self.n1.node, self.n2.node, self.coord]
        # copy this list to network, too
        self.net.NodeList = self.nl
        # first of all, initialize protocol's nodelist
        self.n1.node.protocol.NodeList = self.n1.NodeList
        #self.coordclass.NodeList = self.NodeList
        self.coord.protocol.NodeList = self.NodeList

    def testInitCoord(self):
        """ tests the initialization of coordinator. """
        self.coord.protocol.initCoord(self.n1.node.protocol.NodeList)
        # test if it actually exist any list in coord's protocol
        self.assertTrue(self.coord.protocol.NodeList)
        self.assertEqual(len(self.coord.protocol.NodeList),\
                         len(self.n1.NodeList))

    def testBadProcessRecvdMessage(self):
        """ tests the reception of a message. """
        # append a meaningless, false message to incoming messages list
        self.coord.protocol.incoming_messages.append('false_message')
        # observe what it is being returned
        self.msg = self.coord.protocol.processRecvdMessage()
        self.assertFalse(self.msg)

    def testINIT_receipt(self):
        """ tests the reception of an INIT-message. """
        # create an init message
        self.msg = INIT(1, 'coord', 'init stats', 0.1)
        # test the function
        self.coord.protocol.INIT_receipt(self.msg)
        # check if message is being processed properly
        self.assertEqual(self.coord.protocol.all_vectors[1], \
                         [0.1, 'init stats'])

    def testLocalDataArrival(self):
        """ tests the local data arrival method. """
        self.d = self.coord.protocol.localDataArrival()
        self.assertTrue(self.d)

    def testGetNodeWeight(self):
        """ tests the getNodeWeight method. """
        self.coord.protocol.all_vectors = {1:[0.1, 'some data'], 2:[0.1, 'more data']}
        self.w = self.coord.protocol.getNodeWeight(2)
        self.assertEqual(self.n2.node.weight, self.w)

    def testBadNodeWeight(self):
        """ tests for a bad name given in the getNdeWeight method. """
        self.coord.protocol.all_vectors = {1:[0.1, 'some data'], 2:[0.1, 'more data']}
        self.w = self.coord.protocol.getNodeWeight('non-existent-name')
        self.assertIsNone(self.w)


if __name__ == '__main__':
    unittest.main()

