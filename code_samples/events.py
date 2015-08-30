#!/usr/bin/env python
# Events.py

from SimPy.Simulation import *

class Event:
    """ Class implementing named events==signals for synchronization of processes.
    Not to be confused with events as in discrete _event_ simulation

    Provides for semaphores and also for mass-reactivation of processes after event.
    """
    def __init__(self, name):
        self.name = name
        self.waits = []     # set of processes waiting for event
        self.queues = []    # FIFO queue for processes waitinf for semaphore
        self.occurred = False

    def set(self):
        """ Produces a signal;
        Set this event if no process waitinf or queuing;
        reactivate all processes waiting for this event;
        reactivate first process in FIFO queue for this event
        """
        if not self.waits and not self.queues:
            self.occurred = True
        else:
            # shcedule activation for all waiting processes
            for p in self.waits:
                reactivate(p)
            self.waits = []
        if self.queues:
            # Activate first process in queue to enter critical section
            p = self.queues.pop(0)
            reactivate(p)

    def wait(self, proc):
        """ Consumes a signal if it has been sent,
        else process 'proc' waits for this event.
        Return value indicates whether process has to wait.
        """
        if not self.occurred:
            self.waits.append(proc)
            return True
        else:
            self.occurred = False
            return False

    def queue(self, proc):
        """ Consumes a signal if it has been sent;
        else process 'proc' queues for this event
        Return valu idnicates whether process ha to quit. 
        """
        if not self.occurred:
            self.queues.append(proc)
            return True
        else:
            self.occurred = False
            return False


