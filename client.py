import threading
import socket
import sys
from tkinter import *

nick = ""
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
            print('** Left the chat **')
            client.close()
            sys.exit()
            break


def write():
    while True:
        msgInput = input("")
        message = f'{nick}: {msgInput}'
        client.send(message.encode())
        if msgInput == "leave":
            client.close()
            sys.exit()


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
