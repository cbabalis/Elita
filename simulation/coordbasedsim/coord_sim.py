#!/usr/bin/env python

""" simulates a coordinator-based algorithm. """

from SimPy.Simulation import *
#from SimPy.SimulationTrace import *
import sys
sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
sys.path.insert(1, '/home/blaxeep/Workspace/diploma/trunk/simulation')
from network import Network, NetStats
from environment import Environment
from sources import Sources
from node import Node#, NodeClass

sys.path.insert(2, '/home/blaxeep/Workspace/diploma/trunk/protocol')
from protocol import Protocol
from decentralizedProtocol import NodeProtocol
from message import Message
from ordinarynodeprotocol import OrdinaryNodeProtocol
from coordprotocol import CoordinatorProcess

sys.path.insert(3, '/home/blaxeep/Workspace/diploma/trunk/simulation/coordbasedsim')
from nodecoordclass import NodeClass
from coordclass import CoordClass
import pdb


maxSimTime = 20
max_nodes = 5

def main():
    initialize()
    env = Environment()
    net = Network()
    nl = []
    # an instance that contains network stats
    stats = NetStats()

    for i in range(max_nodes-1):
        n = NodeClass(i, 0.2, 'coordbased', Sources(), net)
        nl.append(n)
    # declare coordinator
    c = CoordClass('coord', 0.3, 'coordbased', Sources(), net)
    # populate network with nodes
    nl.append(c)
    init_net_list(nl, net)
    init_node_protocol(nl)
    c.node.protocol.initCoord(nl)
    #activate(net, net.run())
    print "coord has been started"
    activate(c, c.run())
    print "coord ok, now initializing nodes"
    for ncls in nl:
        #initPhase(ncls.node)
        activate(ncls, ncls.run())
    # manual import of net's message queue to coord
    #c.node.protocol.incoming_messages = net.MSG_QUEUE
    # c.node.protocol.processRecvdMessage()
    simulate(until=maxSimTime)
    pdb.set_trace()



def init_net_list(nl, net):
    """ sets a NODE's list (not nodeclass list) to network. """
    li = []
    for nc in nl:
        li.append(nc.node)
    net.setNodeList(li)


def init_node_protocol(nl):
    """ inits the nodes so as to run the protocol. """
    # set coord to every node
    for nc in nl:
        nc.node.protocol.initProtocol(nl)
        if nc.node.name != 'coord':
            nc.node.protocol.assignCoord('coord')
            nc.node.protocol.initialization()

def initPhase(node):
    """ initializes the protocol from nodes' perspective.
    @node is the current node
    """
    if node.name == 'coord':
        return
    # check if COORD exists for sure
    assert node.protocol.COORD
    # init the protocol by sending the init message
    node.protocol.initialization()



if __name__ == '__main__':
    main()
