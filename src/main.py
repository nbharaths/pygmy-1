from __future__ import print_function

import random

import pandas as pd

from node import Node

products = ['fish', 'salt', 'boars']


def main():
    peer_types = ['buyer', 'seller']
    df_ip = pd.read_csv('ips.csv', delimiter=',')
    n = df_ip.shape[0]
    max_items = 3  # make this configurable
    print('Number of nodes in network - ', n)
    df_conn = pd.read_csv('connections.csv')

    nodes = {}
    for index, row in df_ip.iterrows():
        nodes[row['Node']] = Node(row['Node'], row['IP'], random.choice(peer_types))

    for index, row in df_conn.iterrows():
        nodes[row['Node1']].add_neighbour(nodes[row['Node2']])


if __name__ == "__main__":
    main()
