#!/usr/bin/env python

""" Unit test for streamhandler.py"""

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/userinterface')
from streamhandler import StreamHandler
import unittest


class TestStreamHandler(unittest.TestCase):
    """ tests for streamhandler.py """

    def setUp(self):
        """ initial setup for testing. """
        # txt file for testing the reading of a 'txt' file
        self.txt_file = '/home/blaxeep/Workspace/test/simpy/test.txt'
        # a binary file as we want it
        self.bin_file = '/home/blaxeep/Workspace/vsam/wc_day44'
        # a bad binary file (our demanded structure is different)
        self.bad_bin_file = '/home/blaxeep/Workspace/test/bad_bin'
        self.handler = StreamHandler(self.bin_file)

    def testIsBinary(self):
        """ tests the behavior of isbinary method when input is a
        binary file.
        """
        self.result = self.handler.isbinary(self.bin_file)
        self.assertTrue(self.result)

    def testIsBinaryNot(self):
        """ tests the behavior of isbinary method when input is not a 
        binary file.
        """
        self.result = self.handler.isbinary(self.txt_file)
        self.assertFalse(self.result)

    def testGoodStream(self):
        """ tests if a generator that generates correct items is
        created.
        """
        # create the generator
        self.gen = self.handler.readStream(self.bin_file)
        # produce ten items and check if their length of each one is 8
        for i in range(10):
            self.item = self.gen.next()
            self.assertEqual(len(self.item), 8)

    def testOtherFormatStream(self):
        """ tests that a generator is created."""
        # create a generator of items that contains other format
        self.gen = self.handler.readStream(self.bin_file, 'LLHHII')
        # produce ten items and check if item's length is other than 8
        # and check if there actually is (exists) an item
        for i in range(10):
            self.item = self.gen.next()
            self.assertNotEqual(len(self.item), 8)
            self.assertTrue(self.item)

    def testSendItem(self):
        """ tests the sendItem method. It should return several items."""
        self.item_generator = self.handler.readStream(self.bin_file)
        for i in range(10):
            self.item = self.handler.sendItem()
            self.assertTrue(self.item)
        

    def testInfiniteSendItem(self):
        """ tests the behavior of sendItem method in the particular
        case of the user demanding more data than the generator is able
        to produce.
        """
        self.item_generator = self.handler.readStream(self.bin_file)
        i = 0
        while True:
            self.item = self.handler.sendItem()
            if self.item == 'stream ended':
                self.assertTrue(self.item)
                break

if __name__ == '__main__':
    unittest.main()

