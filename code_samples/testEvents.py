#!/usr/bin/env python
# testEvents.py

from SimPy.Simulation import *
from events import *

""" Pavlov's drooling dogs.
Scenario: Four dogs wait for the bell to ring and start to drool
when they hear it.
"""

class BellMan(Process):
    def ring(self):
        while True:
            bell.set()
            print '%s %s rings bell '%(now(), self.name)
            yield hold, self, 5


class PavlovDog(Process):
    def behave(self):
        while True:
            if bell.wait(self):
                yield passivate, self
                print '%s %s drools '%(now(), self.name)

initialize()
bell = Event('bell')
for i in range(4):
    p = PavlovDog('Dog %s'%(i+1))
    activate(p, p.behave())
b = BellMan('Pavlov')
activate(b, b.ring())
print "\n Pavlov's dogs"
simulate(until=10)


""" PERT simulation
Scenario: A job takes 10 parallel activities of different duration
to complete before it is done.
"""

class Activity(Process):
    def __init__(self, name):
        Process.__init__(self, name)
        self.event = Event('completion nof %s'%self.name)
        allEvents.append(self.event)

    def perform(self):
        yield hold, self, random.randint(1, 100)
        self.event.set()
        print "%s Event '%s' fired"%(now(), self.event.name)


class TotalJob(Process):
    def perform(self, allEvents):
        for e in allEvents:
            if e.wait(self):
                yield passivate, self
        # not waiting for any events anymore -- all events were set
        print now(), 'All done'

import random
initialize()
allEvents = []
for i in range(10):
    a = Activity('Activity %s'%(i+1))
    activate(a, a.perform())
t = TotalJob()
activate(t, t.perform(allEvents))
print '\n PERT network simulation'
simulate(until=100)

""" Traffic intersection as critical region.
Scenario: 20 cars crossing a US-style four-way stop intersectoin
are simulated. On such intersections, only one car is allowed
on the intersection. The others have to wait until the intesection
is clear. They cross in FIFO order.
"""
class Car(Process):
    def drive(self):
        if intersectionFree.queue(self):
            print "%s %s waiting to enter intersection "%(now(), self.name)
        yield hold, self, 1
        print "%s %s crossed intersection"%(now(), self.name)
        intersectionFree.set()


initialize()
intersectionFree = Event('Intersection')
intersectionFree.set()
arrtime = 0.0
for i in range(20):
    c = Car('Car %s'%(i+1))
    activate(c, c.drive(), at=arrtime)
    arrtime += 0.2
print '\n Critical section/semaphore'
simulate(until=100)

