#Autor: Anderson Liege
#Data:14/10/2021
#Projeto Lombada Educativa
 
#Bibliotecas
import json
import time 
import socket
import numpy as np
from numpy.core.numeric import False_, NaN
from serial_config import*
from socket_config import*
from sensor_config import*
from datetime import datetime
from threading import Thread
from binascii import hexlify


# Códigos de erros
SENSOR_ERROR = "1"
OS_ERROR = "2"
JSON_ERROR = "3"

global flag_habilita_envio_vel_display
flag_habilita_envio_vel_display = 'True'

def habilita_envio_vel_display(dado):
    global flag_habilita_envio_vel_display
    flag_habilita_envio_vel_display = dado

'''
#Chama a funçao send_vel com velocidade = 88km/h para saber quando o programa será iniciado de forma visual
send_vel(0x58,0x18,0x78)
time.sleep(2)
'''

#Tratamento de Threads
#Thread de tratamento dos dados do sensor e envio de dados via socket para servidor da aplicação
def sensor_data():
#Declaração das variáveis utilizadas nessa função ou fora dela (global variables)
    global flag_habilita_envio_vel_display
    global id
    id = 0
    global magnitude_velocidade_media
    global velocidade_media
    global magnitude_distancia_media
    global distancia_media
    global data_hora
    velocidade_media = 0
    velocidades_objeto = []
    magnitudes_velocidade = []
    distancias_objeto= []
    magnitudes_distancia = []
    objeto_detectado = False
    flag_envia_display_velocidade = False
    flag_envia_ctrl_c_sensor = True
    global flag_sensor_conectado
    flag_sensor_conectado = False
    global flag_erro
    flag_erro = False
    global tipo_erro
    global codigo_erro
    global descricao_erro
    global ser_sensor
    global ser_conversor_display
    global portas_usb_encontradas
    global dados_json_entrada_saida
    dados_json_entrada_saida ={
        "pacote":""
    }
    global dados_json_socket
    dados_json_socket = {
    "id": "", 
    "pacote": "",
    "data_hora": "",
    "magnitude_vel": "", 
    "vel_medida": "", 
    "magnitude_dist": "", 
    "dist_medida": ""
    }
    global dados_json_error_socket
    dados_json_error_socket = {
        "pacote": "",
        "data/hora": "",
        "tipo_notiticacao":"",
        "codigo":"",
        "descricao":""
    }

    global flag_envia_entrada_socket
    flag_envia_entrada_socket = False
    global flag_envia_saida_socket
    flag_envia_saida_socket = False
    global flag_envia_dados_medicao_socket
    flag_envia_dados_medicao_socket = False
    global flag_envia_erro_medicao_socket 
    flag_envia_erro_medicao_socket = False

    while True:
        time.sleep(0.01)    
        try:
            if ser_sensor.is_open:
                #Instanciando datetime para coletar hora do evento
                data_hora = datetime.now() # current date and time
                #Aguarda dados do sensor
                try:
                    if flag_envia_ctrl_c_sensor:
                        ser_sensor.write(b'\x03')
                        print("CTRL+C ENVIADO COM SUCESSO")
                        flag_envia_ctrl_c_sensor = False
                except Exception as e:
                    print("ERRO AO ENVIAR CTRL+C ", e)
                if ser_sensor.inWaiting() > 0:
                    sensor_data = ser_sensor.readline().decode("utf-8")
                    try:
                        dict_json = json.loads(sensor_data)
                        ###print('DADOS SENSOR', dict_json)
                        
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

                                #Habilita flag de envio de entrada do objeto via socket
                                flag_envia_entrada_socket = True


                            elif dict_json['DetectedObject'] == 'Gone':
                                objeto_detectado = False                
                                #Calculos de velocidade e sua magnitude
                                if len(velocidades_objeto) == 0:
                                    print("LISTA VAZIA")
                                    velocidade_media = 0
                                    magnitude_velocidade_media = 0
                                    distancia_media = 0
                                    magnitude_distancia_media = 0
                                    flag_envia_display_velocidade = False
                                else:
                                    flag_envia_display_velocidade = True
                                    velocidade_media = int(np.around(np.mean(velocidades_objeto)))
                                    magnitude_velocidade_media = np.around(np.mean(magnitudes_velocidade))

                                    #Calculos de distancia e sua magnitude
                                    distancia_media = np.around(np.mean(distancias_objeto))
                                    magnitude_distancia_media = np.around(np.mean(magnitudes_distancia))

                                    #Habilita flag de envio de saída do objeto via socket
                                    flag_envia_saida_socket = True   

                                    #Habilita flag de envio dos dados de detecção do objeto via socket
                                    flag_envia_dados_medicao_socket = True

                                '''
                                try:
                                    
                                    #Envio de dados para o display
                                    msb_CRC_hex, lsb_CRC_hex = display_protocolo(velocidade_media)
                                    
                                    if flag_envia_display_velocidade and flag_habilita_envio_vel_display == 'True':
                                        ser_conversor_display.write(serial.to_bytes([CABECALHO,COMANDO,ID_FAIXA,velocidade_media,msb_CRC_hex, lsb_CRC_hex,RODAPE])) 
                                        #send_vel(velocidade_media, msb_CRC_hex, lsb_CRC_hex)
                                    
                                    #Habilita flag de envio de saída do objeto via socket
                                    flag_envia_saida_socket = True   

                                    #Habilita flag de envio dos dados de detecção do objeto via socket
                                    flag_envia_dados_medicao_socket = True

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
                                    #print('ERRO AO ENVIAR DADOS VIA SOCKET DE SAÍDA DO OBJETO: ', e)
                                    print('ERRO AO ENVIAR DADOS VIA SOCKET DE SAÍDA DO OBJETO: ')
                                '''
                                
                    except json.JSONDecodeError as e:
                        ser_sensor.write(b'\x03')
                        tipo_erro = 'ERROR'
                        codigo_erro = JSON_ERROR 
                        descricao_erro = e
                        flag_erro = True
                        print("ERRO JSON CÓDIGO {}, DESCRIÇÃO DO ERRO: ".format(codigo_erro), e)
                        time.sleep(1)

        except serial.SerialException as e:
            flag_sensor_conectado = False
            tipo_erro = 'ERROR'
            codigo_erro = SENSOR_ERROR
            descricao_erro = e
            flag_erro = True
            print("ERRO SERIAL SENSOR CÓDIGO {}, DESCRIÇÃO DO ERRO: ".format(codigo_erro), e)
            time.sleep(1)
        
        except OSError as e:
            flag_sensor_conectado = False
            tipo_erro = 'ERROR'
            codigo_erro = OS_ERROR
            descricao_erro = e
            flag_erro = True
            print("ERRO DE SISTEMA CÓDIGO {}, DESCRIÇÃO DO ERRO: ".format(codigo_erro), e)
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
            
            #Habilita flag de envio do erro de medicao via socket
            flag_envia_erro_medicao_socket = True
        
#Start da thread       
sensorThread = Thread(target=sensor_data)
sensorThread.daemon = True
sensorThread.start()


def socket_envio_dados():

    maquina_estado_dados = 0

    global dados_json_entrada_saida
    dados_json_entrada_saida = {
        "pacote":""
    }

    global id
    global magnitude_velocidade_media
    global velocidade_media
    global magnitude_distancia_media
    global distancia_media
    global data_hora

    global flag_envia_entrada_socket            
    global flag_envia_saida_socket
    global flag_envia_dados_medicao_socket
    global flag_envia_erro_medicao_socket
    global dados_json_socket
    global dados_json_error_socket
    global clientSocket
    global flag_erro_envio_dados_socket
    flag_erro_envio_dados_socket = False

    while(True):
        time.sleep(0.01)
        try:

            if flag_erro_envio_dados_socket == False:

                if flag_envia_entrada_socket:
                    flag_envia_entrada_socket = False
                    maquina_estado_dados = 0
                    #Pacote Json que indica entrada de objeto na zona de detecção
                    dados_json_entrada_saida =  {
                                                    "pacote": "E1"
                                                }
                    #Convertendo o Json em Str e add o paragrafo para ser enviado via socket pacote de entrada do objeto na zona de detecção                              
                    dados_json_entrada_saida = json.dumps(dados_json_entrada_saida) + "\n"
                    #Envio dos dados de entrada via socket  
                    clientSocket.send(dados_json_entrada_saida.encode('utf8'))
                    maquina_estado_dados+=1
                                       
                if flag_envia_saida_socket and maquina_estado_dados == 1:
                    flag_envia_saida_socket = False
                    #Pacote Json que indica saída de objeto na zona de detecção
                    dados_json_entrada_saida =  {
                                                    "pacote": "S1"
                                                }
                    #Convertendo o Json em Str e add o paragrafo para ser enviado via socket pacote de saida do objeto na zona de detecção                              
                    dados_json_entrada_saida = json.dumps(dados_json_entrada_saida) + "\n"
                    #Envio dos dados de saída via socket  
                    clientSocket.send(dados_json_entrada_saida.encode('utf8'))
                    maquina_estado_dados+=1 
                                      
                if flag_envia_dados_medicao_socket and maquina_estado_dados == 2:
                    flag_envia_dados_medicao_socket = False
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
                    #Envio dos dados calculados via socket                                    
                    clientSocket.send(dados_json_socket.encode('utf8'))
                    print("DADOS DE MEDIÇÃO ENVIADOS VIA SOCKET")
                    maquina_estado_dados = 0
                    
                if flag_envia_erro_medicao_socket:
                    flag_envia_erro_medicao_socket = False
                    #Convertendo o Json em Str e add o paragrafo para ser enviado via socket                                    
                    dados_json_error_socket = json.dumps(dados_json_error_socket) + "\n"
                    #Envio dos dados via socket  
                    clientSocket.send(dados_json_error_socket.encode('utf8'))

        except socket.error as e:
            flag_erro_envio_dados_socket = True
            print('ERRO AO ENVIAR DADOS VIA SOCKET DO TIPO: ', e)
            time.sleep(2)

#Start da thread   
socket_thread = Thread(target=socket_envio_dados)
socket_thread.daemon = True
socket_thread.start()

def main_code():
    global flag_erro
    flag_erro = False
    global tipo_erro
    global codigo_erro
    global descricao_erro
    global ser_sensor
    global ser_conversor_display
    global portas_usb_encontradas
    global flag_sensor_conectado
    flag_sensor_conectado = False
    global clientSocket
    global flag_erro_envio_dados_socket
    flag_erro_envio_dados_socket = False

    while True:
        time.sleep(1)
        portas_usb_encontradas = get_porta_sensor()  
        try:
            if flag_sensor_conectado == False:
                ser_sensor = serial.Serial(portas_usb_encontradas[0], 115200, timeout=0)
                ser_sensor.write(b'\x03')
                flag_sensor_conectado = True
                print("SENSOR CONECTADO")
        except serial.SerialException as e:
            flag_sensor_conectado = False
            portas_usb_encontradas = get_porta_sensor()
            tipo_erro = 'ERROR'
            codigo_erro = SENSOR_ERROR
            descricao_erro = e
            flag_erro = True
            print("ERRO SERIAL SENSOR CÓDIGO {}, DESCRIÇÃO DO ERRO: ".format(codigo_erro), e)
            #time.sleep(1)
            #ser_sensor.close()    
        '''
        try:
            ser_conversor_display = serial.Serial(portas_usb_encontradas[1], 9600, timeout=0)
        except serial.SerialException as e:
            portas_usb_encontradas = get_porta_sensor()
            tipo_erro = 'ERROR'
            codigo_erro = '6'
            descricao_erro = e
            flag_erro = True
            print('CONVERSOR DISPLAY DESCONECTADO', e)
            time.sleep(1)
            ser_conversor_display.close()   
        '''

        if flag_erro_envio_dados_socket:        

            try:
                clientSocket = socket.socket()        
                clientSocket.connect((HOST, PORT))
                print("Conexão socket estabelecida")
                # keep track of connection status
                flag_conexao_socket = True
                flag_erro_envio_dados_socket = False
            except:
                print('Erro de conexão socket tipo: ')
                flag_conexao_socket = False
                clientSocket = socket.socket()
                print("Conexão perdida...tentando reconectar")
                #pass        
                while not flag_conexao_socket:
                    # attempt to reconnect, otherwise sleep for 2 seconds
                    try:
                        clientSocket.connect((HOST, PORT))
                        flag_conexao_socket = True
                        flag_erro_envio_dados_socket = False
                        print("Reconexão estabelecida com sucesso")
                    except socket.error as e:
                        print('Erro de conexão socket tipo: ', e)
                        time.sleep(1)

        