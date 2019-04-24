import random, simpy
import utils
import numpy as np, networkx as nx
RANDOM_SEED = 42
SIM_TIME = 10000
T_proposer = 20
T_step = 200
T_final = 3
L_proposer = 3000
MAX_STEPS = 15
L_step = 3000
N = 2000 # We have to simulate a network of N nodes
G = None
W = 0 # Total stake in the system
nodes = []

#########################################
# Network setup

while (not G) or (not nx.is_connected(G)):
    z = np.random.uniform(4,9,N) # create degree sequence of N nodes uniformly distributed among{4,5,...,8}
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

# def deliverMsg(evt):
#     env = evt.value[0]
#     neighbour_id = evt.value[1]
#     message = evt.value[2]
#     neighbour = nodes[neighbour_id]
#     neighbour.rcv_pipe.put(message)
#     print ("At %d, sending %s to %d"%(env.now, message, neighbour_id))

def verifyAndGossipPriorityProposal(env, node, message):
    if not node.max_priority_proposal_message or message.payload.priority > node.max_priority_proposal_message.payload.priority:
        # print ("At %d, node %d gossipped block proposal message."%(env.now,node_id))
        node.max_priority_proposal_message = message
        # relay this message
        for neighbour in node.getNeighbourIds():
            event = simpy.events.Timeout(env, delay=node.getNonBlockDelay(neighbour), value=(env, neighbour, message))
            event.callbacks.append(verifyAndGossip)
      
def verifyAndGossipBlockProposal(env, node, message):
    print("%s heard block proposal %s"%(str(node), message.payload.random_string))
    if not utils.verifySortition(message.pub_key, message.payload.priority_proposal_payload.vrf_hash, message.payload.priority_proposal_payload.proof, message.payload.prev_block_hash, message.payload.priority_proposal_payload.round, 0, T_proposer, None, message.payload.stake, W):
        print("%s Sortition not validated"%(str(node), ))

        return None
    node.block_proposals_heard.append(message.payload)
    # relay this message
    for neighbour in node.getNeighbourIds():
        event = simpy.events.Timeout(env, delay=node.getBlockDelay(neighbour), value=(env, neighbour, message))
        event.callbacks.append(verifyAndGossip)
 
def verifyAndGossip(evt):
    env = evt.value[0]
    node_id = evt.value[1]
    message = evt.value[2]
    node = nodes[node_id]
    #Check if this message has come this way before
    if (message.r, message.s) in node.messages_seen:
        return None
    # Add this message to seen list
    node.messages_seen.append((message.r, message.s,))
    # Verify message signature
    if utils.verifySignature(message.r, message.s, str(message.payload), message.pub_key):
        if type(message.payload).__name__ == "PriorityProposalPayload":
            verifyAndGossipPriorityProposal(env, node, message)
        elif type(message.payload).__name__ == "BlockProposalPayload":
            verifyAndGossipBlockProposal(env, node, message)

class PriorityProposalPayload():
    def __init__(self, round, vrf_hash, proof, sub_user_idx, priority):
        self.round = round
        self.vrf_hash = vrf_hash
        self.proof = proof
        self.sub_user_idx = sub_user_idx
        self.priority = priority
    def __str__(self):
        return str(self.round) + str(self.vrf_hash) + str(self.sub_user_idx) + str(self.priority)

class BlockProposalPayload():
    def __init__(self, prev_block_hash, priority_proposal_payload, stake):
        self.prev_block_hash = prev_block_hash
        self.random_string = str(random.getrandbits(256))
        self.priority_proposal_payload = priority_proposal_payload
        self.stake = stake
    def __str__(self):
        return str(self.prev_block_hash) + str(self.random_string) + str(self.priority_proposal_payload)

class Message:
    def __init__(self, payload, priv_key, pub_key):
        self.payload = payload
        self.pub_key = pub_key
        self.r, self.s = utils.signMessage(str(payload), priv_key)


class Block:
    def __init__(self, prev_block, random_string=str(random.getrandbits(256))):
        self.prev_block = prev_block
        self.prev_block_hash = self.prev_block.hash()
        # if random_string == None:
        #     random_string = 
        self.random_string = random_string
    def __str__(self):
        return self.prev_block_hash + self.random_string

class GenesisBlock(Block):
    def __init__(self):
        self.prev_block_hash = "Genesis: "
        self.random_string = "We are building the best Algorand Discrete Event Simulator"
    def __str__(self):
        return super().__str__()
    def hash(self):
        return utils.hashBlock(str(self))

class Node:
    def __init__(self, id, env):
        self.id = id
        self.priv_key, self.pub_key = utils.generateKeys()
        self.stake = random.randint(1,50) #Assign random uniform stake
        self.block_pointer = GenesisBlock()
        self.round = 0
        self.max_priority_proposal_message = None
        self.env = env
        # Ref: https://simpy.readthedocs.io/en/latest/examples/process_communication.html
        self.rcv_pipe = simpy.Store(env)

    def __str__(self):
        return str(self.id)

    def getNeighbourIds(self):
        return [n for n in G[self.id]]

    def getBlockDelay(self, neighbour_id):
        return G.edges[self.id, neighbour_id, 0]['block_delay']

    def getNonBlockDelay(self, neighbour_id):
        return G.edges[self.id, neighbour_id, 0]['non_block_delay']

    def gossip(self, message, is_block, timeout):
        # Message = <Payload||Public Key|| Meta data for Signature verification>
        if message:
            for neighbour in self.getNeighbourIds():
                # print("%d neighbour %d"%(self.id, neighbour))
                event = simpy.events.Timeout(self.env, delay=self.getBlockDelay(neighbour) if is_block else self.getNonBlockDelay(neighbour), value=(self.env, neighbour, message))
                event.callbacks.append(verifyAndGossip)
        return env.timeout(timeout)

    def start(self):
        # starts the simulation process for this node

        self.block_proposals_heard = []
        self.messages_seen = []
        #print("%d : %d"%(self.id, W))
        hash, proof, j = utils.sortition(self.priv_key, str(self.block_pointer.hash()), self.round, 0, T_proposer, None, self.stake, W )
        if j > 0:
            # candidate for block proposal
            print("%d : %d"%(self.id, j))
            priority = utils.evaluatePriority(str(hash), j)
            # Construct message to gossip
            priority_proposal_payload = PriorityProposalPayload(self.round, hash, proof, j, priority)
            message = Message(priority_proposal_payload, self.priv_key, self.pub_key)
            self.max_priority_proposal_message = message
            yield self.gossip(message, False, 3000)
        else:
            # just relay node
            self.gossip(None, True, 3000)
        # Gossip block proposal over. Now check if this is the greatest priority proposed block
        if self.max_priority_proposal_message and self.max_priority_proposal_message.pub_key == self.pub_key :
            # This dude is block proposer! Congratulations! Now make a block proposal message
            block_proposal_payload = BlockProposalPayload(self.block_pointer.hash(), self.max_priority_proposal_message.payload, self.stake)
            message = Message(block_proposal_payload, self.priv_key, self.pub_key)
            yield self.gossip(message, True, 1)
            print ("%d is block proposer with priority %s"%(self.id, self.max_priority_proposal_message.payload.priority))

        # Node checks its selection in voting committee using sortition
        # hash, proof, j = utils.sortition(self.priv_key, str(self.block_pointer.hash()), self.round, 0, T_proposer, None, self.stake, W )
        
        yield env.timeout(2000)
            

#########################################
# Setup nodes 

nodes = []
if __name__ == '__main__' :
    
    #########################################
    # Create an environment and start the setup process
    print('Algorand Simulator')
    env = simpy.Environment()
    random.seed(RANDOM_SEED)  # This helps reproducing the results
    for i in range(N):
        nodes.append(Node(i, env))
        W += nodes[i].stake
        # print("%d stake: %d"%(nodes[i].id, nodes[i].stake))
        env.process(nodes[i].start())
    print("Created nodes")
    # For one-to-one or many-to-one type pipes, use Store
    # for n in nodes[0].getNeighbourIds():
    #     env.process(nodes[n].broadcast("Yo from %d"%(n), True))
    # env.process(nodes[0].receive(3000))
    # print(nodes[0].getNeighbourIds())
    # b = PriorityProposalPayload(1,2,3,4)
    # m = Message(b, nodes[0].priv_key, nodes[0].pub_key)
    # env.process(nodes[0].gossip(m, True, 3000))

    env.run(until=SIM_TIME)
    # t1 = Txn(1, 2, 10)
    # t2 = Txn(2, 3, 15)
    # t3 = Txn(4, 3, 12)
    # g = GenesisBlock()
    # print(g)
    # b = Block(g, [t1,t2,t3])
    # print(b)

