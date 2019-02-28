from __future__ import print_function

import random

import pandas as pd

from node import Node


def main():
    peer_type = ['buyer', 'seller']
    df_ip = pd.read_csv('ips.csv', delimiter=',')
    N = df_ip.shape[0]
    print('Number of nodes in network - ', N)
    df_conn = pd.read_csv('connections.csv')

    nodes = {}
    for index, row in df_ip.iterrows():
        print(row['Node'], row['IP'])
        nodes[row['Node']] = Node(row['Node'], row['IP'], random.choice(peer_type))

    for index, row in df_conn.iterrows():
        nodes[row['Node1']].add_neighbour(row['Node2'])

    print(nodes)


if __name__ == "__main__":
    main()
