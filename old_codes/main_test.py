#Autor: Anderson Liege
#Data:14/10/2021
#Projeto Lombada Educativa
 
#Bibliotecas
import json
from numpy.core.numeric import NaN
import serial
import time # Para usar o time.sleep
from datetime import datetime
from threading import Thread
from crc_16bits import*
from binascii import hexlify
import socket
import numpy as np

#Constantes do protocolo do display
CABECALHO = 0xAB 
COMANDO = 0x81
ID_FAIXA = 0x10
RODAPE = 0xCD

#Contantes da comunicação via socket
HOST = '192.168.0.100'
PORT = 5000
clientSocket = socket.socket()

#Configuração Serial
PORTA_SENSOR = '/dev/ttyACM0'
ser_Sensor = serial.Serial(PORTA_SENSOR, 115200, timeout=0)
ser_Sensor.reset_input_buffer()

PORTA_CONVERSOR_RASP = '/dev/ttyS0'
ser_Rasp = serial.Serial(PORTA_CONVERSOR_RASP, 9600, timeout=0)
ser_Rasp.reset_input_buffer()

#CRC configuração
formato_CRC = crc_16("HEX")

#Definicção das Funções
#Função de envio de dados para display de velocidade
def sendVel(vel, crc16_alta, crc16_baixa):
    ser_Rasp.write(serial.to_bytes([CABECALHO,COMANDO,ID_FAIXA,vel,crc16_alta, crc16_baixa,RODAPE])) 

#Função que cria o pacote de dados de velocidade para ser enviado ao display de velocidade
def displayProcotolo(velocidade_sensor):
#Escreve protocolo em formato HEX e o dado (velocidade) com duas casas decimais ex:0F ou 0A...
    protocolo = f'{COMANDO:x}{ID_FAIXA:x}{velocidade_sensor:0{2}x}'
    #print('Protocolo a ser enviado', protocolo)
    CRC_16_bits = (formato_CRC.crc16_CCITT(str(protocolo))) 
    msb_CRC = (CRC_16_bits[0:1])
    lsb_CRC = (CRC_16_bits[1:4])
    msb_CRC_hex = int.from_bytes(msb_CRC, 'big', signed=False)
    lsb_CRC_hex= int.from_bytes(lsb_CRC, 'big', signed=False) 
    return msb_CRC_hex, lsb_CRC_hex

#Chama a funçao sendVel com velocidade = 10km/h para saber quando o programa será iniciado de forma visual
sendVel(0x0A,0x62,0xCF)
time.sleep(2)

#Tratamento de Threads
#Thread de tratamento dos dados do sensor e envio de dados via socket para servidor da aplicação
def sensorData():
#Declaração das variáveis utilizadas nessa função ou fora dela (global variables)
    id = 0
    velocidade_media = 0
    velocidades_objeto = []
    magnitudes_velocidade = []
    distancias_objeto= []
    magnitudes_distancia = []
    objeto_detectado = False
    global flag_erro
    flag_erro = False
    global tipo_erro
    global codigo_erro
    global descricao_erro
    dados_json_entrada_saida ={
        "pacote":""
    }
    dados_json_socket = {
    "id": "", 
    "pacote": "",
    "data_hora": "",
    "magnitude_vel": "", 
    "vel_medida": "", 
    "magnitude_dist": "", 
    "dist_medida": ""
    }
    dados_json_error_socket = {
        "pacote": "",
        "data/hora": "",
        "tipo_notiticacao":"",
        "codigo":"",
        "descricao":""
    }
    
    while True:
        time.sleep(0.01)    
        try:
            if ser_Sensor.is_open:
                #Instanciando datetime para coletar hora do eventoS
                data_hora = datetime.now() # current date and time
                #Aguarda dados do sensor
                if ser_Sensor.inWaiting() > 0:
                    sensor_data = ser_Sensor.readline().decode("utf-8")
                    try:
                        dict_json = json.loads(sensor_data)
                        #####print('DADOS SENSOR', dict_json)
                        
                        #Trecho para calcular a média da velocidade e distância quando o objeto está dentro da zona de detecção
                        if objeto_detectado:
                            if 'unit' in dict_json and dict_json['unit'] == 'kmph':
                                magnitudes_velocidade.append(int(dict_json['magnitude']))
                                velocidades_objeto.append(int(dict_json['speed']))
                        
                            if 'unit' in dict_json and dict_json['unit'] == 'm':
                                magnitudes_distancia.append(int(dict_json['magnitude']))    
                                distancias_objeto.append(int(dict_json['range']))    
                        
                        #Tratamento do pacote 'DetectedObject', quando existe ou deixa de existir o objeto na zona de detecção 
                        if 'DetectedObject' in dict_json:
                            if dict_json['DetectedObject'] == 'Present':
                                objeto_detectado = True                              
                                #Incremento do ID dos eventos
                                id = id + 1

                                #Limpeza dos dados armazenados em casa vetor 
                                velocidades_objeto.clear()
                                magnitudes_velocidade.clear()
                                distancias_objeto.clear()
                                magnitudes_distancia.clear()
                                #Pacote Json que indica entrada de objeto na zona de detecção
                                dados_json_entrada_saida =  {
                                                            "pacote": "E1"
                                                            }
                                #Convertendo o Json em Str e add o paragrafo para ser enviado via socket pacote de entrada do objeto na zona de detecção                              
                                dados_json_entrada_saida = json.dumps(dados_json_entrada_saida) + "\n"
                                try:
                                    clientSocket.send(dados_json_entrada_saida.encode('utf8'))
                                    ######print("OBJETO DETECTADO")
                                except socket.error as e:
                                    tipo_erro = 'ERROR'
                                    codigo_erro = '1'
                                    descricao_erro = e
                                    flag_erro = True
                                    print('ERRO AO ENVIAR DADOS VIA SOCKET: ', e)

                            elif dict_json['DetectedObject'] == 'Gone':
                                objeto_detectado = False                
                                #Calculos de velocidade e sua magnitude
                                if len(velocidades_objeto) == 0:
                                    print("LISTA VAZIA")
                                    velocidades_objeto = [0]
                                velocidade_media = int(np.around(np.mean(velocidades_objeto)))
                                magnitude_velocidade_media = np.around(np.mean(magnitudes_velocidade))

                                #Calculos de distancia e sua magnitude
                                distancia_media = np.around(np.mean(distancias_objeto))
                                magnitude_distancia_media = np.around(np.mean(magnitudes_distancia))

                                #Encapsulamento dos dados calculados em um Json
                                dados_json_socket = {
                                                    "id": str(id), 
                                                    "pacote":"VV",
                                                    "data_hora": str(data_hora.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]),
                                                    "magnitude_vel": str(magnitude_velocidade_media), 
                                                    "vel_medida": str(velocidade_media), 
                                                    "magnitude_dist": str(magnitude_distancia_media), 
                                                    "dist_medida": str(distancia_media)
                                                    } 
                                #Convertendo o Json em Str e add o paragrafo para ser enviado via socket                                   
                                dados_json_socket = json.dumps(dados_json_socket) + "\n"

                                try:
                                    #Envio de dados para o display
                                    msb_CRC_hex, lsb_CRC_hex = displayProcotolo(velocidade_media)
                                    sendVel(velocidade_media, msb_CRC_hex, lsb_CRC_hex)
                                    #Envio dos dados do sensor via socket 
                                    #Pacote Json que indica saída de objeto na zona de detecção
                                    dados_json_entrada_saida =  {
                                                            "pacote": "S1"
                                                                }
                                    #Convertendo o Json em Str e add o paragrafo para ser enviado via socket pacote de saida do objeto na zona de detecção                              
                                    dados_json_entrada_saida = json.dumps(dados_json_entrada_saida) + "\n"
                                    clientSocket.send(dados_json_entrada_saida.encode('utf8'))   
                                    #Envio dos dados calculados via socket                                    
                                    clientSocket.send(dados_json_socket.encode('utf8'))
                                except serial.SerialException as e:
                                    tipo_erro = 'ERROR'
                                    codigo_erro = '0'
                                    descricao_erro = e
                                    flag_erro = True
                                    print('ERRO AO ENVIAR DADOS AO DISPLAY: ', e)

                                except socket.error as e:
                                    tipo_erro = 'ERROR'
                                    codigo_erro = '1'
                                    descricao_erro = e
                                    flag_erro = True
                                    print('ERRO AO ENVIAR DADOS VIA SOCKET: ', e)

                    except json.JSONDecodeError as e:
                        tipo_erro = 'ERROR'
                        codigo_erro = '2'
                        descricao_erro = e
                        flag_erro = True
                        print("ERRO JSON DO TIPO: ", e)
                        time.sleep(1)

        except serial.SerialException as e:
            tipo_erro = 'ERROR'
            codigo_erro = '3'
            descricao_erro = e
            flag_erro = True
            print('SENSOR DESCONECTADO: ', e)
            time.sleep(1)

        except OSError as e:
            tipo_erro = 'ERROR'
            codigo_erro = '4'
            descricao_erro = e
            flag_erro = True
            print("ERRO DE OS DO TIPO: ", e)
            time.sleep(1)
        
        #Envio de erros via socket
        if flag_erro:    
            flag_erro = False
            dados_json_error_socket =   {
                                        "pacote": "ER",
                                        "data_hora": data_hora.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3],
                                        "tipo_notiticacao":tipo_erro,
                                        "codigo":codigo_erro,
                                        "descricao": str(descricao_erro)
                                        }
            #Convertendo o Json em Str e add o paragrafo para ser enviado via socket                                    
            dados_json_error_socket = json.dumps(dados_json_error_socket) + "\n"
            ######print("ERRO A SER ENVIADO VIA SOCKET: ", dados_json_error_socket)
            try:
                clientSocket.send(dados_json_error_socket.encode('utf8'))
            except:
                print("LOGAR ERRO DE ENVIO VIA SOCKET IMPLEMENTAR LOG")

        
#Start das threads        
sensorThread = Thread(target=sensorData)
sensorThread.daemon = True
sensorThread.start()


while True:
    time.sleep(2)  
    try:
        ser_Sensor = serial.Serial(PORTA_SENSOR, 115200, timeout=0)
    except serial.SerialException as e:
        tipo_erro = 'ERROR'
        codigo_erro = '5'
        descricao_erro = e
        flag_erro = True
        print('SENSOR DESCONECTADO', e)
        time.sleep(1)
        ser_Sensor.close()    

    try:
        # configure socket and connect to server
        clientSocket = socket.socket()
        clientSocket.connect((HOST, PORT))
        # keep track of connection status
        connected = True
        #####print("Conectado ao servidor")
    except socket.error as e:
        print('Erro de conexão socket tipo: ', e)
        connected = False
        clientSocket = socket.socket()
        print("Conexão perdida...tentando reconectar")
        pass        
        while not connected:
            # attempt to reconnect, otherwise sleep for 2 seconds
            try:
                clientSocket.connect((HOST, PORT))
                connected = True
                print("Reconexão estabelecida com sucesso")
            except socket.error as e:
                print('Erro de conexão socket tipo: ', e)
                time.sleep(1)

