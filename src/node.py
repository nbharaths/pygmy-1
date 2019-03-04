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
    sellers_list = []
    wait_time = None
    can_buy = True

    # exposed
    def get_peertype(self):
        return self.peertype

    # exposed
    def get_node_id(self):
        return self.node_id

    # exposed
    def get_product_name(self):
        return self.product_name

    def init(self, node_id, ip, peertype, wait_time = 1, product_count = 3, hop_count = 3):
        self.node_id = node_id
        self.ip = ip
        self.peertype = peertype
        self.neighbourlist = []
        self.wait_time = wait_time
        if peertype == 'seller':
            self.product_name = random.choice(products)
            self.product_count = product_count
        else:
            self.replies = []
            self.hop_count = hop_count
        print("Initialized ", self.peertype, " ID -", self.node_id)

    def node_start_t(self):
        for i in range(10):  # TO DO: Needs to be run infinitely
            wait_time = random.random() * self.wait_time  # Multiplying with 1000 for milliseconds

            self.product_to_buy = random.choice(products)
            print("!! Searching for", self.product_to_buy)
            self.lookup(self.product_to_buy, self.hop_count, [])
            print("Waiting for ", wait_time)
            time.sleep(wait_time)

            if self.sellers_list:
                selected_seller = random.choice(self.sellers_list)
                self.buy(selected_seller)
            else:
                print("Buy order failed !!")



    def node_start(self):
        node_start_thread = t.Thread(target=self.node_start_t())
        node_start_thread.start()

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def transact(self):
        # t.Lock().acquire()
        # print("Acquired lock")
        self.product_count -= 1
        print("Selling", self.product_name, "Product Count", self.product_count)

        if self.product_count < 1:
            self.product_name = random.choice(products)
            self.product_count = 3
            print("No products left!! Re-initializing with", self.product_name, self.product_count)
        # t.Lock().release()
        # print("Released the lock")

    def lookup_t(self, product_name, hopcount, peer_path):

        if hopcount == 0:
            return

        hopcount -= 1

        if self.peertype == "seller" and product_name == self.product_name:
            print("Sending prompt to node -", peer_path[0])
            self.reply(self.node_id, peer_path)

        for neighbour in self.neighbourlist:
            neighbour.lookup(product_name, hopcount, peer_path + [self.node_id])

    def lookup(self, product_name, hopcount, peer_path):
        lookup_thread = t.Thread(target=self.lookup_t, args=(product_name, hopcount, peer_path, ))
        lookup_thread.start()

    def reply_t(self, sellerid, peer_path):
        if len(peer_path) < 1:
            peer_node = Pyro4.Proxy("PYRONAME:" + sellerid)
            if self.product_to_buy == peer_node.get_product_name():  # This ensure that you are buying what you want
                self.sellers_list.append(sellerid)
                return

        for neighbour in self.neighbourlist:
            if peer_path  and neighbour.get_node_id() == peer_path[-1]:
                peer_path.pop()
                neighbour.reply(sellerid, peer_path)

    def reply(self, sellerid, peer_path):
        reply_thread = t.Thread(target=self.reply_t, args=(sellerid, peer_path, ))
        reply_thread.start()


    def buy(self, peerid):
        peer_node = Pyro4.Proxy("PYRONAME:" + peerid)
        print("Buying from", peerid, peer_node.get_product_name())
        peer_node.transact()


def main():
    node_id = sys.argv[1]

    Pyro4.Daemon.serveSimple({Node: node_id}, ns=True)


if __name__ == "__main__":
    main()
