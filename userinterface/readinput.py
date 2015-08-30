#!/usr/bin/env python
# -*-coding: utf-8-*-
# @author: blaxeep

""" This module provides an interface for reading a configuration file.

"""


from configobj import ConfigObj
import os
import os.path


class ReadInput:
    """ This class reads a file.conf and extracts its data. """
    
    def __init__(self):
        """ inits the ReadInput instance. """
        self.path = self.askPath()
        self.data = self.extractData(self.path)

    def askPath(self, path=''):
        """ Asks path for configuration file from the user and
        validates it.
        """
        self.path = path
        # check if the file path is correct and repeat 'till it is
        while not self.isFile(self.path):
            self.path = raw_input('Please insert configuration file path: ') 
        return self.path

    def extractData(self, path):
        """ Returns a dictionary structure with all data

        This method returns all data (nodes and their data,
        configuration details, etc) in a dictionary structure.
        """
        self.path = path
        # check if the file exists
        if self.isFile(self.path) :
            # if it exists, then extract data
            self.raw_data = self.readConfigFile(self.path)
        else:
            # else, print an error message
            print "No such file exists! program is exiting..."
        return self.raw_data

    @classmethod
    def readConfigFile(cls, path):
        """ Reads the configuration file given from path.

        This method reads the file that corresponds to given path and
        returns a dictionary with all elements (keys and values) inside
        it.
        """
        # open the file and read it as a dictionary (key:value1, value2, ...)
        config = ConfigObj(path)
        # return the dictionary
        return config

    def isFile(self, path):
        """ Checks if the given path corresponds to a file. 
        
        This method checks if the path that is corresponding to a 
        particular file exists and returns true or false, depending
        on the result.
        """
        is_file = os.path.isfile(path)
        return is_file


