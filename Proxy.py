##########################################################################
"""
#   ESTUDANTES: Amanda Hellen, Gabriel Silva, Yago Mescolotte
#	Proxy.py
#	DATE 09/2019
#   PROFESSORA: Hana Karina
#
"""

from _thread import *
from socket import *
import json

print("Iniciando Proxy Python")
print("Carregando Configurações")

with open("config.json") as data_file:
	config = json.load(data_file)

proxyIp = config['server ip']
proxyGate = config['porta']


print("Configurações Carregadas")


def proxy_thread(connection_socket, ):
	# print("***New Thread***")
	
	# May just be part of the message
	msg = connection_socket.recv(4096).decode("utf-8")
	server_socket = socket(AF_INET, SOCK_STREAM)

	msg2 = msg.split("\r\n", 1)
	msg_param = msg.split("\r\n")  # separado por linhas, parametros da requisicao
	msg_primary = msg_param[0].split(" ")  # primeira linha com os paramentros get, url e versao http
	if msg_primary[0] == "GET":
		print(msg_param)
		print(msg_primary)

		# for each cada bloco msg_param
		# msg_param.find('Connection:')

		request = "GET"  # comeca montar o pacote de requisicao
		print("\n")
		# Checar se a página esta em cache
		#   Chegar se esta dentro da politica de atualização
		#   Enviar solicitação ao servidor caso precise
		#     Obter resposta do servidor
		# Devolver resposta	ao usuário
		
		aux = msg_primary[1][7:]  # Remove 'http://'
		aux = aux.split("/", 1)  # Separates domain from the data
		domain = aux[0]
		print("DOMAIN: " + domain)

		try:
			# catch the ip from the domain
			ip = gethostbyname(domain)
			print("IP: " + ip)
		except:
			connection_socket.send(bytes("HTTP/1.1 502 Bad Gateway\r\n", "utf-8"))
		
		request += " /" + aux[1] + " " + msg_primary[2] + "\r\n" + msg2[1]
		print("REQUEST: ", end = '')
		print(bytes(request, "utf-8"))
		
		try:
			# open the TCP connection
			server_socket.connect((ip, 80))
			
			server_socket.send(bytes(request, "utf-8"))
			
			# Receive the data from server
			dados = server_socket.recv(4096)
			# http = server_socket.recv(4096).decode("utf-8")
			
			print("DADOS: ", end='')
			print(dados)
			connection_socket.send(dados)
			# connection_socket.send(bytes(http, "utf-8"))
		except:
			connection_socket.send(bytes("HTTP/1.1 502 Bad Gateway\r\n", "utf-8"))
		
		# close the connection and server sockets
		server_socket.close()
		connection_socket.close()
		
	else:
		connection_socket.send(bytes("HTTP/1.1 501 Not Implemented\r\n", "utf-8"))


def initialize():
	# create TCP welcoming socket
	try:
		proxy_socket = socket(AF_INET, SOCK_STREAM)
		proxy_socket.bind(("", proxyGate))
	except:
		print("Não foi possivel conectar a porta: " + proxyGate)
		return
	
	# server begins listening for incoming TCP requests
	proxy_socket.listen(5)
	# output to console that server is listening
	print("The Proxy running over TCP is ready to receive ... ")
	
	while True:
		# establish connection with client
		connection_socket, addr = proxy_socket.accept()
		# print('Connected to :', addr[0], ':', addr[1])
		
		# Start a new thread and return its identifier
		start_new_thread(proxy_thread, (connection_socket,))
	
	# close the TCP Proxy
	proxy_socket.close()


if __name__ == '__main__':
	initialize()
