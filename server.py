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
exit = False
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
politicaReemplazo = None
direccionReal = ''

paginasDisponiblesReal = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco real disponible, ordenado de menor a mayor) 
                              # ]      
paginasDisponiblesSwap = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco swap disponible, ordenado de menor a mayor) 
                              # ]                                                                                   
procesos = []               # CONTENIDO DE LISTA: (cada index representa un proceso, los procesos estan en orden de llegada)
procesosTerminados = []
                              # [
	                            #    [
                              #       (idProceso),
	                            #	      (marcosRestantes)		              
	                            #    ]
                              # ]
                            # Utilizado tambien para saber cual proceso reemplazar:
                            #     FIFO: se reeemplaza el primer proceso en llegar, en la lista se borra elimina el primer elemento (shift left)
                            #     LIFO: se reemplaza el ultimo proceso en llegar, en la lista se borra el ultimo elemento  
tablaComandos = [["Tiempo", "Comando", "Direccion", "M", "S", "Terminados"]]                            

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

def borraMemorias():
  global memoriaReal
  global memoriaSwap
  global tamanoMemoriaReal
  global tamanoMemoriaSwap
  global tamanoPagina
  global nMarcosPaginaReal
  global nMarcosPaginaSwap
  global memoriasDefinidas
  global paginasDisponiblesReal
  global paginasDisponiblesSwap
  global procesos
  global procesosTerminados
  global tablaComandos
  
  memoriaReal = []
  memoriaSwap = []
  tamanoMemoriaReal = None
  tamanoMemoriaSwap = None
  tamanoPagina = None
  nMarcosPaginaReal = None
  nMarcosPaginaSwap = None
  memoriasDefinidas = False
  paginasDisponiblesReal = []
  paginasDisponiblesSwap = []
  procesos = []
  procesosTerminados = []
  tablaComandos = tablaComandos[0:1]
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
	global politicaReemplazo
	politicaReemplazo = mm
	return

# P n p   (cargar un proceso)
# Se trata de una solicitud de “n” bytes para cargar un proceso a la memoria.
# “n” podría no ser múltiplo del tamaño de la página 

# “p”  es un número entero arbitrario que indica el identificador de proceso. 
# Ejemplo:

def indexNuevoProcesoPorReemplazar():
	if(politicaReemplazo == "FIFO"):
		return int(0)
	elif(politicaReemplazo == "LIFO"):
		return int(len(procesos)-1)

def eliminarProcesoReemplazado():
	if(politicaReemplazo == "FIFO"):
		procesos.pop(0)
	elif(politicaReemplazo == "LIFO"):
		procesos.pop()
	return

def eliminarProcesoEspecifico(p):
  global procesos
  global procesosTerminados
  for i in range(0, len(procesos)):
		if(procesos[i][0] == p):
			procesosTerminados.append(procesos.pop(i)[0])
			return 0
  print >> sys.stderr, "No se encontro el proceso especificado"
  return -1

def P(n,p):
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global procesos	
	idProcesoPorRemplazar = None
	n = int(n)
	p = int(p)
	nMarcosPagina = int(math.ceil(n/tamanoPagina))
	if(n>tamanoMemoriaReal*1024):
		print >>sys.stderr, "El tamano del proceso no puede ser mas grande que el de la memoria real"
		return

#Caben todos en memoria real
	if(nMarcosPagina <= len(paginasDisponiblesReal)):	
		procesos.append([p, nMarcosPagina]) # Agrega nuevo proceso [idProceso, marcosRestantes]
		for i in range(0, nMarcosPagina):
			memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i] # Modifica la lista:  [indexMarcoReal] = [idProceso, idMarcoVirtual]

#Caben algunos directamente en memoria real y los demas entran por reemplazo (swap)
	elif(nMarcosPagina > len(paginasDisponiblesReal) and nMarcosPagina-len(paginasDisponiblesReal) <= len(paginasDisponiblesSwap)):	
		marcosReemplazados = len(paginasDisponiblesReal) #Cantidad de marcos que entran directamente en memoria real

	#Entran directo a memoria real los pocos marcos que aun caben
		if(len(paginasDisponiblesReal) > 0):			
			for i in range(0, nMarcosPagina-len(paginasDisponiblesReal)):
				memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i] # Modifica la lista:  [indexMarcoReal] = [idProceso, idMarcoVirtual]	

	#Se ejecuta el while mientras que haya marcos pendientes por "swap-in" a memoria real
		while(marcosReemplazados < nMarcosPagina): 
			indexProceso = indexNuevoProcesoPorReemplazar()	#Se escoje para reemplazar el proceso correspondiente a la politica,
						#si se llegan a reemplazar todos los marcos de ese proceso (procesos[i][1] == 0),
						#entonces se escoje el proximo proceso a reemplazar, segun la politica correspondiente
			#Se recorre la memoria real en busqueda de marcos del proceso por reemplazar
			for i in range(0, len(memoriaReal)):				
				if(procesos[indexProceso][1] == 0):#Se agotaron los marcos en memoria real del proceso por reemplazar
					eliminarProcesoReemplazado()#Se elimina proceso del arreglo procesos
					break
				elif(marcosReemplazados == nMarcosPagina):#Ya se termino de "swap-in" los marcos solicitados
					break
				elif(memoriaReal[i][0] == procesos[indexProceso][0]):
					memoriaSwap[paginasDisponiblesSwap.pop(0)] = memoriaReal[i] #	
					memoriaReal[i] = [p, marcosReemplazados] # Modifica la lista:  [indexMarcoReal][idProceso, idMarcoVirtual]	
					marcosReemplazados+=1
					procesos[indexProceso][1] -= 1
		procesos.append([p, nMarcosPagina]) # Agrega nuevo proceso [idProceso, marcosRestantes]				
			
#Memoria real y Memoria swap llenas
	else:
		print >>sys.stderr, "Memoria Real y Swap llenas"
		return
	# print >>sys.stderr, memoriaReal
	# print >>sys.stderr, "*******************************************************************"
	# print >>sys.stderr, memoriaSwap			
	return

# A d p m  
# Es una solicitud para accesar la dirección virtual “d” del proceso “p”. Si “m” es 0, la dirección correspondiente sólo se lee; si es 1, también se modifica.“d” puede tener un valor desde cero hasta la dirección virtual máxima del proceso expresada en bytes. 

# Ejemplo: 

# A 17 5 0  (accesar para lectura la dirección virtual 17 del proceso 5)

def A(d,p,m):
  global direccionReal
  d=int(d)
  p=int(p)
  m=int(m)
  marcoVirtual = d/tamanoPagina
  for real in memoriaReal:
    if(real[0]==p and real[1]==marcoVirtual):
      if(m==0):
        print >>sys.stderr, "Se leyo ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
      elif(m==1):
        print >>sys.stderr, "Se modifico ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
      direccionReal = (memoriaReal.index(real) * tamanoPagina) + (d % tamanoPagina)
      return 
  for swap in memoriaSwap:
    if(swap[0]==p and swap[1]==marcoVirtual):
      if(m==0):
        print >>sys.stderr, "Se leyo ["+str(memoriaSwap.index(swap))+":"+str(p)+"."+str(d)+"]"
      elif(m==1):
        print >>sys.stderr, "Se modifico ["+str(memoriaSwap.index(swap))+":"+str(p)+"."+str(d)+"]"
      direccionReal = (memoriaSwap.index(real) * tamanoPagina) + (d % tamanoPagina)
      return
  print >>sys.stderr, "La direccion ["+str(p)+"."+str(d)+"] no se encuentra en memoria Real ni Swap"		
  return

# L p
# Liberar las páginas del proceso “p”.
# PROCESS: Se liberan todas las páginas del proceso “p”, tanto las que estaban en memoria real como aquellas que se encontraban en el área de swapping, quedando varios marcos de página o pedazos del área de swapping vacíos y disponibles para otras operaciones. 


def L(p):
  global memoriaReal
  global memoriaSwap
  p=int(p)
  if(eliminarProcesoEspecifico(p) == 0):
    for i in range(0, len(memoriaReal)):
      if(memoriaReal[i]!=None):
        if(memoriaReal[i][0] == p):
          paginasDisponiblesReal.append(i)
          memoriaReal[i] = None
    for i in range(0, len(memoriaSwap)):
      if(memoriaSwap[i]!=None):
        if(memoriaSwap[i][0] == p):
          paginasDisponiblesSwap.append(i)
          memoriaReal[i] = None
    paginasDisponiblesReal.sort()
    paginasDisponiblesSwap.sort()		
    print >>sys.stderr, "Las paginas de la memoria Real y memoria Swap del proceso "+str(p)+" han sido liberadas"
    return
  print >>sys.stderr, "El proceso "+str(p)+" no existe"

  # print >>sys.stderr, memoriaReal
  # print >>sys.stderr, "*******************************************************************"
  # print >>sys.stderr, memoriaSwap		
  return

# F 
# Fin. Es siempre la última línea de un conjunto de especificaciones; pero pueden seguir otras líneas más para otro conjunto de solicitudes, empezando por el comando que indica la política. Habrá al menos dos especificaciones, una para cada política de reemplazo.

def F():
  imprimirTablaComados()
  borraMemorias()
  return

# E
# Exit. Última línea del archivo. 
# PROCESS: se termina la simulación
# OUTPUT: El comando de INPUT y mensaje de despedida...

def E():
  global exit
  exit = True
  return

def imprimirMemoria(memoria, tipo):
  return ' '.join(('{}[{}:{}.{}]').format(tipo, i, memoria[i][0], memoria[i][1]) if i % 5 != 0
    else '{}[{}:{}.{}]\n'.format(tipo, i, memoria[i][0], memoria[i][1])
    for i in range(0, len(memoria)) if memoria[i] != None)

def imprimirComando(time, comando):
  global direccionReal
  renglonComando = [time, comando, direccionReal, imprimirMemoria(memoriaReal, 'M'), imprimirMemoria(memoriaSwap, 'S'),
    ', '.join(str(p) for p in procesosTerminados)]
  direccionReal = ''
  tablaComandos.append(renglonComando)
  tablaComandos.append(['------------------'] * 6)
  print tabulate([tablaComandos[0], renglonComando], headers='firstrow', tablefmt='orgtbl')
  return

def imprimirTablaComados():
  print tabulate(tablaComandos, headers='firstrow', tablefmt='orgtbl')
  return

def call_instruction(data):
  parsed_data = data.split() 
  start_time = time.time()  
  eval(parsed_data[0])(*parsed_data[1:len(parsed_data)])
  end_time = time.time()
  if memoriasDefinidas:
    imprimirComando(end_time - start_time, data)
  return

try:
  print >>sys.stderr, 'connection from', client_address

  # Receive the data 
  while not exit:   
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

