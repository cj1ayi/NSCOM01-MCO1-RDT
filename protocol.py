import struct

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

def compute_checksum(payload):
    return sum(payload) & 0xFFFF

def build_packet(opcode, seq_num, payload=b""):
    checksum = compute_checksum(payload)
    header = struct.pack("!BIHH", opcode, seq_num, len(payload), checksum)
    return header + payload

def parse_packet(data):
    opcode, seq_num, payload_length, checksum = struct.unpack("!BIHH",data[:9])
    payload = data[9:]
    return opcode, seq_num, payload_length, checksum, payload

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