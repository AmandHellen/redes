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
from datetime import datetime

# ###################### INICIALIZAÇÂO DO PROGRAMA ######################
print("Iniciando Proxy Python")
print("Carregando Configurações")

with open("config.json") as data_file:
	config = json.load(data_file)

proxyIp = config['Server ip']
proxyGate = config['Porta']
domainNotAllow = config['Domain not Allowed']
timeNotAllow = config['Time not Allowed']
daysNotAllow = config['Days not Allowed']
# wordsNotAllow = config['Words not Allowed']

print("Configurações Carregadas")
# ###################### FINALIZAÇÂO DA INICIALIZAÇÂO ######################

cache = []  #essa eh nossa cache


def controle_acesso(domain):
	relogioAtual = datetime.now()
	week = relogioAtual.strftime('%a').upper()
	time = relogioAtual.strftime('%H:%M')
	
	# para o horário n permitido
	if timeNotAllow[0] < time and time > timeNotAllow[1]:
		print(time)
		print("Time Not ALLOWED")
		return -1
	
	# para os dias não permitidos
	for daysNot in daysNotAllow:
		if week == daysNot.upper():
			print("Day Not ALLOWED")
			return -1
	
	# para o domínio não permitido
	for domainNot in domainNotAllow:
		x = domain.find(domainNot)
		if x >= 0:
			print("Domain Not ALLOWED")
			return -1
	
	return 0


def store_cache(request, hora):
	print(hora)
	cache.append((request, hora))
	print(cache)
	#hora_timeout = datetime.now()
	#minutos = hora_timeout.minute - hora.minute
	#print(minutos)


def proxy_thread(connection_socket, ):
	# print("***New Thread***")
	
	# May just be part of the message
	msg = connection_socket.recv(4096)
	print(msg)
	msg = msg.decode("utf-8")
	server_socket = socket(AF_INET, SOCK_STREAM)

	msg2 = msg.split("\r\n", 1)
	msg_param = msg.split("\r\n")  # separado por linhas, parametros da requisicao
	msg_primary = msg_param[0].split(" ")  # primeira linha com os paramentros get, url e versao http
	if msg_primary[0] == "GET":
		print("#"*120)
		print("MSG_PARAM: ", end='')
		print(msg_param)
		print("MSG_PRIMARY: ", end='')
		print(msg_primary)
		
		# colocar todas os parametros importantes no dicionario, que seus valores serão atualizados e depois processados
		thisdict = {
			"Connection: ": "",
			"AlgumaCoisa: ": ""
		}
		for bloco in msg_param:
			for parm in thisdict:  # cada parametro a ser procurado
				x = bloco.find(parm)
				if x >= 0:  # caso tenha encontrado atualiza seu valor
					thisdict[parm] = bloco[x + len(parm):]
		
		print("DICIONARIO: ", end='')
		print(thisdict)
		
		aux = msg_primary[1][7:]  # Remove 'http://'
		aux = aux.split("/", 1)  # Separates domain from the data
		domain = aux[0]
		caminho = " /"  # monta o caminho necessário para requisição
		
		if len(aux) > 1:  # garante a execução, caso n haja aux[1]
			caminho += aux[1]
		
		print("DOMAIN: " + domain)
		allowed = controle_acesso(domain) #controle de acesso do dominio
		if allowed == 0:
			try:
				# catch the ip from the domain
				ip = gethostbyname(domain)
				print("IP: " + ip)
			except:
				connection_socket.send(bytes("HTTP/1.1 502 Bad Gateway\r\n", "utf-8"))
			
			# Monta a requisição
			request = "GET" + caminho + " " + msg_primary[2] + "\r\n"

			hora = datetime.now()
			store_cache(request, hora)  # TODO penso que request esta equivocado, prefira (domain + " /" + caminho) e não esqueça de salvar a pagina q recebemos
			if len(msg2) > 1:
				request += msg2[1]
			print("REQUEST: ", end='')
			print(bytes(request, "utf-8"))

			try:
				# open the TCP connection
				server_socket.connect((ip, 80))

				server_socket.send(bytes(request, "utf-8"))

				# Receive the data from server
				dados = server_socket.recv(4096)

				print("DADOS: ", end='')
				print(dados)
				connection_socket.send(dados)
			except:
				connection_socket.send(bytes("HTTP/1.1 502 Bad Gateway\r\n", "utf-8"))
		else:
			connection_socket.send(bytes("HTTP/1.1 200 OK\r\n", "utf-8"))  # TODO Com a pagina de not allowed

		# close the connection and server sockets
		server_socket.close()
		connection_socket.close()
		
		print("#" * 120 + "\n")
		
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
	print("The Proxy running over TCP is ready to receive ... \n")
	
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
