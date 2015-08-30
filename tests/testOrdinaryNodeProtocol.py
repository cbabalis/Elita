#!/usr/bin/env python

""" Unit test for signals.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from ordinarynodeprotocol import OrdinaryNodeProtocol
from signals import NEW_EST, ADJ_SLK
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from node import Node
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation/coordbasedsim')
from nodecoordclass import NodeClass

import unittest

class TestOrdinaryProtocol(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for testing """
        # define network first
        self.net = Network()
        self.n1 = NodeClass(1, 0.1, 'coordbased', 'sources', self.net)
        self.n2 = NodeClass(2, 0.1, 'coordbased', 'sources', self.net)
        self.coord = NodeClass('coord', 0.1, 'coordbased', 'sources', self.net)
        # create a list with the nodes and the coordinator
        self.NodeList = [self.n1.node, self.n2.node, self.coord.node]
        # copy this list to network, too
        self.net.NodeList = self.NodeList
        # first of all, initialize protocol's nodelist
        self.n1.node.protocol.NodeList = self.n1.NodeList

    def testAssignCoord(self):
        """ checks if coordinator is setted up. """
        for n in self.NodeList:
            n.protocol.assignCoord(self.coord.node.name)
        for n in self.NodeList:
            self.assertEqual('coord', n.protocol.COORD)

    def testNodeWeight(self):
        """ checks if it returns the weight of the node each time. """
        self.w = self.n1.node.protocol.getNodeWeight()
        self.assertTrue(self.w)

    def testNonexistentNodeWeight(self):
        """ checks if it returns None in case the node name does not
        exist.
        """
        self.non_existent_node = OrdinaryNodeProtocol(3, self.net)
        self.w = self.non_existent_node.getNodeWeight()
        self.assertFalse(self.w)

    def testInitialization(self):
        """ checks if initialization runs ok. """
        self.n1.node.protocol.initialization()
        self.msg = self.net.MSG_QUEUE.pop(0)
        self.assertEqual(self.msg.signal, 'INIT')

    def testREQ_receipt(self):
        """ tests REQ_receipt(). 
        
        Test should be ok if a REP message is contained in message list
        of network.
        """
        self.n1.node.protocol.REQ_receipt()
        self.msg = self.net.MSG_QUEUE.pop(0)
        self.assertEqual(self.msg.signal, 'REP')

    def testNEW_EST_receipt(self):
        """ tests NEW_EST_receipt() method. """
        # first, create a NEW_EST message
        self.msg = NEW_EST('coord', self.NodeList, [0,1,2,3,4,5])
        # then test method
        self.n1.node.protocol.NEW_EST_receipt(self.msg)
        # finally check the results
        self.assertEqual(self.n1.node.protocol.cm.estimate, \
                            self.msg.content)
        self.assertEqual(len(self.n1.node.protocol.cm.slack), \
                            len(self.msg.content))

    def testADJ_SLK_receipt(self):
        """ tests ADJ_SLK_receipt(). """
        # preliminaries (create ADJ_SLK message and init slack vector)
        self.init_msg = NEW_EST('coord', self.NodeList, [1,1,1,1,1])
        self.n1.node.protocol.NEW_EST_receipt(self.init_msg)
        self.msg = ADJ_SLK('coord',1, [1,2,3,4,5] )
        # first receipt of an adj_slk message
        self.n1.node.protocol.ADJ_SLK_receipt(self.msg)
        # check that length is equal
        self.assertEqual(len(self.n1.node.protocol.cm.slack), \
                        len(self.msg.content))
        # create and receive a second adj_slk message
        self.msg = ADJ_SLK('coord',1, [1,2,3,4,5] )
        self.n1.node.protocol.ADJ_SLK_receipt(self.msg)
        # compare the two vectors. new slack should be added to the old
        self.assertNotEqual(self.n1.node.protocol.cm.slack, \
                            self.msg.content)


if __name__ == '__main__':
    unittest.main()
