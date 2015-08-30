#!/usr/bin/env python
# -*-coding: utf-8-*-

from vec_ops import VectorOps
from monitoredfunctionimpl import MonitoredFunctionImpl
from random import choice
from SimPy.Simulation import *

import pdb


class BalancingProcess:
    """ Balancing process. """

    def __init__(self, coord_protocol, mf):
        """ inits balancing process
        @mf is monitoredfunction.
        """
        self.coord = coord_protocol
        self.balancing_group = []
        self.not_balancing_group = []
        self.mf = mf
        self.balance_mon = Monitor()
        #self.balance_mon.observe(0)


    def startBalancing(self, *args):
        """ starts a balancing process.
        @param *args is either one balancing element or many.
        """
        assert len(self.not_balancing_group) < 1\
            and len(self.balancing_group) < 1,\
             "wrong in startBalancing"
        self.balance_mon.observe(1.0)
        # add to not balancing group all nodes
        for n in self.coord.NodeList:
            self.not_balancing_group.append(BalancingElement(n.name))
        # and remove the incoming ones
        for elem in args:
            self.check_group(elem, self.not_balancing_group)
            #self.balancing_group.append(elem)
            self.add_to_balancing_group(elem)
        # now check the balance that form the nodes in balancing
        # group only
        self.check_balance()

    def check_balance(self):
        """ checks if the ball is monochromatic.
        @return True if the ball is monochromatic, False otherwise.
        """
        self.b = self.compute_balanced_vec()
        if self.mf.isMonochromatic(self.coord.cm.estimate, self.b):
            self.success(self.b)
        else:
            self.fail()

    def compute_balanced_vec(self):
        """ computes the balanced vector from the elements that are
        contained in balancing group only.
        @return the balanced vector
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
        return self.b

    def success(self, balanced):
        """ actions taken in case of a successful balancing process.
        @param balanced is the balanced vector
        """
        # for each item in balancing group:
        #   send an ADJ-SLK message with its data
        #   and terminate balancing process
        for elem in self.balancing_group:
            self.slack = self.calcSlackVector(elem, balanced)
            self.msg = BalancingMessage(elem.node_name, self.slack)
            self.sendBalancingResults(self.msg)
        self.stop_balancing()

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

    def sendBalancingResults(self, message):
        """ Sends the balancing results to coordinator protocol.
        @param message is a BalancingMessage message.
        """
        self.coord.recvBalancingResults(message)

    def fail(self):
        """ if no balancing achieved, then try again!"""
        # dum spiro spero
        if self.nbg_exists():
            # select a new node to participate in balancing process
            self.candidate = self.chooseRandomNode()
            # and send its name to node, so as to notify it.
            self.msg = BalancingMessage(self.candidate, 'REQ')
            #pdb.set_trace()
            self.sendBalancingResults(self.msg)
        else:
            # if no more nodes remain into not balancing, group, then
            # send an appropriate message to node so as to recompute
            # estimate.
            self.msg = BalancingMessage(self.coord.node_name, 'FAIL')
            self.stop_balancing()
            self.sendBalancingResults(self.msg)

    def nbg_exists(self):
        """ checks if not balancing group has more elements or not.
        @return True if even a sinlge element exists in nbg and
        False otherwise.
        """
        if len(self.not_balancing_group) > 0:
            return True
        else:
            return False

    def chooseRandomNode(self):
        """ chooses a random node from not_balancing_group so as to be
        the new member of the balancing_group.
        @return a random node id.
        """
        # choose a random element
        self.lucky_node = choice(self.not_balancing_group)
        # and return only its id
        return self.lucky_node.node_name

    def stop_balancing(self):
        """ stops a balancing process. """
        self.not_balancing_group = []
        self.balancing_group = []
        self.balance_mon.observe(0.0)

    def addToBalancing(self, *args):
        """ adds one (or more) node(s) to balancing process.
        @param *args is(are) the new node(s).
        """
        if len(self.balancing_group) < 1 and\
            len(self.not_balancing_group) < 1:
                self.startBalancing(*args)
        else:
            for elem in args:
                self.add_to_balancing_group(elem)
                self.check_group(elem, self.not_balancing_group)
            # we are here because we need to continue with the
            # balancing process.
            self.check_balance()

    def check_group(self, elem, group):
        """ checks if an element exists into the not balancing group.
        @param elem is the element to check.
        """
        for ge in group:
            if elem.node_name == ge.node_name:
                group.remove(ge)
                break

    def add_to_balancing_group(self, elem):
        exists = False
        for be in self.balancing_group:
            if be.node_name == elem.node_name:
                exists = True
        if not exists:
            self.balancing_group.append(elem)



## Classes that help balancing procedure -----------------------------

class BalancingElement:
    """ simulates a balancing element.

    A balancing element is consisted of:
    1. a node's name (id)
    2. its local statistics vector,
    3. its drift vector and
    4. its weight.
    """
    def __init__(self, node_name, localStatistics='', drift='', weight=''):
        """inits the balancing element. """
        self.node_name = node_name
        self.localStatistics = localStatistics
        self.drift = drift
        self.assign_weight(weight)

    def assign_weight(self, weight):
        if weight:
            self.weight = float(weight)
        else:
            self.weight = ''


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

