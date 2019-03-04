from __future__ import print_function

import Pyro4
import pandas as pd

products = ['fish', 'salt', 'boars']


def main():
    peer_types = ['buyer', 'seller']
    df_ip = pd.read_csv('ips.csv', delimiter=',')
    df_params = pd.read_csv('params.csv', delimiter=',')
    n = df_ip.shape[0]
    max_items = df_params['max_items']  # make this configurable
    print('Number of nodes in network - ', n)
    df_conn = pd.read_csv('connections.csv')

    nodes = {}
    for index, row in df_ip.iterrows():
        print("Connecting to uri:", "PYRONAME:" + row['Node'])
        nodes[row['Node']] = Pyro4.Proxy("PYRONAME:" + row['Node'])
        nodes[row['Node']].init(node_id=row['Node'], ip=row['IP'], peertype=peer_types[index % 2],
                                max_wait_time=df_params['max_wait_time'],
                                hop_count=df_params['hop_count'])
        print(nodes[row['Node']].get_peertype())

    for index, row in df_conn.iterrows():
        nodes[row['Node1']].add_neighbour(nodes[row['Node2']])
        nodes[row['Node2']].add_neighbour(nodes[row['Node1']])

    for node in nodes.values():
        if node.get_peertype() == peer_types[0]:
            # TO DO: Create constants for peer types
            node.node_start()


if __name__ == "__main__":
    main()
