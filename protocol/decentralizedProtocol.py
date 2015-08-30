#!/usr/bin/env python
# -*-coding: utf-8-*-


""" This module represents the decentralized protocol implementation. """

# imports
from computationalmodel import ComputationalModel
from protocol import Protocol
from monitoredfunctionimpl import MonitoredFunctionImpl
import sys
sys.path.insert(0,'/home/blaxeep/Workspace/diploma/trunk/simulation')
sys.path.append('/home/blaxeep/Workspace/diploma/trunk/node')
from message import Message
from vec_ops import VectorOps

import pdb  # Debugging purposes CLEANUP


class NodeProtocol(Protocol):
    """ This class implements the protocol from node's side. """

    def __init__(self, name, network):
        """ kind of constructor for node protocol. """
        self.cm = ComputationalModel()
        self.node_name = name
        self.network = network
        self.all_vectors = {}   # dictionary: <node_id:vector> pairs
        self.incoming_messages = [] # a list of all incoming messages
        # the list of all nodeclass instances (each contains a node)
        self.NodeList = [] 
        # state of the node TODO it can be completely removed
        self.state = None   
        self.mf = MonitoredFunctionImpl()   # TODO must be given by user


    ## API ------------------------------------------------------------
    
    def sendMessage(self, msg):
        """ sends a message to appropriate node. """
        # call environment function here
        self.network.addMsgToQueue(msg)

    def bcastStatVector(self, vector):
        """ Broadcasts the initial statistics vector to the other nodes. """
        # create a list with all id's
        self.id_list = self.getAllNodesId(self.NodeList)
        # create the message with the list of nodes as recipients
        self.msg = self.createMessage(vector, self.id_list)
        # and send it
        self.sendMessage(self.msg)

    def recvMessage(self, msg):
        """ receives a message. """
        self.incoming_messages.append(msg)

    def set_state(self, state):
        """ sets the state of the system. """
        self.state = state

    ## Gather new data, check, and send -------------------------------

    def getDataFromNode(self):
        """ gets data from node and returns it"""
        self.my_node = self.getMyNode()
        self.data = self.my_node.gatherData()
        return self.data

    def getMyNode(self):
        """ returns the node where this instance of protocol runs. """
        #self.my_node = [item for item in self.NodeList \
        #                        if item.node.name == self.node_name][0]
        #return self.my_node.node
        self.my_node = None
        for item in self.NodeList:
            if item.node.name == self.node_name:
                self.my_node = item.node
                return self.my_node
        return self.my_node

    def createMessage(self, content, recp):
        """ creates a message for sending """
        self.new_msg = Message(self.node_name, recp, content)
        return self.new_msg

    ## Initialization phase of protocol -------------------------------


    def getAllNodesId(self, nl):
        """ returns a list with the id's of all nodes. """
        # init an empty list
        self.id_list = []
        # for every node, take the id and append it to list
        for node_class in nl:
            self.id_list.append(node_class.node.name)
        return self.id_list

    def recvStatVector(self, vector):
        """ receives the local statistics vector from other nodes. """
        self.vector = vector
        return vector

    def updateStatVector(self, node_id, vector):
        """ updates the local statistics vector from other nodes. """
        if node_id in self.all_vectors:
            self.all_vectors[node_id][1] = vector
        else:
            print "Error here! This id doesn't exist in all_vectors list!" 

    def calcEstimate(self):
        """ calculates estimate vector for first time. """
        # while there is a message in incoming_messages list, 
        while self.incoming_messages:
            # remove it from list
            self.msg = self.incoming_messages.pop(0)
            # process the message and extract the id and the vector
            self.nodeID, self.vec = self.processMessage(self.msg)
            # process it and add it to all_vectors dictionary
            self.updateStatVector(self.nodeID, self.vec)
        # now calculate estimate vector for this node
        self.recalcEstimateVector()

    def recalcEstimateVector(self):
        """ calculates the estimate vector. """
        # init sum of weights in the minimum permitted value
        # (so as to avoid division with zero)
        self.sumw = 0.000000000001
        # for every single node
        for node in self.all_vectors:
            # get the weight and the last statistic vector
            self.w = float(self.all_vectors[node][0])
            self.v = self.all_vectors[node][1]
            # compute the denominator
            self.sumw += self.w
            # and compute the numerator
            self.cm.estimate = VectorOps.addTo(self.cm.estimate, 
                    VectorOps.mult(self.v, self.w))
        # calculate the final estimate vector
        self.cm.estimate = VectorOps.multBy\
                                (self.cm.estimate, 1.0/self.sumw)

    def calcDriftVector(self):
        """ calculates drift vector. 
        
        Drift vector is the following vector:
            u(t)  = e(t) + Δv(t), where
            Δv(t) = v(t) - v'(t)
        """
        # calculate Δv(t)
        self.dv = VectorOps.subFrom(self.cm.localStatistics, \
                                    self.cm.lastStatistics)
        # calculate drift vector
        self.cm.drift = VectorOps.addTo(self.cm.estimate,\
                                    self.dv)

    def recalcLocalStatistics(self, new_vector):
        """ recalculates local statistics vector. """
        self.cm.localStatistics = new_vector

    def processMessage(self, msg):
        """ processes a message.
        This function takes the node's id from the message and the 
        data (different approach if this is a signal or a vector)
        """
        # first, learn who the sender is
        self.node_id = msg.sender
        # check if this is a vector or a signal
        if self.isSignal(msg.content) == False:
            # if it's a vector, then receive the vector
            self.vector = self.recvStatVector(msg.content)
            # and return both node_id and vector
            # so as to process the node's data
            return (self.node_id, self.vector)

    def isSignal(self, content):
        """ checks if the content is a known signal or data. """
        if content == 'SKATILA':
            return True
        else:
            return False


    ## Following functions are called top-level

    def initProtocol(self, node_list):
        """ inits the protocol and the very basic variables and vectors.
        @param node_list is the list that contains all nodes. 
        """
        self.setNodeList(node_list)
        self.initAllVectorsList()

    def setNodeList(self, nl):
        """ sets the list of all nodes """ 
        #for item in nl:
        #    self.NodeList.append(item.node)
        self.NodeList = nl

    def initAllVectorsList(self):
        """ inits the all_vectors vector with node id and weight. """ 
        for nc in self.NodeList:
            self.all_vectors[nc.node.name] = [nc.node.getWeight(), []]

    ## Initialization -------------------------------------------------

    def initialization(self):
        """ runs the initialization of the protocol. """
        # get data from the environment
        self.data_vector = self.getDataFromNode()
        # assign the data to local statistics vector
        self.cm.localStatistics = self.data_vector
        #  and broadcast the vector
        self.bcastStatVector(self.data_vector)

    ## Adjustment messages TODO Fill in some code here ----------------

    ## Processing Stage -----------------------------------------------

    def recvLocalUpdate(self, local_stats_vec):
        """ receives a new local statistics vector from stream. """
        # recalculate local statistics vector
        self.recalcLocalStatistics(local_stats_vec)
        # recalculate drift vector
        self.calcDriftVector()
        # check if the ball remains monochromatic and
        # send a message to all if necessary
        self.checkBall(local_stats_vec)

    def recvNewMessage(self):
        """ receives a new message. """
        while self.incoming_messages:
            # take the new message
            self.msg = self.incoming_messages.pop(0)
            # process the message and extract the id and the vector
            self.nodeID, self.vec = self.processMessage(self.msg)
            # update this node's last statistics vector to hold the new one
            self.updateStatVector(self.nodeID, self.vec)
            # recalculate estimate vector e(t)
            self.recalcEstimateVector()
            # check if the ball is monochromatic and
            # send a message with the local statistics vector to all nodes,
            # if necessary
            self.checkBall(self.cm.localStatistics)

    def checkBall(self, local_stats_vec):
        """ checks if the ball remains monochromatic. """
        if not self.mf.isMonochromatic(self.cm.estimate, self.cm.drift):
            self.cm.lastStatistics = local_stats_vec

    def dontSend(self):
        """ returns true or false, depending on isMonochromatic answer.
        if it's true, then send message else not."""
        return self.mf.isMonochromatic(self.cm.estimate, self.cm.drift)

def DEBUG(param, msg=''):
    """ Prints the param. """
    print msg + str(param)

