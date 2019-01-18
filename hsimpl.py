import threading
import socket
import time
import pickle
import math

class Message :

	def __init__(self,direction,nodeId,hopcount) :
		self.direction = direction
		self.nodeId = nodeId
		self.hopcount = hopcount

	def messageToString(self) :
		return self.direction+':'+str(self.nodeId)+':'+str(self.hopcount)

	def stringToMessage(self,strm):
		parts = strm.split(':')
		self.direction = parts[0]
		self.nodeId = int(parts[1])
		self.hopcount = int(parts[2])

	def paddedString1024(self) :
		ans = self.messageToString()
		while len(ans) != 1024 :
			ans = ans + '$'
		return ans

	def unpaddedString(self,strm) :
		strm = strm[:strm.index('$')]
		return strm		

class Node :

	def  __init__(self,NodeId,NodeHost,NodePort,clockwiseNeighbor,antiClockwiseNeighbor):
		
		# Base
		self.NodeId = NodeId
		self.NodeHost = NodeHost
		self.NodePort = NodePort
		self.clockwiseNeighbor = clockwiseNeighbor
		self.antiClockwiseNeighbor = antiClockwiseNeighbor
		self.status = 'Active'
		
		# Message Handling
		self.sendBufferClockwise = []
		self.sendBufferAntiClockwise = []
		self.receiveBufferClockwise = []
		self.receiveBufferAntiClockwise = []

		# Connection Purpose
		self.endpoint = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.endpoint.bind((self.NodeHost,self.NodePort))
		self.clockwiseNeighborConnection = None
		self.antiClockwiseNeighborConnection = None


	def joinRing(self,clockwiseNeighbor,antiClockwiseNeighbor):
		

		self.clockwiseNeighborConnection = socket.socket()
		state = 0
		while state == 0 :
			try :
				self.clockwiseNeighborConnection.connect(('',clockwiseNeighbor))
			except :
				continue
			state = 1

		self.antiClockwiseNeighborConnection = socket.socket()

		state = 0
		while state == 0 :
			try :
				self.antiClockwiseNeighborConnection.connect(('',antiClockwiseNeighbor))
			except :
				continue
			state = 1
		
	def sendMessageClockwise(self,message):
		self.clockwiseNeighborConnection.send(message.paddedString1024().encode())		

	def sendMessageCounterClockwise(self,message):
		self.antiClockwiseNeighborConnection.send(message.paddedString1024().encode())

	def transition(self,message) :
		global n
		for phase in range(int(math.log2(n))) :
			if self.status == 'Active' :
				self.sendMessageClockwise(Message('Clockwise',self.NodeId,2**phase))
				self.sendMessageCounterClockwise(Message('CounterClockwise',self.NodeId,2**phase))


def receiver(node) :
	global n
	node.endpoint.listen()
	con1,addr1 = node.endpoint.accept()
	con2,addr2 = node.endpoint.accept()
	time.sleep(5)
	for phase in range(int(math.log2(n))) :
			for i in range(3) :
				msg = Message('Clockwise',0,0)				
				msgstr = msg.unpaddedString(con1.recv(1024).decode())
				msg.stringToMessage(msgstr)
				#print('Message received at Node ',node.NodeId,' ',msgstr,' from 1')
				if msg.hopcount-1 != 0 :
					if msg.nodeId > node.NodeId :
						
				if msg.hopcount-1 == 0 and msg.nodeId > node.NodeId :

				msg = Message('Clockwise',0,0)				
				msgstr = msg.unpaddedString(con2.recv(1024).decode())
				msg.stringToMessage(msgstr)
				#print('Message received at Node ',node.NodeId,' ',msgstr,' from 2')


			


def launcher(nodeId,nodeHost,nodePort,clockwiseNeighbor,antiClockwiseNeighbor) :
	
	x = Node(nodeId,nodeHost,nodePort,clockwiseNeighbor,antiClockwiseNeighbor)
	t1 = threading.Thread(target=receiver,args=(x,))
	t1.start()
	x.joinRing(clockwiseNeighbor,antiClockwiseNeighbor)
	time.sleep(5)
	x.transition(None)
	t1.join()

	
if __name__ == "__main__" :

	nodeseed = int(input("Enter seed port number : "))
	n = int(input("Number of participants : "))
	threadlist = []
	for i in range(n):
		nodeId = int(input("Enter Node ID : "))
		nodeHost = 'localhost'
		nodePort = nodeseed+i
		if i != n-1 :
			clockwiseNeighbor = nodePort+1
		else :
			clockwiseNeighbor = nodeseed
		if i != 0 :
			antiClockwiseNeighbor = nodePort-1
		else :
			antiClockwiseNeighbor = nodeseed+n-1
		t = threading.Thread(target=launcher,args=(nodeId,nodeHost,nodePort,clockwiseNeighbor,antiClockwiseNeighbor,))
		threadlist.append(t)
		t.start()


	for t in threadlist :
		t.join()










		