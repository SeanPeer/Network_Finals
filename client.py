import threading
import socket
import sys
from tkinter import *
import os

nick = ""
userInputMsg = ""
msgInput = ""

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
        global msgInput
        # msgInput = input("")

        if userInputMsg != "":
            if msgInput != userInputMsg:
                msgInput = userInputMsg
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

    # Chat window
    def goAhead(self, name):
        global userInputMsg

        self.login.destroy()
        start_client(name)

        frame = Tk()
        frame.title("TextBox Input")
        frame.geometry('1000x600')

        # Function for getting Input
        # from textbox and printing it
        # at label widget

        def getInput():
            global userInputMsg
            userInputMsg = inputTxtMsg.get(1.0, "end-1c")
            lbl.config(text="Provided Input: " + userInputMsg)

        # TextBox Creation message
        inputTxtMsg = Text(frame,
                           height=5,
                           width=20)

        inputTxtMsg.pack()

        # send message Button Creation
        sendMsgButton = Button(frame,
                               text="message",
                               command=getInput)
        sendMsgButton.pack()

        # Label Creation
        lbl = Label(frame, text="")
        lbl.pack()
        frame.mainloop()

        # self.layout(name)


GUI()
