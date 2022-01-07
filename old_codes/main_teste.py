#Autor: Anderson Liege
#Data:14/10/2021
#Projeto Lombada Educativa
 
#Bibliotecas
import json
import serial
import time # Para usar o time.sleep
from crc_16bits import*
from binascii import hexlify

#Constantes
CABECALHO = 0xAB 
COMANDO = 0x81
ID_FAIXA = 0x10
RODAPE = 0xCD

#Serial
ser_Sensor = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
ser_Sensor.reset_input_buffer()

ser_Rasp = serial.Serial('/dev/ttyS0', 9600, timeout=0)
ser_Rasp.reset_input_buffer()


#CRC config
formato_CRC = crc_16("HEX")

#Funções
def sendVel(vel, crc16_alta, crc16_baixa):
    ser_Rasp.write(serial.to_bytes([CABECALHO,COMANDO,ID_FAIXA,vel,crc16_alta, crc16_baixa,RODAPE])) 

sendVel(0x0B,0x72,0xEE)
time.sleep(2)    

while True:
    time.sleep(0.01)
    
    try:
        ser_Sensor = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
    except serial.SerialException as e:
        print('sensor desconectado')
        time.sleep(1)
        ser_Sensor.close()    

    time.sleep(0.01)
    
    try:
        if ser_Sensor.is_open:
            if ser_Sensor.inWaiting() > 0:
                sensor_data = ser_Sensor.readline().decode("utf-8")
                print('sensor conectado')
                print(sensor_data)
                try:
                    dict_json = json.loads(sensor_data)
                    print('Dados recebidos pelo sensor:', dict_json)
                    velocidade_sensor = int(dict_json['DetectedObjectVelocity'])
                    print('Velocidade do sensor:', velocidade_sensor)
# Escreve protocolo em formato HEX e o dado (velocidade) com duas casas decimais ex:0F ou 0A...
                    protocolo = f'{COMANDO:x}{ID_FAIXA:x}{velocidade_sensor:0{2}x}'
                    print('Protocolo a ser enviado', protocolo)
                    CRC_16_bits = (formato_CRC.crc16_CCITT(str(protocolo))) 
                    msb_CRC = (CRC_16_bits[0:1])
                    lsb_CRC = (CRC_16_bits[1:4])
                    msb_CRC_hex = int.from_bytes(msb_CRC, 'big', signed=False)
                    lsb_CRC_hex= int.from_bytes(lsb_CRC, 'big', signed=False) 
                    sendVel(velocidade_sensor, msb_CRC_hex, lsb_CRC_hex)
                except json.JSONDecodeError as e:
                    print("JSON:", e)
                    pass
    except:
        #pass
        print('pass')