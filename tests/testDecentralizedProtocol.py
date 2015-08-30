#!/usr/bin/env python

""" Unit test for decentralizedprotocol.py. """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from decentralizedProtocol import NodeProtocol
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from message import Message
import unittest


class TestDecentralizedProtocol(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for testing """
        # define network first
        self.net = Network()
        # and init two nodes
        self.n1 = NodeProtocol('n1', self.net)
        self.n2 = NodeProtocol('n2', self.net)
        # finally put the nodes to nodelist of network
        self.NodeList = [self.n1, self.n2]
        # initialize the stats
        self.stats = [0,1,2,3,4,5,6,7,8,90]
        # add the nodes to the global list
        self.n1.NodeList = [self.n1, self.n2]
        self.n1.all_vectors = {'n1':[0.2, self.stats], 'n2':[0.1, self.stats]}


    def testSendMessage(self):
        """ tests if sendMessage sends a message to network. """
        self.msg = Message('n1', 'n2', self.stats)
        self.n1.sendMessage(self.msg)
        self.assertTrue(self.net.MSG_QUEUE, msg='msg queue is ' + 
                        str(self.net.MSG_QUEUE))

    @unittest.skip("no real node has been created")
    def testBcastStatVector(self):
        """ tests if broadcast works. """
        self.n1.bcastStatVector(self.stats)
        self.assertTrue(self.net.MSG_QUEUE)

    def testRecvMessage(self):
        """ checks if the recvMessage method is ok."""
        self.msg = Message('n1', 'n2', self.stats)
        self.n1.recvMessage(self.msg)
        self.assertTrue(self.n1.incoming_messages)
    
    def testCreateMessage(self):
        """ checks if a Message object is created. """
        self.msg = self.n1.createMessage(self.stats, 'n2')
        self.assertIsInstance(self.msg, Message)

    def testRecvStatVector(self):
        """ checks the receiving of stat vector. """
        self.result = self.n1.recvStatVector(self.stats)
        self.assertEqual(self.result, self.stats)

    def testRecalcEstimateVector(self):
        """ checks the recalcEstimateVector. """
        self.n1.cm.localStatistics = self.stats
        self.n1.recalcEstimateVector()
        self.assertTrue(self.n1.cm.estimate, msg='In testRecalcEstimate')

    def testCalcEstimate(self):
        """ checks if the estimate is calculated correctly. """
        # create a message and add it to incoming_messages list
        self.n1.incoming_messages.append(Message('n1', 'n2', self.stats))
        # calculate the estimate from this message
        self.n1.calcEstimate()
        self.assertTrue(self.n1.cm.estimate)

    def updateStatVector(self):
        """ checks if the statistics vector is updated correctly. """
        self.new_vector = [0,2,4,6,8,0,2,4,6,8]
        self.n1.updateSAtatVector('n1', self.new_vector)
        self.assertEqual(self.new_vector, self.n1.all_vectors['n1'][1])

    def testCalcDriftVector(self):
        """ checks if drift vector is calculated. """
        self.n1.cm.localStatistics = [2,4,6,8,2,4,6,8,2,4]
        self.n1.cm.lastStatistics = self.stats
        self.n1.calcEstimate()
        self.n1.calcDriftVector()
        # steps above are necessary so as to initialize correctly
        self.assertTrue(self.n1.cm.drift)

    def testProcessMessage(self):
        """ checks the processMessage method. """
        self.msg = Message('n1', 'n2', self.stats)
        self.node_id, self.v = self.n1.processMessage(self.msg)
        self.assertEqual(self.node_id, 'n1', msg='node id is '+str(self.node_id))
        self.assertEqual(self.v, self.stats)

    def testInitAllVectorsList(self):
        """ checks the initAllVectorsList method. """
        self.n1.initAllVectorsList()
        self.assertTrue(self.n1.all_vectors)



if __name__ == '__main__':
    unittest.main()
