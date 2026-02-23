import struct, os
from cryptography.fernet import Fernet

## opcodes
OP_RRQ    = 0
OP_WRQ    = 1
OP_SACK   = 2
OP_DATA   = 3
OP_ACK    = 4
OP_SYN    = 5
OP_SYNACK = 6
OP_FIN    = 7
OP_FINACK = 8
OP_ERROR  = 9

## error codes
ER_TIMEOUT = 0
ER_FNF = 1
ER_FAE = 2
ER_UNEXPECTED = 3
ER_CHECKSUM = 4
ER_SPACE = 5

KEY = b'xcc0ANVsck0eHjD06oqVJb6RInqz-BO6TlU5ZCelx50='
cipher = Fernet(KEY)

def compute_checksum(payload):
    return sum(payload) & 0xFFFF

def build_packet(opcode, seq_num, payload=b"", spoof=False):
    encrypted = cipher.encrypt(payload) if payload else b""
    checksum = compute_checksum(encrypted)

    if spoof:  # ------------------------------ for checksum error demo
        checksum = 67

    header = struct.pack("!BIHH", opcode, seq_num, len(encrypted), checksum)
    return header + encrypted

def parse_packet(data):
    opcode, seq_num, payload_length, checksum = struct.unpack("!BIHH", data[:9])
    encrypted = data[9:]

    payload = cipher.decrypt(encrypted) if encrypted else b""
    return opcode, seq_num, payload_length, checksum, payload, encrypted

def print_error(ermsg):
    print("Error received.")
    match ermsg:
        case x if x == ER_TIMEOUT:
            print("Error: Timeout")

        case x if x == ER_FNF:
            print("Error: File not found")

        case x if x == ER_FAE:
            print("Error: File already exists")

        case x if x == ER_UNEXPECTED:
            print("Error: Unexpected packet")

        case x if x == ER_CHECKSUM:
            print("Error: Checksum mismatch")

        case x if x == ER_SPACE:
            print("Error: Not enough space for this file")

def get_disk_space(path="."):
    stat = os.statvfs(path)
    return stat.f_bavail * stat.f_frsize