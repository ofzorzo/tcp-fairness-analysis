import time
import socket
import argparse
import csv
import os
from threading import Thread

def log_to_csv(cliente, log):
	file_name = os.getcwd() + "\\client_" + cliente[0].replace('.', '-') + "_" + str(cliente[1]) + ".csv"
	with open(file_name, mode='w', newline='') as csv_log: # mode='w' creates the file if it does not exist, and empties it if it already exists
		log_writer = csv.writer(csv_log, delimiter=',')
		log_writer.writerow(["Time", "bits/s", "MBytes/s"])
		for row in log:
			log_writer.writerow(row)

'''
ideia pra parsear os resultados:
	dividir em intervalos. o tempo inicial é dado pela menor primeira linha dentre os .csv's. a partir do tempo inicial eu divido todos os .csv's em intervalos de 0.1s; somo os valores de um dado intervalo, de modo que terei a taxa de transmissão total da rede.
	um intervalo é dado por [tempo_atual, tempo_atual+0.1). OU SEJA, é um intervalo aberto. Tempo atual seria, por exemplo, a menor primeira linha dentre os .csv's; depois, somaríamos 0.1 a esse tempo atual e o resultado seria o novo tempo atual, para definir o próximo intervalo, do tipo: [tempo_atual+0.1, tempo_atual+0.1+0.1)
'''

def client_socket(con, cliente):
	print('Conectado por', cliente)
	prev_time = time.time()
	elapsed_time = time.time() - prev_time
	curr_bytes = 0
	log = []
	while True:
		if elapsed_time >= 0.1:
			bits_per_sec = (curr_bytes*8)/elapsed_time
			mbytes_per_sec = (curr_bytes/1000000)/elapsed_time
			print( str(bits_per_sec) + " bits/s. Ou " + str(mbytes_per_sec ) + " MBytes/s.")
			curr_bytes = 0
			prev_time = time.time()
			elapsed_time = time.time() - prev_time
			log.append([time.time(), bits_per_sec, mbytes_per_sec])
		else:
			elapsed_time = time.time() - prev_time
		try:
			msg = con.recv(65536) # maximum data to be received (aka maximum number of bytes taken from the TCP Buffer in the OS; the number of bytes received/taken might be lower if the buffer doesn't have that many bytes): https://docs.python.org/3/library/socket.html#socket.socket.recv
			curr_bytes += len(msg)
			if not msg:
				break
		except:
			print("Connection was forcibly closed by the remote host.")
			exit()
	print('Finalizando conexao do cliente', cliente)
	con.close()
	log_to_csv(cliente, log)

def welcoming_socket(host, port):
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	orig = (host, port)
	tcp.bind(orig)
	tcp.listen(1)
	threads = []
	while True:
		con, cliente = tcp.accept()
		t = Thread(target=client_socket, args=[con, cliente])
		threads.append(t)
		t.start()
	for t in threads:
		t.join()
	tcp.close()

def parse_params():
	parser = argparse.ArgumentParser(description="Server for analyzing TCP's congestion control.")
	parser.add_argument('-p', '--port', type=int, default=5000, choices=range(0, 65536), metavar="[0-65535]", help="Port the server will listen to. Default value is 5000.")
	args = parser.parse_args()
	return args.port

if __name__ == "__main__":
	host = '' # For IPv4 addresses, two special forms are accepted instead of a host address: '' represents INADDR_ANY, which is used to bind to all interfaces. As described in https://docs.python.org/3/library/socket.html.
	port = parse_params()
	welcoming_socket(host, port)