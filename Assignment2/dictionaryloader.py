import sys
import xmlrpc.client

def consistent_hash(x):
	return int(hash(x) & ((1<<16)-1))

if __name__ == '__main__' :

	if len(sys.argv) != 3 :
		print('Usage : PYTHONHASHSEED=0 python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>')
		sys.exit(1)

	else :
		# try:
			url = sys.argv[1]
			dictFile = sys.argv[2]
			with xmlrpc.client.ServerProxy(url) as proxy :
				with open(dictFile) as dictFileHandle:
					for line in dictFileHandle:
						targetUrl = proxy.find_successor(consistent_hash(line.strip().split(':')[0]))
						with xmlrpc.client.ServerProxy(targetUrl) as targetproxy :
							targetproxy.insert(line)
		# except:
		# 	print('Wrong inputs are supplied')	
		# 	print('Usage : python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>')
