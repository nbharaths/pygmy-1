Environment Setup

There are two config files ips.csv and connections.csv. The former describes the peers in the
format Node ID, IP Address. The latter describes the network topology in the form of edges
Node1, Node2. Modify the config files as required to setup the environment. (We do not
need IPs as we dynamically find the hostname and the nameserver, which then figures out
the topology)
There are two Python files node.py and main.py - node.py represents the peer and its func-
tionalities. main.py is used to initialize the network and start program execution.
There is an additional file params.csv that takes in configurable values like max items,
hop count, max wait time, NS HOST (name server host) and NS PORT (name server port).
Note: Configuring NS HOST and NS PORT is mandatory and probably the only thing you
would need to do to run the programs smoothly.

Program Execution

Start the Pyro4 name server from any of the machines using pyro4-ns -n hostname -p port
Start the individual peers on their respective machines using the command python3 node.py
NodeID. Note that the NodeID here must match the ones used in the config files ips.csv
and connections.csv. This is imperative for the Pyro4 name server to figure out the net-
work topology. Run main.py from the machine where the configs are located. Also ensure
params.csv is present along with node.py at launch because this helps point to the name
server directly.
