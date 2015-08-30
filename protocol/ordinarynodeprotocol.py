#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module represents a node as part of the centralized algorithm,
as described in the following paper:
'A geometric approach to monitoring threshold functions over
distributed data streams'.
"""

# imports
from computationalmodel import ComputationalModel
from signals import *
from vec_ops import VectorOps
import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
from message import Message
from decentralizedProtocol import NodeProtocol
from monitoredfunctionimpl import MonitoredFunctionImpl
import pdb


class OrdinaryNodeProtocol(NodeProtocol):
    """ Represents an ordinary node, which inherits the basic features
    of a protocol.
    """

    def __init__(self, node_name, network):
        """ inits the protocol for a particular node. """
        self.node_name = node_name
        self.network = network
        self.cm = ComputationalModel()
        self.all_vectors = {}
        self.incoming_messages = []
        self.COORD = '' # init coord to null
        # special ack is True if node waits for a NEW_EST or ADJ_SLK msg
        self.special_ack = ''
        self.weight = 0 # init the weight to zero.
        self.NodeList = []   # list of all nodeclass instances
        self.mf = MonitoredFunctionImpl()


    def assignCoord(self, nodeId):
        """ assigns the particular nodeId to the coordinator """
        self.COORD = nodeId

    def getNodeWeight(self):
        """ sets the weight of node. """
        for nc in self.NodeList:
            if self.node_name == nc.node.name:
                return float(nc.node.getWeight())
        return None
    
    def initialization(self):
        """ inits the centralized protocol. """
        # first of all set the weight
        self.weight = self.getNodeWeight()
        # hold the initial statistics vector to last statistics
        self.cm.lastStatistics = self.getDataFromNode()
        # set slack vector to 0
        self.cm.slack = VectorOps.init_empty_vector(self.cm.slack, \
                        self.cm.lastStatistics)
        # create then init message
        self.init_msg = INIT(self.node_name, \
                                self.COORD, \
                                self.cm.lastStatistics,\
                                self.weight)
        # send message to network
        self.sendMessage(self.init_msg)

    ## Processing stage -----------------------------------------------

    def newDataArrival(self):
        """ Upon arrival of new data on a node's local stream,
        recalculate v(t) and u(t), and check if B(e(t), u(t))
        remains monochromatic.
        If not, send a REP(v(t), u(t)) message to the coordinator, and
        wait for either a NEW_EST or an ADJ_SLK message.
        """
        self.recvLocalUpdate(self.getDataFromNode())
        if not self.dontSend():
            # second part of the documentation algorithm is done by 
            # the following method.
            self.REQ_receipt()

    def processNewMessage(self):
        """ processes a new message. """
        if self.incoming_messages:
            # take the new message
            self.msg = self.incoming_messages.pop(0)
            # and examine different signal types
            if self.msg.signal == 'REQ':
                self.REQ_receipt()
            elif self.msg.signal == 'NEW_EST':
                self.NEW_EST_receipt(self.msg)
            elif self.msg.signal == 'ADJ_SLK':
                self.ADJ_SLK_receipt(self.msg)
            else:
                print "MESSAGE-ERROR: No such message (ordinarynodeprotocol)"

    def REQ_receipt(self):
        """ Upon receipt of a REQ message, send a REP(v(t), u(t))
        message to the coordinator and wait for either a NEW_EST or an
        ADJ_SLK message.
        """
        # calculate drift vector
        self.calcDriftVector()
        # create a REP message
        self.msg = REP(self.node_name, self.COORD,\
                    self.cm.localStatistics, self.cm.drift)
        # and send it
        self.sendMessage(self.msg)
        self.waitSpecialAck() # TODO Implement this

    def calcNodeDriftVector(self):
        """ calculates the drift vector of a node.
        """
        self.weightEstimate = 1.0
        self.ratioW = self.weightEstimate/self.weight
        # compute statistics delta vector.
        # delta = (weight*localStatistics - weightEstimate*localEstimate -
        # (weight - weightEstimate)*globalEstimate) / weight
        self.cm.delta = VectorOps.multAndAdd(self.cm.localStatistics, \
                        self.weight, self.localEstimate)
        VectorOps.multAndAddTo(self.cm.delta, self.ratioW-self.weight,\
                                self.cm.globalV)
        # update drift vector
        VectorOps.cpy(self.cm.drift, self.cm.globalV)
        VectorOps.addTo(self.cm.drift, self.cm.delta)
        VectorOps.multAndAddTo(self.cm.drift, 1.0/self.weight, self.cm.slack)


    def waitSpecialAck(self):
        """ waits for a specific message type (either NEW_EST or ADJ_SLK)"""
        self.special_ack = True

    def checkSpecialAck(self, message):
        """ checks the kind of message.
        If message is AJD_SLK or NEW_EST, then procceed.
        """
        if self.special_ack:
            if message.signal != 'NEW_EST' and message.signal != 'ADJ_SLK':
                print "No such signal exists"
                return False
        # if special ack is deactivated or the answer is the appropriate one,
        # then deactivate the special ack and return True
        self.special_ack = False
        return True
    
    def NEW_EST_receipt(self, message):
        """ Upon receipt of a NEW_EST message, 
        update the estimate vector e(t) to the value specified in the 
        message,
        set the value of v' to the statistics vector sent to the
        coordinator, and
        set the slack vector to 0.
        """
        self.cm.estimate = message.content
        self.cm.lastStatistics = self.cm.localStatistics
        self.cm.slack = [0] * len(message.content)

    def ADJ_SLK_receipt(self, message):
        """ Upon receipt of an ADJ_SLK message, add the value specified
        in the message to the value of the slack vector (δ <- δ + Δδ).
        """
        self.cm.slack = VectorOps.addTo(self.cm.slack, message.content)

    def ACK_receipt(self, ack):
        """ Upon receipt of an ACK, just make the coord_received_msg
        True.
        @param ack: the ack sent from node.
        """
        self.coord_received_msg = True
