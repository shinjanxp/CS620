import threading, sys, time, xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import datetime

FINGER_TABLE_SIZE = 16


def consistent_hash(x):
	# return hash(x) & ((1<<32)-1)
	return int(hash(x) & ((1<<16)-1))

def is_in_interval(value, start, end):
	if not value:
		return False
	if start < end:
		if value >= start and value <= end:
			return True
		else:
			return False
	elif start > end:
		if value > end and value < start:
			return False
		else:
			return True
	else:
		return True

class Node :

	def __init__(self,host, port, node_0_url=None):
		self.port = port
		self.host = host
		self.url = "http://" + self.host + ":" + str(self.port)
		self.finger = []
		self.next = 0
		self.server = SimpleXMLRPCServer((self.host, self.port))
		print("Starting rpc server on port "+str(self.port)+"...")
		self.node_id = consistent_hash(self.url)
		print("I am node " + str(self.node_id))
		self.data = {}

		# register rpcs
		self.server.register_function(self.join, "join")
		self.server.register_function(self.join_done, "join_done")
		self.server.register_function(self.find_successor, "find_successor")
		self.server.register_function(self.insert, "insert")
		self.server.register_function(self.lookup, "lookup")
		self.server.register_function(self.printFingerTable, "printFingerTable")
		self.server.register_function(self.get_predecessor, "get_predecessor")
		self.server.register_function(self.notify, "notify")
		self.server.register_function(self.stabilize, "stabilize")
		self.server.register_function(self.fix_fingers, "fix_fingers")
		# RPC thread
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.start()
		
		if node_0_url:
			while True:
				with xmlrpc.client.ServerProxy(node_0_url) as proxy:
					success, self.successor, self.predecessor, self.finger = proxy.join(self.url)
					if success == 404:
						time.sleep(5)
						continue
					self.log_local(""+self.successor + "" + str(self.predecessor) + str(self.finger))

				self.stabilize()
				self.log_local("After stabilize, pre, succ: " + str(self.predecessor) + self.successor)
				if self.predecessor:
					with xmlrpc.client.ServerProxy(self.predecessor) as proxy:
						proxy.stabilize()

				self.fix_fingers()
				with xmlrpc.client.ServerProxy(node_0_url) as proxy:
					proxy.join_done(self.url)
				break
		else :
			self.create()



		# Fix finger table thread
		self.refresh_thread = threading.Thread(target=self.refresh)
		self.refresh_thread.start()

		self.server_thread.join()


	# RPC definitions

	def join(self,url): # to be invoked at node-0 by all joining nodes
		if self.join_lock:
			return (404, False, False, False)
		self.join_lock = True
		self.log_local("join request received from " + url)
		# self.predecessor = None 
		# with xmlrpc.client.ServerProxy(url) as proxy:
		# 	self.successor = proxy.find_successor(self.node_id)
		# self.finger = [self.successor] * FINGER_TABLE_SIZE
		assigned_key = consistent_hash(url)
		successor = self.find_successor(assigned_key)
		# If I am my successor then I am the only node in the N/W now. set the new node to my successor.
		if self.successor == self.url:
			self.successor = url 
			self.finger[0] = self.successor
		return ( 200, successor, False, [successor]+ [False]*(FINGER_TABLE_SIZE-1),)

	def join_done(self, url):
		self.join_lock = False
		return True

	def find_successor(self, key, traceFlag=False): # returns url of successor of key
		if is_in_interval(key, self.node_id+1, consistent_hash(self.successor)):
			self.log_local("Successor found " + self.successor)
			self.log_common("Successor found " + self.successor)
			return self.successor
		else:
			n_prime = self.closest_preceding_node(key) 

			with xmlrpc.client.ServerProxy(n_prime) as proxy:
				self.log_local("Executing find_successor on "+ n_prime)
				self.log_common("Executing find_successor on "+ n_prime)
				return proxy.find_successor(key)
		pass

	def insert(self, word):
		key = word.strip().split(':')[0]
		meaning = word.strip().split(':')[1]
		self.data[key] = meaning
		self.log_local('Current Dictionary : ' + str(self.data))
		return True
		

	def lookup(self, word):
		return self.data[word]
		

	def printFingerTable(self):
		pass
	def get_predecessor(self):
		return self.predecessor
	def notify(self, n_prime):
		if not self.predecessor	or is_in_interval(consistent_hash(n_prime), consistent_hash(self.predecessor)+1, self.node_id-1):
			self.predecessor = n_prime
		print("Predecessor: ", self.predecessor)
		return True

	# End RPC definitions

	def create(self):
		self.node_id = consistent_hash(self.url)
		self.predecessor = False
		self.successor = self.url
		self.finger = [self.successor] + [False] * (FINGER_TABLE_SIZE-1)
		self.join_lock = False

	def closest_preceding_node(self,key) : # returns url of closest preceding node to key
		for entry in reversed(self.finger):
			# if consistent_hash(entry) > self.node_id and consistent_hash(entry) < key:
			if is_in_interval(consistent_hash(entry), self.node_id+1, key-1):
				return entry
		return self.url

	def stabilize(self):
		x = None
		with xmlrpc.client.ServerProxy(self.successor) as proxy:
			x = proxy.get_predecessor()

		if is_in_interval(consistent_hash(x), self.node_id+1, consistent_hash(self.successor)-1):
			self.successor = x
			self.finger[0] = self.successor
		with xmlrpc.client.ServerProxy(self.successor) as proxy:
			proxy.notify(self.url)
		self.log_local("Successor: "+ str(self.successor))
		self.log_local("Predecessor: "+ str(self.predecessor))
		return True

	def fix_fingers(self):
		for entry in self.finger:
			self.next = self.next +1
			if self.next > FINGER_TABLE_SIZE:
				self.next = 1
			self.finger[self.next-1] = self.find_successor(self.node_id + 2**(self.next - 1))	
		print (self.finger)
		return True	

	def refresh(self):
		while True:
			self.stabilize()
			time.sleep(1)
			self.fix_fingers()
			print (self.finger)
			print("-----------------------------------------------------------------------------------------")
			time.sleep(10)

	# Loggers
	def log_common(self, message):
		logger = open("logs/common_logs.txt","a")
		now = datetime.datetime.now()
		
		logger.write(now.isoformat() + ":  ["+ self.url +" ("+ str(self.node_id) +")] " + message+"\n")
		logger.close()

	def log_local(self, message):
		logger = open("logs/"+ self.host + "_" + str(self.port) +"_logs.txt","a")
		now = datetime.datetime.now()
		logger.write(now.isoformat() + ":  ["+ self.url +" ("+ str(self.node_id) +")] " + message+"\n")
		logger.close()


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Not enough arguments. Syntax: python3 nodeutil.py <host> <port> <node-0 url, leave blank if this is node-0>")
		sys.exit()
	host = sys.argv[1]
	port = sys.argv[2]

	if len(sys.argv) >=4:
		node = Node(host, int(port), sys.argv[3])
	else:
		node = Node(host, int(port))
