#!/usr/bin/env python
# -*-coding: utf-8-*-


""" This module represents the balancing process. """

from vec_ops import VectorOps
from monitoredfunctionimpl import MonitoredFunctionImpl
from random import choice

import pdb


class BalancingProcess:
    """ Balancing process. """

    def __init__(self, coord_protocol, mf):
        """ inits the balancing process. """
        # an instance of the protocol that call the balancing process
        self.coord = coord_protocol
        self.balancing_group = []
        self.not_balancing_group = []
        self.mf = mf


    def startBalancing(self, *args):
        """ Starts the balancing process.
        
        Constructs the balanced vector from the coordinator itself and
        the node that sent the REP message.
        @param *args more nodes or coord itself
        """
        assert self.balancing_group == [] and self.not_balancing_group == []
        # maybe setState here
        self.initBalancingGroups(*args)
        self.addToBalancing(*args)

    def initBalancingGroups(self, *args):
        """ initializes balancing groups.

        balancing_group should be empty, while
        not_balancing_group should be full of Balancing Elements,
        one per each node.
        """
        # init balancing group to be empty
        self.balancing_group = []
        # set not_balancing_group to contain a balancing element for
        # every node.
        for n in self.coord.NodeList:
            self.elem = self.createBalancingElement(n) #(nc.node), for nc
            self.not_balancing_group.append(self.elem)

    def checkForCoord(self, node):
        """ checks if the node is the coordinator.
        @node the node to be checked
        @return True if node is coordinator and False if it is not.
        Deprecated
        """
        if node.name == 'coord':
            return True
        else:
            return False

    def createBalancingElement(self, node):
        """ creates a balancing element from a node. 
        @node is a node instance
        @return a balancing element.
        """
        self.node_name = node.name
        self.localStatistics = node.protocol.cm.localStatistics
        self.drift = node.protocol.cm.drift
        self.weight = node.weight
        self.be = BalancingElement(self.node_name, self.localStatistics,
                                    self.drift, self.weight)
        return self.be
    
    def checkBalance(self):
        """ Checks if the balanced vector and the estimate vector form
        a monochromatic ball.

        @return is_monochromatic
        """
        pass

    def addToBalancing(self, *args):
        """ adds to balancing_group one or more elements.

        Problem is we don't know the number of elements that will be
        added to balancing_group, so we need something more dynamic.
        more info: http://docs.python.org/library/sys.html
        """
        # this is routine check in case a balancing process starts but
        # no initialization has been done.
        if not self.not_balancing_group:
            self.initBalancingGroups()
        for elem in args:
            if not self.existsInBalancingGroup(elem):
                self.e = None
                for nbg in self.not_balancing_group:
                    if nbg.node_name == elem.node_name:
                        self.e = nbg
                if self.e:
                    # if this node is not in balancing group then add it
                    self.balancing_group.append(self.e)
                    # and remove it from not balancing group
                    self.not_balancing_group.remove(self.e)
                else:
                    print "BALANCING-ERROR: elem doesn't have a group"
        # now compute the balanced vector
        self.computeBalancedVector()

    def existsInBalancingGroup(self, element):
        """ checks if the element already exists in balancing group.
        
        If element already exists, it returns True, else
            it retunrs False.
        @param element the element we want to check if it's in the bg.
        """
        for item in self.balancing_group:
            if str(item.node_name) == str(element.node_name):
                return True
        return False

    def computeBalancedVector(self):
        """ computes the balanced_vector.

        b = sum(w(i) * u(i))/sum(w(i)), where node i ε balancing_group.
        """
        # initialize a balanced vector b
        self.b = [0] * self.mf.getDimension()
        self.total_weight = 0.0
        # compute the balanced vector b
        for elem in self.balancing_group:
            self.w = elem.weight
            self.total_weight += self.w
            self.b = VectorOps.multAndAddTo(self.b, self.w, elem.drift)
        self.b = VectorOps.multBy(self.b, 1.0/self.total_weight)
        # check if ball B(e(t), b) is monochromatic (step 1 of coord)
        if self.mf.isMonochromatic(self.coord.cm.estimate, self.b):
            self.successfulBalancing(self.b)
        else:
            self.unsuccessfulBalancing()

    def successfulBalancing(self, b):
        """ Balancing is successful, so:
        for each item in the balancing group:
            1. calculate slack vector adjustment
            2. send to item an ADJ-SLK message
        exit balancing process.
        @param b is the balanced vector
        """
        pdb.set_trace()
        for elem in self.balancing_group:
            self.slack = self.calcSlackVector(elem, b)
            self.sendSlackToCoord(self.slack, elem.node_name)
        self.stopBalancing()

    def calcSlackVector(self, element, b):
        """ calculates the slack vector adjustments for a particular
        node.
        @param element is the element from the node we want to send slack.
        @param b is the balanced vector.
        @return is the slack vector for the particular node.
        """
        self.slack = VectorOps.subFrom(VectorOps.mult(b, element.weight),\
                        VectorOps.mult(element.drift, element.weight))
        return self.slack

    def sendSlackToCoord(self, slack, node_name):
        """ sends the slack vector of the particular node to coordinator.
        @param slack is the slack vector
        @param node_name is the name of the node.
        """
        # create a simple message with node_name and slack vector
        self.msg = BalancingMessage(node_name, slack)
        # and send it
        self.sendBalancingResults(self.msg)

    def unsuccessfulBalancing(self):
        """ While there are nodes in the not_balancing group, then
                select one random node
                send it a REQ message
                recompute balanced vector.
        If no nodes are remaining in the not_balancing group, then
            calculate a new estimate vector
            send a NEW_EST message to every node, and
            exit the balancing process.
        """
        pdb.set_trace()
        # if there are nodes not contained in the balancing group:
        while self.existBalancingGroup():
            # select one at random
            self.lucky_name = self.chooseRandomNode()
            # and send it a REQ-message.
            self.msg = BalancingMessage(self.lucky_name, 'REQ')
            self.sendBalancingResults(self.msg)
            # acquire the new node and add it to balancing group
            self.acquireNewNode(self.lucky_name)
            # now recalculate balanced vector b
            self.computeBalancedVector()
        # if being here, it's a total balancing failure.
        # continue recalculating global estimate
        self.stopBalancing()
        self.msg = BalancingMessage(self.lucky_name, 'FAIL')

    def existBalancingGroup(self):
        if len(self.not_balancing_group) > 0:
            return True
        return False

    def stopBalancing(self):
        """ clear balancing state.
        """
        self.balancing_group = []
        self.not_balancing_group = []

    def chooseRandomNode(self):
        """ chooses a random node from not_balancing_group so as to be
        the new member of the balancing_group.
        @return a random node id.
        """
        # choose a random element
        self.lucky_node = choice(self.not_balancing_group)
        # and return only its id
        return self.lucky_node.node_name

    def isCoord(self, node):
        """ Tests if the randomly chosen node is the coordinator.
        @return True if the chosen node is the coordinator and
                False elsewhere.
        deprecated
        """
        if str(node.node_name) == 'coord':
            return True
        else:
            return False

    def sendBalancingResults(self, message):
        """ Sends the balancing results to coordinator protocol.
        @param message is a BalancingMessage message.
        """
        self.coord.recvBalancingResults(message)

    def acquireNewNode(self, node_name):
        """ acquires a new node for the balancing group.
        This method removes the node from not_balancing_group and
        adds it to balancing_group.
        @node_name: is a string that represents the name of a node.
        """
        # boolean variable that informs us if node_name has been found
        self.found = False  
        # search in not_balancing_group and find which balancing
        # element has the same name with the node_name given as param
        for elem in self.not_balancing_group:
            if elem.node_name == node_name:
                # remove balancing element from not_balancing_group and
                self.not_balancing_group.remove(elem)
                # add it to balancing_group
                self.balancing_group.append(elem)
                self.found = True
                break
        if not self.found:
            print "This is an error in acquireNewNode()."


class BalancingElement:
    """ simulates a balancing element.

    A balancing element is consisted of:
    1. a node's name (id)
    2. its local statistics vector,
    3. its drift vector and
    4. its weight.
    """
    def __init__(self, node_name, localStatistics, drift, weight):
        """inits the balancing element. """
        self.node_name = node_name
        self.localStatistics = localStatistics
        self.drift = drift
        self.weight = float(weight)


class BalancingMessage:
    """ creates a balancing message for internal communication of the
    balancing process with the coordinator protocol.
    """
    def __init__(self, node_name, data):
        """ inits the message.

        @param node_name is the name of the node.
        @param data is the data the balancing process sends to
        coordinator protocol. It can be either a slack vector or a
        REQ - signal.
        """
        self.node_name = node_name
        self.data = data

