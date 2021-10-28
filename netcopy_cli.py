import socket
import struct
import sys
import hashlib


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

    try:
        server_addr = (sys.argv[1], int(sys.argv[2]))
        checksum_server_addr = (sys.argv[3], int(sys.argv[4]))
        file_id = sys.argv[5]
        infile_path = sys.argv[6]
    except IndexError:
        print("Specify server address, checksum server address, file id, and infile path in args!")
        print("Example: localhost 10000 localhost 10001 testfile.txt /testfile.txt")
        sys.exit(1)

    client.connect(server_addr)
    with open(infile_path, 'rb') as f:
        l = f.read(1024)
        while (l):
            client.sendall(l)
            #print("line: ", l)
            l = f.read(1024)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as checksum_server:
        m = hashlib.md5()
        m.update(file_id.encode())
        #print("Ellenorzo kod: ", m.hexdigest())
        msg = ("BE|" + file_id + "|60|" + str(len(m.hexdigest())) + "|" + m.hexdigest())
        checksum_server.connect(checksum_server_addr)
        checksum_server.sendall(msg.encode())
        received_status = checksum_server.recv(128)
        print("CHECKSUM_SRV_STATUS: ", received_status.decode())
        checksum_server.close()

    client.close()


    
