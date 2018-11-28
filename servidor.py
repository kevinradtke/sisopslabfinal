#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import heapq
import math
from tabulate import tabulate
from termcolor import colored, cprint

# CORRER la siguiente linea para instalar dependencias
# sudo pip install -r requirements.txt

class Process:
	def __init__(self, pid, size, priority):
		self.pid = pid
		self.size = size
		self.priority = priority
		self.paginas = []
		self.initialTime= time.time()
		self.endTime = -1
		self.tiempoCPU = 0
		self.active = True
		self.pageFaults = 1
		self.pageVisits = 1

class MarcoPagina:
		def __init__(self, size_marcos):
			self.size_marcos = size_marcos
			self.inUse = False
			self.Process = Process(-1,-1,-1)

def printline():
	for i in range(110):
		if i%2==0:
			cprint("_",'yellow',attrs=['bold'],end='')
		else:
			cprint("_",'red',attrs=['bold'],end='')

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

processes = []
processes.append(0)
counterPID = 1

try:
	print >>sys.stderr, 'connection from', client_address
	counter = -1
	quantum = 0
	RealMemory = 0
	SwapMemory = 0
	PageSize = 0
	mp = []
	MaxPriority = -1
	priorityQueue = []
	heapq.heapify(priorityQueue)
	
    # Receive the data
	while True:
		data = connection.recv(256)
		print >>sys.stderr, 'server received "%s"' % data
		if data:
			# Counter para controlar en que linea vamos
			counter = counter + 1
			
			# If para obtener el quantum, segunda linea del objeto data
			if(counter == 1):
				InformacionInicial = data.split(' ')
				quantum = float(InformacionInicial[1])
				print >> sys.stderr, quantum

			# If para obtener la memoria real, tercera linea del objeto data
			if(counter == 2):
				InformacionInicial = data.split(' ')
				RealMemory = float(InformacionInicial[1])
				print >> sys.stderr, RealMemory

			# If para obtener el tamaño de la memoria de swap, cuarta linea del objeto data
			if(counter == 3):
				InformacionInicial = data.split(' ')
				SwapMemory = float(InformacionInicial[1])
				print >> sys.stderr, SwapMemory

			# If para obtener el tamaño de cada pagina, quinta linea del objeto data
			if(counter == 4):
				InformacionInicial = data.split(' ')
				PageSize = float(InformacionInicial[1])
				print >> sys.stderr, PageSize

				# Crear marcos de pagina
				for x in range(0, int(RealMemory/PageSize)):
					mp.append(MarcoPagina(int(PageSize*1024)))

			# A partie de la sexta linea, son los queries que si tienen que procesar
			if(counter > 4):
				Queries = data
				Instruccion = Queries.split(' ')

				# Variable para saber si el proceso entro a algun marco de pagina
				breaked = False

				# Variable para saber si ya salio un proceso. Despues buscamos en la cola
				# de listos si existe un proceso que pueda accesar	
				borrado = False

				# Intruccion para crear un nuevo proceso
				# Nos dan el tamaño del proceso y su prioridad
				# Al crear los procesos estos son cargados en los marcos de pagina
				# si existe un marco libre este se carga en esa, pero debe de ser menor 
				# prioridad que las que ya estan cargadas, al cargare una pagina
				# esta pasa a CPU. Cuando se carga una pagina de un proceso y esta es de mayor
				# prioridad que las que existe, sacamos la que haya usado mas veces, si existe 
				# empate usamos FIFO, y es cargada en SwapMemory y tambien se agrega a la cola
				# de listos.
				if(Instruccion[0] == 'Create'):
					# Crear un proceso si recibimos como instruccion un 'Create'
					pagina = int(math.ceil(int(Instruccion[1]) / (PageSize*1024)))
					numPages = []
					for i in range(pagina):
						numPages.append(0)
					p = Process(counterPID, int(Instruccion[1]), int(Instruccion[2]))
					p.paginas = numPages		

					# Aumentamos el PID para tener un control de los procesos
					counterPID = counterPID + 1

					# Agregamos p a un lista de procesos para accesar a ellos despues
					processes.append(p)

					# Recorremos todos los marcos de página para ver si existe posibilidad de 
					# agregar un nuevo proceso o intercambiarlo
					for x in mp:
						# Checar si el marco de página esta vacio y si el proceso entrante
						# es lo suficientemente proritario para acceder a ella
						if(x.inUse == False and p.priority > MaxPriority):
							MaxPriority = p.priority
							x.Process = p
							x.inUse = True
							x.Process.paginas[0] = 1
							breaked = True
							break
					
					# Si el proceso nunca se puso en algun marco de página (memoria real)
					# lo guardamos en una colo de prioridades
					if(breaked == False):
						heapq.heappush(priorityQueue,(p.pid, p))

					print >> sys.stderr, 'Create'


# ##################################


				# Si recibimos una instruccion de 'Address' tenemos que cargar la pagina que 
				# nos dicen a la direccion indicada, si es que es posible
				if(Instruccion[0] == 'Address'):
					ProcesoACargar = int(Instruccion[1])
					PaginaACargar = int(Instruccion[2])
					PaginaACargar = int(PaginaACargar/1024)

					for x in mp:
						if(x.Process.pid == ProcesoACargar):
							if(x.Process.paginas[PaginaACargar] == True):
								print >> sys.stderr, 'El proceso ya se encuentra cargada'

					print >> sys.stderr, 'Address'

				if(Instruccion[0] == 'Fin'):
					# Guardamos el proceso que tenemos que borrar
					ProcesoABorrar = int(Instruccion[1])

					# Buscamos entre todos los marcos de pagina el proceso que es 
					# necesario borrar
					for x in mp:
						if(x.Process.pid == ProcesoABorrar):
							x.Process = Process(-1,-1,-1)
							x.inUse = False
							borrado = True
							break
					
					# Tenemos que actualizar la variable para saber cual es el programa con
					# mayor prioridad en los marcos
					aux = -1
					for x in mp:
						if(x.inUse == True):
							if(aux < x.Process.priority):
								aux = x.Process.priority
					
					MaxPriority = aux

					# Si un elemento fue borrado tenemos que introducir el siguiente elemento de la
					# priority queue a los marcos de pagina
					if(borrado):
						if(priorityQueue):
							process = priorityQueue[0]
						p = process[1]
						print >> sys.stderr, p.pid
						for x in mp:
							if(x.inUse == False and p.priority > MaxPriority):
								MaxPriority = p.priority
								x.Process = p
								x.Process.paginas[0] = 1
								x.inUse = True
								if(priorityQueue):
									heapq.heappop(priorityQueue)
								borrado = False
								break

					print >> sys.stderr, 'Fin'

			for x in mp:
				print >> sys.stderr, x.Process.pid, x.Process.paginas

			print >>sys.stderr, 'sending answer back to the client'

			connection.sendall('process created')

		else:
			print >>sys.stderr, 'no data from', client_address
			connection.close()
			sys.exit()

finally:
     # Clean up the connection
	print >>sys.stderr, 'se fue al finally'


	#SE CREAN VARIABLES Y TABLAS PARA INSERTAR DATOS
	tableL = []
	tableG = []
	turnaroundSum = 0
	tEsperaSum = 0
	visitasTot = 1
	pageFaultsTot = 1

	#SE INSERTAN DATOS EN LAS TABLAS
	for p in processes:
		if(p != 0):
			turnaround = p.endTime-p.initialTime
			tEspera = turnaround - p.tiempoCPU
			turnaroundSum += turnaround
			tEsperaSum += tEspera
			visitasTot += p.pageVisits
			pageFaultsTot += p.pageFaults
			tableL.append([p.pid, p.tiempoCPU, turnaround, turnaround-p.tiempoCPU, p.pageVisits, p.pageFaults, 1-p.pageFaults/p.pageVisits])

	tableG.append([turnaroundSum/len(processes), tEsperaSum/len(processes),visitasTot, pageFaultsTot, 1-pageFaultsTot/visitasTot])


	#TABULA RESULTADOS FINALES
	printline()
	cprint('\nDATOS LOCALES PARA CADA PROCESO','blue',attrs=['bold'])

	print tabulate(tableL, headers=["pid","CPU time", "Turnaround", "t. espera", "# de visitas a pag.", "# de page faults", "rendimiento"])

	printline()
	cprint('\nDATOS GLOBALES','cyan',attrs=['bold'])

	print tabulate(tableG, headers=["Turnaround promedio", "t. espera promedio", "# de visitas a pag.", "# de page faults", "rendimiento"])

	printline()
	print('\n')

	connection.close()


#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
