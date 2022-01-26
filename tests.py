import socket  
import time 
import json
from threading import Thread
# configure socket and connect to server  
clientSocket = socket.socket()  
host = '192.168.0.97'
port = 3000  
clientSocket.connect( ( host, port ) )  
clientSocket.setblocking(0)	
#clientSocket.setblocking(0)	  
# keep track of connection status  
connected = True  
print( "connected to server" )  

dados_json_entrada_saida =  {
                            "pacote": "E1"
                            }
#Convertendo o Json em Str e add o paragrafo para ser enviado via socket pacote de entrada do objeto na zona de detecção                              
dados_json_entrada_saida = json.dumps(dados_json_entrada_saida) + "\n"



def sensor_data():
    while True:  
    # attempt to send and receive wave, otherwise reconnect  
        try:          
            print("Não PAREI")
            clientSocket.send(dados_json_entrada_saida.encode('utf8'))  
            time.sleep(2)
        except socket.error:
            print("ERRO SOCKET")

#Start das threads        
sensorThread = Thread(target=sensor_data)
sensorThread.daemon = True
sensorThread.start()


while True:  
    time.sleep(2)
    # attempt to send and receive wave, otherwise reconnect  
    try:   
        clientSocket.connect( ( host, port ) )        
        print("SOCKET CONECTADO")
    except socket.error as e:  
        # set connection status and recreate socket  
        connected = False  
        clientSocket = socket.socket()  
        print( "CONEXAO PERDIDA", e )  
        while not connected:  
            # attempt to reconnect, otherwise sleep for 2 seconds  
            try:  
                clientSocket.connect( ( host, port ) )  
                connected = True  
                print( "RECONEXAO ESTABELECIDA" )  
            except:  
                print('nao consegui conectar')
                time.sleep( 2 )  
  
 