import socket
import threading

class Node :

	def __init__(self,nodeId,port,hostname,predecessor,successor,lengthOfRing):
		
		self.nodeId = nodeId
		self.port = port
		self.hostname = hostname
		self.predecessor = predecessor
		self.successor = successor
		self.lengthOfRing = lengthOfRing
		self.finger = []
		self.endpoint = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.endpoint.bind((self.hostname,self.port))

	def join(self,nodeIdInTargetRing):

		self.predecessor = None 
		self.successor = nodeIdInTargetRing.find_successor(self)

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




			

