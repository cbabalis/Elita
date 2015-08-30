#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module represents the decentralized coordinator """

from ordinarynodeprotocol import OrdinaryNodeProtocol
from decentralizedProtocol import *
from computationalmodel import ComputationalModel
from vec_ops import VectorOps
from balancingprocess import BalancingProcess, \
BalancingElement, BalancingMessage
from monitoredfunctionimpl import MonitoredFunctionImpl
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from signals import *

import pdb


class CoordinatorProcess(OrdinaryNodeProtocol):
    """ Represents the coordinator process """

    def __init__(self, node_name, network):
        """ inits the coordinator. """
        self.node_name = node_name
        self.network = network
        self.cm = ComputationalModel()
        self.all_vectors = {}
        self.incoming_messages = []
        # initialize the balancing process with the coordinatorProcess
        self.bp = BalancingProcess(self)
        # a list containing messages with results from balancing process
        self.balancing_msgs = []
        self.weight = 0 # weight for coord, too
        self.mf = MonitoredFunctionImpl()
        self.NodeList = []


    ## Coordinator initialization -------------------------------------

    def initCoord(self, nl):
        """ initializes the coordinator with all the nodes etc. 
        @param nl: Node list consisted of NodeClass instances
        """
        self.initProtocol(nl)
        self.weight = self.getWeight()

    def getWeight(self):
        """ gets the weight of the coord"""
        if self.all_vectors.has_key(self.node_name):
            return self.all_vectors[self.node_name][0]
        else:
            print "can't get the coord's weight! can't find coord"

    def processRecvdMessage(self):
        """ processes a received message. """
        # first check if there are new messages
        while self.incoming_messages:
            # remove a message from the list
            self.msg = self.incoming_messages.pop(0)
            try:
                if self.msg.signal == 'INIT':
                    self.INIT_receipt(self.msg)
                elif self.msg.signal == 'REP':
                    self.REP_receipt()
            except AttributeError:
                print "BAD-MESSAGE: No such message is expected"
                return False
            else:
                print "BAD-MESSAGE:no such message exists."
    
    def INIT_receipt(self, message):
        """ In case a node receives an INIT-type message, it
        calculates the estimate vector and
        informs the nodes via a NEW_EST message.
        """
        # set the particular node to all_vectors
        self.all_vectors[message.sender] = [message.weight, message.content]
        # if all nodes have sent a INIT message, then
        if self.allMessagesReceived():
            # calculate the estimate
            self.calcEstimate()
            # create a NEW-EST message
            self.new_est = self.createNEW_EST()
            # and broadcast new_est message
            self.sendMessage(self.new_est)

    def allMessagesReceived(self):
        """ this method tests if all messages have been received by
        the coordinator.
        @return True if every node has sent a message and False otherwise.
        """
        if len(self.NodeList) == len(self.all_vectors):
            return True
        else:
            return False

    def createNEW_EST(self):
        """ This method creates a new estimate-message and sends it to 
        all nodes.
        @return message of NEW_EST type.
        """
        # get all nodes (except coordinator)
        self.id_list = self.getAllNodesID()
        # create a new_est message
        self.msg = NEW_EST(self.node_name, self.id_list, self.cm.estimate)
        return self.msg

    def getAllNodesID(self):
        """ this method returns all nodes' ids except this of coord"""
        # create a list of all node's ids:
        self.id_list = self.getAllNodesId(self.NodeList)
        # but remove coordinator (it's itself)
        self.id_list.remove('coord')
        return self.id_list

    def calcEstimate(self):
        """ calculates the estimate vector. """
        # be sure that every node has sent its local statistics vector
        if self.allMessagesReceived():
            self.recalcEstimateVector() # inherited from NodeProtocol
        else:
            print "Not all nodes have sent their local stats vector!"

    def coordCalcDriftVector(self, coord, node):
        """ calculates the drift vector for each node.
        @coord is the coordinator
        @node is the node we want to calculate its drift vector
        """
        # TODO continue here

    
    ## Processing stage at coordinator --------------------------------

    def localDataArrival(self):
        """ receives local data. """
        self.data = self.getDataFromNode()
        return self.data

    def localDataProcess(self, data):
        """ Upon arrival of new data on the local stream, recalculate
        v1(t) and u1(t) and check if B(e(t), u1(t)) remains
        monochromatic. If not, initiate a balancing process, setting
        the balancing group to P' = {<1, v1(t), u1(t)>}
        """
        self.recvLocalUpdate(data)
        if not self.dontSend():
            # set the balance group
            self.coord_elem = self.createBalancingElement(self.node_name,\
                    self.cm.localStatistics, self.cm.drift, self.weight)
            # and initiate a balancing process
            self.bp.startBalancing(self.coord_elem)

    def REP_receipt(self, node_name, node_local_stats, node_drift):
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




