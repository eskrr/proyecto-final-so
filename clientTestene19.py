#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The client program sets up its socket differently from the way a server does. Instead of binding to a port and listening, 
# it uses connect() to attach the socket directly to the remote address.

import socket
import sys
import time
import random

politica = sys.argv[1]; seed = sys.argv[2] #política de memoria y semilla del generador random.

# mensajes que el cliente envía al servidor. El primer elemento de cada tuple indica el tiempo en el cual se manda el
# mensaje, a partir del tiempo 0. Pasando los mensajes de inicialización, ese tiempo puede ser modificado de manera aleatoria.

messages = [(0.0,'RealMemory 2'),(0.1,'SwapMemory 4'),(0.2,'PageSize 16'),(0.3,'PoliticaMemory FIFO'),(1,'P 2048 1'), \
		(2,'A 1 1 0'),(3,'A 33 1 1'),(4,'P 32 2'),(5,'A 15 2 0'),(6,'A 82 1 0'), \
		(7,'L 2'),(8,'P 32 3'), \
		(9,'L 1'), (10,'F'), (11, 'E')]
		
# ajusta la política de acuerdo al primer argumento
messages[3] = (0.3, 'PoliticaMemory ' + politica)


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in 
# the server.
		

try:

	previousMsgTime = 0.0
	debug1 = False

	# Send data
	firstTime = True
	for m in messages:
		
		timestamp = float(m[0])
		msg = m[1]
		initialMsg = timestamp < 1.0 #mensajes de inicializacion: don't modify time.
		
		if firstTime:
			firstTime = False
			thisMsgTime = 0.0
			initialTime = time.time()
			if seed != '0': random.seed (int(seed)) #inicializa random generator
		
		else: 
			thisMsgTime = timestamp
		
			#posiblemente altera el thisMsgTime para mensajes excepto los primeros
			if not initialMsg:
				if seed != '0':
					thisMsgTime += random.uniform(-1, 1)
					if thisMsgTime < 0.0: thisMsgTime = timestamp
					if debug1: print >>sys.stderr, 'randomised', thisMsgTime
				
			if thisMsgTime > previousMsgTime: #duermete
				sleepTime =  thisMsgTime - previousMsgTime
				if debug1: print >>sys.stderr, 'sleeptime', sleepTime
				time.sleep(sleepTime)
			else:
				thisMsgTime = previousMsgTime
			
		
		if debug1: print >>sys.stderr, 'antes de calcular timedM', thisMsgTime	
		timedM = msg
			 
		print >>sys.stderr, 'client sending "%s"' % timedM
		sock.sendall(timedM)
		previousMsgTime = thisMsgTime
		
		# Look for the response
		respuesta = sock.recv(256)
		print >>sys.stderr, 'client received "%s"' % respuesta
		timestamp1 = time.time() - initialTime
		if debug1: print >>sys.stderr, 'timestamp', timestamp1
	#end for.
	# sock.close()
	

finally:
	print >>sys.stderr, 'closing socket'
	sock.close()




def main(args):
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

