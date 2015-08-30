#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module runs a simulation of coordbased algorithm. """

import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/simulation')
from message import Message
from environment import Environment
#from SimPy.SimulationTrace import *
from SimPy.Simulation import *
from random import Random, expovariate
sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from decentralizedProtocol import NodeProtocol
from ordinarynodeprotocol import OrdinaryNodeProtocol
from coordprotocol import CoordinatorProcess
sys.path.insert(2, '/home/blaxeep/Workspace/diploma/trunk/node')
from node import Node

import pdb


class NodeClass(Process):
    """ simulates one node. """
    NodeList = []
    mean_waiting_time = 0
    total_waiting_time = 0
    busy_cpu = 0

    def __init__(self, name, weight, protocol, sources, network):
        """ simulates a node instance for centralized protocol. """
        Process.__init__(self)
        self.node = Node(name, weight, protocol, sources, network)
        self.waiting_time = 0   # waiting time for this particular node
        self.msg_number = 0     # messages this node sent
        # signal for knowing if this simulation event is passive or not
        self.sleeping = False
        NodeClass.NodeList.append(self)

    def run(self):
        while True:
            # initialize incoming data, incoming messages and timeout 
            # simulation objects
            self.dj = DataJob()
            self.im = IncomingMsgs()
            self.to = TimeOut()
            # wait for a while before generating new data for current node
            yield hold, self, 0.1
            # generate new data and assign to new_data a true/false value:
            # if new_data = True then no action is taken, else send message
            # to coordinator.
            new_data = self.dj.recvEnvironmentData(self.node)
            # and activate them
            activate(self.dj, self.dj.run(self.node, new_data))
            activate(self.im, self.im.run(self.node, self.to))
            activate(self.to, self.to.run(self.im))


class DataJob(Process):
    """ This class is responsible for the simulating the incoming data.
    """

    def __init__(self):
        Process.__init__(self)

    def run(self, node, dont_send):
        """ simulates the arrival of new data. If it's ok, then wait
        for some time, else send message to coordinator.
        @node is the node that generates the data.
        @dont_send is a boolean variable that when it's true, then
        no action is taken else node sends its data to coordinator.
        """
        if dont_send:
            yield hold, self, 0.7
        else:
            yield request, self, node.protocol.network.net_chnls
            # simulate time needed to send the message to coordinator
            yield hold, self, 0.1
            # and send message to coordinator
            self.sendMessageToCoord(node)
            yield release, self, node.protocol.network.net_chnls

    def recvEnvironmentData(self, node):
        """ receives data from environment and checks it. """
        self.data = node.protocol.getDataFromNode()
        node.protocol.recvLocalUpdate(self.data)
        return node.protocol.dontSend()

    def sendMessageToCoord(self, node):
        """ sends a message to coordinator.
        This method creates a message according to standards and
        sends it to the network.
        @data the data to be sent (vector)
        """
        # create the message
        self.msg = node.protocol.createMessage(\
        node.protocol.cm.localStatistics, 'coord')
        # and send it
        node.protocol.sendMessage(self.msg)
    

class IncomingMsgs(Process):
    """ This class manages the incoming messages from the coordinator.
    """
    def __init__(self):
        Process.__init__(self)

    def run(self, node, timeout):
        """ simulation """
        if node.protocol.incoming_messages:
            yield request, self, node.sources.cpu
            # process the new message
            node.protocol.processNewMessage()
            yield hold, self, 0.1
            # release the cpu
            yield release, self, node.sources.cpu
        else:
            # reactivate the time out process
            reactivate(timeout)
            # and passivate
            yield passivate, self


class TimeOut(Process):
    """ simulates a timeout timer """

    def __init__(self):
        Process.__init__(self)

    def run(self, in_msgs):
        # maybe I could totally remove following line
        yield hold, self, 0.7
        reactivate(in_msgs)
        yield passivate, self

