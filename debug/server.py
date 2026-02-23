""" Main server file """
import socket
import os
from protocol import *

# INITIALIZATION ==========================================================
# Creating server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8888))



# SYN/SYNACK ============================================================
def synsynack(addr):
	print("\nReceived SYN from ", addr)

	synack_packet = build_packet(OP_SYNACK, 0)
	sock.sendto(synack_packet, addr)
	return



# RRQ ==================================================================
def rrq(addr, payload):
	filename = payload.decode()
	print(f"Client requests file: {filename}")

	filepath = os.path.join("server_files", filename)
	if not os.path.exists(filepath):
		error = build_packet(OP_ERROR, ER_FNF)
		sock.sendto(error, addr)
		return

	else:
		filesize = os.path.getsize(filepath)
		sack = build_packet(OP_SACK, 0, str(filesize).encode())
		sock.sendto(sack, addr)

		# wait for ack seq=0
		data, _ = sock.recvfrom(1024)
		opcode, seq_num, _, _, _, _ = parse_packet(data)

		if opcode == OP_ERROR:
			print_error(seq_num)
			return

		if opcode == OP_ACK and seq_num == 0:
			with open(filepath, "rb") as f:
				seq = 1
				attempts = 0
				while True:
					chunk = f.read(512)
					if not chunk: 
						break
					
					# retransmission
					packet = build_packet(OP_DATA, seq, chunk)
					sock.settimeout(5)
					attempts = 0

					while True:
						try:
							sock.sendto(packet, addr)
							data, _ = sock.recvfrom(1024)
							opcode, seq_num, _, _, _, _ = parse_packet(data)

							if opcode == OP_ACK and seq_num == seq:
								seq += 1
								break

							elif opcode == OP_ERROR:
								print_error(seq_num)

						except socket.timeout:
							print(f"Timeout, resending DATA#{seq}...")
							attempts += 1
			
							if attempts >= 5: # 5 attempts and timeout is called
								error = build_packet(OP_ERROR, ER_TIMEOUT)
								sock.sendto(error, addr)
								print("Session timed out. Client unresponsive.")
								sock.settimeout(None)
								return

			# send FIN
			fin = build_packet(OP_FIN, 0)

			for attempt in range(5):
				try:
					sock.sendto(fin, addr)
					data, addr = sock.recvfrom(1024)
					opcode, ermsg, _, _, _, _ = parse_packet(data)

					if opcode == OP_FINACK:
						print(f"Client successfully downloads {filename}")
						return

					elif opcode	== OP_ERROR:
						print_error(ermsg)
						return
				except socket.timeout:
					print(f"Timeout, resending FIN")
			else:
				error = build_packet(OP_ERROR, ER_TIMEOUT)
				sock.sendto(error, addr)
			

			sock.settimeout(None)
			return



# WRQ ====================================================================
def wrq(addr, payload):
		filename, filesize = payload.split(b'\x00')
		filename = filename.decode()
		filesize = int(filesize.decode())
		free_space = get_disk_space("server_files")

		filepath = os.path.join("server_files", filename)
		if os.path.exists(filepath):
			error = build_packet(OP_ERROR, ER_FAE)
			sock.sendto(error, addr)
			return

		elif free_space < filesize:
			error = build_packet(OP_ERROR, ER_SPACE)
			sock.sendto(error, addr)
			return

		else:
			sack = build_packet(OP_SACK, 0) # Acts as ACK0, no need for ACK0 anymore
			sock.sendto(sack, addr)

			# wait for ACK seq=0
			data, _ = sock.recvfrom(1024)
			opcode, seq_num, _, _, _, _ = parse_packet(data)

			if opcode == OP_ACK and seq_num == 0:
				file_data = b""

				sock.settimeout(5)
				attempts = 0

				while True:
					try:
						data, addr = sock.recvfrom(1024)
						opcode, seq_num, _, checksum, payload, encrypted = parse_packet(data)
						attempts = 0

						if opcode == OP_DATA:

							# verify checksum
							if compute_checksum(encrypted) != checksum:
								error = build_packet(OP_ERROR, ER_CHECKSUM)
								sock.sendto(error, addr)
								print("Checksum mismatch. Disregarding packet...")
								continue # server retransmit

							file_data += payload
							ack = build_packet(OP_ACK, seq_num)
							sock.sendto(ack, addr)

						elif opcode == OP_FIN:
							# save file
							with open(f"server_files/{filename}", "wb") as f:
								f.write(file_data)
							print(f"{filename} was uploaded to the server.")

							finack = build_packet(OP_FINACK, 0)
							sock.sendto(finack, addr)
							sock.settimeout(None)
							return

						elif opcode == OP_ERROR:
							print_error(seq_num)

					except socket.timeout:
						attempts += 1
						print(f"Timed out. Resending ACK#{seq_num}...")
						
						if attempts >= 5: # 5 attempts and timeout is called
							error = build_packet(OP_ERROR, ER_TIMEOUT)
							sock.sendto(error, addr)
							print("Session timed out. Client unresponsive.")
							sock.settimeout(None)
							return



# MAIN LOOP ==============================================================
print("Server is active and listening on port 8888!")

while True:  # Constant loop, listening for messages
	sock.settimeout(None)
	data, addr = sock.recvfrom(1024)
	opcode, seq_num, payload_length, checksum, payload, _ = parse_packet(data)
	print("Received packet from ", addr)

	if opcode == OP_SYN:
		synsynack(addr)

	elif opcode == OP_RRQ:
		rrq(addr, payload)
						
	elif opcode == OP_WRQ:
		wrq(addr, payload)