""" Main server file """

import socket
from protocol import *

class Server:
	def __init__(self):
		# Creating server socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('127.0.0.1', 8888))

		""" P.S., server currently listening on port 8888
			TFTP uses port 69 but maybe since this is supposed to be our own protocol
			it can be different? But anws just consider it a placeholder for now """

		self.loop() # Move to main server loop

	def __del__(self):
		# close socket
		self.sock.close()

	def loop(self):
		print("Server is active and listening on port 8888!")

		while True: # Constant loop, listening for messages
			data, addr = self.sock.recvfrom(1024)
			opcode, seq_num, payload_length, checksum, payload = parse_packet(data)
			print("Received packet from ", addr)

			if opcode == OP_SYN:
				print("\nReceived SYN from ", addr)
				SYNACK = build_packet(OP_SYNACK, 0)
				self.sock.sendto(SYNACK, addr)

if __name__ == "__main__":
	server = Server()