""" Main client file """
import socket
from protocol import *

# INITIALIZATION =================================================
# Creating client socket, creating var for server address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('127.0.0.1', 8888)

# Port set to 0 so OS gives any avail port
sock.bind(('', 0))



# HANDSHAKE (SYN/SYNACK) ========================================
# SYN and SYNACK trading. Check if server is active, basically
print("Attempting to reach server...")
sock.settimeout(3)

		# Three attempts to reach server until client gives up.
		connected = False
		for i in range(3):
			try:
				SYN = build_packet(OP_SYN, 0)
				self.sock.sendto(SYN, self.server_addr)

				data, _ = self.sock.recvfrom(1024)
				opcode, _, _, _, _ = parse_packet(data)
				if opcode == OP_SYNACK:
					connected = True
					break

	except socket.timeout:
		print("Failed to reach server. Retrying...")

if not connected:
	print("Failed to reach server. Please check if server is running.")
else:
	print("\nServer connected!")



# TERMINATION ====================================================
# Closes socket and sends FIN
def close_socket():

	# Sending FIN. Three attempts before giving up
	fin_sent = False
	sock.settimeout(5)
	for i in range(3):
		try:
			FIN = (b'\x07')
			sock.sendto(FIN, server_addr)

			data, _ = sock.recvfrom(1024)
			if int.from_bytes(data[:2]) == 8:
				fin_sent = True
				break

		except socket.timeout:
			print("Failed to reach server. Retrying...")

	if not fin_sent:
		print("Error in reaching server. Server may be closed.")

	sock.close()



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
			print("downlao")

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

