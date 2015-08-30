#!/usr/bin/env python

# simulation libs
from SimPy.Simulation import *
# import random
import sys
from network import Network
from environment import Environment

#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
# import from node module
from sources import Sources
from node import Node, NodeClass
from message import Message

#sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from protocol import Protocol
from decentralizedProtocol import NodeProtocol

from pprint import pprint

import pdb  # Debugging purposes


maxSimTime = 10
max_nodes = 5

def main():
    initialize()
    env = Environment()
    net = Network()
    nl = []

    for i in range(max_nodes):
        n = NodeClass(i, '0.2', 'decentralized', Sources(), net)
        nl.append(n)
    # populate network with nodes
    init_net_list(nl, net)
    #init protocol
    init_protocol_requirements(nl)
    init_protocol_phase(nl, net)
    print_results(nl)
    # activate(net, net.run())
    # for i, ncls in zip(range(len(nl)), nl):
    for ncls in nl:
        activate(ncls, ncls.run())
    activate(net, net.run())
    simulate(until=maxSimTime)


## FUNCTIONS ---------------------------------------------


def init_protocol_requirements(nl):
    """ inits the protocol requirements of each node.
    passes the list, common to every node and such.
    """
    for nc in nl:
        nc.node.protocol.initProtocol(nl)

def init_protocol_phase(nl, net):
    """ runs the protocol and all its phases. """
    # first of all initialize the nodes. each node should gather data and
    # transmit it to other nodes through network.
    for nc in nl:
        nc.node.protocol.initialization()
    # now network sends back the messages
    while net.MSG_QUEUE:
        net.mcastMsg(net.extractMsgFromQueue())
    # finally, each node should calculate its estimate
    for nc in nl:
        nc.node.protocol.calcEstimate()

def gather_new_data(nl, net):
    """ when new data is gathered: """
    # each node gathers new data and sends it to net if necessary
    for nc in nl:
        d = nc.node.gatherData()
        nc.node.protocol.recvLocalUpdate(d)
    while net.MSG_QUEUE:
        net.mcastMsg(net.extractMsgFromQueue())
    for nc in nl:
        nc.node.protocol.recvNewMessage()



## Helpful functions --------------------------------------------------

def init_net_list(nl, net):
    """ sets a NODE's list (not nodeclass list) to network. """
    li = []
    for nc in nl:
        li.append(nc.node)
    net.setNodeList(li)


## Irrelevant functions -----------------------------------------------

def print_msg(msg):
    print msg

def print_results(nl):
    for nc in nl:
        print 'estimate vector is ' + str(nc.node.protocol.cm.estimate)




if __name__ == '__main__':
    main()
