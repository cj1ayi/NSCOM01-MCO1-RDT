""" Main client file """
import socket
import os
from protocol import *

import time # ------------------------ used for the snail file error checking

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
		opcode, ermsg, _, _, _, _ = parse_packet(data)

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



# DOWNLOAD (RRQ) ================================================
def download():
	filename = input("Enter filename of file to download: ").strip()
	rrq = build_packet(OP_RRQ, 0, filename.encode())
	sock.sendto(rrq, server_addr)

	data, _ = sock.recvfrom(1024)
	opcode, ermsg, _, _, payload, _ = parse_packet(data)

	if opcode == OP_ERROR:
		print_error(ermsg)
		if ermsg == ER_FNF:
			print("This file does not exist in the server.")
			print("Press ENTER to continue.")
			input()
		return

	elif opcode == OP_SACK:
		# send ACK seq=0 (so we dont have to use ACK#0 lol)
		ack = build_packet(OP_ACK, 0)
		sock.sendto(ack, server_addr)
		file_data = b"" # store all chunks here

		# Checking filesize VS free space
		free_space = get_disk_space("downloads")
		filesize = int(payload.decode())
		if free_space < filesize:
			print("Not enough space to download this file.")
			error = build_packet(OP_ERROR, ER_SPACE)
			sock.sendto(error, server_addr)
			return

		sock.settimeout(5)
		attempts = 0 # when 5 attempts have happened and no reply, timeout error is called

		# loop receiving data packets
		while True:
			try:
				data, _ = sock.recvfrom(1024)
				opcode, seq_num, _, checksum, payload, encrypted = parse_packet(data)
				attempts = 0 # reset since packet was received

				if opcode == OP_DATA:

					# verify checksum
					if compute_checksum(encrypted) != checksum:
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
					print("Press ENTER to continue.")
					input()

					finack = build_packet(OP_FINACK, 0)
					sock.sendto(finack, server_addr)
					sock.settimeout(None)
					return

				elif opcode == OP_ERROR:
					print_error(seq_num)

			except socket.timeout:
				attempts += 1
				print(f"Timeout. Resending ACK#{seq}...")
				
				if attempts >= 5: # 5 attempts and timeout is called
					error = build_packet(OP_ERROR, ER_TIMEOUT)
					sock.sendto(error, server_addr)
					print("Session timed out. Server unresponsive.")
					print("Press ENTER to continue.")
					input()
					sock.settimeout(None)
					return



# UPLOAD (WRQ) ==============================================
def upload():

	filename = input("Enter filename of file to upload: ")

	filepath = os.path.join("uploads", filename)
	if not os.path.exists(filepath):
		print("This file is not inside the 'uploads' folder.")
		print("Please move all files to be uploaded in the 'uploads' folder.")
		print("Press ENTER to continue.")
		input()
		return

	elif ' ' in filename:
		print("There are spaces in your filename, please remove them.")
		print("Press ENTER to continue.")
		input()
		return()

	else:
		filesize = os.path.getsize(filepath)

		if filename == "fakegeronimo.txt": # ---------------------------------- for fake geronimo not enough space error demo
			filesize = 1099511627776
		
		payload = filename.encode() + b'\x00' + str(filesize).encode()
		wrq = build_packet(OP_WRQ, 0, payload)
		sock.sendto(wrq, server_addr)

		data, _ = sock.recvfrom(1024)
		opcode, ermsg, _, _, payload, _ = parse_packet(data)

		if opcode == OP_ERROR:
			print_error(ermsg)
			print("Press ENTER to continue.")
			input()
			return

		elif opcode == OP_SACK:
			# send ACK seq=0 to confirm transfer start
			ack = build_packet(OP_ACK, 0)
			sock.sendto(ack, server_addr)

			with open(filepath, "rb") as f:
				seq = 1
				while True:
					chunk = f.read(512)
					
					if not chunk: # Entirety of file has been read
						break

					packet = build_packet(OP_DATA, seq, chunk)
					sock.settimeout(5)
					attempts = 0

					if filename == "snail.jpeg":
						time.sleep(7)

					while True:
						try:
							sock.sendto(packet, server_addr)
							data, _ = sock.recvfrom(1024)
							opcode, seq_num, _, _, _, _ = parse_packet(data)
							attempts = 0

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
								sock.sendto(error, server_addr)
								print("Session timed out. Server unresponsive.")
								print("Press ENTER to continue.")
								input()
								sock.settimeout(None)
								return
					else:
						error = build_packet(OP_ERROR, ER_TIMEOUT)
						sock.sendto(error, server_addr)

			# Send FIN
			fin = build_packet(OP_FIN, 0)

			for attempt in range(5):
				try:
					sock.sendto(fin, server_addr)
					data, _ = sock.recvfrom(1024)
					opcode, ermsg, _, _, _, _ = parse_packet(data)

					if opcode == OP_FINACK:
						print(f"{filename} was uploaded successfully!")
						print("Press ENTER to continue.")
						input()
						sock.settimeout(None)
						return

					elif opcode == OP_ERROR:
						print_error(ermsg)
				except socket.timeout:
					print(f"Timeout, resending FIN")
			else:
				error = build_packet(OP_ERROR, ER_TIMEOUT)
				sock.sendto(error, server_addr)




# MAIN LOOP =======================================================
while True:
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
			#upload
			upload()

		case "3":
			print("Exiting program...")
			sock.close()
			break

		case _:
			#incorrect input
			print("Something seems to be wrong with your input.\n",
				  "Press ENTER to continue.")
			input()

