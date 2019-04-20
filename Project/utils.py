from functools import reduce
from fastecdsa import keys,curve,ecdsa
from hashlib import sha384
from operator import mul
from fractions import Fraction
import random
import numpy as np

def generateKeys():
    priv_key,pub_key = keys.gen_keypair(curve.P256) # Refer https://safecurves.cr.yp.to/ Options : P256,P224,...
    return priv_key,pub_key

def generateNumberOfNeighbors():
    return random.choice(list(range(4,9)))

def generateBlockDelay():
    return max(0,np.random.normal(200,400))

def generateNonBlockDelay():
    return max(0,np.random.normal(30,64))

def signMessage(message,priv_key):
    r,s = ecdsa.sign(message,priv_key)
    return [r,s]

def verifySignature(r,s,message,pub_key):
    return ecdsa.verify((r,s),message,pub_key)

def assignStake():
    return random.choice(list(range(1,51)))

def generatePRGValue(seed):
    random.seed(a=seed)
    return random.randrange(0,2**256)

def sortition(priv_key,seed,threshold,role,userweight,totalweight):
    message = generatePRGValue(seed)
    signedMessage = signMessage(message,priv_key)
    successProb = threshold/totalweight
    j=0
    v = signedMessage/2**256
    while v < binomialSum(j,userweight,successProb) or v >= binomialSum(j+1,userweight,successProb) :
        j=j+1
    return [signedMessage,j]

def binomialSum(j,w,p):
    sum = 0
    for k in range(j+1):
        sum = sum + sympy.binomial(w,k) * (p**k) * ((1-p)**(w-k))
    return sum

# For testing Purpose Only

if __name__ == '__main__' :
    priv_key,pub_key = generateKeys()  # Private keys in ECDSA are integers while Public Key are points on curve
    l = signMessage('Extremers',priv_key)
    print(verifySignature(l[0],l[1],'Extremers',pub_key))
    print(verifySignature(l[0],l[1],'Extremerso',pub_key))
    priv_key,pub_key = generateKeys()
    print(verifySignature(l[0],l[1],'Extremers',pub_key))
    print(generateNumberOfNeighbors())
    print(binomialSum(1,4,2))
    

