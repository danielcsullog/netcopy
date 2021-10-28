import socket
import select
import sys
import time
 
class checksum:
    def __init__(self, file_id, validsec, length, checksum):
        self.id = file_id
        self.sec = validsec
        self.size = length
        self.checksum_md5 = checksum

checksum_list = []

#TCP connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as checksum_server:

    try:
        server_addr = (sys.argv[1], int(sys.argv[2]))
    except IndexError:
        print("Specify a server address (for example: localhost 10000)")
        sys.exit(1)

    checksum_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    checksum_server.bind(server_addr)
    checksum_server.listen(5)

    sockets = [ checksum_server ]

    while True:
        if len(checksum_list) > 0:
            #print("-----------------")
            #print("Hossz: ", len(checksum_list))
            for obj in checksum_list:
                #print(obj.id, str(obj.sec), obj.size, obj.checksum_md5, sep = ' ')
                if obj.sec > 0:
                    obj.sec = obj.sec - 1
                else:
                    print("Torolve: ", obj.id)
                    checksum_list.remove(obj)

        readable, writable, exceptional = select.select(sockets, sockets, sockets, 1)

        if not (writable or readable or exceptional):
            continue

        for sock in readable:
            if sock is checksum_server:                  #what server do when client is connected
                client, client_addr = sock.accept()
                sockets.append(client)
                print("Csatlakozott: ", client_addr) 
            else:                               #when client connected do with client:
                msg = sock.recv(128)           #ide lehet irni hogy packer.size ha van
                if not msg:                    #what server do when client disconnects
                    sockets.remove(sock)
                    sock.close()
                    print("Kilepett")
                else:                           #what server do when client is active
                    print("Kapott adat: ", msg.decode())
                    data = msg.decode()
                    f_id = data.split('|')[1]
                    if data.split('|')[0] == "BE":
                        sec = data.split('|')[2]
                        size = data.split('|')[3]
                        md5 = data.split('|')[4]
                        checksum_list.append(checksum(f_id, int(sec), size, md5))
                        result = "OK".encode()
                    else:
                        #print(data.split('|')[0])
                        for obj in checksum_list:
                            if obj.id == f_id:
                                print("I found it: ", obj.id, str(obj.sec), obj.size, obj.checksum_md5, sep = ' ')
                                result = (obj.size + "|" + obj.checksum_md5).encode()
                                break
                            else:
                                print('0|')
                                result = "0|".encode()

                    sock.sendall(result)

                    