from __future__ import print_function

import random

import Pyro4
import socket

products = ['fish', 'salt', 'boars']


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(object):
    def __init__(self, id, ip, peertype, product_name = None, product_count = None):
        self.id = id
        self.ip = ip
        self.peertype = peertype
        self.neighbourlist = []
        self.product_name = product_name
        self.product_count = product_count
        self.max_items = 3

    # Randomly assign buyer or seller

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def transact(self):
        self.product_count -= 1

        if self.product_count == 0:
            self.product_name = random.choice(products)
            self.product_count = self.max_items

    def lookup(self, product_name, hopcount, peer_path):

        if hopcount == 0:
            return

        hopcount -= 1

        if self.type == "seller" and product_name == self.product_name:
            self.reply(self.id, peer_path)

        for neighbour in self.neighbourlist:
            neighbour.lookup(product_name, hopcount, peer_path + [self.id])

    def reply(self, sellerid, peer_path):
        if not peer_path:
            self.buy(sellerid)

        for neighbour in self.neighbourlist:
            if neighbour.id == peer_path[-1]:
                peer_path.pop()
                neighbour.reply(sellerid, peer_path)

    def buy(self, peerid):
        peer_node = Pyro4.Proxy(peerid)
        peer_node.transact()
        print('Bought from ', peerid)


def main():
    Pyro4.Daemon.serveSimple(
        {
            Node: "src.node"
        },
        host=socket.gethostbyname(socket.gethostname()),
        ns=True)


if __name__ == "__main__":
    main()
