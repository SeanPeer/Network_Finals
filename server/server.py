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

# checking if the given file name from client exists in server folder - if yes - send its content
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
                port = int(client.recv(1024).decode())
                download(filecontent, port)
                print(f"file '{filename}' sent to the client")
            else:
                client.send(f"file '{filename}' is not found at the server's folder".encode())
                print(f"file '{filename}' is not found at the server's folder")

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


# sending the client the file he asked
def download(filecontent, port):

    PACK_SIZE = 512

    # make all packet contain an header of sequence number and its content
    def udp_packet(id, content):
        packet = {'seqnum': id, 'content': content}
        # pickle is used to turn content into bytes
        packet = pickle.dumps(packet)
        return packet

    # send the specific packet to a specific client - we shall know which packet is it because of the sequence
    def send_packet(udpsock, address, datatosend, seqnum):
        flag = True
        while flag:
            # create packet
            packet = udp_packet(seqnum, datatosend)
            udpsock.sendto(packet, address)
            try:
                ack, _ = udpsock.recvfrom(PACK_SIZE)
                if int(pickle.loads(ack)) == seqnum:
                    flag = False
            except Exception as e:
                print(f"Timed Out: Acknowledgement not received for '{seqnum}' ")
                print(f"resending packet '{seqnum}'")
    # create UDP socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # setting a timeout for socket
    udp_sock.settimeout(3.0)

    address = ("127.0.0.1", port)
    sequence = randint(0, 4096)
    stop = False
    while stop is False:
        if len(filecontent) + 4 > PACK_SIZE:
            data = filecontent[:PACK_SIZE]
            send_packet(udp_sock, address, data, sequence)
            filecontent = filecontent[PACK_SIZE:]
        else:
            # make the file content out of range for sure
            filecontent += b"yyyy"
            send_packet(udp_sock, address, filecontent, sequence)
            stop = True
        sequence += 1

    udp_sock.close()


print('Server is listening.........')
receive()