import threading
import socket

host = '127.0.0.1'
port = 50000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 50005))
server.listen()

clients = []
clientNickName = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    selection = 0
    while True:
        try:
            message = client.recv(1024).decode()
            partMsg = message.split(":")

            if partMsg[1] == ' leave':
                clientIndex = clients.index(client)
                clients.remove(client)
                client.close()
                nickName = clientNickName[clientIndex]
                broadcast(f'{nickName} has left the chat !'.encode())
                clientNickName.remove(nickName)

            else:
                broadcast(message.encode())
        except:
            print('wrong place')
            #     clientIndex = clients.index(client)
            #     clients.remove(client)
            #     client.close()
            #     nickName = clientNickName[clientIndex]
            #     broadcast(f'{nickName} has left the chat !'.encode())
            #     clientNickName.remove(nickName)
            break


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


print('Server is listening.........')
receive()
