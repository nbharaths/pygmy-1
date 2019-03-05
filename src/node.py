from __future__ import print_function

import random
import sys
import threading as t
import time
import socket

import Pyro4

products = ['fish', 'salt', 'boars']
# Pyro4.config.NS_HOST = '128.119.243.168' #  socket.gethostbyname(socket.gethostname())
# Pyro4.config.NS_PORT = 8111


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
    lock = t.Lock()
    product_to_buy = None
    start_time = None
    end_time = None

    # exposed
    def get_peertype(self):
        return self.peertype

    # exposed
    def get_node_id(self):
        return self.node_id

    # exposed
    def get_product_name(self):
        return self.product_name

    # exposed
    def get_product_to_buy(self):
        return self.product_to_buy

    # exposed
    def get_start_time(self):
        return self.start_time

    # exposed
    def get_end_time(self):
        return self.end_time

    # Initialising the Node object. Randomly assigning which product it will sell in the case of a Seller.
    def init(self, node_id, ip, peertype, wait_time = 4, product_count = 2, hop_count = 5):
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

    # Thread for starting the lookpup call along with the background timer until the wait time
    def node_start_t(self):
        for i in range(10):  # TO DO: Needs to be run infinitely
            wait_time = random.random() * self.wait_time
            self.start_time = time.time()
            self.product_to_buy = random.choice(products)
            print("Searching for", self.product_to_buy)
            self.lookup(self.product_to_buy, self.hop_count, [])
            time.sleep(wait_time)
            print(self.sellers_list)
            if self.sellers_list:
                selected_seller = random.choice(self.sellers_list)
                self.buy(selected_seller)
            else:
                print("Buy order failed, wait time was set to ", wait_time)

    def node_start(self):
        print("Creating the node thread", self.node_id)
        node_start_thread = t.Thread(target=self.node_start_t)
        print("Starting the node thread", self.node_id)
        node_start_thread.start()
        print("Started the node thread", self.node_id)
        return

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def transact(self, buyerid):
        if self.product_count < 1:
            self.product_name = random.choice(products)
            self.product_count = 3
            print("No products left!! Re-initializing with", self.product_name, self.product_count)
            return None

        else:
            buyer_node = Pyro4.Proxy("PYRONAME:" + buyerid)
            if self.product_name == buyer_node.get_product_to_buy():  # This ensure that you are buying what you want
                self.product_count -= 1
                print("Selling", self.product_name, "Product Count", self.product_count)
                return self.node_id, self.product_name

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
        lookup_thread = t.Thread(target=self.lookup_t, args=(product_name, hopcount, peer_path,))
        lookup_thread.start()

    def reply_t(self, sellerid, peer_path):
        if len(peer_path) < 1:

            peer_node = Pyro4.Proxy("PYRONAME:" + sellerid)
            if self.product_to_buy == peer_node.get_product_name():  # This ensure that you are buying what you want
                self.sellers_list.append(sellerid)
                return

        for neighbour in self.neighbourlist:
            if peer_path and neighbour.get_node_id() == peer_path[-1]:
                peer_path.pop()
                neighbour.reply(sellerid, peer_path)

    def reply(self, sellerid, peer_path):
        reply_thread = t.Thread(target=self.reply_t, args=(sellerid, peer_path,))
        reply_thread.start()

    def buy(self, peerid):
        peer_node = Pyro4.Proxy("PYRONAME:" + peerid)
        self.lock.acquire()
        seller_id = peer_node.transact(self.node_id)
        self.lock.release()
        if seller_id:
            print("Bought from", seller_id)
        else:
            print("Couldn't buy")

def main():
    node_id = sys.argv[1]
    Pyro4.Daemon.serveSimple({Node: node_id}, host= '192.168.0.8', ns=True)

if __name__ == "__main__":
    main()
