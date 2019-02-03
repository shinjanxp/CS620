import xmlrpc.server
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import math

global engaged
global node

class Node :

	def __init__(self,keys,predecessor,successor,fingerTable,url,nodeId):
		self.keys = keys
		self.predecessor = predecessor
		self.successor = successor
		self.fingerTable = fingerTable
		self.nodeURL = url
		self.engaged = 'No'
		self.nodeId = nodeId

	def unwrap(self,resDict):
		self.keys = resDict['keys']
		self.predecessor = resDict['predecessor']
		self.successor = resDict['successor']
		self.fingerTable = resDict['fingerTable']		


def hasher(target):
	return hash(target) & ((1<<32)-1)



# TO-DO : Implement Join
def join(url) :
	if node.engaged == 'Yes' :
		return None
	else :
		node.engaged = 'Yes'
		key = hasher(url)

		if node.successor == None and node.successor == None :
			node.successor = url
			node.predecessor = url
			newNodeKeys = []
			for i in range(len(node.keys)//2,len(node.keys)) :
				newNodeKeys.append(node.keys[i])
				node.keys.remove(node.keys[i])

			newNodePredecessor = node.nodeURL
			newNodeSuccessor = node.nodeURL
			newNodeFingerTable = []
			for i in range(32) :
				newNodeFingerTable.append(node.nodeURL)
				node.fingerTable.append(url)
			newNode = Node(newNodeKeys,newNodePredecessor,newNodeSuccessor,newNodeFingerTable,url,0)
			join_done(url)
			return newNode

		else :
			if int(math.fabs(hasher(node.successor) - key)) > int(math.fabs(hasher(node.nodeURL) - key)) : 
				node.successor = url
				node.predecessor = url
				newNodeKeys = []
				for i in range(len(node.keys)//2,len(node.keys)) :
					newNodeKeys.append(node.keys[i])
					node.keys.remove(node.keys[i])

				newNodePredecessor = node.nodeURL
				newNodeSuccessor = node.nodeURL
				newNodeFingerTable = []
				for i in range(32) :
					newNodeFingerTable.append(node.nodeURL)
					node.fingerTable.append(url)
				newNode = Node(newNodeKeys,newNodePredecessor,newNodeSuccessor,newNodeFingerTable,url,0)
				join_done(url)
				return newNode
			else :
				print('Here')
				with xmlrpc.client.ServerProxy(node.successor) as proxy :
					newNode = proxy.join(nodeURL)
					join_done(url)
					return newNode


# TO-DO : Implement Join Done
def join_done(url) :
	node.engaged = 'No'
	return True

# TO-DO : Implement Find
def find_node(key,traceFlag):
	pass

# TO-DO : Implement Insert
def insert(word):
	pass

# TO-DO : Implement Lookup
def lookup(word):
	pass

# TO-DO : Implement Print Finger Tables
def printFingerTable():
	pass

if __name__ == '__main__':
	
	nodeHost = input('Please Enter Node IP : ')
	nodePort = int(input('Please Enter Port Number : '))
	nodeId = input('Please Enter Node Id : ')
	nodeURL = 'http://'+nodeHost+':'+str(nodePort)+'/'
	node = Node([],None,None,[],nodeURL,nodeId)

	server = SimpleXMLRPCServer((nodeHost,nodePort))

	server.register_function(join,'join')
	server.register_function(join_done,'join_done')
	listener = threading.Thread(target=server.serve_forever)
	listener.start()	

	# if nodeId == 'node-0' :
	# 	server.register_function(join,'join')
	# 	server.register_function(join_done,'join_done')
	# 	server.serve_forever()

	if nodeId != 'node-0' :
		targetURL = input('Please enter target URL : ')
		with xmlrpc.client.ServerProxy(targetURL) as proxy :
			node.unwrap(proxy.join(nodeURL))
			print('Successor of Node ',nodeId,': ',node.successor)
			print('Predecessor of Node ',nodeId,': ',node.successor)



	listener.join()		