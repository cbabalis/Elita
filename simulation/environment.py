#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module simulates the environment of a simulation, as well as
the functionality it should display.
"""

from SimPy.Simulation import *
import random
import sys
import os
import pdb
sys.path.insert(0, '/storage/tuclocal/babalis/source/trunk/userinterface')
#interface_path = os.path.abspath('../trunk/userinterface/')
#sys.path.insert(0, interface_path)
from streamhandler import StreamHandler
from network import *
#sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/node')
node_path = '/storage/tuclocal/babalis/source/trunk/node/'
sys.path.insert(1, node_path)
from node import Node
from sources import Sources
#import nodeprocess
from nodeprocess import *
#sys.path.insert(2, '/home/blaxeep/Workspace/diploma/trunk/protocol/coordbasedProtocol')
coordbased_prot = '/storage/tuclocal/babalis/source/trunk/protocol/coordbasedProtcool'
sys.path.insert(2, coordbased_prot)
from nodeProtocol import NodeProtocol
from coordProtocol import CoordProtocol
#sys.path.insert(3, '/home/blaxeep/Workspace/diploma/trunk/results')
#from results import NetResults, MonitorResults
results_path = '/storage/tuclocal/babalis/source/trunk/results'
sys.path.insert(3, results_path)
from results import NetResults, MonitorResults, PrintMonitor


class Environment(Process):
    """ Simulates the environment where the nodes are found."""

    def __init__(self, sh='streamhandler', network=None, max_nodes=5, \
                    max_coord=1, data_rate=1):
        """ Environment is initialized and basic functionality starts.
        @param sh is a streamhandler
        @param network is the network
        @param max_nodes is the maximum number of nodes in the system
        @param max_coord is the maximum number of coords in the system
        """
        Process.__init__(self)
        self.ncl = []   # list of node processes
        self.sh = sh
        self.max_nodes = max_nodes
        self.max_coord = max_coord
        self.data_rate = data_rate
        self.net = network
        self.start()


    def start(self):
        """ this method starts all the preliminary work that has to
        be done for the environment to run.
        """
        self.init_network()
        self.create_nodes()
        self.setup_environment()

    def create_nodes(self):
        """ this method creates all nodes necessary to the system."""
        # initialize all node processes
        for i in range(self.max_nodes):
            # create a node process instance, add it to ncl list
            self.ncl.append(NodeProcess(i, SimEvent(), self.net))
            # and activate it
            activate(self.ncl[i], self.ncl[i].run())
        # initialize all coordinator processes
        for i in range(self.max_coord):
            # add to the position the max_nodes number as offset
            position = i + self.max_nodes
            self.ncl.append(CoordProcess(position, SimEvent(), self.net))
            self.ncl[position].nodes_num = self.max_nodes
            activate(self.ncl[position], self.ncl[position].run())

    def init_network(self):
        """ inits the network. If no network exists, then
        just inititalize one.
        """
        if not self.net:
            self.net = Network()

    def setup_environment(self):
        """ sets up basic functionality. """
        # set name of coordinator to all nodes
        for i in range(self.max_nodes):
            self.ncl[i].node.protocol.COORD = \
                            self.ncl[self.max_nodes].node.name
        # set up the node number in the coordinator protocol, too
        nl = self.return_nodelist()
        self.ncl[self.max_nodes].node.protocol.set_nodelist(nl)
        self.net.setNodeList(nl)
        

        # create a list of nodes only and assign it to coord

    def return_nodelist(self):
        """ returns a list full of nodes only. """
        nl = []
        for n in self.ncl:
            nl.append(n.node)
        return nl

    def run(self):
        """ simulation functionality. Here the environment runs
        its simulation.
        """
        while True:
            # collect a tuple
            self.t = self.collect_item()
            # analyze it to its basic fields
            self.item = self.analyze_tuple(self.t)
            # compute a time to wait and if necessary, wait
            wait_time = self.compute_waiting_time(self.item, now())
            if wait_time > 0:
                yield hold, self, wait_time
            # send the item to the appropriate node
            self.send_item(self.item)

    def collect_item(self):
        """ collects an item from the stream handler. """
        try:
            self.item = self.sh.sendItem()
            return self.item
        except Exception:
            print 'no more items available!'
            sys.exit(0)

    def analyze_tuple(self, t):
        """ analyzes a tuple of data to its basic fields.
        @param t is a tuple from the stream
        """
        self.item = Item(t[0], t[1], t[3])
        return self.item

    def compute_waiting_time(self, item, now, offset=897256801):
        """ computes the time remaining for an item to be available.
        @param item is the item
        @param now is the current moment in simulation
        @param offset is a value that helps us to compute timestamps
        """
        self.current_time = (now * self.data_rate)+ offset 
        self.wait_time = float(item.timestamp - self.current_time)
        return self.wait_time

    def send_item(self, item):
        """ sends an item to the appropriate node.
        @param item is the item to be sent
        """
        # find the node to whom the item should go
        self.node_proc = self.find_recipient(item.recp_name)
        # append the item to its list
        self.node_proc.node.raw_data.append(item.data)
        # append the whole item to another list
        self.node_proc.set_item(item)
        # and notify the node process instance that new data arrived
        self.node_proc.arrival.signal()

    def find_recipient(self, recp):
        """ finds the node to whom an item is intended to go
        @recp is the recipient's name
        """
        # compute the recipient as recp = large_num mod all_nodes_num
        self.recipient = recp % (self.max_nodes + self.max_coord)
        # and search for this node into the node processes list
        for item in self.ncl:
            if item.node.name == str(self.recipient):
                return item
        print 'no such recipient exists!' + str(self.recipient)


class Item:
    """ This class represents an item with clear fields. """
    def __init__(self, timestamp, recp_name, data):
        """ initialize the item
        @param timestamp is the time moment the item arrives.
        @param recp_name is the name of the recipient.
        @param data is the data that the item carries.
        """
        self.timestamp = timestamp
        self.recp_name = recp_name
        self.data = data



def main():
    params = assign_params()
    maxTime, maxNodes, maxCoords, dataRate, datapath = params
    sh = StreamHandler(datapath)
    initialize()
    net = Network()
    stats = NetStats()  # for network statistics
    node_stats = NodeStats()    # for node statistics
    env = Environment(sh, net, maxNodes, maxCoords, dataRate)
    activate(env, env.run())
    simulate(until=maxTime)
    r = NetResults(stats)
    #monitor_results(env, params)
    print_results(env, params, stats)



def assign_params(maxTime=100, maxNodes=2, maxCoords=1, dataRate=1.0,
                    datapath='/home/blaxeep/Workspace/vsam/wc_day44'):
    """ assign parameters to the system.
    @param maxTime is the maximum time the system is allowed to run in
    time.
    @param maxNodes is the number of nodes
    @param maxCoords is the number of coords
    @param dataRate is the rate that the data flow.
    @param datapath is the path where the data is found.
    """
    maxTime = float(sys.argv[1])
    maxNodes = int(sys.argv[2])
    maxCoords = int(sys.argv[3])
    dataRate = float(sys.argv[4])
    datapath = str(sys.argv[5])
    return (maxTime, maxNodes, maxCoords, dataRate, datapath)

def monitor_results(env, params):
    for n in env.ncl:
        pathname = '/storage/tuclocal/babalis/results/data_res' + str(n.name)
        MonitorResults(n.data_mon, (str(params) + '\ndata statistics'), pathname)
        MonitorResults(n.node.protocol.state_mon, 'state statistics',pathname)
        if n.name == n.node.protocol.COORD:
            MonitorResults(n.node.protocol.bp.balance_mon, \
                    'balancing process statistics', pathname)

def print_results(env, params, stats):
    print "simulation_title:t%s n%s c%s r%s" %(params[0], params[1], params[2],params[3])
    for n in env.ncl:
        print "node:"+str(n.name) # + " params:" + str(params)
        PrintMonitor(n.data_mon, 'data statistics')
        PrintMonitor(n.node.protocol.state_mon, 'state statistics')
        if n.name == n.node.protocol.COORD:
            PrintMonitor(n.node.protocol.bp.balance_mon,'balance stats')
    print "msgs_in_network,total_travel_time"
    print str(stats.incoming_msgs) + "," + str(stats.travel_time)


if __name__ == '__main__':
    main()


