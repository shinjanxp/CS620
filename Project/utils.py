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
    print('the message : ',message)
    r,s = ecdsa.sign(message,priv_key)
    return [r,s]

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
    j=0
    v = (sum(signedMessage)%(2**256))/2**256
    while (v < binomialSum(j,userweight,successProb) or v >= binomialSum(j+1,userweight,successProb)) and (j<userweight) :
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
    for k in range(j+1):
        sum = sum + sympy.binomial(w,k) * (p**k) * ((1-p)**(w-k))
    return sum

def evaluatePriority(signedMessage,subuserIndex):
    h = hashlib.sha256()
    h.update((signedMessage+str(subuserIndex)).encode())
    return h.hexdigest()

def hashBlock(message):
    h = hashlib.sha256()
    h.update(message.encode())
    return h.hexdigest()

# For testing Purpose Only

if __name__ == '__main__' :
    priv_key,pub_key = generateKeys()  
    l = signMessage('Extremers',priv_key)
    #print(verifySignature(l[0],l[1],'Extremers',pub_key))
    #print(verifySignature(l[0],l[1],'Extremerso',pub_key))
    priv_key,pub_key = generateKeys()
    #print(verifySignature(l[0],l[1],'Extremers',pub_key))
    #print(generateNumberOfNeighbors())
    #print('Binomial Sum: ',binomialSum(1,4,0.2))
    #print(generatePRGValue('whoa'))
    m = generatePRGValue('whoa')
    #print(signMessage('43309844026517770324480508592060893747934569917128262563705402482600339672645',priv_key))
    #print(evaluatePriority('axe',1))
    print(sortition(priv_key,evaluatePriority('axe',1),1,2,15,'hehe',12,100))
    hash,proof,j = sortition(priv_key,evaluatePriority('axe',1),1,2,15,'hehe',12,100)
    print(j)
    print(verifySortition(pub_key,hash,proof,evaluatePriority('axe',1),1,2,15,'hehe',12,100))


