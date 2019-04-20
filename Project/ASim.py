import random, simpy
import utils
import numpy as np, networkx as nx
RANDOM_SEED = 42
T_proposer = 20
T_step = 200
T_final = 3
L_proposer = 3000

L_step = 3000
N = 20 # We have to simulate a network of N nodes
G = None

#########################################
# Network setup

while (not G) or (not nx.is_connected(G)):
    z = np.random.uniform(4,9,2000) # create degree sequence of 2000 nodes uniformly distributed among{4,5,...,8}
    z = list(map(int, z)) # Convert to integers as the above produces floats
    # It's possible that degree sequence adds up to odd number, so the following statement make sets the first number of 5 if it's even and 6 otherwise
    if sum(z) %2 !=0:
        z[0] = 5 if z[0]%2 ==0 else 6
    G = nx.configuration_model(z)  # Create graph from configuration model
degree_sequence = [d for n, d in G.degree()]  # degree sequence

#########################################
# Setting delays for block and non-block messages

edges =list(G.edges)
block_delay = {}
block_delay_distribution = list(np.random.normal(200, 400, G.number_of_edges()))
non_block_delay = {}
non_block_delay_distribution = list(np.random.normal(30, 64, G.number_of_edges()))

for e in edges:
    block_delay[e] = max(0, block_delay_distribution.pop())
    non_block_delay[e] = max(0, non_block_delay_distribution.pop())
nx.set_edge_attributes(G, block_delay, 'block_delay')
nx.set_edge_attributes(G, non_block_delay, 'non_block_delay')
# print(nx.get_edge_attributes(G,'non_block_delay'))

#########################################
# Class definitions

class Txn:
    def __init__(self, creditor, debitor, amount):
        self.creditor=creditor
        self.debitor=debitor
        self.amount=amount
    def __str__(self):
        return "%s pays %s to %s"%(self.creditor, self.amount, self.debitor)

class Block:
    def __init__(self, prev_block, txns):
        self.prev_block = prev_block
        self.prev_block_hash = utils.hashBlock(str(self.prev_block))
        self.txns = txns
    def __str__(self):
        s = self.prev_block_hash
        for t in self.txns:
            s+= "||"+str(t)
        return s

class GenesisBlock(Block):
    def __init__(self):
        return super().__init__("", None)
    def __str__(self):
        return "We are building the best Algorand Discrete Event Simulator"

class Node:
    def __init__(self, id):
        self.id = id
        self.priv_key, self.pub_key = utils.generateKeys()
        self.stake = random.randint(1,50)
        
    def getNeighbours(self):
        return [n for n in G[self.id]]
    # def broadcast

#########################################
# Setup nodes 

print('Algorand')
random.seed(RANDOM_SEED)  # This helps reproducing the results
nodes = []
for i in range(N):
    nodes.append(Node(i))
print("Created nodes")

# t1 = Txn(1, 2, 10)
# t2 = Txn(2, 3, 15)
# t3 = Txn(4, 3, 12)
# g = GenesisBlock()
# print(g)
# b = Block(g, [t1,t2,t3])
# print(b)
#########################################
# Create an environment and start the setup process
env = simpy.Environment()
