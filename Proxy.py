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
from datetime import datetime, timedelta

# ###################### INICIALIZAÇÂO DO PROGRAMA ######################
print("Iniciando Proxy Python")
print("Carregando Configurações")

with open("config.json") as data_file:
	config = json.load(data_file)

proxyIp = config['Server ip']
proxyGate = config['Porta']
cache_time = config['Cache time']
cache_times = cache_time.split(":")
cache_time = timedelta(minutes=int(cache_times[0]), seconds=int(cache_times[1]))

# Carrega as páginas de resposta
error501 = bytes(config['501'], "utf-8")
error502 = bytes(config['502'], "utf-8")
error600 = bytes(config['600'], "utf-8")  # Domain
error601 = bytes(config['601'], "utf-8")  # Day
error602 = bytes(config['602'], "utf-8")  # Time
error603 = bytes(config['603'], "utf-8")  # Word

domainNotAllow = config['Domain not Allowed']
timeNotAllow = config['Time not Allowed']
daysNotAllow = config['Days not Allowed']
wordsNotAllow = config['Words not Allowed']

print("Configurações Carregadas")
# ###################### FINALIZAÇÂO DA INICIALIZAÇÂO ######################

cache = {}  # Cache {URL : [TIME, DADOS}


def controle_acesso(domain):
	relogioAtual = datetime.now()  # type time
	week = relogioAtual.strftime('%a').upper()
	time = relogioAtual.strftime('%H:%M')
	
	# para o horário não permitido
	times = timeNotAllow[0].split(":")  # separando horas dos minutos
	time0 = 60*int(times[0]) + int(times[1])
	
	times = timeNotAllow[1].split(":")  # separando horas dos minutos
	time1 = 60*int(times[0]) + int(times[1])
	
	times = time.split(":")  # separando horas dos minutos
	time = 60*int(times[0]) + int(times[1])
	
	if time0 < time < time1:
		print("Time Not ALLOWED: ", end='')  # gerar o feed beack
		return -1, error602
		
	# para os dias não permitidos
	for daysNot in daysNotAllow:
		if week == daysNot.upper():
			print("Day Not ALLOWED: ", end='')  # gerar o feed beack
			return -1, error601
	
	# para o domínio não permitido
	for domainNot in domainNotAllow:
		x = domain.find(domainNot)
		if domain.upper() == domainNot.upper():
			print("Domain Not ALLOWED: ", end='')  # gerar o feed beack
			return -1, error600
	
	return 0, ""

def chek_cache(url):
	if url in cache:  # verifica se existe a chave
		page_in_cache = cache[url]
		old_time = page_in_cache[0]
		time = datetime.now()
		
		if (time - old_time) < cache_time:
			return page_in_cache[1]
		
	return bytes("", "utf-8")


def proxy_thread(connection_socket, ):
	# print("***New Thread***")
	
	# May just be part of the message
	msg = connection_socket.recv(8192)
	
	msg = msg.decode("utf-8")
	server_socket = socket(AF_INET, SOCK_STREAM)

	msg2 = msg.split("\r\n", 1)
	msg_param = msg.split("\r\n")  # separado por linhas, parametros da requisicao
	msg_primary = msg_param[0].split(" ")  # primeira linha com os paramentros get, url e versao http
	
	if msg_primary[0] == "GET":
		'''
		print("#"*120)
		print("MSG_PARAM: ", end='')
		print(msg_param)
		print("MSG_PRIMARY: ", end='')
		print(msg_primary)
		'''
		
		# colocar todas os parametros importantes no dicionario, que seus valores serão atualizados e depois processados
		thisdict = {
			"Connection: ": "",
			"Location: ": ""
		}
		for bloco in msg_param:
			for parm in thisdict:  # cada parametro a ser procurado
				x = bloco.find(parm)
				if x >= 0:  # caso tenha encontrado atualiza seu valor
					thisdict[parm] = bloco[x + len(parm):]
		
		'''
		print("DICIONARIO: ", end='')
		print(thisdict)
		'''
		
		if msg_primary[1][0:7] != "http://":
			connection_socket.send(error501)
			# close the connection and server sockets
			server_socket.close()
			connection_socket.close()
			return
			
		aux = msg_primary[1][7:]  # Remove 'http://'
		aux = aux.split("/", 1)  # Separates domain from the data
		domain = aux[0]
		caminho = " /"  # monta o caminho necessário para requisição
	
		if len(aux) > 1:  # garante a execução, caso n haja aux[1], ou seja caminho
			caminho += aux[1]
		
		'''
		print("DOMAIN: " + domain)
		'''
		
		domain_aux = domain.split(".", 1)
		allowed, error = controle_acesso(domain_aux[0])  #controle de acesso do proxy, domain, time, day
		if allowed != 0:
			# pagina não permitida
			print(msg_primary[1])  # gerar o feed beack
			connection_socket.send(error)
			server_socket.close()
			connection_socket.close()
			return
		
		# Verifica a cache de dados
		dados = chek_cache(msg_primary[1])
		if dados != bytes("", "utf-8"):
			connection_socket.send(dados)
			print("CACHE: ", end='')  # gerar o feed beack
			print(msg_primary[1])  # gerar o feed beack
			server_socket.close()
			connection_socket.close()
			return
			
		try:
			# busca o IP pelo dominio
			ip = gethostbyname(domain)
			
			'''
			print("IP: " + ip)
			'''
			
		except:
			connection_socket.send(error502)
			server_socket.close()
			connection_socket.close()
			return
		
		# Monta a requisição
		request = "GET" + caminho + " " + msg_primary[2] + "\r\n"

		if len(msg2) > 1:
			request += msg2[1]
		
		'''
		print("REQUEST: ", end='')
		print(bytes(request, "utf-8"))
		'''
		
		try:
			# abre a conexão TCP
			server_socket.connect((ip, 80))

			server_socket.send(bytes(request, "utf-8"))

			# Receive the data from server
			# May just be part of the message
			dados = server_socket.recv(8192)
			while True:
				try:
					dados_decode = dados.decode("utf-8")
					break
				except:
					dados += server_socket.recv(8192)
				
			for word in wordsNotAllow:
				x = dados_decode.find(word)
				if x >= 0:
					print("Word Not ALLOWED: ", end='')  # gerar o feed beack
					print(msg_primary[1])  # gerar o feed beack
					connection_socket.send(error603)
					server_socket.close()
					connection_socket.close()
					return
			
			cache[msg_primary[1]] = [datetime.now(), dados]
		except:
			connection_socket.send(error502)
			server_socket.close()
			connection_socket.close()
			return
		
		'''
		print("DADOS: ", end='')
		print(dados)
		'''
		
		connection_socket.send(dados)
		print("SERVER: ", end='')
		print(msg_primary[1])
		
		'''
		print("#" * 120 + "\n")
		'''
		
	# Outros protocolos além do GET
	else:
		connection_socket.send(error501)
		
	# close the connection and server sockets
	server_socket.close()
	connection_socket.close()


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
