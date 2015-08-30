#!/usr/bin/env python
# -*-coding: utf-8-*-

class Protocol:
    """ Implements a protocol interface """

    def sendMessage(self, msg):
        raise NotImplementedError

    #def mcastMsg(self, msg):
    #    raise NotImplementedError

    def bcastStatVector(self, vector):
        raise NotImplementedError

    def recvMessage(self, msg):
        raise NotImplementedError
