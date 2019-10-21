import socket
import string
import random
import argparse
from threading import Thread

def random_generator(size=4096, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))

def connect_to_server(host, port):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest = (host, port)
    tcp.connect(dest)
    msg = random_generator()
    while True:
        tcp.send(msg.encode()) # https://docs.python.org/2/library/socket.html#socket.socket.send
    tcp.close()

def parse_params():
	parser = argparse.ArgumentParser(description="Client for analyzing TCP's congestion control.")
	parser.add_argument('-p', '--port', type=int, default=5000, choices=range(0, 65536), metavar="[0-65535]", required=True, help="Port the server is listening to. Default value is 5000.")
	parser.add_argument('-i', '--host', type=str, default='127.0.0.1', required=True, help="Server's IP. Default value is 127.0.0.1.")
	args = parser.parse_args()
	return args.host, args.port

if __name__ == "__main__":
	host, port = parse_params()
	connect_to_server(host, port)