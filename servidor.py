#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
from tabulate import tabulate
from termcolor import colored, cprint

class Process:
	def __init__(self, pid, size, priority):
		self.pid = pid
		self.size = size
		self.priority = priority
		self.initialTime= time.time()
		self.endTime = -1
		self.tiempoCPU = 0
		self.active = True
		self.pageFaults = 1
		self.pageVisits = 1

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
    # Receive the data
	while True:
		data = connection.recv(256)
		print >>sys.stderr, 'server received "%s"' % data
		if data:
			counter = counter + 1
			if(counter == 1):
				InformacionInicial = data.split(' ')
				quantum = float(InformacionInicial[1])
				print >> sys.stderr, quantum

			if(counter == 2):
				InformacionInicial = data.split(' ')
				RealMemory = float(InformacionInicial[1])
				print >> sys.stderr, RealMemory

			if(counter == 3):
				InformacionInicial = data.split(' ')
				SwapMemory = float(InformacionInicial[1])
				print >> sys.stderr, SwapMemory

			if(counter == 4):
				InformacionInicial = data.split(' ')
				PageSize = float(InformacionInicial[1])
				print >> sys.stderr, PageSize

			if(counter > 4):
				Queries = data
				Instruccion = Queries.split(' ')

				if(Instruccion[0] == 'Create'):
					p = Process(counterPID, int(Instruccion[1]), int(Instruccion[2]))
					counterPID = counterPID + 1
					processes.append(p)
					print >> sys.stderr, 'Create'

				if(Instruccion[0] == 'Address'):
					print >> sys.stderr, 'Address'

				if(Instruccion[0] == 'Fin'):
					print >> sys.stderr, 'Fin'


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
