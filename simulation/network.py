#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SimPy.Simulation import *
from random import Random, expovariate
import sys
import pdb


class Network:
    """ Simulates the network module. """

    def __init__(self):
        """ simulates the network """
        # define network sources
        self.net_chnls = Resource(capacity=10, \
                            name='Incoming Channels', qType=PriorityQ)
        self.MSG_QUEUE = [] # list of messages
        self.NodeList = []  # list of nodes
        self.new_msg = False# TODO implement a lock if necessary

    def addMsgToQueue(self, msg):
        """ This method adds the message to the MSG_QUEUE.
        @msg is the message added to MSG_QUEUE.
        """
        # add message to the message queue
        self.MSG_QUEUE.append(msg)
        # and increase counter for incoming messages by one
        NetStats.incoming_msgs += 1
        # and call the sendMsg method
        self.msgSend()

    def msgSend(self):
        """ sends a message to the appropriate recipient, after a short
        trip inside the network.
        """
        # while MSG_QUEUE has more messages
        while self.MSG_QUEUE:
            #extract the oldest message from queue
            self.msg = self.extractMsgFromQueue()
            # send it appropriately (multicast or just send)
            self.mcastOrSend(self.msg)

    def extractMsgFromQueue(self):
        """ extracts the message from queue. """
        # remove the first element of list
        self.message = self.MSG_QUEUE.pop(0)
        return self.message

    def mcastOrSend(self, msg):
        """ sends the message, whether broadcast or simple sending is
        needed.
        @msg is the message to be sent.
        """
        # check whether it is a list or a node
        if isinstance(msg.recipient, list):
            for recp in msg.recipient:
                self.send(recp, msg)
        else:
            self.send(msg.recipient, msg)
        NetStats.outgoing_msgs += 1

    def send(self, recipient, message):
        """ sends a message to the particular recipient.
        @recipient is the recipient (a single string)
        @message is the message to be sent
        """
        mc = SendJob(self.NodeList)
        activate(mc, mc.send(message, recipient))

    def setNodeList(self, nl):
        """ inits the Node list with NODES. """
        self.NodeList = nl



class SendJob(Process):
    """ this class is responsible for simulation. """
    def __init__(self, nodelist):
        Process.__init__(self)
        self.nodelist = nodelist

    def send(self, msg, recp):
        """ send the msg to the recp.
        @msg is the message
        @recp is the recipient
        """
        # retrieve the recipient
        self.recp = self.identifyNode(recp)
        # if recipient exists, then:
        if self.recp:
            # try to acquire recipient's channel
            yield request, self, self.recp.sources.av_channels
            # "travel" through network for some time
            self.travel_time = self.travelingTime()
            yield hold, self, self.travel_time
            NetStats.travel_time += self.travel_time
            # send the message and count another send
            self.recp.protocol.recvMessage(msg)
            NetStats.send_job_msgs += 1
            # and release the channel
            yield release, self, self.recp.sources.av_channels
        else:
            # no such recipient exists. passivate it.
            yield passivate, self

    def identifyNode(self, recp):
        """ identifies the node where the message should be sent.
        @recp the name of the recipient (string)
        @return the node that should recieve the message. If no node
        has been found, then return None.
        """
        for n in self.nodelist:
            if str(n.name) == str(recp):
                return n
        return None

    def travelingTime(self):
        """ returns the time a message travels into the network.
        @return the traveling time.
        """
        # the bigger the self.delay, the smaller the actual delay
        self.delay = 1000
        # not constant seed for real randomness
        self.seed = random.randint(12345, 98765)
        return random.Random(self.seed).expovariate(self.delay)


class NetStats:
    """ This class holds statistics for network. """
    incoming_msgs = 0
    outgoing_msgs = 0
    travel_time = 0.0
    send_job_msgs = 0
    send_method_m = 0
