import struct
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

KEY = b'xcc0ANVsck0eHjD06oqVJb6RInqz-BO6TlU5ZCelx50='
cipher = Fernet(KEY)

def compute_checksum(payload):
    return sum(payload) & 0xFFFF

def build_packet(opcode, seq_num, payload=b""):
    encrypted = cipher.encrypt(payload) if payload else b""
    if payload:
        '''
        print(f"[build_packet] Original payload: {payload}") #DEBUG
        print(f"[build_packet] Encrypted payload: {encrypted}") #DEBUG
        '''
    checksum = compute_checksum(encrypted)
    header = struct.pack("!BIHH", opcode, seq_num, len(encrypted), checksum)
    return header + encrypted

def parse_packet(data):
    opcode, seq_num, payload_length, checksum = struct.unpack("!BIHH", data[:9])
    encrypted = data[9:]
    
    if encrypted:
        '''
        print(f"[parse_packet] Encrypted payload received: {encrypted}") #DEBUG
        '''
    payload = cipher.decrypt(encrypted) if encrypted else b""
    if encrypted:
        '''
        print(f"[parse_packet] Decrypted payload: {payload}") #DEBUG
        '''
    return opcode, seq_num, payload_length, checksum, payload, encrypted

def print_error(ermsg):
    print("Error received.")
    match ermsg:
        case x if x == ER_TIMEOUT:
            print("Error type: Timeout")

        case x if x == ER_FNF:
            print("Error type: File not found")

        case x if x == ER_FAE:
            print("Error type: File already exists")

        case x if x == ER_UNEXPECTED:
            print("Error type: Unexpected packet")

        case x if x == ER_CHECKSUM:
            print("Error type: Checksum mismatch")

