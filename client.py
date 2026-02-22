""" Main client file """
import socket
import os
from protocol import *

# INITIALIZATION =================================================
# Creating client socket, creating var for server address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('127.0.0.1', 8888)

# Port set to 0 so OS gives any avail port
sock.bind(('', 0))



# HANDSHAKE (SYN/SYNACK) ========================================
# SYN and SYN-ACK trading. Check if server is active, basically
print("Attempting to reach server...")
sock.settimeout(3)

# Three attempts to reach server until client gives up.
connected = False
for i in range(3):
	try:
		SYN = build_packet(OP_SYN, 0)
		sock.sendto(SYN, server_addr)

		data, _ = sock.recvfrom(1024)
		opcode, ermsg, _, _, _ = parse_packet(data)

		if opcode == OP_SYNACK:  
			connected = True
			break

		elif opcode == OP_ERROR:
			print_error(ermsg)

	except socket.timeout:
		print("Failed to reach server. Retrying...")

if not connected:
	print("Failed to reach server. Please check if server is running.")
else:
	print("\nServer connected!")
	sock.settimeout(None)





# TERMINATION ====================================================
# Closes socket and sends FIN
def close_socket():

	# Sending FIN. Three attempts before giving up
	fin_sent = False
	sock.settimeout(5)
	for i in range(3):
		try:
			FIN = build_packet(OP_FIN, 0)
			sock.sendto(FIN, server_addr)

			data, _ = sock.recvfrom(1024)
			opcode, ermsg, _, _, _ = parse_packet(data)

			if opcode == OP_FINACK:
				fin_sent = True
				break

			elif opcode == OP_ERROR:
				print_error(ermsg)

		except socket.timeout:
			print("Failed to reach server. Retrying...")

	if not fin_sent:
		print("Error in reaching server. Server may be closed.")

	sock.close()



# DOWNLOAD (RRQ) ================================================
def download():
	filename = input("Enter filename of file to download: ").strip()
	rrq = build_packet(OP_RRQ, 0, filename.encode())
	sock.sendto(rrq, server_addr)

	data, _ = sock.recvfrom(1024)
	opcode, ermsg, _, _, payload = parse_packet(data)

	if opcode == OP_ERROR:
		print_error(ermsg)
		return

	elif opcode == OP_SACK:
		# send ACK seq=0 (so we dont have to use ACK#0 lol)
		ack = build_packet(OP_ACK, 0)
		sock.sendto(ack, server_addr)
		# loop receiving data packets
		file_data = b"" # store all chunks here

		while True:
			data, _ = sock.recvfrom(1024)
			opcode, seq_num, _, checksum, payload = parse_packet(data)

			if opcode == OP_DATA:

				# verify checksum
				if compute_checksum(payload) != checksum:
					error = build_packet(OP_ERROR, ER_CHECKSUM)
					sock.sendto(error, server_addr)
					continue # server retransmit

				file_data += payload
				ack = build_packet(OP_ACK, seq_num)
				sock.sendto(ack, server_addr)

			elif opcode == OP_FIN:
				# save file
				with open(f"downloads/{filename}", "wb") as f:
					f.write(file_data)
				print(f"Downloaded {filename} successfully!")

				finack = build_packet(OP_FINACK, 0)
				sock.sendto(finack, server_addr)
				break

			elif opcode == OP_ERROR:
				print_error(seq_num)



# UPLOAD (WRQ) ==============================================
def upload():
	filename = input("Enter filename of file to upload: ")



# MAIN LOOP =======================================================
while True and connected:
	print("\n\n================================================")
	print("\nSelect action:")
	print("[1] Download File")
	print("[2] Upload File")
	print("[3] Exit")
	print()

	action_chosen = input(">>> ").strip()

	match action_chosen:
		case "1":
			#download
			download()

		case "2":
			print("upload")
			#upload

		case "3":
			print("Exiting program...")
			close_socket()
			connected = False

		case _:
			#incorrect input
			print("Something seems to be wrong with your input.\n",
				  "Press ENTER to continue.")
			input()

