import threading
import socket

nick = input("choose a nickname : ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 50005))


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nick.encode())
            else:
                print(message)
        except:
            print('** an Error is occurred **')
            client.close()
            break


def write():
    while True:
        msgInput = input("")
        message = f'{nick}: {msgInput}'
        client.send(message.encode())
        if msgInput == "leave":
            client.close()


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
