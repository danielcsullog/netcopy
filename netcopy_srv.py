import socket
import select
import sys
import hashlib

#TCP connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

    try:
        server_addr = (sys.argv[1], int(sys.argv[2]))
        checksum_server_addr = (sys.argv[3], int(sys.argv[4]))
        file_id = sys.argv[5]
        outfile_path = sys.argv[6]
    except IndexError:
        print("Specify server address, checksum server address, file id, and outfile path in args!")
        print("Example: localhost 10000 localhost 10001 testfile.txt outdir/secondoutdir")
        sys.exit(1)



    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(server_addr)
    server.listen(1)

    client, client_addr = server.accept()
    print("Csatlakozott: ", client_addr) 

    with open(outfile_path, 'wb') as f:
        while True:
            data = client.recv(1024)
            if not data:
                break
            #print("data: ", data.decode())
            f.write(data)
    server.close()
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as checksum_server:
    msg = ("KI|" + file_id)

    checksum_server.connect(checksum_server_addr)
    checksum_server.sendall(msg.encode())
    
    received_msg = checksum_server.recv(1024)
    size = received_msg.decode().split('|')[0]
    received_md5 = received_msg.decode('utf-8').split('|')[1]
    print("Received size:  ", size, " Received md5: ", received_md5)

    generated_md5 = hashlib.md5()
    generated_md5.update(file_id.encode())

    if received_md5 == generated_md5.hexdigest():
        print("CSUM OK")
    else:
        print("CSUM CORRUPTED")

    checksum_server.close() 
