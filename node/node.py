#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module describes a node. """

# following two lines are for network import
import sys
import os
#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/simulation')
#sim_path = os.path.abspath('../simulation')
sim_path = '/storage/tuclocal/babalis/source/trunk/simulation'
sys.path.insert(0, sim_path)
from message import Message
from random import Random, expovariate
#sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/protocol')
#from decentralizedProtocol import NodeProtocol
#from ordinarynodeprotocol import OrdinaryNodeProtocol
#from coordprotocol import CoordinatorProcess
import pdb
#sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/protocol/coordbasedProtocol')
#coordbased_prot = os.path.abspath('../trunk/protocol/coordbasedProtocol')
coordbased_prot = '/storage/tuclocal/babalis/source/trunk/protocol/coordbasedProtocol'
sys.path.insert(1, coordbased_prot)
from coordProtocol import *
from nodeProtocol import *
import time



class Node:
    """ This class defines a node and its special operations."""

    def __init__(self, name, weight, protocol_name, \
                    sources, network, node_type='node'):
        """ inits a node instance.
        @param name is the name of the node.
        @param weight is the weight of the node.
        @param protocol_name is the name of the protocol.
        @param sources is the Sources of the node (CPU, RAM, Channels).
        @param network is the network (for sending messages, etc.)
        """
        self.name = str(name)
        self.weight = weight
        self.protocol = self.selectProtocol(protocol_name, \
                                self.name, network, node_type)
        self.sources = sources
        self.raw_data = []  # items that have come but not read yet
        self.max_queue_msgs = 0


    def selectProtocol(self, protocol_name, node_name, network, node_type):
        """ selects which protocol the node will have. 
        
        if it is a coordinator, then the node will have coord protocol.
        if it is a simple node of the coord-based algorithm, then
            the node will have the appropriate protocol.
        Same goes if its about decetralized algorithm.
        """
        self.protocol_name = protocol_name
        # first of all, if node is coordinator, return it immediately
        if str(node_type).lower() == 'coord':
            return CoordProtocol(node_name, network)
        # if protocol name is one of the supported, then return it
        # else, return an error message
        if self.protocol_name.lower() == 'decentralized':
            return NodeProtocol(node_name, network)
        elif self.protocol_name.lower() == 'coordbased':
            return NodeProtocol(node_name, network) #OrdinaryNodeProtocol(node_name, network)
        else:
            print 'No supported protocol!'

    def getWeight(self):
        """ returns the weight of this node. """
        return float(self.weight)

    def setWeight(self, weight):
        """ sets a new weight value for this node. """
        self.weight = weight
    
    def handleData(self):
        """ handles the data that have been accumulated."""
        self.computeMaxQueueMsgs()
        #pdb.set_trace()
        # the algorithm has 3 cases:
        #   if state == 'INIT' then initialize protocol
        #   if state != 'INIT' and !wait_ACK() then:
        #       -> add all incoming tuples to localStatistics
        #       -> check if ball is monochromatic and run protocol
        #   else:
        #       do nothing
        if self.protocol.state == 'INIT' and self.protocol.ack==True:
            self.protocol.start(self.raw_data, self.weight)
        elif self.protocol.state == 'SAFE':    #and self.protocol.cm.estimatenot and notself.protocol.wait_ack()
            # pass items to protocol and check for monochromicity
            self.protocol.recv_local_update(self.raw_data)
        else:
            return False    # if false, just wait more
        return True # if true, then compute statitistcs

    def handleCoordData(self):
        """ handles the data as coordinator. """
        if self.protocol.state == 'INIT':
            self.protocol.start_coord(self.raw_data, self.weight)
        elif self.protocol.state == 'SAFE': 
            self.protocol.recv_local_update(self.raw_data)
        else:
            return False
        return True

    def computeMaxQueueMsgs(self):
        """ computes the max number of accumulated messages in the
        queue.
        """
        if len(self.raw_data) > self.max_queue_msgs:
            self.max_queue_msgs = len(self.raw_data)


