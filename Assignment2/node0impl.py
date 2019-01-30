import socket

if __name__ == '__main__':

	dirserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	port = 8080
	dirserver.bind(('',port))
	dirserver.listen(5)
	seedNodes = []
	threads = []
	for i in range(20):
		threads.append(None)
	while True:
		b = True
		client,addr = dirserver.accept()
		for i in range(20) : 
			if threads[i] == None :
				threads[i] = threading.Thread(target=request,args=(client,addr,seedNodes))
				threads[i].start()
				b = False
				break

		if b :
			client.send(("Server is busy , unable to handle any request currently\n").encode())