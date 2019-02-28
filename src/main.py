from __future__ import print_function

import random

import pandas as pd

from node import Node


def main():
    peer_type = ['buyer', 'seller']
    df_ip = pd.read_csv('ips.csv')
    N = df_ip.shape[0]
    df_conn = pd.read_csv('connections.csv')

    nodes = []
    for index, row in df_ip.iterrows():
        nodes.append(Node(random.choice(peer_type)))

    for node in nodes:
        print(node.type)


if __name__ == "__main__":
    main()
