from __future__ import print_function

import random
import socket
import sys
import threading as t
import time

import Pyro4
import pandas as pd

# List of products that will be part of the bazaar
products = ['fish', 'salt', 'boars']

# Constants for readability
BUYER = 'buyer'
SELLER = 'seller'


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(object):
    # Object variable initialized, not keeping them in an init function call because of a Pyro constraint
    node_id = None
    ip = None
    peertype = None
    product_name = None
    product_count = None
    replies = None
    hop_count = None
    neighbourlist = None
    sellers_list = []
    sellers_time_list = []
    wait_time = None
    can_buy = True
    lock = t.Lock()
    product_to_buy = None
    timestamp = None

    # Methods exposed for making the Pyro proxy objects get the attributes of actual object
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

    # Custom init call kept due to Pyro proxy object initialization constraints
    def init(self, node_id, ip, peertype, wait_time=4, product_count=2, hop_count=3, ns_host=None, ns_port=None):
        self.node_id = node_id  # Id of the node
        self.ip = ip  # IP address of the node
        self.peertype = peertype  # Type of the peer (buyer/seller)
        self.neighbourlist = []  # List of adjacent peers
        self.wait_time = wait_time  # Time to wait after buyer lookup
        if peertype == SELLER:
            self.product_name = random.choice(products)
            self.product_count = product_count
        else:
            self.hop_count = hop_count  # Hop counts for lookup
        self.ns_host = ns_host
        self.ns_port = ns_port
        print("Initialized ", self.peertype, " ID -", self.node_id)

    # Thread for starting the lookup call along with the background timer until the wait time
    def node_start_t(self):
        for i in range(100):  # Currently kept it 100 not letting the network run for infinite time

            # Reinitializing the lists
            self.sellers_list = []
            self.sellers_time_list = []

            wait_time = random.random() * self.wait_time  # Multiplying with 1000 for milliseconds
            self.timestamp = time.time()
            self.product_to_buy = random.choice(products)
            print("Searching for", self.product_to_buy)
            self.lookup(self.product_to_buy, self.hop_count, [], self.timestamp)  # Start the lookup call
            time.sleep(wait_time)

            if self.sellers_list:  # If list of sellers populated
                # print(self.sellers_time_list)
                selected_seller = random.choice(self.sellers_list)  # Choose a seller randomly and try to transact
                self.buy(selected_seller)
                file_name = self.node_id + "_search_request_time"
                f = open(file_name, 'a')
                f.write(str(self.sellers_time_list[0]) + "\n")
            else:
                print("Buy order failed")  # , wait time was set to ", wait_time)

    # This is the method starting the node thread
    def node_start(self):
        print("Creating the node thread", self.node_id)
        node_start_thread = t.Thread(target=self.node_start_t)
        print("Starting the node thread", self.node_id)
        node_start_thread.start()
        print("Started the node thread", self.node_id)
        return

    # Method for adding the neighbouring peer node in the topology into the current node's list
    def add_neighbour(self, neighbour):
        self.neighbourlist.append(neighbour)  # Add adjacent peer to current peer's list

    # Final method called from the buy method to complete the transaction
    def transact(self, buyerid):
        if self.product_count < 1:  # Ensures positive product counts
            self.product_name = random.choice(products)
            self.product_count = 3
            print("No products left! Re-initializing with", self.product_name, self.product_count)
            return None

        else:
            ns = Pyro4.locateNS(host=self.ns_host, port=self.ns_port)  # use your own nameserver
            uri = ns.lookup(buyerid)
            buyer_node = Pyro4.Proxy(uri)
            if self.product_name == buyer_node.get_product_to_buy():  # This ensures that you are buying what you want
                self.product_count -= 1
                print("Selling", self.product_name, "Product Count", self.product_count)
                return self.node_id, self.product_name

    # The lookup thread starter method
    def lookup_t(self, product_name, hopcount, peer_path, timestamp):

        if hopcount == 0:
            return

        hopcount -= 1  # Decrement hopcount

        if self.peertype == SELLER and product_name == self.product_name:
            print("Sending prompt to node -", peer_path[0])  # Send a reply
            self.reply(self.node_id, peer_path, timestamp)

        for neighbour in self.neighbourlist:  # Call lookup in a flood-fill manner
            neighbour.lookup(product_name, hopcount, peer_path + [self.node_id], timestamp)

    # The lookup thread wrapper method
    def lookup(self, product_name, hopcount, peer_path, timestamp):
        lookup_thread = t.Thread(target=self.lookup_t, args=(product_name, hopcount, peer_path, timestamp))
        lookup_thread.start()

    # The reply thread starter method
    def reply_t(self, sellerid, peer_path, timestamp):
        if len(peer_path) < 1:  # Reply has come back to original buyer
            ns = Pyro4.locateNS(host=self.ns_host, port=self.ns_port)  # use your own nameserver
            uri = ns.lookup(sellerid)
            peer_node = Pyro4.Proxy(uri)
            if self.product_to_buy == peer_node.get_product_name():  # This ensures that you are buying what you want
                self.sellers_list.append(sellerid)
                self.sellers_time_list.append((time.time() - timestamp) * 1000)
                return

        for neighbour in self.neighbourlist:
            if peer_path and neighbour.get_node_id() == peer_path[-1]:  # Reverse the path to buyer
                peer_path.pop()
                neighbour.reply(sellerid, peer_path, timestamp)

    # The reply thread wrapper method
    def reply(self, sellerid, peer_path, timestamp):
        reply_thread = t.Thread(target=self.reply_t, args=(sellerid, peer_path, timestamp))
        reply_thread.start()

    # Buy method that will be called by the buyer nodes
    def buy(self, peerid):
        ns = Pyro4.locateNS(host=self.ns_host, port=self.ns_port)  # use your own nameserver
        uri = ns.lookup(peerid)
        peer_node = Pyro4.Proxy(uri)

        # For getting the RPC latency.
        # Assumption: We'll be making an RPC and record the time for getting back the reply
        start_time = time.time()
        peer_node.get_node_id()
        end_time = time.time()
        print("RPC call from ", self.node_id, "to", peerid, "took:", (end_time - start_time) * 1000, "ms")
        file_name = self.node_id + "-" + peerid
        f = open(file_name, 'a')
        f.write(str((end_time - start_time) * 1000) + "\n")

        self.lock.acquire()
        seller_id = peer_node.transact(self.node_id)
        self.lock.release()  # Release lock after transaction
        if seller_id:
            print("Bought from", seller_id)
        else:
            print("Couldn't buy")


def main():
    # Reading from the csv file
    node_id = sys.argv[1]
    df_params = pd.read_csv('params.csv', delimiter=',')
    NS_HOST = df_params['Value'][3]
    NS_PORT = int(df_params['Value'][4])

    # Creating the Pyro Daemon
    daemon = Pyro4.Daemon(host=socket.gethostbyname(socket.gethostname()))
    ns = Pyro4.locateNS(host=NS_HOST, port=NS_PORT)
    uri = daemon.register(Node)
    ns.register(node_id, uri)

    print("Ready")
    print(uri)
    daemon.requestLoop()


if __name__ == "__main__":
    main()
