Environment Setup

There are two config files _ips.csv_  and _connections.csv_ . The former describes the peers in the format Node ID, IP Address . The latter describes the network topology in the form of edges Node1, Node2 . Modify the config files as required to setup the environment.

There are two Python files _node.py_ and _main.py_  - _node.py_  represents the peer and its functionalities. _main.py_  is used to initialize the network and start program execution.

Program Execution

Start the Pyro4 name server from any of the machines using _pyro4-ns -n hostname -p port_  
Start the individual peers on their respective machines using the command _python3 node.py NodeID_ . Note that the NodeID here must match the ones used in the config files _ips.csv_  and _connections.csv_ . This is imperative for the Pyro4 name server to figure out the network topology. 
Run _main.py_ from the machine where the configs are located.