#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module impelements the coord protocol in the coordbased version
of the following paper:
A Geometric Approach to Monitoring Threshold Functions 
Over Distributed Data Streams
"""

# imports 
from nodeProtocol import *
import sys
import os
#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
#protocol_path = os.path.abspath('../')
protocol_path = '/storage/tuclocal/babalis/source/trunk/protocol'
sys.path.insert(0, protocol_path)
from vec_ops import VectorOps
from signals import *
from computationalmodel import ComputationalModel
from balancingprocess import *
#sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
#node_path = os.path.abspath('../../node')
node_path = '/storage/tuclocal/babalis/source/trunk/node'
sys.path.insert(1, node_path)
from node import *
from message import Message



class CoordProtocol(NodeProtocol):
    """ This class implements the protocol from coord's side. """

    def __init__(self, name, network):
        """ initializes a coordinator protocol. """
        NodeProtocol.__init__(self, name, network)
        self.COORD = name  # this node is the coord
        self.NodeList = []  # list that contains all nodes
        # dictionary that holds <node_id: [lastStats, weight]>
        self.all_vectors = {}
        # balancing necessary elements
        self.bp = BalancingProcess(self, self.mf)
        self.balancing_msgs = []
        # first thing TODO is to call set_nodelist()
    
    
    def set_nodelist(self, li):
        """ sets a list to the coord's nodelist.
        @param li is a list.
        """
        self.NodeList = li


    ## Coord initialization phase ------------------------------------

    def start_coord(self, raw_data, weight):
        """ starts the coordinator. 
        @param raw_data is the data that coord-node has to process.
        @param weight is the weight of this node.
        @param ls is a list that contains all the nodes.
        """
        # set the weight of the node to protocol
        self.set_weight(weight)
        # read all waiting, raw data and pass it to a sketch
        self._read_data(raw_data)
        # update last statistics vector to hold the localstats
        self._set_lastStatistics(self.ams.sketch)
        # update slack vector to 0
        VectorOps.init_empty_vector(self.cm.slack, \
                                    self.cm.lastStatistics)
        self.all_vectors[self.node_name] = \
                        [self.weight, self.cm.lastStatistics]
        #self.process_recvd_msg()

    def process_message(self):
        """ processes a received message. """
        # first, check if there are new messages
        while self.incoming_messages:
            self.msg = self.incoming_messages.pop(0)
            try:
                if self.msg.signal == 'INIT':
                    self.INIT_receipt(self.msg)
                    break
                elif self.msg.signal == 'REP':
                    self.REP_receipt(self.msg)
                    break
            except AttributeError:
                print 'BAD-MESSAGE: No such message is expected \
                        (in process_recv_msg)'
                return False
            # finally, a little test about acks:
            if self.msg.signal != 'ACK':
                # if message is NOT an ack, then send an ACK!
                self._send_ACK(self.node_name, self.msg.sender)


    ## INIT receipt --------------------------------------------------

    def INIT_receipt(self, message):
        """ In case a node receives an INIT-type message, it
        calculates the estimate vector and
        informs the nodes via a NEW_EST message.
        (algorithm 2 in lift[2006]).
        @param message is an INIT-message.
        """
        # set the particular node's characteristics to all_vectors
        self.all_vectors[message.sender] = [message.weight, message.content]
        # if all nodes have sent an INIT message, then
        if self.all_msgs_received():
            # calculate the estimate
            self.calc_estimate()
            # change the state of the system.
            self.set_state('SAFE')
            # create a NEW-EST message
            self.new_est = self.create_NEW_EST()
            # and broadcast new_est message
            self.sendMessage(self.new_est)
    
    def all_msgs_received(self):
        """ this method tests if all messages have been received by
        the coordinator.
        @return True if coord has received a message from every node
        and False otherwise.
        """
        # if length of nodelist-1 (-1 because of the coord) is equal
        # to length of all vectors, then continue
        self.coord_num = 1
        if len(self.NodeList) == len(self.all_vectors):
            return True
        return False

    def send_new_est(self):
        """ sends a new estimate message to all nodes."""
        # change the state of the system.
        self.set_state('SAFE')
        # create a NEW-EST message
        self.new_est = self.create_NEW_EST()
        # and broadcast new_est message
        self.sendMessage(self.new_est)

    def calc_estimate(self):
        """ calculates the estimate vector. """
        # if every node has sent its last statistics vector
        if self.all_msgs_received():
            # then, calculate estimate
            self.recalc_estimate()
        else:
            # else, print an error message
            print "Not all nodes have sent their local stats vector!"
        

    def create_NEW_EST(self):
        """ This method creates a new estimate-message and sends it to
        all nodes.
        @return message of NEW-EST-type.
        """
        # get all nodes (except coordinator)
        self.namelist = self.get_simple_nodes_name()
        # create and return a new_est message
        return NEW_EST(self.node_name, self.namelist, self.cm.estimate)

    def get_simple_nodes_name(self):
        """ gets the names of simple nodes (except coord).
        @return a list with all these names.
        """
        # init an empty list
        self.simple_namelist = []
        # add every name to the list
        for n in self.NodeList:
            self.simple_namelist.append(n.name)
        # remove coordinator's name from list and return it
        self.simple_namelist.remove(self.COORD)
        return self.simple_namelist

    def recalc_estimate(self):
        """ calculates the estimate vector. """
        # init sum of weights to the minimum permitted value
        # so as to avoid division with zero.
        self.sumw = 0.000000000001
        # for every single node:
        for node in self.all_vectors:
            # get the weight and the last statistic vector
            self.w = float(self.all_vectors[node][0])
            self.v = self.all_vectors[node][1]
            # compute the denominator
            self.sumw += self.w
            # and compute the numerator
            self.cm.estimate = VectorOps.addTo(self.cm.estimate,\
                                VectorOps.mult(self.v, self.w))
            # calculate the final estimate vector
            self.cm.estimate = VectorOps.multBy\
                                    (self.cm.estimate, 1.0/self.sumw)
            self.update_threshold(self.cm.estimate)


    ## Local data arrival --------------------------------------------

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
            # if it is not, then initiate a balancing process,
            self.coord_elem = self.createBalancingElement(self.node_name,\
                        self.cm.localStatistics, self.cm.drift, self.weight)
            # initiating the balancing group with this very element
            self.bp.addToBalancing(self.coord_elem)


    ## REP receipt ---------------------------------------------------

    def REP_receipt(self, message):
        """ REP receipt. It analyzes the message to the appropriate
        fields and sends it to rep_actions() for further analysis.
        @param message is a REP-type message.
        """
        # first of all, set the state to unsafe
        self.set_state('UNSAFE')
        # now analyze the message more
        node_name = message.sender
        node_local_stats = message.content[0]
        node_drift = message.content[1]
        # update all_vectors
        self.all_vectors[node_name][1] = node_local_stats
        # now call the rep_actions:
        self.rep_actions(node_name, node_local_stats,\
                            node_drift)

    def rep_actions(self, node_name, node_local_stats, node_drift):
        """ Upon receipt of a REP message from the node p, initiate a 
        balancing process, setting the balancing group to 
        P' = {<1, v1(t), u1(t)>, <i, vi, ui>}.
        @param node_name is the name of the node that sent the REP msg.
        @param nodelLocalStats is the local statistics of the node.
        @param nodeDrift is the drift vector of the node.
        """
        self.coord_elem = self.createBalancingElement(self.node_name,\
        self.cm.localStatistics, self.cm.drift, self.weight)
        
        self.node_elem = self.createBalancingElement(node_name,\
        node_local_stats, node_drift, self.getNodeWeight(node_name))
        self.bp.addToBalancing(self.coord_elem, self.node_elem)

    def createBalancingElement(self, name, local_stats, drift, weight):
        """ Creates a balancing element for the node given.

        @param name the name of the node
        @param local_stats the local statistics vector of the node
        @param drift the drift vector of the node
        @param weight the weight of the node.
        @return a BalancingElement which contains the params above.
        """
        assert weight, 'this msg means that weight is null'
        # create the balancing element
        elem = BalancingElement(name, local_stats, drift, weight)
        # and return it
        return elem

    def getNodeWeight(self, node_name):
        """ gets the weight of the particular node.

        @param node_name the name of the node we search for.
        @return the weight of the node.
        """
        if node_name in self.all_vectors:
            return self.all_vectors[node_name][0]
        else:
            print "BAD-DATA: No such node name exists in list"
            return None

    def recvBalancingResults(self, msg):
        """ receives the result of balancing process.
        It is either a slack vector (successful balancing), 
        or a send_req signal (unsuccessful balancing).
        @param msg is a message received from balancing process.
        """
        self.balancing_msgs.append(msg)
        # remove this line if there is a problem, added 26/11
        self.analyzeBalancingResults()

    def analyzeBalancingResults(self):
        """ reads and analyzes the messages from the balancing procedure."""
        while self.balancing_msgs:
            # extract the first message from the list
            self.msg = self.balancing_msgs.pop(0)
            if self.msg.data == 'REQ': 
                # if it's a req-message AND node_name is not the coord
                if self.msg.node_name != 'coord':
                    # create and send a req message to a random node
                    self.req_msg = self.createREQMessage(self.msg)
                    self.sendMessage(self.req_msg)
                else:
                    continue
            elif self.msg.data == 'FAIL':
                # if balancing process has failed, then
                # recompute global estimate
                self.send_new_est()
            else:
                self.manipulateADJ_SLKMessage(self.msg)

    def createREQMessage(self, message):
        """ creates a REQ message.
        @param message is a message that contains the name of the node
        @return a REQ-type message.
        """
        self.msg = REQ(self.node_name, message.node_name)
        return self.msg

    def manipulateADJ_SLKMessage(self, message):
        """ Manipulates an ADJ_SLK message.
        If recipient is coordinator, then set slack vector directly to
        it, else send and ADJ_SLK message to the appropriate node.
        @message is the message that came from balancing procedure.
        """
        # first check if recipient of this slack vector is the coordinator
        if message.node_name == 'coord':
            self.cm.slack = message.data
        else:
            # else, send a ADJ_SLK message to the node
            self.adj_slk_msg = self.createADJ_SLKMessage(self.msg)
            self.sendMessage(self.adj_slk_msg)


    def createADJ_SLKMessage(self, message):
        """ creates an ADJ_SLK message.
        @param message is a message that contains a balancing message
        (it consists of node's id and slack vector).
        @return the message to be sent.
        """
        self.msg = ADJ_SLK(self.node_name, message.node_name, message.data)
        return self.msg




