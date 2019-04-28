#!/usr/bin/python3
import random, simpy
import utils
import numpy as np, networkx as nx
from matplotlib import pyplot as plt
import time

# Non-variable parameters
RANDOM_SEED = 42
SIM_TIME = 100000
MAX_STEPS = 10
MAX_ROUNDS = 2
N = 256 # We have to simulate a network of N nodes

# Variable parameters
t_proposer = 15
t_step = 32
t_final = 3
T_step = 2/3
T_final = 3/4
L_quiscent = 3000
L_proposer = 100
L_step = 3000
L_block = 30000

# Global initializations
G = None
nodes = []
ctx = {
    'W' : 0,
    'weight':{}
}
pkiddict = {}
proposer_count = {}
#########################################
# Network setup

while (not G) or (not nx.is_connected(G)):
    z = np.random.uniform(2,5,N) # create degree sequence of N nodes uniformly distributed among{4,5,...,8}
    z = list(map(int, z)) # Convert to integers as the above produces floats
    # It's possible that degree sequence adds up to odd number, so the following statement make sets the first number of 5 if it's even and 6 otherwise
    if sum(z) %2 !=0:
        z[0] = 3 if z[0]%2 ==0 else 4
    G = nx.configuration_model(z)  # Create graph from configuration model
degree_sequence = [d for n, d in G.degree()]  # degree sequence

#########################################
# Setting delays for block and non-block messages

edges =list(G.edges)
block_delay = {}
block_delay_distribution = list(np.random.normal(200, 400, G.number_of_edges()))
non_block_delay = {}
non_block_delay_distribution = list(np.random.normal(40, 64, G.number_of_edges()))

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
#     self.log ("At %d, sending %s to %d\n"%(env.now, message, neighbour_id))

def verifyAndGossipPriorityProposal(env, node, message):
    node.priority_proposal_messages_heard.append(message)
    if not node.max_priority_proposal_message or message.payload.priority > node.max_priority_proposal_message.payload.priority:
        # self.log ("At %d, node %d gossipped block proposal message.\n"%(env.now,node_id))
        node.max_priority_proposal_message = message
        # relay this message
        for neighbour in node.getNeighbourIds():
            event = simpy.events.Timeout(env, delay=node.getNonBlockDelay(neighbour), value=(env, neighbour, message))
            event.callbacks.append(verifyAndGossip)
      
def verifyAndGossipBlockProposal(env, node, message):
    # verify sortition
    if not utils.verifySortition(message.pub_key, message.payload.priority_proposal_payload.vrf_hash, message.payload.priority_proposal_payload.proof, message.payload.prev_block_hash, message.payload.priority_proposal_payload.round, 0, t_proposer, None, message.payload.stake, ctx['W']):
        return None
    # Check whether proposal is coming from highest priority proposer
    if node.max_priority_proposal_message and not node.max_priority_proposal_message.pub_key == message.pub_key:
        return None
    node.block_proposal_message_heard = message
    # relay this message
    for neighbour in node.getNeighbourIds():
        event = simpy.events.Timeout(env, delay=node.getBlockDelay(neighbour), value=(env, neighbour, message))
        event.callbacks.append(verifyAndGossip)
 
def verifyAndGossipCommitteeVote(env, node, message):
    node.votes_heard.append(message)
    # relay this message
    for neighbour in node.getNeighbourIds():
        event = simpy.events.Timeout(env, delay=node.getNonBlockDelay(neighbour), value=(env, neighbour, message))
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
        elif type(message.payload).__name__ == "CommitteeVotePayload":
            verifyAndGossipCommitteeVote(env, node, message)

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

class CommitteeVotePayload():
    def __init__(self, prev_block_hash, curr_block_hash, round, step, j, vrf_hash, vrf_proof):
        self.prev_block_hash = prev_block_hash
        self.curr_block_hash = curr_block_hash
        self.round = round
        self.step = step
        self.j = j
        self.vrf_hash = vrf_hash
        self.vrf_proof = vrf_proof

    def __str__(self):
        return str(self.prev_block_hash) + str(self.curr_block_hash) + str(self.round) + str(self.step) + str(self.j) + str(self.vrf_hash) + str(self.vrf_proof) 

class Message:
    def __init__(self, payload, priv_key, pub_key):
        self.payload = payload
        self.pub_key = pub_key
        self.r, self.s = utils.signMessage(str(payload), priv_key)


class Block:
    def __init__(self, prev_block_hash, random_string=str(random.getrandbits(256)),prev_block_pointer=None):
        self.prev_block_hash = prev_block_hash
        self.random_string = random_string
        self.prev_block_pointer = prev_block_pointer
    def __str__(self):
        return self.random_string
    def hash(self):
        return utils.hashBlock(str(self))

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
        global pkiddict
        self.id = id
        self.priv_key, self.pub_key = utils.generateKeys()
        self.stake = random.randint(1,50) #Assign random uniform stake
        self.block_pointer = GenesisBlock()
        self.round = 0
        self.max_priority_proposal_message = None
        self.env = env
        # Ref: https://simpy.readthedocs.io/en/latest/examples/process_communication.html
        self.rcv_pipe = simpy.Store(env)
        pkiddict[str(self.pub_key)] = self.id
        self.logfile = open("./logs/"+str(self.id)+".log", 'w+')

    def __str__(self):
        return str(self.id)
    
    def log(self, message):
        self.logfile.write(message)

    def getNeighbourIds(self):
        return [n for n in G[self.id]]

    def getBlockDelay(self, neighbour_id):
        return G.edges[self.id, neighbour_id, 0]['block_delay']

    def getNonBlockDelay(self, neighbour_id):
        return G.edges[self.id, neighbour_id, 0]['non_block_delay']

    def gossip(self, message, is_block):
        # Message = <Payload||Public Key|| Meta data for Signature verification>
        if message and not self.faulted:
            for neighbour in self.getNeighbourIds():
                # self.log("%d neighbour %d\n"%(self.id, neighbour))
                event = simpy.events.Timeout(self.env, delay=self.getBlockDelay(neighbour) if is_block else self.getNonBlockDelay(neighbour), value=(self.env, neighbour, message))
                event.callbacks.append(verifyAndGossip)
        # return env.timeout(timeout)
    def committeeVote(self, step, t, value):
        hash, proof, j = utils.sortition(self.priv_key, str(self.block_pointer.hash()), self.round, step, t, "committee", self.stake, ctx['W'] )
        self.log("%d: Sortition hash, proof, j: %s, %s, %d"%(self.env.now, str(hash), str(proof), str(j)))
        if j > 0 :
            self.log ("%d: %d selected in committee\n"%(self.env.now, self.id))
            committee_vote_payload = CommitteeVotePayload(str(self.block_pointer.hash()), str(value), self.round, step, j, hash, proof)
            message = Message(committee_vote_payload, self.priv_key, self.pub_key)
            self.gossip(message, False)
    
    def processMsg(self, t, message):
        if message.payload.prev_block_hash != utils.hashBlock(str(self.block_pointer)):
            return 0, None, None
        votes = utils.verifySortition(message.pub_key, message.payload.vrf_hash, message.payload.vrf_proof, message.payload.prev_block_hash, message.payload.round, message.payload.step, t, "committee", ctx['weight'][str(message.pub_key)], ctx['W'])
        return votes, message.payload.curr_block_hash, message.payload.vrf_hash

    def countVotes(self, step, T, t):
        self.counts = {}
        self.voters = []
        for message in self.votes_heard:
            votes, value, sorthash = self.processMsg(t, message)
            if message.pub_key in self.voters or votes == 0:
                continue
            self.voters.append(message.pub_key)
            self.counts[value] = votes if value not in self.counts else self.counts[value] + votes
            if self.counts[value] > T * t:
                return value
        return None
    
    def byzagreement(self,round,block,t_step):
        hblock = yield from self.reduction(utils.hashBlock(str(block)),t_step)
        self.log('%d: %d Result of Reduction is %s, %d\n'%(self.env.now,self.id,str(hblock),t_step))
        hblock1 = yield from self.binarybyzagreement(round,hblock,t_step)
        yield self.env.timeout(L_step)
        r = self.countVotes('FINAL',T_final,t_final)
        if hblock1 == r :
            self.log('%d:Final consensus is achieved with block %s\n'%(self.env.now,str(block)))
            return 'FINAL',block
        else :    
            self.log('%d:Tentative consensus is achieved with block %s\n'%(self.env.now,str(block)))
            return 'TENTATIVE',block
    
    
    def commonCoin(self, step, t):
        minhash  = 2**256
        for m in self.votes_heard:
            votes, value, sorthash = self.processMsg(t, m)
            for j in range(1, votes):
                h = int(utils.hashBlock(str(sorthash) + str(j)), base=16)
                if h < minhash :
                    minhash = h
        self.log('Result of Common Coin : %s\n'%(str(minhash % 2)))
        return minhash % 2
         
    def binarybyzagreement(self,round,block_hash,t_step):
        step = 3
        r = block_hash
        eblock = Block(self.block_pointer.hash(),'Empty',self.block_pointer)
        empty_hash = utils.hashBlock(str(eblock))
        while step < MAX_STEPS :
            self.committeeVote(step, t_step, r)
            yield self.env.timeout(L_step)
            r = self.countVotes(step,T_step,t_step)
            if r == None :
                r = block_hash
            elif r != empty_hash :
                for s in range(step+1,step+4) :
                    self.committeeVote(s, t_step, r)
                if step == 3 :
                    self.committeeVote("FINAL", t_final, r)
                return r
            step += 1

            self.committeeVote(step, t_step, r)
            yield self.env.timeout(L_step)
            r = self.countVotes(step,T_step,t_step)
            if r == None :
                r = block_hash
            elif r == empty_hash :
                for s in range(step+1,step+4) :
                    self.committeeVote(s, t_step, r)
                return r
            step += 1

            self.committeeVote(step, t_step, r)
            yield self.env.timeout(L_step)
            r = self.countVotes(step,T_step,t_step)
            if r == None:
                if self.commonCoin(step, t_step) == 0:
                    r = block_hash
                else:
                    r = empty_hash
            step += 1
        self.hangForever()

    def hangForever(self):
        self.log("%d: Hanging up %d\n"%(self.env.now, self.id))
        self.env.timeout(2**256)

    def reduction(self, hblock,t_step):
        self.votes_heard = []
        self.committeeVote(3, t_step, str(hblock))
        yield self.env.timeout(L_block + L_step)
        # self.log ("%d: %d heard %d votes\n"%(self.env.now, self.id, len(self.votes_heard)))
        # Count received votes
        hblock1 = self.countVotes(3, T_step, t_step)
        self.log("%d: %d got max votes for %s\n"%(self.env.now,self.id, hblock1))
        eblock = Block(self.block_pointer.hash(),'Empty',self.block_pointer)
        ehash = utils.hashBlock(str(eblock))
        self.votes_heard = []
        if hblock1 == None :
            self.committeeVote(4, t_step,str(ehash))
        else :
            self.committeeVote(4, t_step,str(hblock1))
        yield self.env.timeout(L_step)
        hblock2 = self.countVotes(4, T_step, t_step)
        self.votes_heard = []
    
        if hblock2 == None :
            self.log('%d: %d Result of Reduction is Empty Hash\n'%(self.env.now,self.id))
            return ehash
        else :
            self.log('%d: %d Result of Reduction is \n'%(self.env.now,self.id),hblock2)
            return hblock2    

    def start(self, t_step,fault_flag):
        # starts the simulation process for this node
        self.emptyblocks = 0
        while self.round < MAX_ROUNDS:
            self.block_proposal_message_heard = None
            self.priority_proposal_messages_heard = []
            self.messages_seen = []
            self.votes_heard = []
            self.is_block_proposer = False
            self.is_committee_member = False
            self.faulted = False
            # 1. After consensus on a block in the previous round, each node queries PRG
            # 2. With the output of the PRG and τ proposer = 20, each node should check whether it has been selected as a block proposer or not
            hash, proof, j = utils.sortition(self.priv_key, str(self.block_pointer.hash()), self.round, 0, t_proposer, None, self.stake, ctx['W'] )
            self.log("%d: Sortition hash, proof, j: %s, %s, %d"%(self.env.now, str(hash), str(proof), str(j)))
            message = None
            if j > 0:
                self.log("%d: %d selected as priority proposer\n"%(self.env.now,self.id))
                # 3. In case a node is selected as a block proposer, compute priority for each of the selected sub-user.
                priority = utils.evaluatePriority(str(hash), j)
        
                # 4. After computing priority, gossip a message with the highest priority sub-user information.
                priority_proposal_payload = PriorityProposalPayload(self.round, hash, proof, j, priority)
                message = Message(priority_proposal_payload, self.priv_key, self.pub_key)
                self.max_priority_proposal_message = message

                # 5. Each proposer node will then wait for time λ proposer = 3 seconds to hear priorities broadcast by other proposer nodes of the network.
                self.gossip(message, False)
            yield self.env.timeout(L_proposer)
            # If selected as priority proposal, need to measur stuff for 2.2. Comment out after use
            if j>0:
                proposer_count[pkiddict[str(self.max_priority_proposal_message.pub_key)]] = 1 if pkiddict[str(self.max_priority_proposal_message.pub_key)] not in proposer_count else proposer_count[pkiddict[str(self.max_priority_proposal_message.pub_key)]] +1
            yield self.env.timeout(1)
            self.priority_proposal_messages_heard.sort(key=lambda x: x.payload.priority)
            self.log("Priority proposals heard:\n")
            for item in self.priority_proposal_messages_heard:
                self.log(str(item.payload)+"\n")

            # Experiment 2.3 Fail stop adversary fails now
            if fault_flag[self.id] != 1 :
                self.faulted = True
            # 6. The node with the highest priority creates a block proposal and broadcast it to the network.
            if self.max_priority_proposal_message and self.max_priority_proposal_message.pub_key == self.pub_key :
                # self.log (proposer_count)
                # plt.title('View of proposers for each other')
                # plt.xlabel("Node ID")
                # plt.ylabel("No. of proposers who consider this max priority")
                # plt.bar(range(len(proposer_count)), proposer_count.values(), align='center')
                # plt.xticks(range(len(proposer_count)), list(proposer_count.keys()))
                # plt.show()
                self.is_block_proposer = True
                self.log("%d: %d selected as highest priority block proposer\n"%(self.env.now,self.id))
   
                block_proposal_payload = BlockProposalPayload(self.block_pointer.hash(), self.max_priority_proposal_message.payload, self.stake)
                message = Message(block_proposal_payload, self.priv_key, self.pub_key)
                self.gossip(message, True)

            yield self.env.timeout(L_step)
            #self.log ("%d: %d heard block_proposal_message %s\n"%(self.env.now, self.id, str(self.block_proposal_message_heard.payload)))

            if self.block_proposal_message_heard:
                block = Block(self.block_proposal_message_heard.payload.prev_block_hash, self.block_proposal_message_heard.payload.random_string,self.block_pointer)
            # If they do not hear a Block proposal from the highest priority block-proposer within this period they commit vote for a Empty Block
            else:
                block = Block(self.block_pointer.hash(),"Empty",self.block_pointer)
            #yield from self.reduction(block.hash())

            new_block_pointer = yield from self.byzagreement(self.round,block,t_step)
            self.block_pointer = new_block_pointer[1]
            if self.block_pointer.random_string == 'Empty':
                self.emptyblocks+=1
            yield self.env.timeout(2000)
            self.log('Block No. %d is created\n'%(self.round+1))
            self.log('Blockchain Traversal\n')
            self.traverseBlockchain(self.round+1)
            self.round += 1  
        self.logfile.close()          

    def traverseBlockchain(self,round):
        tmp = self.block_pointer
        while tmp :
            self.log('Block No. %d : %s\n'%(round,str(tmp)))
            if type(tmp) != type(GenesisBlock()) :
                tmp = tmp.prev_block_pointer
            else :
                tmp = None
            round-=1

            
        
def simulate(t_step,fault_flag):

    #########################################
    # Create an environment and start the setup process
    print('Algorand Simulator')
    env = simpy.Environment()
    random.seed(RANDOM_SEED)  # This helps reproducing the results
    for i in range(N):
        n = Node(i, env)
        nodes.append(n)
        ctx['W'] += n.stake
        ctx['weight'][str(n.pub_key)] = n.stake 
        #print("%d stake: %d\n"%(nodes[i].id, nodes[i].stake))
        env.process(nodes[i].start(t_step,fault_flag))
    print("Created nodes")

    env.run(until=SIM_TIME*64)
    for i in range(N):
        if fault_flag[i] == 1:
            print('Number of Empty Blocks = ',nodes[i].emptyblocks)
            break
    print('End of Simulation')
    

    
        
            

#########################################
# Setup nodes 

nodes = []
fault_flag = [0]*256
emptyblock = 0
if __name__ == '__main__' :
    fraction = 0.5
    fault_flag = utils.generateRandomBinaryList(fraction,256)
    simulate(32,fault_flag)
    mean_stakes,count = utils.mean_sub_user,utils.count
    mean_stakes = [a/count for a in mean_stakes]
    # plt.title('Stakes vs Mean Sub Users selected')
    # plt.plot(list(range(52)),mean_stakes)
    # plt.show()
    # self.log('Number of Empty Blocks = ',emptyblock/256)
