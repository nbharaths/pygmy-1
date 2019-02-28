from __future__ import print_function

import Pyro4


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

    # Randomly assign buyer or seller

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def lookup(self, product_name, hopcount):

        if hopcount == 0:
            return

        hopcount -= 1

        if self.type == "seller" and product_name == self.product_name:
            self.reply(self.id)

        for neighbour in self.neighbourlist:
            neighbour.lookup(product_name, hopcount)

    def reply(self, sellerid):
        pass

    def buy(self, peerid):
        pass


def main():
    Pyro4.Daemon.serveSimple(
        {
            Node: "src.node"
        },
        ns=True)


if __name__ == "__main__":
    main()
