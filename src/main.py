from __future__ import print_function
import Pyro4
import pandas as pd

from node import Node


def main():

    df = pd.read_csv('config.csv')
    print(df)
    Pyro4.Daemon.serveSimple(
        {
            Node: "src.node"
        },
        ns=True)


if __name__ == "__main__":
    main()
