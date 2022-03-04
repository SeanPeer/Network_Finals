import pickle
from random import randint
import threading
import socket
import sys
from tkinter import *

nick = ""
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init_udp_client():
    """ create udp client socket from any available port """
    while True:
        try:
            port = randint(1024, 49152)
            udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_client.bind(('127.0.0.1', port))
            return udp_client, port
        except:
            pass


client.connect(('127.0.0.1', 50005))


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nick.encode())

            elif message.startswith('DOWNLOAD'):
                filename = message.split(" ")[-1].strip()
                udp_client, port = init_udp_client()
                client.send(f"{port}".encode())
                download(filename, udp_client)

            else:
                print(message)
        except:
            print('** Left the chat **')
            client.close()
            sys.exit()
            break


def download(filename, udp_client):
    def write_file(filecontent):
        with open(filename, "wb") as f:
            f.write(filecontent)

    PACK_SIZE = 557

    received_bytes = {}
    while True:

        packet, saddr = udp_client.recvfrom(PACK_SIZE)
        if len(packet) == 0:
            break

        else:
            packet = pickle.loads(packet)
            seqnum = packet.get("seqnum")
            content = packet.get("content")
            udp_client.sendto(pickle.dumps(seqnum), saddr)

            # if the packet has a tail - clean the end of the packet from the tail and receive content
            if content[-4:] == b"yyyy":
                content = content[:-4]
                received_bytes[seqnum] = content
                break
            # keep receive cuz its not the end
            else:
                received_bytes[seqnum] = content

    udp_client.close()
    write_file(b"".join(received_bytes.values()))
    print(f"'{filename}' downloaded successfully")


def write():
    while True:
        msgInput = input("")
        if "download" in msgInput:
            message = f'{nick}: {msgInput}'

        else:
            message = f'{nick}: {msgInput}'

        client.send(message.encode())
        if msgInput == "leave":
            client.close()
            sys.exit()
            break


def start_client(nickname):
    global nick
    nick = nickname

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()


# GUI class for the chat
class GUI:
    def __init__(self):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        # setup window
        self.login = Toplevel()
        self.login.title("Chat Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=200)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to enter the chatroom",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.1,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Nickname: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        # typing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.22)

        # set the focus of the cursor
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name):
        self.login.destroy()
        start_client(name)

        # self.layout(name)


GUI()