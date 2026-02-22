# NSCOM01 MCO1: Reliable Data Transfer Protocol over UDP (RDTP)
A simple custom application-layer protocol built on top of UDP that provides reliable, ordered file transfer between a client and server. 

## Authors
Jacoba Luna
Roberta Tan

## Features

- **File Download & Upload** — Transfer files reliably between client and server
- **Stop-and-Wait Protocol** — Sequenced DATA packets with ACK confirmation
- **Timeout & Retransmission** — Automatic retry on packet loss (up to 5 attempts)
- **Checksum Verification** — 16-bit checksum on encrypted payloads for integrity
- **Encryption** — AES-128-CBC + HMAC-SHA256 payload encryption
- **Session Management** — SYN/SYNACK handshake and FIN/FINACK termination
- **Error Handling** — File not found, file already exists, session mismatch, checksum mismatch, timeout

## Project Structure

```
NSCOM01-MCO1-RDT/
├── client.py          # Client implementation
├── server.py          # Server implementation
├── protocol.py        # Shared protocol (opcodes, packet building/parsing, encryption)
├── downloads/         # Client: downloaded files saved here
├── uploads/           # Client: files to upload placed here
├── server_files/      # Server: files available for download / uploaded files stored here
└── .gitignore
```

## Requirements

- Python 3.10+
- `cryptography` library

```bash
pip install cryptography
```

## Running the program

**1. Start the server:**
```bash
python server.py
```

**2. Start the client (in a separate terminal):**
```bash
python client.py
```

**3. Use the menu:**
```
Select action:
[1] Download File
[2] Upload File
[3] Exit
```

## Usage

### Download
1. Place the file you want to serve in `server_files/`
2. Run server and client
3. Select option 1, enter the filename
4. File is saved to `downloads/`

### Upload
1. Place the file you want to upload in `uploads/`
2. Run server and client
3. Select option 2, enter the filename (no spaces allowed)
4. File is saved to `server_files/` on the server

## Protocol Summary

| Op Code | Name    | Description              |
|---------|---------|--------------------------|
| 0       | RRQ     | Read Request (download)  |
| 1       | WRQ     | Write Request (upload)   |
| 2       | SACK    | Session Acknowledgement  |
| 3       | DATA    | File data chunk          |
| 4       | ACK     | Acknowledgement          |
| 5       | SYN     | Connection check         |
| 6       | SYNACK  | Connection confirmed     |
| 7       | FIN     | Transfer complete        |
| 8       | FINACK  | FIN acknowledged         |
| 9       | ERROR   | Error with error code    |

## Packet Header Format

```
+----------+-----------+----------------+----------+-------------------+
| Op Code  | Seq #     | Payload Length | Checksum | Encrypted Payload |
| (1 byte) | (4 bytes) | (2 bytes)      | (2 bytes)| (variable)       |
+----------+-----------+----------------+----------+-------------------+
```
