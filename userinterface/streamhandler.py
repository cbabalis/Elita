#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module is able to read a stream. """

import os
import sys
import struct
import pdb

class StreamHandler:
    """ A stream is read and methods about it are defined. """

    def __init__(self, stream_filename):
        """ init.
        @param stream_filename is the name of stream file.
        """
        self.stream_name = stream_filename
        # check if stream is binary
        #if not self.isbinary(self.stream_name):
        #    print "STREAM-ERROR: Not a binary stream given as input."
        # if it is, then initialize the stream and
        self.item_generator = self.readStream(self.stream_name)
        #R = WorldCupRequest()   # TODO Implement these three lines
        # the results code
        #stats = WorldCupStreamStats()



    def sendItem(self):
        """ sends an item.
        @return an item.
        """
        return self.item_generator.next()

    def readStream(self, name='wc_day44', item_format='>LLLLBBBB'):
        """ opens the file and reads the (binary) stream.
        It reads the file given with the item format given and returns
        a generator that "yields" items.
        @param name is the name of the binary file.
        @param item_format is the format of the struct we want to
        "extract" from the binary file. Default is (4 longs - 4 bytes)
        and big-endian format.
        @return a generator that generates stream items.
        """
        # open the file and create a struct format
        f = open(name, 'rb')
        s = struct.Struct(item_format)
        # read the binary file block-by-block and yield a block each
        # time, until the file ends. Print an ending-statement and exit
        while True:
            try:
                data = f.read(s.size)
                fields = s.unpack(data)
                yield fields
            except BaseException:
                # in case something is wrong and file has more to give
                if f.read(1) != '':
                    continue
                # else just exit
                yield 'stream ended'
                break
        f.close()

#    def isbinary(self, path):
#        """ checks if the file is binary or not.
#        @param path is the path were the file is found.
#        @return True if the file is binary and
#                False if the file is not (i.e. it's text.)
#        """
#        # run a shell command and write the results into a file
#        self.process = subprocess.call(["file -bi "+path+">> isbin.txt"], 
#        shell=True)
#        # open the file and check if binary word is in it.
#        self.f = open('isbin.txt', 'r')
#        self.result = self.f.read()
#        # finally, destroy the isbin.txt file
#        self.process = subprocess.call(["rm isbin.txt"], shell=True)
#        if 'binary' in self.result:
#            return True
#        else:
#            return False

def main():
    sh = StreamHandler(sys.argv[1])
    temp = ''
    while temp != 'stream ended':
        temp = sh.sendItem()



if __name__ == '__main__':
    main()

