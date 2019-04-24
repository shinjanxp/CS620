from functools import reduce
from fastecdsa import keys,curve,ecdsa
import hashlib
from operator import mul
from fractions import Fraction
import random
import numpy as np
import sympy

# Used for generating Key Pairs for each node
# Private keys in ECDSA are integers while Public Key are points on curve P256
def generateKeys():
    priv_key,pub_key = keys.gen_keypair(curve.P256) # Refer https://safecurves.cr.yp.to/ Options : P256,P224,...
    return priv_key,pub_key


# For ensuring connected network
def generateNumberOfNeighbors():
    return random.choice(list(range(4,9)))


# For Randomizing Blocking and Non Blocking Delays
def generateBlockDelay():
    return max(0,np.random.normal(200,400))

def generateNonBlockDelay():
    return max(0,np.random.normal(30,64))


# For signing and verifying messages 
def signMessage(message,priv_key):
    r,s = ecdsa.sign(message,priv_key)
    return r,s

def verifySignature(r,s,message,pub_key):
    return ecdsa.verify((r,s),message,pub_key)

def assignStake():
    return random.choice(list(range(1,51)))

def generatePRGValue(seed):
    random.seed(a=seed)
    return random.randrange(0,2**256)

def sortition(priv_key,prevBlockHash,roundNo,stepNo,threshold,role,userweight,totalweight):
    seed = str(prevBlockHash)+str(roundNo)+str(stepNo)
    message = generatePRGValue(seed)
    signedMessage = signMessage(str(message),priv_key)
    successProb = threshold/totalweight
    #print('Probability : ',successProb)
    j=0
    v = int(hashBlock(str(signedMessage)),base=16)/2**256 #(sum(signedMessage)%(2**256))/2**256
    while ((v < binomialSum(j,userweight,successProb)) or (v >= binomialSum(j+1,userweight,successProb))) and (j<=userweight) :
        j=j+1
    return (sum(signedMessage)%(2**256)),signedMessage,j

def verifySortition(pub_key,hash,signedMessage,prevBlockHash,roundNo,stepNo,threshold,role,userweight,totalweight):
    seed = str(prevBlockHash)+str(roundNo)+str(stepNo)
    message = generatePRGValue(seed)
    if verifySignature(signedMessage[0],signedMessage[1],str(message),pub_key) :
        successProb = threshold/totalweight
        j=0
        v = hash/2**256
        while (v < binomialSum(j,userweight,successProb) or v >= binomialSum(j+1,userweight,successProb)) and (j<userweight) :
            j=j+1
        return j
    else :
        return 0

def binomialSum(j,w,p):
    sum = 0
 #   print('p = ',p)
    for k in range(j):
        sum = sum + sympy.binomial(w,k) * (p**k) * ((1-p)**(w-k))
 #   print('B(%d,%d,%f) : %f'%(j,w,p,sum))
    return sum

def evaluatePriorityHash(signedMessage,subuserIndex):
    h = hashlib.sha256()
    h.update((signedMessage+str(subuserIndex)).encode())
    return h.hexdigest()

def evaluatePriority(signedMessage,noOfSubUsers):
    max = evaluatePriorityHash(signedMessage,0)
    for i in range(noOfSubUsers):
        x = evaluatePriorityHash(signedMessage,i)
        if max < x:
            max = x
    return max

def hashBlock(message):
    h = hashlib.sha256()
    h.update(message.encode())
    return h.hexdigest()

# For testing Purpose Only

if __name__ == '__main__' :
    
    priv_key,pub_key = generateKeys()  
    l = signMessage('Extremers',priv_key)
    
    # --------- Unit Test for Signature Verification ---------------
    #print(verifySignature(l[0],l[1],'Extremers',pub_key))
    #print(verifySignature(l[0],l[1],'Extremerso',pub_key))   
    #priv_key,pub_key = generateKeys()
    #print(verifySignature(l[0],l[1],'Extremers',pub_key))

    # --------- Unit Test for Number of Neighbours generation ---------------
    #print(generateNumberOfNeighbors())

    # --------- Unit Test for Number of Binomial Sum ---------------
    #print('Binomial Sum: ',binomialSum(1,4,0.2))

    # --------- Unit Test for Number of PRG generation ---------------
    #print(generatePRGValue('whoa'))

    
    # --------- Unit Test for Sortition and Verify Sortition ---------------
    # Test Desc : Number of Subusers selected should be proportional to user weight
    m = generatePRGValue('whoa')
    print(sortition(priv_key,evaluatePriority('axe',1),1,2,15,'hehe',20,100))
    hash,proof,j = sortition(priv_key,evaluatePriority('axe',1),1,2,15,'hehe',20,100)
    print(j)
    print(verifySortition(pub_key,hash,proof,evaluatePriority('axe',1),1,2,15,'hehe',20,100))
    priv_key2,pub_key2 = generateKeys()
    print(sortition(priv_key2,evaluatePriority('axe',1),1,2,15,'hehe',80,100))
    hash,proof,j = sortition(priv_key2,evaluatePriority('axe',1),1,2,15,'hehe',80,100)
    print(j)
    print(verifySortition(pub_key2,hash,proof,evaluatePriority('axe',1),1,2,15,'hehe',80,100))


