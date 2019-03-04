Environment Setup

There are two config files ips.csv and connections.csv . The former describes the peers in the format Node ID, IP Address . The latter describes the network topology in the form of edges Node1, Node2 . Modify the config files as required to setup the environment.

There are two Python files node.py and main.py - node.py represents the peer and its functionalities. main.py is used to initialize the network and start program execution.

Program Execution

Start the Pyro4 name server from any of the machines using pyro4-ns -n hostname -p port
Start the individual peers on their respective machines using the command python3 node.py NodeID . Note that the NodeID here must match the ones used in the config files ips.csv and connections.csv . This is imperative for the Pyro4 name server to figure out the network topology. Run main.py from the machine where the configs are located.
