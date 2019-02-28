from __future__ import print_function
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(object):
    def __init__(self, type):
        self.type = type

    # Randomly assign buyer or seller

    def lookup(self, product_name, hopcount):
        pass

    def reply(self, sellerID):
        pass

    def buy(self, peerID):
        pass
