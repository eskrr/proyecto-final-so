#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import math
from tabulate import tabulate

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)


# Wait for a connection
print >>sys.stderr, 'waiting for a connection'
connection, client_address = sock.accept()

#accept() returns an open connection between the server and client, along with the address of the client. The connection is actually a different socket on another port (assigned by the kernel). Data is read from the connection with recv() and transmitted with sendall().

# *****************************FUNCIONALIDAD***********************************

# Los siguientes mensajes le llegan al servidor al principio de la simulación, y sirven para inicializar parámetros de la simulación: tamaño en kilobytes de la memoria real y del área de swapping, esta última desde luego mucho mayor que la real; y tamaño fijo de las páginas (reales y virtuales) en kilobytes. 

# RealMemory m                // tamaño de la memoria real, en k’s
# SwapMemory n               // tamaño del área de swapping, en k’s
# PageSize p                      // en bytes

# ************************ DEFINICION VARIABLES *******************************
# Como nuestras politicas de reemplazo (FIFO y LIFO) no necesitan bitReferencia, 
# bitModificacion o contador, no seran incluidos en nuestro servidor.
memoriaReal = []            # CONTENIDO DE LISTA: (cada index representa el ID de cada marco real) 
                              # [ 
                              #   [ 
                              #     (idProceso), 
                              #     (idMarcoVirtual) 
                              #   ]
                              # ]
memoriaSwap = []            # CONTENIDO DE LISTA: (cada index representa el ID de cada marco swap) 
                              # [ 
                              #   [ 
                              #     (idProceso), 
                              #     (idMarcoVirtual) 
                              #   ]
                              # ]
tamanoMemoriaReal = None
tamanoMemoriaSwap = None
tamanoPagina = None
nMarcosPaginaReal = None
nMarcosPaginaSwap = None
memoriasDefinidas = False

paginasDisponiblesReal = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco real disponible, ordenado de menor a mayor) 
                              # ]      
paginasDisponiblesSwap = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco swap disponible, ordenado de menor a mayor) 
                              # ]                                                                                   
procesos = []               # CONTENIDO DE LISTA: (cada index representa un proceso, los procesos estan en orden de llegada)
                              # [
                              #     (idProceso),
                              # ]
                            # Utilizado tambien para saber cual proceso reemplazar:
                            #     FIFO: se reeemplaza el primer proceso en llegar, en la lista se borra elimina el primer elemento (shift left)
                            #     LIFO: se reemplaza el ultimo proceso en llegar, en la lista se borra el ultimo elemento                              

def defineMemorias():
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global memoriasDefinidas
	nMarcosPaginaReal = int(math.ceil((tamanoMemoriaReal*1024)/tamanoPagina))
	nMarcosPaginaSwap = int(math.ceil((tamanoMemoriaSwap*1024)/tamanoPagina))
	for i in range (0, nMarcosPaginaReal):
		memoriaReal.append(None)
		paginasDisponiblesReal.append(i)
	for i in range (0, nMarcosPaginaSwap):
		memoriaSwap.append(None)
		paginasDisponiblesSwap.append(i)
	memoriasDefinidas=True
	return

def RealMemory(m):
	global tamanoMemoriaReal
	tamanoMemoriaReal = int(m)
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None):
		defineMemorias()
	return 

def SwapMemory(n):
	global tamanoMemoriaSwap
	tamanoMemoriaSwap = int(n)
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None):
		defineMemorias()  
	return 

def PageSize(p):
	global tamanoPagina
	tamanoPagina = int(p)
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None):
		defineMemorias()  
	return

# Respuestas del servidor al cliente: después de cada uno de estos comandos, el servidor regresa al cliente un mensaje que indica qué fué lo que se recibió; por ejemplo “Recibido - real memory tal y tal”. El cliente siempre despliega (es decir, envía a stderr) el mensaje enviado al servidor, y el mensaje-resultado que el servidor envía de regreso al cliente

# Una vez concluida la inicialización, el cliente podrá enviar al servidor cualquiera de los siguientes comandos:

# PolíticaMemory mm     // la política de memoria a simular. Será el primer comando una vez concluída la inicialización.

def PoliticaMemory(mm):
	return

# P n p   (cargar un proceso)
# Se trata de una solicitud de “n” bytes para cargar un proceso a la memoria.
# “n” podría no ser múltiplo del tamaño de la página 

# “p”  es un número entero arbitrario que indica el identificador de proceso. 
# Ejemplo:

def P(n,p):
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global procesos	
	n = int(n)
	p = int(p)
	nMarcosPagina = int(math.ceil(n/tamanoPagina))
	if(n>tamanoMemoriaReal*1024):
		print >>sys.stderr, "El tamano del proceso no puede ser mas grande que el de la memoria real"
		return

#Caben todos en memoria real
	if(nMarcosPagina <= len(paginasDisponiblesReal)):	
		procesos.append[p) # Agrega a procesos [idProceso]
		for i in range(0, nMarcosPagina):
			memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i] # Modifica la lista:  [indexMarcoReal][idProceso, idMarcoVirtual]

#Caben algunos en memoria real y los demas en memoria swap
	else if(nMarcosPagina > len(paginasDisponiblesReal) and nMarcosPagina-len(paginasDisponiblesReal <= len(paginasDisponiblesSwap))):	
		procesos.append[p) # Agrega a procesos [idProceso]
		for i in range(0, nMarcosPagina):
			memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i] # Modifica la lista:  [indexMarcoReal][idProceso, idMarcoVirtual]	

#Memoria real llena, pero se pueden swapear marcos a memoria swap
	else if(len(paginasDisponiblesReal)==0 and nMarcosPagina <= len(paginasDisponiblesSwap))):	
		procesos.append[p) # Agrega a procesos [idProceso]
		for i in range(0, nMarcosPagina):
			memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i] # Modifica la lista:  [indexMarcoReal][idProceso, idMarcoVirtual]	
			
#Memoria real y Memoria swap llenas
	else:
		print >>sys.stderr, "Memoria Real y Swap llenas"
		return		
	return

# A d p m  
# Es una solicitud para accesar la dirección virtual “d” del proceso “p”. Si “m” es 0, la dirección correspondiente sólo se lee; si es 1, también se modifica.“d” puede tener un valor desde cero hasta la dirección virtual máxima del proceso expresada en bytes. 

# Ejemplo: 

# A 17 5 0  (accesar para lectura la dirección virtual 17 del proceso 5)

def A(d,p,m):
	return

# L p
# Liberar las páginas del proceso “p”.

def L(p):
	return

# PROCESS: Se liberan todas las páginas del proceso “p”, tanto las que estaban en memoria real como aquellas que se encontraban en el área de swapping, quedando varios marcos de página o pedazos del área de swapping vacíos y disponibles para otras operaciones. 

def F():
	return

# F 
# Fin. Es siempre la última línea de un conjunto de especificaciones; pero pueden seguir otras líneas más para otro conjunto de solicitudes, empezando por el comando que indica la política. Habrá al menos dos especificaciones, una para cada política de reemplazo.

def E():
	return

# E
# Exit. Última línea del archivo. 
# PROCESS: se termina la simulación
# OUTPUT: El comando de INPUT y mensaje de despedida...

def call_instruction(data):
	data = data.split()
	print >>sys.stderr, 'Instruccion solicitada: ' + data[0]
	print >>sys.stderr, 'parametros: ' + ''.join(data[1:len(data)])
	# Se ejecuta la instruccion solicitada
	print >>sys.stderr, 'Funciona ejecutar: ' + '{}({})'.format(data[0], ','.join(data[1:len(data)]))      
	eval(data[0])(*data[1:len(data)])
	if memoriasDefinidas:
		print >>sys.stderr, tabulate([["Tiempo", "Comando", "Direccion", "M", "S", "Terminados"], [None, None, None, None, None, None]], 
		headers='firstrow', tablefmt='orgtbl')  
	return

try:
  print >>sys.stderr, 'connection from', client_address

  # Receive the data 
  while True:   
    data = connection.recv(256)
    print >>sys.stderr, 'server received "%s"' % data
    if data:
      call_instruction(data)

      print >>sys.stderr, 'sending answer back to the client'
      connection.sendall('va de regreso...' + ''.join(data))
    else:
      print >>sys.stderr, 'no data from', client_address
      connection.close()
      sys.exit()
      
finally:
     # Clean up the connection
  print >>sys.stderr, 'se fue al finally'
  connection.close()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
