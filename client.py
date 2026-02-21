""" Main client file """
import socket

class Client:
	def __init__(self):
		# Creating client socket, creating var for server address
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_addr = ('127.0.0.1', 8888)

		# Port set to 0 so OS gives any avail port
		self.sock.bind(('', 0))

		# Moving to main loop
		self.handshake() # Or handshake loop?

	def __del__(self):
		# Close socker
		self.sock.close()

	def handshake(self):
		# SYN and SYNACK trading. Check if server is active, basically
		print("Attempting to reach server...")
		self.sock.settimeout(3)

		# Three attempts to reach server until client gives up.
		connected = False
		for i in range(3):
			try:
				SYN = (b"\x00")
				self.sock.sendto(SYN, self.server_addr)

				data, _ = self.sock.recvfrom(1024)
				if int.from_bytes(data[:2]) == 1:
					connected = True
					break

			except socket.timeout:
				print("Failed to reach server. Retrying...")

		if not connected:
			print("Failed to reach server. Please check if server is running.")
		else:
			print("\nServer connected!")
			self.main() # Go to main loop

	def main(self):
		# main loop
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
					print("downlao")

				case "2":
					print("upload")
					#upload

				case "3":
					#exit
					print("Exiting program...")
					return

				case _:
					#incorrect input
					print("Something seems to be wrong with your input.\n",
						  "Press ENTER to continue.")
					input()


if __name__ == "__main__":
	client = Client()