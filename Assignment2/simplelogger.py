def logit(message):
	logger = open(myip+"_logs.txt","a")
	logger.write(message+"\n")
	logger.close()

