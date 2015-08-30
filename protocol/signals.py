#!/usr/bin/env python
# -*-coding: utf-8-*-

""" This module contains some signals for coordinator-based protocol
implementation as it is described in 
'A geometric approach to monitoring threshold functions over
distributed data streams' paper.
"""

# imports
import sys
#sys.path.insert(0, '/home/blaxeep/Workspace/diploma/trunk/node')
import os
node_path = os.path.abspath('../node')
sys.path.insert(0, node_path)
from message import Message


class INIT(Message):
    """ Used by nodes to report their initial statistics vector to the
    coordinator in the initialization stage.
    """

    def __init__(self, node_name, coord, init_stats, weight):
        Message.__init__(self, node_name, coord, init_stats)
        self.signal = 'INIT'
        self.weight = weight


class REQ(Message):
    """ Used by the coordinator during the balancing process to request
    that a node send its statistics vector and drift vector.
    """

    def __init__(self, coord, node_name):
        """ initializes the REQ message. """
        Message.__init__(self, coord, node_name)
        self.signal = 'REQ'


class NEW_EST(Message):
    """ Used by coordinator to report the new estimate vector to the
    nodes.
    """

    def __init__(self, coord, nodeList, estimate):
        """ initializes the new special message."""
        # create the message
        Message.__init__(self, coord, nodeList, estimate)
        # then, set the signal
        self.signal = 'NEW_EST'


class REP(Message):
    """ Used by nodes to report information to the coordinator when a
    local constraint has been violated, or when the coordinator
    requests information from the node.
    """

    def __init__(self, node_name, coord, local_stats, drift):
        """ initializes a REP message. """
        # create the message. Content contains two vectors here
        Message.__init__(self, node_name, coord, (local_stats, drift))
        # and set the signal to REP (so as coord treat it properly)
        self.signal = 'REP'


class ADJ_SLK(Message):
    """ Used by the coordinator to report slack vector adjustments to 
    nodes after a successful balancing process.
    """

    def __init__(self, coord, node_name, slack):
        """ initializes an ADJ_SLK message. """
        # create the message
        Message.__init__(self, coord, node_name, slack)
        # set the signal
        self.signal = 'ADJ_SLK'


class ACK(Message):
    """ Used by the coordinator to assure a node that the message the
    node has been sent, is delivered.
    """

    def __init__(self, sender, recipient):
        """initializes an ACK message. """
        # create an empty message
        Message.__init__(self, sender, recipient, [])
        # set the signal
        self.signal = 'ACK'

