""" Main server file """
import socket
import os
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
		sessions[addr] = True
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

	elif opcode == OP_RRQ:
		filename = payload.decode()
		print(f"Client requests file: {filename}")

		filepath = os.path.join("server_files", filename)
		if not os.path.exists(filepath):
			error = build_packet(OP_ERROR, 0, b"File not found")
			sock.sendto(error, addr)
		else:
			filesize = os.path.getsize(filepath)
			sack = build_packet(OP_SACK, 0, str(filesize).encode())
			sock.sendto(sack, addr)

			# wait for ack seq=0
			data, _ = sock.recvfrom(1024)
			opcode, seq_num, _, _, _ = parse_packet(data)

			if opcode == OP_ACK and seq_num == 0:
				with open(filepath, "rb") as f:
					seq = 1
					while True:
						chunk = f.read(512)
						if not chunk: 
							break
						
						# retransmission
						packet = build_packet(OP_DATA, seq, chunk)
						sock.settimeout(5)

						for attempt in range(3):
							try:
								sock.sendto(packet, addr)
								data, _ = sock.recvfrom(1024)
								opcode, seq_num, _, _, _ = parse_packet(data)

								if opcode == OP_ACK and seq_num == seq:
									seq += 1
									break
							except socket.timeout:
								print(f"Timeout, resending DATA#{seq}...")

				# send FIN
				fin = build_packet(OP_FIN, 0)
				sock.sendto(fin, addr)
				sock.settimeout(None)

						
