#!/usr/bin/env python

""" Unit test for message.py """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
from message import Message
import unittest

class BadMessage(unittest.TestCase):
    
    def setUp(self):
        """ initial set up for testing """
        self.msg = Message('', '', '')  # blank message created

    def testBadSender(self):
        """ tests for no sender. It should fail. """
        self.assertFalse(self.msg.isSender())

    def testBadRecipient(self):
        """ tests for bad recipient. It should fail. """
        self.assertFalse(self.msg.isRecipient())

    def testBadContent(self):
        """ tests for bad content. It should fail. """
        self.assertFalse(self.msg.isContent())

    def testEmptyMessage(self):
        """ tests for empty message. It should fail. """
        self.assertEqual(self.msg.isEmpty(), 0)


class GoodMessage(unittest.TestCase):
    
    def setUp(self):
        """ initial setup for testing """
        self.msg = Message('Sender', 'Recepient', 'Content')

    def testGoodSender(self):
        """ tests for good sender. It should pass. """
        self.assertTrue(self.msg.isSender())

    def testGoodRecipient(self):
        """ tests for good recipient. It should pass. """
        self.assertTrue(self.msg.isRecipient())
    
    def testGoodContent(self):
        """ tests for good content. It should pass. """
        self.assertTrue(self.msg.isContent())

    def testRealMsg(self):
        """ tests for an existed, 'populated' message. It should pass. """
        self.assertFalse(self.msg.isEmpty())

    @unittest.skip("no use for this test")
    def testLargeMsg(self):
        """ tests for a large message. It should pass. """
        self.assertRaises(Message.OutOfRangeError, self.msg.size, 999999999999)

    def testComputeMsgSize(self):
        """ tests for size computation. It should pass. """
        self.assertTrue(self.msg.computeMsgSize())


if __name__ == '__main__':
    unittest.main()

