import os
import pickle
import socket
import threading
from random import randint

host = '127.0.0.1'
port = 50000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 50005))
server.listen()

clients = []
clientNickName = []


def broadcast(message):
    for client in clients:
        client.send(message)


# if the file name exists in the server's path - send its content , else - return does not exists.
def read_file(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            filecontent = f.read()
        return filecontent
    else:
        return None


def handle(client):
    while True:
        message = client.recv(1024).decode()
        partMsg = message.split(":")

        if partMsg[1] == ' leave':
            clientIndex = clients.index(client)
            clients.remove(client)
            client.close()
            nickName = clientNickName[clientIndex]
            broadcast(f'{nickName} has left the chat !'.encode())
            clientNickName.remove(nickName)
            break
        if partMsg[1] == ' get users':
            names = str(clientNickName)
            client.send(names.encode())
            continue

        #  connect to user, avi, the message
        if " connect to user" in partMsg[1]:
            msg = partMsg[1].split(", ")
            nickNibour = msg[1]
            if nickNibour in clientNickName:
                nibourIndex = clientNickName.index(nickNibour)
                neighbourClient = clients[nibourIndex]
                neighbourClient.send(msg[2].encode())
                break

        # need to see if to send to self too
        if " send to all, " in partMsg[1]:
            msg = partMsg[1].split("send to all, ")
            broadcast(msg[1].encode())
            break

        if 'download' in partMsg[1]:
            filename = partMsg[1].split(" ")[-1].strip()
            filecontent = read_file(filename)
            if filecontent: 
                client.send(f"DOWNLOAD {filename}".encode())
                download(filecontent)
                print(f"file '{filename}' sent to the client")

            else:
                client.send( f"file '{filename}' not found at server".encode() )
                print(f"file '{filename}' not found at server")

        else:
            broadcast(message.encode())


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode())
        nickName = client.recv(1024).decode()
        clients.append(client)
        clientNickName.append(nickName)

        client.send(f'The nick name you entered is {nickName} !\n\nWelcome to our chat !!\n\n'.encode())
        broadcast(f'{nickName} has joined the chat !'.encode())
        client.send('You are now connected to our chat !'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


# Function for sending the client the file he asked for
def download(filecontent):

    PACK_SIZE = 512

    # Creating an header for each packet contains its number and the content itself
    def udp_packet(id, content):
        packet = {'seqnum': id, 'content': content}
        packet = pickle.dumps(packet)
        return packet

    # sending each packet
    def send_packet(udpsock, address, datatosend, seqnum):
            flag = True
            while flag:
                packet = udp_packet(seqnum, datatosend)
                udpsock.sendto(packet, address)
                
                try:
                    ack, _ = udpsock.recvfrom(PACK_SIZE)
                    if int(pickle.loads(ack)) == seqnum: 
                        flag = False
                except Exception as e:
                    print(f"Timed Out: Acknowledgement not received for '{seqnum}' ")
                    print(f"resending packet '{seqnum}'")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(3.0)
    
    addr = ("127.0.0.1", 50000)
    seqnumber = randint(0, 4096)
    stop = False
    while stop is False:
        if len(filecontent)+4 > PACK_SIZE:
            data = filecontent[:PACK_SIZE]
            send_packet(udp_sock, addr, data, seqnumber)
            filecontent = filecontent[PACK_SIZE:]
        else:
            filecontent += b"yyyy"
            send_packet(udp_sock, addr, filecontent, seqnumber)
            stop = True
        seqnumber += 1

    udp_sock.close()



print('Server is listening.........')
receive()