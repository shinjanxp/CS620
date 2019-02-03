import sys
import xmlrpc.client

if __name__ == '__main__' :

	if len(sys.argv) != 3 :
		print('Usage : python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>')
		sys.exit(1)

	else :
		try:
			url = sys.argv[1]
			dictFile = sys.argv[2]
			dictFileHandle = open(dictFile,'r')
			with xmlrpc.client.ServerProxy(url) as proxy :
					word = dictFileHandle.readline()
					proxy.insert(word)
		except:
			print('Wrong inputs are supplied')	
			print('Usage : python3 dictionaryloader.py <chord-node-url> <path-to-dictionary-file>')
