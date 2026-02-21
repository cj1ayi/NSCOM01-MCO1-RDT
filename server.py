""" Main server file """
import socket
from protocol import *

# INITIALIZATION ==========================================================
# Creating server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8888))

""" P.S., server currently listening on port 8888
	TFTP uses port 69 but maybe since this is supposed to be our own protocol
	it can be different? But anyway just consider it a placeholder for now """

# Session info is stored here
sessions = {}

# MAIN LOOP ==============================================================
print("Server is active and listening on port 8888!")

while True:  # Constant loop, listening for messages
	data, addr = sock.recvfrom(1024)
	opcode, seq_num, payload_length, checksum, payload = parse_packet(data)
	print("Received packet from ", addr)

	if opcode == OP_SYN:
		print("\nReceived SYN from ", addr)
		synack_packet = build_packet(OP_SYNACK, 0)
		sock.sendto(synack_packet, addr)

	# CLIENT TERMINATION (FIN/FINACK) ===================================
	elif opcode == OP_FIN:
		print("\nReceived FIN from ", addr)

		# Removing client from sessions dictionary
		if addr not in sessions:
			print("Error: Unexpected packet")  # -------------------- error
			# TODO: Send error packet
		else:
			sessions.pop(addr)
			print(sessions)
			print(addr, " removed from sessions.")

			finack_packet = build_packet(OP_FINACK, 0)
			sock.sendto(finack_packet, addr)
