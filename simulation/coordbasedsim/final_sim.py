#!/usr/bin/env python


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

sys.path.insert(4, '/home/blaxeep/Workspace/diploma/trunk/userinterface')
from streamhandler import *
import threading
import pdb


maxSimTime = 20
max_nodes = 4

def main():
    initialize()
    env = Environment()
    net = Network()
    nl = []
    stats = NetStats()

    for i in range(max_nodes-1):
        n = NodeClass(i, 0.2, 'coordbased', Sources(), net)
        nl.append(n)
    # declare coordinator
    c = CoordClass('coord', 0.3, 'coordbased', Sources(), net)
    nl.append(c)
    init_env(nl, env)
    init_net_list(nl, net)
    init_threading(nl, env)
    init_node_protocol(nl)
    c.node.protocol.initCoord(nl)
    activate(c, c.run())
    for ncls in nl:
        activate(ncls, ncls.run())
    simulate(until=maxSimTime)








def init_threading(nl, env):
    conditions = []
    items_list = []
    for i in range(max_nodes):
        conditions.append(threading.Condition())
        nl[i].node.condition = conditions[i]
        items_list.append([])
        nl[i].node.new_items = items_list[i]
    env.conditions = conditions
    env.items_list = items_list


def init_env(ncls, env):
    env.set_node_list(ncls)
    env.sh = StreamHandler('/home/blaxeep/Workspace/vsam/wc_day44')
    env.init_data()


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
