#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module represents the simulation in the coordinator. """

from SimPy.Simulation import *
import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
from node import Node
from nodecoordclass import NodeClass, DataJob, TimeOut
import pdb


class CoordClass(NodeClass):
    """ simulates the coordinator. """
    NodeList = []
    mean_waiting_time = 0
    total_waiting_time = 0

    def __init__(self, name, weight, protocol, sources, network):
        """ simulates a node instance for centralized protocol. """
        Process.__init__(self)
        self.node = Node(name, weight, protocol, sources, network)
        self.waiting_time = 0   # waiting time for this particular node
        self.msg_number = 0     # messages this node sent
        self.busy_cpu = 0    # time the cpu is busy
        # signal for knowing if this simulation event is passive or not
        self.sleeping = False
        CoordClass.NodeList.append(self)

    def run(self):
        while True:
            # create the simulation objects
            self.cdj = CoordDataJob()
            self.cim = CoordIncomingMsgs()
            # this class has been imported from nodecoordclass.py
            self.to = TimeOut()
            # wait for a while before generating new data for current node
            yield hold, self, 0.1
            # generate new data and assign to new_data a true/false value:
            # if new_data = True then no action is taken, else send message
            # to coordinator.
            new_data = self.cdj.recvEnvironmentData(self.node)
            # and activate them
            activate(self.cdj, self.cdj.run(self.node, new_data))
            activate(self.cim, self.cim.run(self.to, self.node))
            activate(self.to, self.to.run(self.cim))

    
class CoordDataJob(DataJob):
    """ This class is responsible for the simulation of incoming data.

    This class inherits from DataJob that already is a process.
    """
    def __init__(self):
        DataJob.__init__(self)

    def run(self, node, dont_send):
        """ simulates the case where new local data arrive to coord."""
        if dont_send:
            yield hold, self, 0.7
        else:
            # else, acquire and spend some cpu time
            yield request, self, node.sources.cpu
            yield hold, self, 0.0001
            # and run the protocol
            self.processOwnData(node)
            # finally, release cpu
            yield release, self, node.sources.cpu

    def processOwnData(self, node):
        """ processes the data it received by its node.
        @node is the node
        @data is the new data (vector) that node received by itself.
        """
        data = node.protocol.cm.localStatistics
        node.protocol.localDataProcess(data)


class CoordIncomingMsgs(Process):
    """ this class is responsible for the simulation of coordinator
    behavior during a message reception.
    """
    def __init__(self):
        """ simulates the procedure the coordinator follows when an
        incoming message (or messages) has come.
        """
        Process.__init__(self)

    def run(self, timeout, node):
        """ runs the simulation for an incoming message to coordinator.
        @param timeout
        @param node is the node for which the simulation runs.
        """
        if node.protocol.incoming_messages:
            # extract the first message from the list
            msg = node.protocol.incoming_messages.pop(0)
            # request cpu for processing this task
            yield request, self, node.sources.cpu
            # process the message
            self.processMessage(msg, node)
            # release cpu
            yield release, self, node.sources.cpu
        else:
            # reactivate the time out process
            reactivate(timeout)
            # and passivate
            yield passivate, self

    def processMessage(self, message, node):
        """ processes an incoming message. """
        if hasattr(message, 'signal'):
            self.signal = message.signal
            if self.signal == 'INIT':
                node.protocol.INIT_receipt(message)
            elif self.signal == 'REP':
                node.protocol.REP_receipt(message.sender,\
                        message.content[0], message.content[1])
            else:
                pdb.set_trace()
                print "SIGNAL-ERROR: No such signal exists (coordclass.py)"
        else:
            print 'this message has no signal'


def DEBUG(param, msg=''):
    """ Prints the param. """
    print msg + str(param)
