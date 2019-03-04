from __future__ import print_function

import Pyro4
import pandas as pd

products = ['fish', 'salt', 'boars']
BUYER = 'buyer'  # Constants for readability
SELLER = 'seller'


def main():
    peer_types = ['buyer', 'seller']
    df_ip = pd.read_csv('ips.csv', delimiter=',')  # Read in Node IDs as well as IP Addresses
    n = df_ip.shape[0]
    print('Number of nodes in the network - ', n)
    df_conn = pd.read_csv('connections.csv')  # Read in the network topology edge-wise

    nodes = {}  # Dictionary that holds the Pyro4 proxy objects
    for index, row in df_ip.iterrows():
        print("Connecting to URI:", "PYRONAME:" + row['Node'])
        nodes[row['Node']] = Pyro4.Proxy("PYRONAME:" + row['Node'])  # Creating the Proxy objects
        nodes[row['Node']].init(row['Node'], row['IP'],
                                peer_types[index % 2])  # Instantiating the peer with buyer/seller
        print(nodes[row['Node']].get_peertype())

    for index, row in df_conn.iterrows():  # Adding adjacent peers for each peer to facilitate lookup
        nodes[row['Node1']].add_neighbour(nodes[row['Node2']])
        nodes[row['Node2']].add_neighbour(nodes[row['Node1']])

    for node in nodes.values():
        if node.get_peertype() == BUYER:  # Starts the lookup calls for every buyer
            node.node_start()


if __name__ == "__main__":
    main()
