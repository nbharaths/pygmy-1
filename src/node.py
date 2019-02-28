from __future__ import print_function

import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(object):
    def __init__(self, id, ip, type):
        self.id = id
        self.ip = ip
        self.type = type

    # Randomly assign buyer or seller

    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)

    def lookup(self, product_name, hopcount):
        pass

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
