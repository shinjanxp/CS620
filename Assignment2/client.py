import xmlrpc.client

if __name__ == '__main__' :

	if len(sys.argv) != 2 :
		print('Usage : python3 client.py <chord-node-url>')
		sys.exit(1)

	else :
		try:
			url = sys.argv[1]
			while True:
				choice = input('Enter 1 to do lookup , 2 to exit : ')
				if choice == 1 :
					with xmlrpc.client.ServerProxy(url) as proxy :
							word = input('Enter a word to lookup : ')
							result = proxy.lookup(word)
							print('Result : ',result)

				else :
					print('Exiting...')
					break
		except:
			print('Wrong inputs are supplied')	
			print('Usage : python3 dictionaryloader.py <chord-node-url>')
