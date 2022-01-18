import socket

#Contantes da comunicação via socket
HOST = '192.168.0.100'
PORT = 3000
#Instanciando os métodos da comunicação socket
clientSocket = socket.socket()
#Conectando no servidor
try:
    print('Aguardando conexão com servidor')
    clientSocket.connect((HOST, PORT))
    print('Servidor conectado')
except Exception as e:
    print('Erro do tipo: ', e)