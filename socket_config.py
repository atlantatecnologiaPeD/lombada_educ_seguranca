import socket

#Contantes da comunicação via socket
HOST = '192.168.0.97'
PORT = 3000
#Instanciando os métodos da comunicação socket
clientSocket = socket.socket()
#clientSocket.setblocking(False)
#Conectando no servidor
try:
    print('Aguardando conexão com servidor')
    clientSocket.connect((HOST, PORT))
    print('Servidor conectado')
except Exception as e:
    print('Erro do tipo: ', e)