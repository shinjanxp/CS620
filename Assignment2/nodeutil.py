import threading
from xmlrpc.server import SimpleXMLRPCServer

def consistent_hash(x):
	return hash(x) & ((1<<32)-1)

class Node :

	def __init__(self,host, port):
		self.port = port
		self.host = host
		self.finger = []
		self.server = SimpleXMLRPCServer((self.host, self.port))
		print("Starting rpc server on port "+str(self.port)+"...")
		self.server.register_function(self.join, "join")
		self.server.register_function(self.join_done, "join_done")
		self.server.register_function(self.find_node, "find_node")
		self.server.register_function(self.insert, "insert")
		self.server.register_function(self.lookup, "lookup")
		self.server.register_function(self.printFingerTable, "printFingerTable")
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.start()
		self.server_thread.join()


	# rpc methods
	def join(self,url):
		self.predecessor = None 
		# self.successor = nodeIdInTargetRing.find_successor(self)
	def join_done(self, url):
		pass
	def find_node(self, key, traceFlag):
		return "I am node " +  str(consistent_hash("http://"+self.host+":"+str(self.port)))
	def insert(self, word):
		pass
	def lookup(self, word):
		pass
	def printFingerTable(self):
		pass


	def find_successor(self,targetNode) :
		
		if targetNode.nodeId > self.nodeId and targetNode.nodeId <= self.successor.nodeId :
			return self.successor.nodeId

		else :
			checkpoint = closest_preceding_node(targetNode)
			return checkpoint.find_successor(targetNode)

	def find_successor_by_value(self,targetId) :
		
		if targetId > self.nodeId and targetId <= self.successor.nodeId :
			return self.successor.nodeId

		else :
			checkpoint = closest_preceding_node(targetId)
			return checkpoint.find_successor_by_value(targetId)


	def closest_preceding_node(self,targetNode) :

		for i in range(self.lengthOfRing - 1 , -1 , -1) :
			if self.finger[i] > self.id and self.finger[i] < targetNode.nodeId :
				return 	self.finger[i]
		return self.nodeId

	def closest_preceding_node_ny_value(self,targetId) :

		for i in range(self.lengthOfRing - 1 , -1 , -1) :
			if self.finger[i] > self.id and self.finger[i] < targetId :
				return 	self.finger[i]
		return self.nodeId

	# Needs	to be called periodically
	def stabilize(self):

		x = self.successor.predecessor
		if x > self.nodeId and x < self.successor.nodeId :
			self.successor = x
		successor.notify(self)

	def notify(self,targetNode):

		if self.predecessor == None or (targetNode.nodeId > self.predecessor.nodeId and targetNode.nodeId < self.nodeId) :
			self.predecessor = targetNode.nodeId

	
	# Needs to be called periodically
	def fix_fingers(self):
		for i in range(0,self.lengthOfRing) :
			finger[i] = self.find_successor_by_value(self.nodeId+2**i)



if __name__ == "__main__":
	node = Node("localhost",8000)
