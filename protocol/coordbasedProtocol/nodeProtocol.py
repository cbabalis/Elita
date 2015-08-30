#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module impelements the node protocol in the coordbased version
of the following paper:
A Geometric Approach to Monitoring Threshold Functions 
Over Distributed Data Streams
"""


#from nodeprotocol import *
from SimPy.Simulation import *
import sys
import os
#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
#protocol_path = os.path.abspath('../trunk/protocol')
protocol_path = '/storage/tuclocal/babalis/source/trunk/protocol'
sys.path.insert(0, protocol_path)
from vec_ops import VectorOps
from signals import *
from computationalmodel import ComputationalModel
from protocol import Protocol
from monitoredfunctionimpl import MonitoredFunctionImpl
#sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
node_path = '/storage/tuclocal/babalis/source/trunk/node'
sys.path.insert(1, node_path)
from node import *
from message import Message
#sys.path.append('/home/blaxeep/Workspace/diploma/trunk/data')
#data_path = os.path.abspath('../trunk/data')
data_path = '/storage/tuclocal/babalis/source/trunk/data'
sys.path.insert(2, data_path)
from ams import *

import pdb


class NodeProtocol(Protocol):
    """ This class implements the protocol from node's side. """

    def __init__(self, name, network):
        """ kind of constructor for node protocol. """
        self.cm = ComputationalModel()
        self.ams = AMS_Sketch()
        self.node_name = name
        self.network = network
        self.incoming_messages = [] # a list of all incoming messages
        self.COORD = None # coordinator's name
        self.weight = None
        self.ack = True    # ack for a successful message sending
        # state of the node
        self.state = 'INIT'
        # bit of hardcoded
        self.mf = MonitoredFunctionImpl(len(self.ams.sketch))
        self.state_mon = Monitor()
        #self.state_mon.observe(0)


    ## API ------------------------------------------------------------
    
    def sendMessage(self, msg):
        """ sends a message to appropriate node. """
        # call environment function here
        self.network.addMsgToQueue(msg)
        # and wait for an acknowledgement
        self._set_ack(False)

    def bcastStatVector(self, vector):
        """ Broadcasts the initial statistics vector to the other 
        nodes. """
        # create a list with all id's
        self.id_list = self.getAllNodesId(self.NodeList)
        # create the message with the list of nodes as recipients
        self.msg = self.createMessage(vector, self.id_list)
        # and send it
        self.sendMessage(self.msg)

    def recvMessage(self, msg):
        """ receives a message. """
        if not self.is_ack(msg):
            self.incoming_messages.append(msg)
            self.process_message()
    
    def is_ack(self, msg):
        """ checks if the msg is an ack.
        @param msg is the message.
        """
        # if the message has attribute signal and it is ACK
        if hasattr(msg, 'signal'):
            if msg.signal == 'ACK':
                # set ack=True and return True
                self._set_ack(True)
                return True
        # else return False
        return False

    def set_state(self, state):
        """ sets the state of the system. """
        self.state = state
        if self.state == 'SAFE':
            self.state_mon.observe(1.0)
        else:
            self.state_mon.observe(0.0)
        #self.state_mon.observe(self.state)

    def set_coord(self, coord_name):
        """ sets the coord. """
        self.coord = coord_name

    def set_weight(self, weight):
        """ sets the weight of a node. """
        self.weight = weight


    ## Initialization of the protocol --------------------------------

    def start(self, raw_data, weight):
        """ starts the protocol. Initialization phase of the 
        coordinator-based algorithm is implemented, exactly as it is
        presented in the paper [lift2006].
        @param raw_data is a list that contains items of unprocessed
        data.
        """
        # first of all, set the weight of the node to protocol
        self.set_weight(weight)
        # read all waiting, raw data and pass it to a sketch
        self._read_data(raw_data)
        # update last statistics vector to hold the localstats
        self._set_lastStatistics(self.ams.sketch)
        # update slack vector to 0
        VectorOps.init_empty_vector(self.cm.slack, \
                                    self.cm.lastStatistics)
        # create an init message
        self.init_msg = self.create_init_msg()
        # send an 'INIT'-type message to coordinator
        self.sendMessage(self.init_msg)
        # finally set change state
        self.set_state('UNSAFE')

    def create_init_msg(self):
        """ creates and returns an 'INIT'-type message. """
        assert self.COORD, "no coordinator has been defined!"
        self.init_msg = INIT(self.node_name, self.COORD,
                            self.cm.lastStatistics, self.weight)
        return self.init_msg


    ## Local arrival (1st phase of processing stage) -----------------

    def recv_local_update(self, raw_data):
        """ receives a new local statistics vector and processes it.
        @param localStats is a local statistics vector
        """
        # read the waiting, raw data and update local statistics
        self._read_data(raw_data)
        # recalculate drift vector
        self.calc_drift()

    def calc_drift(self):
        """ calculates drift vector.
        Drift vector is computed as follows:
            u(t) = e(t) + delta-v(t), where
                delta-v(t) = v(t) = v'(t)
        """
        # calculate delta-v
        self.dv = VectorOps.subFrom(self.cm.localStatistics,\
                                    self.cm.lastStatistics)
        # calculate drift vector
        self.cm.drift = VectorOps.addTo(self.cm.estimate, self.dv)
        # now check if ball is monochromatic
        if not self.check_ball(self.cm.localStatistics):
        # if it is not, then send a REP-message to coordinator
        # (the algorithm here is exactly the same as in REQ_receipt())
            self.REQ_receipt()


    def check_ball(self, localStats):
        """ checks if the ball is monochromatic.
        If it is not, then update lastStatistics with localStatistics
        vector and return False. Else, return True.
        @param localStats is the local statistics vector.
        """
        if not self.mf.isMonochromatic(self.cm.estimate, self.cm.drift):
            self.cm.lastStatistics = localStats
            return False
        return True

    def REQ_receipt(self):
        """ Upon receipt of a REQ message, send a REP(v(t), u(t))
        message to the coordinator and wait for either a NEW_EST or an
        ADJ_SLK message.
        """
        # set the state to unsafe
        self.set_state('UNSAFE')
        # calculate drift vector
        #self.calc_drift()
        # create a REP message
        self.msg = REP(self.node_name, self.COORD,\
                    self.cm.localStatistics, self.cm.drift)
        # and send it
        self.sendMessage(self.msg)
        #self.waitSpecialAck() # TODO Implement this


    ## New message process -------------------------------------------

    def process_message(self):
        """ processes a new message. """
        while self.incoming_messages:
            # extract the new message
            self.msg = self.incoming_messages.pop(0)
            # and examine the different signal types
            if self.msg.signal == 'REQ':
                self.REQ_receipt()
                break
            elif self.msg.signal == 'NEW_EST':
                self.NEW_EST_receipt(self.msg)
                break
            elif self.msg.signal == 'ADJ_SLK':
                self.ADJ_SLK.receipt(self.msg)
                break
            elif self.msg.signal == 'ACK':
                self._set_ack(True)
                break
            else:
                print 'Message error: No such message(nodeprotocol)'
            # finally, a little test about acks:
            if self.msg.signal != 'ACK':
                # if message is NOT an ack, then send an ACK!
                self._send_ACK(self.node_name, self.COORD)

    def NEW_EST_receipt(self, message):
        """ Upon receipt of a NEW_EST message, 
        update the estimate vector e(t) to the value specified in the 
        message,
        set the value of v' to the statistics vector sent to the
        coordinator, and
        set the slack vector to 0.
        """
        # first of all set state
        self.set_state('SAFE')
        self.cm.estimate = message.content
        self.update_threshold(message.content)
        self.cm.lastStatistics = self.cm.localStatistics
        self.cm.slack = [0] * len(message.content)

    def update_threshold(self, threshold):
        """ updates the threshold according to the received message and
        to the already existed threshold.
        @param threshold is the new threshold.
        """
        self.mf.set_threshold(self.cm.estimate)

    def ADJ_SLK_receipt(self, message):
        """ Upon receipt of an ADJ_SLK message, add the value specified
        in the message to the value of the slack vector (δ <- δ + Δδ).
        """
        self.cm.slack = VectorOps.addTo(self.cm.slack, message.content)
        self.set_state('SAFE')


    ## functions used in wide range ----------------------------------

    def _read_data(self, raw_data):
        """ reads data from a list, until the list is empty.
        @param raw_data is a list full of data.
        """
        # read all new data and add it to sketch
        while raw_data:
            self.data = raw_data.pop(0)
            self.ams.update(self.data)
        # update local, last and slack statistics vectors
        self.cm.localStatistics = self.ams.sketch

    def _set_lastStatistics(self, vec):
        """ sets the last staticics vector.
        @param vec is the vector to which lastStats vector will be
        updated.
        """
        self.cm.lastStatistics = vec

    def _set_ack(self, ack=True):
        """ sets the ack True or False, depending on whether an ACK
        has been received or not.
        @param ack is the ACKNOWLEDGEMENT.
        """
        self.ack = ack

    def wait_ack(self):
        """ this method checks if an ack has come.
        @return True if we wait for an ack and false otherwise.
        """
        if not self.ack:
            return False
        return True

    def _send_ACK(self, sender='', recipient=''):
        """ sends an ACKNOWLEDGEMENT signal.
        @param node_name is the name of the node that sends the ACK
        @param recipient is the name of the node to which the ACK is
        sent.
        """
        # create an ACK message
        self.ack_msg = ACK(sender, recipient)
        # be sure that sender AND recipient do exist
        assert self.ack_msg.sender and self.ack_msg.recipient,\
                "no ack_msg.sender or recipient exist (_send_ACK())"
        # and send the ACK
        self.sendMessage(self.ack_msg)




