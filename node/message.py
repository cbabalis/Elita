#!/usr/bin/env python
# -*-coding: utf-8-*-


import pdb

class Message:
    """ Represents a message.

    A message should contain:
        (a) the content to be sent
        (b) the sender
        (c) the recipient
        (d) the size of message, in bytes.
    """

    def __init__(self, sender='', recipient='', content=''):
        """ Inits a message """
        # in case sender and recipient are not strings, then convert it
        self.sender = str(sender)
        self.recipient = self._assign_recipient(recipient)
        self.content = content
        self.size = self.computeMsgSize()

    def _assign_recipient(self, recipient):
        """ this method assigns the recipient to the recipient variable
        @recipient is a list or a string.
        @return a list if recipient is list or a string if it is not.
        """
        if type(recipient) is list:
            return recipient
        else:
            return str(recipient)

    def _set_sender(self, sender):
        """ sets the sender """
        self.sender = sender

    def _get_sender(self):
        """ returns the sender """
        return self.sender

    def _set_recipient(self, recipient):
        """ sets the recipient """
        self.recipient = recipient

    def _get_recipient(self):
        """ gets the recipient """
        return self.recipient

    def _set_content(self, content):
        """ sets content """
        self.content = content

    def _get_content(self):
        """ gets content """
        return self.content

    def computeMsgSize(self):
        """ computes message size. """
        try:
            size = len(self._get_sender()) + \
                        len(self._get_recipient()) + \
                        len(self._get_content())
            return size
        except KeyError:
            print 'No size for message, unfortunately'
            return 0

    def isEmpty(self):
        """ checks if message is empty. """
        return False if self.computeMsgSize() != 0 else True

    def isSender(self):
        """ checks if there is any sender or left blank. """
        return True if self._get_sender() else False

    def isRecipient(self):
        """ checks if there is any recipient or left blank. """
        return True if self._get_recipient() else False

    def isContent(self):
        """ checks if there is any content or left blank. """
        return True if self._get_content() else False


