from fastecdsa import keys,curve,ecdsa
from hashlib import sha384
import random
import numpy as np

def generateKeys():
    priv_key,pub_key = keys.gen_keypair(curve.P256) # Refer https://safecurves.cr.yp.to/ Options : P256,P224,...
    return [priv_key,pub_key]

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

# For testing Purpose Only

if __name__ == '__main__' :
    priv_key,pub_key = generateKeys()  # Private keys in ECDSA are integers while Public Key are points on curve
    l = signMessage('Extremers',priv_key)
    print(verifySignature(l[0],l[1],'Extremers',pub_key))
    print(verifySignature(l[0],l[1],'Extremerso',pub_key))
    priv_key,pub_key = generateKeys()
    print(verifySignature(l[0],l[1],'Extremers',pub_key))
    print(generateNumberOfNeighbors())


