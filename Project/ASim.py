import random, simpy
import numpy as np, networkx as nx
RANDOM_SEED = 42
N = 2000 # We have to simulate a network of N nodes
G = None

while (not G) or (not nx.is_connected(G)):
    z = np.random.uniform(4,9,2000) # create degree sequence of 2000 nodes uniformly distributed among{4,5,...,8}
    z = list(map(int, z)) # Convert to integers as the above produces floats
    # It's possible that degree sequence adds up to odd number, so the following statement make sets the first number of 5 if it's even and 6 otherwise
    if sum(z) %2 !=0:
        z[0] = 5 if z[0]%2 ==0 else 6
    G = nx.configuration_model(z)  # Create graph from configuration model
degree_sequence = [d for n, d in G.degree()]  # degree sequence


# Setup and start the simulation
print('Algorand')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
