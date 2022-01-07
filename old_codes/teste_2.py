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
connection = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
connection.reset_input_buffer()
ser = serial.Serial('/dev/ttyS0', 9600, timeout=0)
ser.write(b'INICIEI\r\n')

#CRC config
formato_CRC = crc_16("HEX")

#Funções
def sendVel(vel, crc16_alta, crc16_baixa):
    ser.write(serial.to_bytes([CABECALHO,COMANDO,ID_FAIXA,vel,crc16_alta, crc16_baixa,RODAPE]))

while True:
    #ser.write(serial.to_bytes([CABECALHO,0x82,ID_FAIXA,0x01,0x8A,0xF4,RODAPE]))
    time.sleep(0.01)
    #print('oi')
    if connection.inWaiting() > 0:
        #print('oi')
        sensor_data = connection.readline().decode("utf-8")
        print(sensor_data)
        #try:
            #dict_json = json.loads(sensor_data)
            #velocidade_sensor = int(dict_json['DetectedObjectVelocity'])
            #print(b'velocidade sensor:', velocidade_sensor)
            #protocolo = f'{COMANDO:x}{ID_FAIXA:x}{velocidade_sensor:x}'
            #CRC_16_bits = (formato_CRC.crc16_CCITT(str(protocolo)))  
            #msb_CRC = (CRC_16_bits[0:1])
            #lsb_CRC = (CRC_16_bits[1:4])
            #msb_CRC_hex = int.from_bytes(msb_CRC, 'big', signed=False)
            #lsb_CRC_hex= int.from_bytes(lsb_CRC, 'big', signed=False) 
            #sendVel(velocidade_sensor, msb_CRC_hex, lsb_CRC_hex)
        #except json.JSONDecodeError as e:
            #print("JSON:", e)
            #time.sleep(1)
