##########################################################################################################################################
#AUTORES: 
# - Antonio de Jesus Rodriguez Navarro - A00820049
# - Sebastian Esquer Gaitan - A00820249
# - Pedro Antonio Gamez - A00369538
# - Gabriel Enrique Zamora - A01330721

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
                              #     (idMarcoVirtual),
	              #	    (tiempoEnMemoriaReal)
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
	              #       (tamanoEnMarcosPagina)		              
	              #    ]
                              # ]
                            # Utilizado tambien para saber cual proceso reemplazar:
                            #     FIFO: se reeemplaza el primer proceso en llegar, en la lista se borra elimina el primer elemento (shift left)
                            #     LIFO: se reemplaza el ultimo proceso en llegar, en la lista se borra el ultimo elemento 
comandosA = 0 # Contador de comandos A ejecutados
metricasProcesos = {} # el id del proceso apuntara a un objeto especial para guardar las metricas de un proceso
class Proceso:
  def __init__(self, id):
    self.id = id
    self.start_time = time.time()
    self.end_time = None
    self.page_faults = 0
    self.swap_ins = 0
    self.swap_outs = 0

  def turnaround(self):
    return self.end_time - self.start_time

  def rendimiento(self):
    return 1 - (self.page_faults / comandosA)

def terminarProcesos():
  global metricasProcesos
  end_time = time.time()
  for proceso_id, proceso in metricasProcesos.iteritems():
    if proceso.end_time == None:
      proceso.end_time = end_time
  return
##########################################################################################################################################
############################################# FUNCIONES CREADAS PARA EL MANEJO DE MEMORIA ################################################
##########################################################################################################################################
################## QUE HACE? ######################
####################################################
# Una vez se tienen todos los tamanos de memorias y pagina definidos, se crean todos los marcos de pagina
# que quepan para cada memoria (Real y Swap). Cada marco de pagina se inicializa con el valor de None
# 
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
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
# Inicializa todas las variables gloabales en 0, justo como cuando se crearon
# Esta funcion es util para la funcion F (justo antes de terminar el programa)
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
  global comandosA
  global metricasProcesos
	
  metricasProcesos = {}
  comandosA = 0
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
# Elimina un proceso en especifico dado un id de proceso, borrandolo de la lista procesos, agregandolo a la lista procesosTerminados y 
# finalmente guardando el tiempo de terminacion del proceso en la clase metricasProcesos. Es importante mencionar que no elimina
# los marcos de memoria almacenados, de eso se encarga el resto del codigo de la funcion L().
####################################################
#################### ENTRADAS ######################
####################################################
# (p) -> El id del proceso a eliminar
####################################################
#################### SALIDAS #######################
####################################################
# Regresa 0 si logro borrar el proceso, y un 1 si no encontro el proceso (no existe un proceso con dicho id)
def eliminarProcesoEspecifico(p):
  global procesos
  global procesosTerminados
  global metricasProcesos
  for i in range(0, len(procesos)):
    if(procesos[i][0] == p):
      procesosTerminados.append(procesos.pop(i)[0])
      metricasProcesos[p].end_time = time.time()
      return 0
  print >> sys.stderr, "******************No se encontro el proceso especificado******************"
  return -1	
####################################################	
################### QUE HACE? ######################
####################################################
# Busca el index de un proceso en especifico dentro de la lista procesos, dado el id del proceso a buscar.
####################################################
#################### ENTRADAS ######################
####################################################
# (id) -> id del proceso a buscar
####################################################
#################### SALIDAS #######################
####################################################
# Regresa el index del proceso que buscaba en caso de que lo encuentre, y un -1 si no encuentra ningun proceso con dicho id
def buscarProcesoPorId(id):
	for process in procesos:
		if(process[0] == id):
			return procesos.index(process)
	return -1
####################################################	
################### QUE HACE? ######################
####################################################
# Funcion modular que se encarga de realizar el swap_in (y el swap_out al mismo tiempo). Su operacion depende de la politica de 
# reemplazo que haya elegido el usuario (FIFO o LIFO). Primero se selecciona el marco de pagina que sufrira de swap_out. 
# En caso de ser FIFO, se busca en la Memoria Real el marco de pagina con mas tiempo dentro de la memoria real, mientras que 
# en caso de ser LIFO, se busca en la Memoria Real el marco de pagina con menos tiempo dentro de lamemoria real. Para cualquiera
# que haya sido la politica, se guarda la direccion Real del marco candidato a ser reemplazado.
# Es importante tomar en cuenta que los parametros de entrada describen los datos del proceso que entrara a Memoria Real.
# Puesto que ya se tiene la direccion del marco candidato, solo es cuestion de realizar el cambio (un swap_out o un swap_in).
# El hecho de ser un swap_out o swap_in depende de donde se llame la funcion, al ser llamada por la funcion P(), significa un 
# swap_out de un marco de Memoria Real a Memoria Swap, mientras que al ser llamada por la funcion A(), representa un swap_in de un
# marco de Memoria Swap directo a Memoria Real.
####################################################
#################### ENTRADAS ######################
####################################################
# (direccionActual) -> la direccion virtual del marco de pagina que entrara a Memoria Principal
# (idProceso) -> el id del proceso del marco de pagina que entrara a Memoria Principal
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
	#Se ejecuta el while mientras que haya marcos pendientes por "swap-in" a memoria real
def swapMarco(direccionActual, idProceso):
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesSwap
	politicaFIFO = False
	if(politicaReemplazo == "FIFO"):
		politicaFIFO = True
	direccion = -1
	#Se recorre la memoria real en busqueda del marco de pagina con el tiempo mas viejo
	if(politicaFIFO):
		tiempoMasViejo = time.time()
		for mem in memoriaReal:
			if(mem[2] < tiempoMasViejo):
				tiempoMasViejo = mem[2]
				direccion = memoriaReal.index(mem)
	#Se recorre la memoria real en busqueda del marco de pagina con el tiempo mas reciente
	else:
		tiempoMasReciente = 0.0
		for mem in memoriaReal:
			if(mem[2] > tiempoMasReciente):
				tiempoMasReciente = mem[2]
				direccion = memoriaReal.index(mem)	
	#Se realiza el swap con la direccion seleccionada				
	memoriaSwap[paginasDisponiblesSwap.pop(0)] = memoriaReal[direccion] #	
	memoriaReal[direccion] = [idProceso, direccionActual, time.time()] # Modifica la lista:  [indexMarcoReal][idProceso, idMarcoVirtual]
	return	
##########################################################################################################################################
############################################# PETICIONES QUE PUEDE REALIZAR EL CLIENTE ###################################################
##########################################################################################################################################	
################### QUE HACE? ######################
####################################################
# En esencia solo se le asigna a la variable global tamanoMemoriaReal el tamano de memoria real (en kilobytes) que el usuario especifique. No 
# obstante, se agrego un edge case donde se considera el caso de tamanos negativos. En caso de que el edge case se cumpla, se terminara el programa (se llama a F y E),
# debido a que son asignaciones de variables globales criticas para el funcionamiento del programa. Ademasdemas de un if que llamara a la funcion crearMemorias()
# en el momento en el que ser hayan utilizado las 3 funciones de inicializacion: RealMemory(), SwapMemory(), PageSize() y PoliticaMemory()
####################################################
#################### ENTRADAS ######################
####################################################
# (m) = Tamano en kilobytes de la memoria princial
####################################################
#################### SALIDAS #######################
####################################################
#
def RealMemory(m):
	global tamanoMemoriaReal
	m = int(m)
	if(m<0):
		print >>sys.stderr, "******************El tamano de la Memoria Real no es valido******************"
		F()
		E()
		return
	tamanoMemoriaReal = m
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()
	return 
####################################################	
################### QUE HACE? ######################
####################################################
# En esencia solo se le asigna a la variable global tamanoMemoriaSwap el tamano de memoria swap (en kilobytes) que el usuario especifique. No 
# obstante, se agrego un edge case donde se considera el caso de tamanos negativos. En caso de que el edge case se cumpla, se terminara el programa 
# (se llama a F y E), debido a que son asignaciones de variables globales criticas para el funcionamiento del programa. Ademasdemas de un if que llamara a la 
# funcion crearMemorias() en el momento en el que ser hayan utilizado las 3 funciones de inicializacion: RealMemory(), SwapMemory(), PageSize() y PoliticaMemory()
####################################################
#################### ENTRADAS ######################
####################################################
# (n) -> tamano en kilobytes de la memoria swap
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def SwapMemory(n):
	global tamanoMemoriaSwap
	n = int(n)
	if(n<0):
		print >>sys.stderr, "******************El tamano de la Memoria Swap no es valido******************"
		F()
		E()
		return	
	tamanoMemoriaSwap = n
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  
	return 
####################################################	
################### QUE HACE? ######################
####################################################
# En esencia solo se le asigna a la variable global tamanoPagina el tamano de pagina (en bytes) que el usuario especifique. No 
# obstante, se agrego un edge case donde se considera el caso de tamanos negativos. En caso de que el edge case se cumpla, se terminara el programa 
# (se llama a F y E), debido a que son asignaciones de variables globales criticas para el funcionamiento del programa. Ademas de un if que llamara a la 
# funcion crearMemorias() en el momento en el que ser hayan utilizado las 3 funciones de inicializacion: RealMemory(), SwapMemory(), PageSize() y PoliticaMemory()
####################################################
#################### ENTRADAS ######################
####################################################
# (p) -> tamano de pagina en bytes
####################################################
#################### SALIDAS #######################
####################################################
# Ninguna
def PageSize(p):
	global tamanoPagina
	p = int(p)
	if(p<0):
		print >>sys.stderr, "******************El tamano de la Pagina no es valido******************"
		F()
		E()
		return	
	tamanoPagina = p
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  
	return
####################################################	
################### QUE HACE? ######################
####################################################
# En esencia solo se le asigna a la variable global politicaReemplazo el string del tipo de politica que el usuario especifique. No 
# obstante, se agrego un edge case en el que solo puedes asignar politicas "FIFO" y "LIFO" para este servidor. En caso de que el edge case se cumpla, 
# se terminara el programa (se llama a F y E), debido a que son asignaciones de variables globales criticas para el funcionamiento del programa. Ademas de un if que 
# llamara a la funcion crearMemorias() en el momento en el que ser hayan utilizado las 3 funciones de inicializacion: RealMemory(), SwapMemory(), PageSize() y PoliticaMemory()
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
		print >>sys.stderr, "******************El servidor solo trabaja con politicas FIFO y LIFO******************"
		F()
		E()
		return	
	politicaReemplazo = mm
	if(tamanoMemoriaReal!=None and tamanoMemoriaSwap!=None and tamanoPagina!=None and politicaReemplazo!=None):
		crearMemorias()  	
	return
####################################################	
################### QUE HACE? ######################
####################################################
# La funcion P es una de las mas complejas. Primero se tienen 3 edge cases para evitar errores de ejecucion: se revisa que el manejador de memoria ya este listo
####################################################
#################### ENTRADAS ######################
####################################################
# Ninguna
####################################################
#################### SALIDAS #######################
####################################################
def P(n,p):
	global memoriaReal
	global memoriaSwap
	global paginasDisponiblesReal
	global paginasDisponiblesSwap
	global procesos		
	global metricasProcesos
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "******************El manejador de memoria no esta listo, primero utilice los comandos:******************/n"
		print >>sys.stderr, "******************-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory******************"
		return
	n = int(n)
	p = int(p)
	if(n>tamanoMemoriaReal*1024):
		print >>sys.stderr, "******************El tamano del proceso excede el de la memoria real******************"
		return	
	if(buscarProcesoPorId(p) != -1): 
		print >>sys.stderr, "******************El ID del proceso que deseas crear ya existe, porfavor selecciona otro ID******************"
		return
	nMarcosPagina = int(math.ceil(n/tamanoPagina))
	idProcesoPorRemplazar = None

#Caben todos en memoria real
	if(nMarcosPagina <= len(paginasDisponiblesReal)):
		procesos.append([p, nMarcosPagina]) # Agrega nuevo proceso [idProceso, totalMarcosPagina]
		metricasProcesos[p] = Proceso(p)			
		for i in range(0, nMarcosPagina):
			memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i, time.time()] #[indexMarcoReal] = [idProceso, idMarcoVirtual, tiempoMemoriaReal]			

#Caben algunos directamente en memoria real y los demas entran por reemplazo (swap)
  	elif(nMarcosPagina > len(paginasDisponiblesReal) and nMarcosPagina-len(paginasDisponiblesReal) <= len(paginasDisponiblesSwap)):	
		procesos.append([p, nMarcosPagina]) # Agrega nuevo proceso [idProceso, totalMarcosPagina]
		metricasProcesos[p] = Proceso(p)		  
		marcosReemplazados = len(paginasDisponiblesReal) #Cantidad de marcos que entran directamente en memoria real

	#Entran directo a memoria real los pocos marcos que aun caben
		if(len(paginasDisponiblesReal) > 0):			
			for i in range(0, nMarcosPagina-len(paginasDisponiblesReal)):
				memoriaReal[paginasDisponiblesReal.pop(0)] = [p, i, time.time()] #[indexMarcoReal] = [idProceso, idMarcoVirtual, tiempoMemoriaReal]	

	#swap-in, indicando direccion de marco virtual inicial y final, ademas del id del proceso
		for i in range(marcosReemplazados, nMarcosPagina):
			swapMarco(marcosReemplazados, p)
			metricasProcesos[p].swap_outs+=1				
			
#Memoria real y Memoria swap llenas
  	else:
		print >>sys.stderr, "******************Memoria Real y Swap llenas******************"
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
	global direccionReal
	global comandosA
	global metricasProcesos
	comandosA += 1
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "******************El manejador de memoria no esta listo, primero utilice los comandos:******************/n"
		print >>sys.stderr, "******************-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory******************"
		return		
	d=int(d)
	p=int(p)
	m=int(m)
	if(buscarProcesoPorId(p) == -1):
		print >>sys.stderr, "******************El proceso al que deseas acceder no existe******************"
		return			
	marcoVirtual = d/tamanoPagina
	if(marcoVirtual >= procesos[buscarProcesoPorId(p)][1]):
		print >>sys.stderr, "******************El proceso "+str(p)+" no contiene la direccion "+str(d)+"******************"
		return		
#La direccion se encontro en Memoria Real	
	for real in memoriaReal:
		if(real[0]==p and real[1]==marcoVirtual):
			if(m==0):
				print >>sys.stderr, "Se leyo ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
			elif(m==1):
				print >>sys.stderr, "Se modifico ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
			direccionReal = (memoriaReal.index(real) * tamanoPagina) + (d % tamanoPagina)
			return 
#Page Fault, se hace swap-in a ese proceso de vuelta a Memoria Real			
	swapMarco(marcoVirtual, p)	
	metricasProcesos[p].page_faults+=1
	metricasProcesos[p].swap_ins+=1
#Ahora que se realizo el swap-in, se vuelve a buscar la direccion virtual en memoria Real	
	for real in memoriaReal:
		if(real[0]==p and real[1]==marcoVirtual):
			if(m==0):
				print >>sys.stderr, "Se leyo ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
			elif(m==1):
				print >>sys.stderr, "Se modifico ["+str(memoriaReal.index(real))+":"+str(p)+"."+str(d)+"]"
			direccionReal = (memoriaReal.index(real) * tamanoPagina) + (d % tamanoPagina)
			return 	
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
	global memoriaReal
	global memoriaSwap
	if(not manejadorMemoriaListo):
		print >>sys.stderr, "******************El manejador de memoria no esta listo, primero utilice los comandos:******************/n"
		print >>sys.stderr, "******************-RealMemory/n SwapMemory/n PageSize/n PoliticaMemory******************"
		return	
	p=int(p)
	if(buscarProcesoPorId(p) == False):
		print >>sys.stderr, "******************El proceso que deseas eliminar no existe******************"
		return
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
	eliminarProcesoEspecifico(p)
	print >>sys.stderr, "Las paginas de la memoria Real y memoria Swap del proceso "+str(p)+" han sido liberadas"
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
def F():	
  terminarProcesos()
  imprimirTablaComados()
  imprimirMetricasProcesos()
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

def imprimirMetricasProcesos():
  tablaMetricas = [['Proceso', 'Turnaround', '# Page Faults', 'Swap Ins', 'Swap Outs', 'Rendimiento']]
  for proceso_id, proceso in metricasProcesos.iteritems():
    tablaMetricas.append([proceso.id, proceso.turnaround(), proceso.page_faults,
                          proceso.swap_ins, proceso.swap_outs, proceso.rendimiento()])
  print tabulate(tablaMetricas, headers='firstrow', tablefmt='orgtbl')
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

