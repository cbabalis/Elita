#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module implements node processes, for various types of nodes.
"""

from SimPy.Simulation import *
import random
import environment
import network
import sys
import os
#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
#node_path = os.path.abspath('../node')
node_path =  '/storage/tuclocal/babalis/source/trunk/node'
sys.path.insert(0, node_path)
from node import Node
from sources import Sources
import pdb



class SimpleNodeProcess(Process):
    """ simulates a node process. """

    def __init__(self, name, signal, network, node_type='node'):
        """ initializes a node process instance.
        @param name is the name of the instance.
        @param signal is a SimEvent() that notifies the node process
        for a new item arrival.
        @param network is the network.
        """
        Process.__init__(self)
        self.name = str(name)
        self.arrival = signal
        self.item_list = [] # list of items (statistics purposes)
        self.node = self._setup_node(name, network, node_type)
        self.stats = NodeStats()
        self.data_mon = Monitor()
        self.data_mon.observe(0)


    def _setup_node(self, name, network, node_type):
        """ creates and sets up a node.
        @param name is the name of the node
        @return a Node instance.
        """
        return Node(name, 0.2, 'coordbased', Sources(), network, node_type)

    def run(self):
        """ runs a simulation """
        while True:
            # if no data exists for further processing then wait for
            # data to come
            if not self.node.raw_data:
                yield waitevent, self, self.arrival
            # after data has come, process it a bit
            yield hold, self, self.delay()
            # and continue with data process phase
            if self.node.raw_data:
                # TODO Code here
                b = self.node.handleData()
                #pdb.set_trace()
                if b: self.compute_list_time(now())

    def delay(self, delay_factor=10):
        """ represents the delay that occurs to a node during data
        collection from environment.
        @param delay_factor is a factor that defines how small (or big)
        the delay will be. The bigger the delay_factor, the smaller the
        delay.
        i.e.delay_factor=10   ->delay=0.01xxx
            delay_factor=100  ->delay=0.001xxx
            delay_factor=1000 ->delay=0.0001xxx
        @return a random, very small delay.
        """
        # not constant seed for real randomness
        self.seed = random.randint(12345, 98765)
        return random.Random(self.seed).expovariate(delay_factor)

    def compute_list_time(self, now, offset=897256801):
        """ computes the total time that all the items wait in a
        node's item list.
        @now is the current time.
        @offset helps us to find the time an item arrived.
        """
        while self.item_list:
            self.it = self.get_item()
            self.atomic_time = float(now + offset - self.it.timestamp)
            self.stats.wait_mon.observe(self.atomic_time)
            self.stats.list_waiting_time += self.atomic_time
            self.stats.total_items += 1

    def set_item(self, item):
        #self.data_mon.observe('INSERT')
        self.data_mon.observe(len(self.item_list))
        self.item_list.append(item)

    def get_item(self):
        #self.data_mon.observe('EXTRACT')
        return self.item_list.pop(0)
        



class NodeProcess(SimpleNodeProcess):
    """ Implements a node process, focused on coord-based version of
    algorithm as described in [lift2006].
    """
    
    def __init__(self, name, signal, network, node_type='node'):
        """ initializes a node process.
        @param name is the name of the node process.
        @param signal is a signal that notifies the process about
        new messages
        @param network is the network.
        """
        SimpleNodeProcess.__init__(self, name, signal, network, node_type='node')

    

class CoordProcess(NodeProcess):
    """ Implements a coordinator process, focused on coord-based
    version of algorithm as described in [lift2006].
    """

    def __init__(self, name, signal, network):
        """ initializes a node process.
        @param name is the name of the node process.
        @param signal is a signal that notifies the process about
        new messages
        @param network is the network.
        """
        NodeProcess.__init__(self, name, signal, network, node_type='coord')
        self.name = str(name)
        self.arrival = signal
        self.node = self._setup_node(name, network, 'coord')

    
    def run(self):
        """ runs a simulation """
        while True:
            # if no data exists for further processing then wait for
            # data to come
            if not self.node.raw_data:
                yield waitevent, self, self.arrival
            # after data has come, process it a bit
            yield hold, self, self.delay()
            # and continue with data process phase
            if self.node.raw_data:
            # TODO Code here
                self.node.handleCoordData()


class NodeStats:
    list_waiting_time = 0.0
    total_items = 0
    wait_mon = Monitor()

