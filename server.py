""" Main server file """
import socket

# INITIALIZATION ==========================================================
# Creating server socket
self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
self.sock.bind(('127.0.0.1', 8888))

""" P.S., server currently listening on port 8888
	TFTP uses port 69 but maybe since this is supposed to be our own protocol
	it can be different? But anws just consider it a placeholder for now """

# Session info is stored here
self.sessions = {}



# MAIN LOOP ==============================================================
print("Server is active and listening on port 8888!")

while True: # Constant loop, listening for messages
	data, addr = self.sock.recvfrom(1024)
	print("Received packet from ", addr)


	# HANDSHAKE (SYN/SYNACK) ============================================
	if int.from_bytes(data[:2]) == 0:
		print("\nReceived SYN from ", addr)

		# Adding new client to sessions dictionary
		if addr in self.sessions:
			print("Error: Unexpected packet") # ------------------- error
			# TODO: Send error packet
		else:
			self.sessions[addr] = {}
			print(self.sessions)
			print(addr, " added to sessions!")

			SYNACK = (b'\x06')
			self.sock.sendto(SYNACK, addr)


	# CLIENT TERMINATION (FIN/FINACK) ===================================
	elif int.from_bytes(data[:2]) == 7:
		print("\nReceived FIN from ", addr)

		# Removing client from sessions dictionary
		if addr not in self.sessions:
			print("Error: Unexpected packet") # -------------------- error
			# TODO: Send error packet
		else:
			self.sessions.pop(addr)
			print(self.sessions)
			print(addr, " removed from sessions.")

			FINACK = (b'\x08')
			self.sock.sendto(FINACK, addr)