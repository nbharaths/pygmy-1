from __future__ import print_function

import random

import Pyro4
import socket
import threading as t
import time
import sys

products = ['fish', 'salt', 'boars']


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(object):
    node_id = None
    ip = None
    peertype = None
    product_name = None
    product_count = None
    replies = None
    hop_count = None
    neighbourlist = None

    def get_peertype(self):  # exposed
        return self.peertype

    def get_node_id(self):  # exposed
        return self.node_id

    def init(self, node_id, ip, peertype):
        self.node_id = node_id
        self.ip = ip
        self.peertype = peertype
        self.neighbourlist = []
        if peertype == 'seller':
            self.product_name = random.choice(products)
            self.product_count = 3  # Configure this
        else:
            self.replies = []
            self.hop_count = 2
        print("Initialized ", self.peertype, "node. ID:", self.node_id)
    # Randomly assign buyer or seller

    def node_start(self):
        print("Starting the buying call for node", self.node_id)

        for i in range(2):
            time.sleep(0.75)
            self.lookup(random.choice(products), self.hop_count, [])

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def dummy(self):
        print('Hello')
        self.product_count += 1

    def transact(self):
        self.product_count -= 1
        print("Node:", self.node_id, "Selling", self.product_name, self.product_count)

        if self.product_count == 0:
            self.product_name = random.choice(products)
            self.product_count = 3
            print("Node:", self.node_id, "No products left", "Re-initializing with", self.product_name, self.product_count)

    def lookup_t(self, product_name, hopcount, peer_path):

        if hopcount == 0:
            return

        hopcount -= 1

        if self.peertype == "seller" and product_name == self.product_name:
            print("Seller found", self.node_id, "Path", peer_path)
            self.reply(self.node_id, peer_path)

        for neighbour in self.neighbourlist:
            neighbour.lookup(product_name, hopcount, peer_path + [self.node_id])

    def lookup(self, product_name, hopcount, peer_path):
        print("Lookup called for", product_name, "Current hop count =", hopcount)
        lookup_thread = t.Thread(target=self.lookup_t, args=(product_name, hopcount, peer_path, ))
        lookup_thread.start()

    def reply_t(self, sellerid, peer_path):
        if len(peer_path) < 1:
            self.buy(sellerid)
            return

        for neighbour in self.neighbourlist:
            if peer_path  and neighbour.get_node_id() == peer_path[-1]:
                peer_path.pop()
                neighbour.reply(sellerid, peer_path)

    def reply(self, sellerid, peer_path):
        print("Reply called for", sellerid, "Peer path =", peer_path)
        reply_thread = t.Thread(target=self.reply_t, args=(sellerid, peer_path, ))
        reply_thread.start()

    def buy_t(self, peerid):
        peer_node = Pyro4.Proxy("PYRONAME:"+peerid)
        peer_node.transact()
        print('Bought from ', peerid)

    def buy(self, peerid):
        print("Buy called for", peerid)
        buy_thread = t.Thread(target=self.buy_t, args=(peerid, ))
        buy_thread.start()


def main():
    node_id = sys.argv[1]
    # node_ip = sys.argv[2]
    #
    # products = ['fish', 'salt', 'boars']
    # peer_types = ['buyer', 'seller']

    Pyro4.Daemon.serveSimple({Node: node_id}, ns=True)

    # peertype = random.choices(peer_types)
    # if peertype == 'seller':
    #     self.product_name = random.choice(products)
    #     self.product_count = 3  # Configure this
    # else:
    #     self.replies = []
    #     self.hop_count = 2
    # print("Initialized ", self.peertype, "node. ID:", self.id
# Randomly assign buyer or seller

if __name__ == "__main__":
    main()
