#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module is responsible for results manipulation and handling.
"""


import os
import pdb
import sys


class NetResults:
    """ Results class reads the statistics from the simulation and
    writes it to a file.
    """

    def __init__(self, net_stats, results_path='/storage/tuclocal/babalis/results/results.txt'):
        """ initializes a Results instance. """
        self.net_stats = net_stats
        self.read_file(results_path)


    def read_file(self, path=''):
        """ writes results to a file.
        @path is the path where the file is.
        """
        # if file does not exist, create it
        if not self.file_exists(path):
            self.create_file(path)
        #pdb.set_trace()
        self.write_results(path)


    def file_exists(self, path):
        """ checks if a file exists or not.
        @param path is the ABSOLUTE path where the file is.
        @return True if file exists and False otherwise.
        """
        if os.path.exists(path):
            return True
        return False

    def create_file(self, path):
        """ creates a file and writes headlines.
        @path is the ABSOLUTE path where the file is.
        """
        f = open(path, 'w')
        self.write_headlines(f)
        f.close()

    def write_headlines(self, f):
        """ write the fields' titles into the file.
        @param f is a file.
        """
        self.headline = 'incoming msgs\toutgoing msgs\ttravel time\t' +\
                        ' send job msgs\n\n'
        f.write(self.headline)

    def write_results(self, path):
        f = open(path, 'a')
        f.write(self.create_stats_line())
        f.close()

    def create_stats_line(self):
        """ creates a line with all stats."""
        column_width = '\t\t\t'
        self.line = str(self.net_stats.incoming_msgs) + column_width +\
                    str(self.net_stats.outgoing_msgs) + column_width +\
                    str(self.net_stats.travel_time) + '\t\t'+\
                    str(self.net_stats.send_job_msgs) + '\n'
        return str(self.line)


class MonitorResults:
    """ saves and writes to file the results of a monitor. """

    def __init__(self, monitor, headlines, pathfile=''):
        """ initializes a MonitorResults object.
        @param monitor is the monitor.
        @param headlines are the headlines that describe the statistics
        following.
        @param pathfile is the path where the file is.
        """
        self.mon = monitor
        self.headlines = headlines
        self.path = pathfile
        self.write_to_file()


    def write_to_file(self):
        """ writes the monitor results to file. """
        assert self.path, "no path exists"
        # open the file
        f = open(self.path, 'a')
        # write the headlines (the title)
        self.write_headlines(f)
        # write all monitor's observations
        self.write_results(f)
        # and finally close the file
        f.close()
    
    def write_headlines(self, f):
        """ writes the headlines to the file.
        @param f is the file.
        """
        f.write("\n\n")
        f.write(self.headlines)

    def write_results(self, f):
        """ writes the statistics from a monitor.
        @param f is the file.
        """
        f.write("\ncount,total,mean,var,\
                timeaverage, timevariance\n")
        f.write("%s,%s,%s,%s,%s,%s" % (self.mon.count(), self.mon.total(),\
                self.mon.mean(), self.mon.var(), self.mon.timeAverage(),\
                self.mon.timeVariance()))


    def write_analytic_results(self, f):
        """ writes the results to the file.
        @param f is the file.
        """
        for item in self.mon:
            f.write("%s\n" % item)


class PrintMonitor:
    """ prints the result of a monitor. """

    def __init__(self, monitor, title):
        """ initializes a printMonitor object.
        @param monitor is the monitor
        @param data_format is the data_format.
        @param title is the title of the monitor.
        """
        self.m = monitor
        self.df = 'count,total,mean,var,timeaverage,timevariance'
        self.title = title
        self.print_results()

    def print_results(self):
        print self.title
        print self.df
        print "%s,%s,%s,%s,%s,%s" %(self.m.count(), self.m.total(),\
            self.m.mean(), self.m.var(), self.m.timeAverage(),\
            self.m.timeVariance())


class Stats:
    incoming_msgs = 0
    outgoing_msgs = 0
    travel_time = 0.0
    send_job_msgs = 0


def main():
    r = Results(Stats())


if __name__ == '__main__':
    main()
