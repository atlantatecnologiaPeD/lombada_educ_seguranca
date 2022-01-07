import socket
from time import sleep
import json


json_data = {"velocidade": "20", "range": "50"}
msg = json.dumps(json_data) + "\n"


while True:
    try:
        # configure socket and connect to server
        clientSocket = socket.socket()
        host = '192.168.0.100'
        port = 5000
        clientSocket.connect((host, port))
        # keep track of connection status
        connected = True
        print("connected to server")
    except socket.error as e:
        print('connection error type', e)
        pass
    # attempt to send and receive wave, otherwise reconnect
    try:
        #clientSocket.connect((host, port))
        clientSocket.send(msg.encode('utf-8'))
        #message_rcv = clientSocket.recv(1024).decode("UTF-8")
        # print(message_rcv)
        sleep(0.1)
    except socket.error as e:
        # set connection status and recreate socket
        print('connection error type', e)
        connected = False
        clientSocket = socket.socket()
        print("connection lost... reconnecting")
        while not connected:
            # attempt to reconnect, otherwise sleep for 2 seconds
            try:
                clientSocket.connect((host, port))
                connected = True
                print("re-connection successful")
            except socket.error as e:
                print('connection error type', e)
                sleep(1)

clientSocket.close()