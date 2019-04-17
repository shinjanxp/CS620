import xmlrpc.client
import sys

def consistent_hash(x):
	return int(hash(x) & ((1<<16)-1))

if __name__ == '__main__' :

	if len(sys.argv) != 2 :
		print('Usage : PYTHONHASHSEED=0 python3 client.py <chord-node-url>')
		sys.exit(1)

	else :
		try:
			url = sys.argv[1]
			while True:
				choice = int(input('Enter 1 to do lookup , 2 to exit : '))
				if choice == 1 :
					with xmlrpc.client.ServerProxy(url) as proxy :
							word = input('Enter a word to lookup : ')
							targetUrl = proxy.find_successor(consistent_hash(word), True)
							with xmlrpc.client.ServerProxy(targetUrl) as targetproxy :
								result = targetproxy.lookup(word)
							print('Result : ',result)

				else :
					print('Exiting...')
					break
		except:
		 	print('Wrong inputs are supplied')	
		 	print('Usage : python3 dictionaryloader.py <chord-node-url>')
