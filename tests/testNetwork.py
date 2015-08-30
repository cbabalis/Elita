#!/usr/bin/env python

""" Unit test for network.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network, SendJob, NetStats
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from node import Node
from message import Message
from sources import Sources

import unittest

class TestNetwork(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for network. """
        self.net = Network()    # init the network
        self.net.NodeList = self.assignNodes(5)
        # counter for counting how many times a method called

    def assignNodes(self, node_num):
        """ creates nodes and returns them. """
        # init a list
        li = []
        for i in range(node_num):
            li.append(Node(i, 0.2, 'decentralized', 'sources', self.net))
        return li
    
    def testAddMsgToQueue(self):
        """ tests the addMsgToQueue method. """
        self.msg = Message(1, 0, 'data')
        self.net.addMsgToQueue(self.msg)
        pass

    def testMsgSend(self):
        """ tests if msgSend works ok. """
        # add a message to MSG_QUEUE
        self.net.MSG_QUEUE.append(Message(1,0,'data'))
        self.net.msgSend()
        self.assertFalse(self.net.MSG_QUEUE)

    def testExtractMsgFromQueue(self):
        """ tests the extraction of a message from message queue."""
        self.net.MSG_QUEUE.append(Message(1,0,'data'))
        self.msg = self.net.extractMsgFromQueue()
        self.assertTrue(self.msg)

    def testMcast(self):
        """ tests the case of sending to multiple recipients."""
        # create a message with multiple recipients
        self.msg = Message(0, [1,2,3], 'data')
        self.net.mcastOrSend(self.msg)
        # dummy
        self.assertEqual(len(self.msg.recipient), 3)

    def testSendSingleMsg(self):
        """ tests the send case a single recipient."""
        self.msg = Message(0, 1, 'data')
        self.net.mcastOrSend(self.msg)
        self.assertEqual(len(self.msg.recipient), 1)

    def testNodeList(self):
        """ tests the nodeList method."""
        self.old_list = self.net.NodeList
        self.net.setNodeList([Node('dummy', '0', '1', '2', '4')])
        self.assertNotEqual(self.net.NodeList, self.old_list)


class TestSendJob(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for SendJob class. """
        self.nodelist = [(Node(1, 0.2, 'decentralized', 'sources','n')),\
                        (Node(3, 0.2, 'decentralized', 'sources', 'n'))]
        self.msg = Message(1, 3, 'data')
        self.job = SendJob(self.nodelist)

    def testSend(self):
        """ it just runs the send method. """
        self.job.send(self.msg, self.msg.recipient)

    def testIdentifyNode(self):
        """ tests identifyNode method for an existing name. """
        self.name = self.job.identifyNode(self.msg.recipient)
        self.assertTrue(self.name)

    def testBadIdentifyNode(self):
        """ tests identifyNode method for a bad (non-existent) name."""
        self.name = self.job.identifyNode('dummy_name')
        self.assertFalse(self.name)

    def testTravelingTime(self):
        """ tests the randomness of traveling time."""
        self.coll = []
        for i in range(100):
            self.coll.append(self.job.travelingTime())
        # now put the list to a set and check if any values are double
        # a valuable source for using set as is exhibited, is here:
        # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
        self.assertEqual(len(set(self.coll)), len(self.coll))


if __name__ == '__main__':
    unittest.main()

