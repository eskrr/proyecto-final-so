##########################################################################################################################################
#AUTORES: 
# -Antonio de Jesus Rodriguez Navarro - A00820049
# -Sebastian Esquer - A00820
#
#

#DESCRIPCION RESUMIDA DEL PROYECTO:
# El proyecto tiene 2 componentes principales, cada uno dividido en un archivo .py diferente: 
# -cliente.py  -> el usuario que hace peticiones de memoria al manejador de memoria virtual paginada
# -server.py -> contiene las memorias y hace de manejador de memoria virtual paginada para llevar acabo las peticiones del cliente

#DESCRIPCION DE "SERVER.PY"
#   Primeramente se establece todo el ambiente necesario para comunicarse correctamente con el cliente, luego de leer la peticion del cliente,
#   se realiza dicho comando ejecutando alguna de las funciones encontradas en "PETICIONES QUE PUEDE REALIZAR EL CLIENTE". Dichas peticiones 
#   se accesan, almacenan o interactuan directamente con los recursos del servidor (sus memorias y otras variables globales). Con el objetivo
#   de hacer el codigo mas modular y facil de entender, se decidio crear diversas funciones auxiliares, las cuales realizan tareas 
#   especificas y concretas. Despues de llevar acabo la peticion del cliente, se devuelve un feedback al cliente por medio de una tabla con 
#   el estado de los recuros (memorias y variables), el comando realizado, ademas de un conteo del tiempo relativo al comienzo del programa. 
#   Finalmente, se termina la conexion con el cliente y el servidor se devuelve al estado de escuchar, en espera de su proxima peticion.

#SECCIONES DE CODIGO PRINCIPALES DEL PROGRAMA
# 	1-. IMPORTACION DE LIBRERIAS UTILIZADAS
# 	2-. CREACION DEL SOCKET Y CONEXION CON CLIENTE
# 	3-. DEFINICION DE VARIABLES GLOBALES
# 	4-. FUNCIONES CREADAS PARA EL MANEJO DE MEMORIA
# 	5-. PETICIONES QUE PUEDE REALIZAR EL CLIENTE
# 	6-. FUNCIONES CREADAS PARA DESPLEGAR FEEDBACK AL CLIENTE
#	7-. RECIBIR INFORMACION DEL CLIENTE Y TERMINAR LA CONEXION
##########################################################################################################################################
################################################# IMPORTACION DE LIBRERIAS UTILIZADAS ####################################################
##########################################################################################################################################
import socket
import sys
import time
import math
from tabulate import tabulate
##########################################################################################################################################
########################################## CREACION DEL SOCKET Y CONEXION CON CLIENTE ####################################################
##########################################################################################################################################
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
exit = False
# Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.
# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
# Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
# Listen for incoming connections
sock.listen(1)
# Wait for a connection
print >>sys.stderr, 'waiting for a connection'
connection, client_address = sock.accept()
# accept() returns an open connection between the server and client, along with the address of the client. The connection is actually a different 
# socket on another port (assigned by the kernel). Data is read from the connection with recv() and transmitted with sendall().

##########################################################################################################################################
################################################## DEFINICION DE VARIABLES GLOBALES ######################################################
##########################################################################################################################################
# Como nuestras politicas de reemplazo (FIFO y LIFO) no necesitan bitReferencia, 
# bitModificacion o contador, no seran incluidos en nuestro servidor.
tamanoMemoriaReal = None	#@ Almacena el tamano (en kilobytes) de la memoria real en un valor entero
tamanoMemoriaSwap = None	#@ Almacena el tamano (en kilobytes) de la memoria swap en un valor entero
tamanoPagina = None	#@ Almacena el tamano (en bytes) de cada pagina en un valor entero
politicaReemplazo = None	#@ Almacena la politica de reemplazo especificada por el usuario en un valor string
manejadorMemoriaListo = False	#@ Un valor booleano que especifica si las memorias(swap y real) ya fueron creadas con sus 
		#  respectivos marco de pagina inicializados todos con valor de None
direccionReal = ''	#@ Utilizada en el comando A para almacenar la direccion real a la que se accede 
tablaComandos = [	#@ Almacena el encabezado del tabulador desplegado en terminal despues de cada comando 
	  [
	    "Tiempo", 
	    "Comando", 
	    "Direccion", 
	    "M", 
	    "S", 
	    "Terminados"
	  ]
	]    
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

paginasDisponiblesReal = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco real disponible, ordenado de menor a mayor) 
                              # ]      
paginasDisponiblesSwap = [] # CONTENIDO DE LISTA:
                              # [ 
                              #   (listado de IDs de cada marco swap disponible, ordenado de menor a mayor) 
                              # ]                         
procesosTerminados = []	                                                                        
procesos = []               # CONTENIDO DE LISTA: (cada index representa un proceso, los procesos estan en orden de llegada)
                              # [
	              #    [
                              #       (idProceso),
	              #	      (marcosRestantes)		              
	              #    ]
                              # ]
                            # Utilizado tambien para saber cual proceso reemplazar:
                            #     FIFO: se reeemplaza el primer proceso en llegar, en la lista se borra elimina el primer elemento (shift left)
                            #     LIFO: se reemplaza el ultimo proceso en llegar, en la lista se borra el ultimo elemento                          

##########################################################################################################################################
############################################# FUNCIONES CREADAS PARA EL MANEJO DE MEMORIA ################################################
##########################################################################################################################################
################## QUE HACE? ######################
####################################################
# Una vez se tienen todos los tamanos de memorias y pagina definidos, se crean todos los marcos de pagina
# que quepan para cada memoria (Real y Swap). Cada marco de pagina se inicializa con el valor de None
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
#
def crearMemorias():
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global manejadorMemoriaListo
	nMarcosPaginaReal = int(math.ceil((tamanoMemoriaReal*1024)/tamanoPagina))
	nMarcosPaginaSwap = int(math.ceil((tamanoMemoriaSwap*1024)/tamanoPagina))
	for i in range (0, nMarcosPaginaReal):
		memoriaReal.append(None)
		paginasDisponiblesReal.append(i)
	for i in range (0, nMarcosPaginaSwap):
		memoriaSwap.append(None)
		paginasDisponiblesSwap.append(i)
	manejadorMemoriaListo=True
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def borraMemorias():
	global memoriaReal
	global memoriaSwap
	global tamanoMemoriaReal
	global tamanoMemoriaSwap
	global tamanoPagina
	global manejadorMemoriaListo
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
	manejadorMemoriaListo = False
	paginasDisponiblesReal = []
	paginasDisponiblesSwap = []
	procesos = []
	procesosTerminados = []
	tablaComandos = tablaComandos[0:1]
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def indexNuevoProcesoPorReemplazar():
	if(politicaReemplazo == "FIFO"):
		return int(0)
	elif(politicaReemplazo == "LIFO"):
		return int(len(procesos)-1)
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def eliminarProcesoReemplazado():
	if(politicaReemplazo == "FIFO"):
		procesos.pop(0)
	elif(politicaReemplazo == "LIFO"):
		procesos.pop()
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def eliminarProcesoEspecifico(p):
	global procesos
	global procesosTerminados
	for i in range(0, len(procesos)):
		if(procesos[i][0] == p):
			procesosTerminados.append(procesos.pop(i)[0])
			return 0
	print >> sys.stderr, "No se encontro el proceso especificado"
	return -1	
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def buscarProcesoPorId(id):
	for process in procesos:
		if(process[0] == id):
			return True
	return False
##########################################################################################################################################
############################################# PETICIONES QUE PUEDE REALIZAR EL CLIENTE ###################################################
##########################################################################################################################################	
################### QUE HACE? ######################
####################################################
#
####################################################
#################### ENTRADAS ######################
####################################################
#
####################################################
#################### SALIDAS #######################
####################################################
#
def RealMemory(m):
	global tamanoMemoriaReal
	m = int(m)
	if(m<0):
		print >>sys.stderr, "El tamano de la Memoria Real no es valido"
		return
	tamanoMemoriaReal = m
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()
	return 
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def SwapMemory(n):
	global tamanoMemoriaSwap
	n = int(n)
	if(n<0):
		print >>sys.stderr, "El tamano de la Memoria Swap no es valido"
		return	
	tamanoMemoriaSwap = n
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  
	return 
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def PageSize(p):
	global tamanoPagina
	p = int(p)
	if(p<0):
		print >>sys.stderr, "El tamano de la Pagina no es valido"
		return	
	tamanoPagina = p
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def PoliticaMemory(mm):
	global politicaReemplazo
	if(mm!="FIFO" and mm!="LIFO"):
		print >>sys.stderr, "El servidor solo trabaja con politicas FIFO y LIFO"
		return	
	politicaReemplazo = mm
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  	
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def P(n,p):
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "El manejador de memoria no esta listo, primero utilice los comandos:/n"
		print >>sys.stderr, "-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory"
		return
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global procesos	
	idProcesoPorRemplazar = None
	n = int(n)
	p = int(p)
	nMarcosPagina = int(math.ceil(n/tamanoPagina))
	if(n>tamanoMemoriaReal*1024):	#Tamano de proceso excede el tamano de la memoria real
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
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def A(d,p,m):
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "El manejador de memoria no esta listo, primero utilice los comandos:/n"
		print >>sys.stderr, "-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory"
		return	
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
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def L(p):
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "El manejador de memoria no esta listo, primero utilice los comandos:/n"
		print >>sys.stderr, "-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory"
		return	
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
					memoriaSwap[i] = None
		paginasDisponiblesReal.sort()
		paginasDisponiblesSwap.sort()		
		print >>sys.stderr, "Las paginas de la memoria Real y memoria Swap del proceso "+str(p)+" han sido liberadas"
		return
	print >>sys.stderr, "El proceso "+str(p)+" no existe"

	# print >>sys.stderr, memoriaReal
	# print >>sys.stderr, "*******************************************************************"
	# print >>sys.stderr, memoriaSwap		
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def F():	
	imprimirTablaComados()
	borraMemorias()
	return
####################################################	
################### QUE HACE? ######################
####################################################
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def E():
	global exit
	exit = True
	return
##########################################################################################################################################
####################################### FUNCIONES CREADAS PARA DESPLEGAR FEEDBACK AL CLIENTE #############################################
########################################################################################################################################## 

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
	if manejadorMemoriaListo:
		imprimirComando(end_time - start_time, data)
	return

##########################################################################################################################################
##################################### RECIBIR INFORMACION DEL CLIENTE Y TERMINAR LA CONEXION #############################################
##########################################################################################################################################
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



# DEFINICION STANDART DE FUNCION MAIN 
def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

