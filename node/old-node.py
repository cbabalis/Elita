# TODO Uneccessary file. just remove it when all is finished.

from SimPy.Simulation import *
## Simulation class ---------------------------------------------------

class NodeClass(Process):
    """ simulates one node """
    NodeList = []   # a list that contains instances of NodeClass
    mean_waiting_time = 0
    total_waiting_time = 0

    def __init__(self, name, weight, protocol, sources, network):
        Process.__init__(self)
        self.node = Node(name, weight, protocol, sources, network)
        self.waiting_time = 0   # waiting time for this particular node
        self.msg_number = 0     # messages this node sent
        NodeClass.NodeList.append(self)

    def run(self):
        """ simulation with protocol """
        while 1:
            # choose a random node to run
            curr_node_sim = self.selectNode()
            curr_node = curr_node_sim.node
            new_data = self.recvEnvironmentData(curr_node)
            if new_data:
                # yield passivate, self
                yield hold, self, 0.7
            else:
                # else, send a message to the network
                if curr_node_sim.passive():
                    reactivate(curr_node_sim)
                yield request, self, curr_node.protocol.network.net_chnls
                # send a message to all nodes
                curr_node.protocol.bcastStatVector(curr_node.protocol.cm.localStatistics)
                # and receive as answer the time needed 
                # for the message to be sent
                self.delay = curr_node.protocol.network.travelingTime()
                yield hold, self, self.delay
                # finally release the channel
                yield release, self, curr_node.protocol.network.net_chnls
                self.msg_number += 1

    def recvEnvironmentData(self, node):
        """ receives data from environment and checks it. """
        self.data = node.protocol.getDataFromNode()
        node.protocol.recvLocalUpdate(self.data)
        return node.protocol.dontSend()


    def selectNode(self):
        """ selects a random node from the list and returns it """
        self.chosen_one = random.randint(0, len(NodeClass.NodeList)-1)
        return NodeClass.NodeList[self.chosen_one]

    ## Coordinator assignment code ------------------------------------

    def selectCoord(self):
        """ selects a coordinator in a random way """
        # choose randomly a node to be the coordinator
        self.coord_id = random.randint(0, len(NodeClass.NodeList)-1)
        # assign a different name to that node
        NodeClass.NodeList[self.coord_id].node.name = 'COORD'
        # return the node
        return self.coord_id

    def returnAllNodes(self):
        """ creates a list of all nodes and returns it """
        self.nl = []    # init an empty node list
        for i, nc in zip(range(len(NodeClass.NodeList)), NodeClass.NodeList):
            self.nl.append(nc.node)
        return self.nl


class GatherItem(Process):
    def __init__(self, new_items):
        Process.__init__(self)
        self.new_items = new_items

    def new_arrival(self):
        if not self.new_items:
            return False
        return True

    def gather(self):
        if self.new_arrival():
            yield passivate, self
        yield waituntil, self, self.new_arrival
        yield hold, self, random.expovariate(1.0/waiting_time)

## Threads for environment-node message exchange ---------------------

class DataReceiver(threading.Thread):
    """ DataReceiver() receives a recently produced item. It represents
    the Consumer in a Consumer-Producer model. It works with threads.
    """

    def __init__(self, condition, item_list, node):
        """ Inits a DataReceiver instance.
        @param condition is a condition variable
        @param item_list is a list that contains items.
        @param node is a Node instance (actually the node that called
        the item).
        """
        threading.Thread.__init__(self)
        self.condition = condition
        self.item_list = item_list
        self.node = node

    def run(self):
        """ runs the thread """
        # init an empty item
        self.item = None
        # if there is no item in item list, then:
        if not self.item_list:
            # try to acquire the condition variable for the critical
            # section and wait for an item to arrive
            self.condition.acquire()
            while True:
                if self.item_list:
                    self.item = self.item_list.pop()
                    break
                self.condition.wait()
            # if an item has arrived, then release the cond variable
            self.condition.release()
            # and return the item
            self.node.pickup_item(self.item)
            time.sleep(1)
        else:
            # else just pop an item from item_list
            self.node.pickup_item(self.item_list.pop())

