from __future__ import print_function

import random

import Pyro4
import pandas as pd

# List of products that will be part of the bazaar
products = ['fish', 'salt', 'boars']

# Constants for readability
BUYER = 'buyer'
SELLER = 'seller'


def main():

    # Currently two possible peer types
    peer_types = ['buyer', 'seller']

    # Reading the csv file for getting the IP's corresponding to the nodes
    df_ip = pd.read_csv('ips.csv', delimiter=',')  # Read in Node IDs as well as IP Addresses
    df_params = pd.read_csv('params.csv', delimiter=',')
    max_items = int(df_params['Value'][0])
    hop_count = int(df_params['Value'][1])
    max_wait_time = int(df_params['Value'][2])

    # Setting the Pyro nameserver host and port
    NS_HOST = df_params['Value'][3]
    NS_PORT = int(df_params['Value'][4])
    n = df_ip.shape[0]

    print('Number of nodes in the network - ', n)
    df_conn = pd.read_csv('connections.csv', delimiter=',')  # Read in the network topology edge-wise

    nodes = {}  # Dictionary that holds the Pyro4 proxy objects

    # Initializing the the nodes
    for index, row in df_ip.iterrows():
        print("Connecting to URI for :", row['Node'])
        ns = Pyro4.locateNS(host=NS_HOST, port=NS_PORT)  # use your own nameserver
        uri = ns.lookup(row['Node'])
        nodes[row['Node']] = Pyro4.Proxy(uri)
        nodes[row['Node']].init(row['Node'], row['IP'],
                                random.choice(peer_types), max_wait_time, max_items, hop_count, NS_HOST,
                                NS_PORT)  # Instantiating the peer with buyer/seller randomly
        print(nodes[row['Node']].get_peertype())

    # Adding adjacent peers for each peer to facilitate lookup
    for index, row in df_conn.iterrows():
        nodes[row['Node1']].add_neighbour(nodes[row['Node2']])
        nodes[row['Node2']].add_neighbour(nodes[row['Node1']])

    # Starting the bazaar
    for node in nodes.values():
        print("Starting node -", node.get_node_id())
        if node.get_peertype() == BUYER:  # Starts the lookup calls for every buyer
            node.node_start()
        print("Started node -", node.get_node_id())


if __name__ == "__main__":
    main()
