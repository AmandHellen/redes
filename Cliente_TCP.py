##########################################################################
"""
#   ESTUDANTES: Amanda Hellen, Gabriel Silva, Yago Mescolotte
#	Proxy.py
#	DATE 09/2019
#   PROFESSORA: Hana Karina
#
"""

import json

with open("config.json") as data_file:
	config = json.load(data_file)

webAcess = config['WebAcess#']

from socket import *

# STUDENTS - replace with your server machine's name
# if the Server is running in the same machine as the client
serverName = gethostname()
# else
# serverName = "192.168.X.X"

# STUDENTS - randomize your port number (use the same one in the server)
# This port number in practice is often a "Well Known Number"
serverPort = 8080

# create TCP socket on client to use for connecting to remote
# server.  Indicate the server's remote listening port
# Error in textbook?   socket(socket.AF_INET, socket.SOCK_STREAM)  Amer 4-2013
clientSocket = socket(AF_INET, SOCK_STREAM)

# open the TCP connection
clientSocket.connect((serverName, serverPort))

# send the request over the TCP connection
# No need to specify server name, port
msg = bytes(webAcess, "utf-8")
print(msg)
clientSocket.send(msg)

# output to console what is sent to the server
print("Sent HTTP Request to Proxy.")

# get the answer from server
data = clientSocket.recv(1024)
print(data)

print("\n" + "MSG OPENED:")
print("#"*120)
data = data.decode('ASCII')
print(data)
print("#"*120 + "\n")

# close the TCP connection
clientSocket.close()
