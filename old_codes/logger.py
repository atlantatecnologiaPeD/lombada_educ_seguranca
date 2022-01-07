#Bibliotecas
import json
import serial_conf
import time # Para usar o time.sleep
from crc_16bits import*
from binascii import hexlify


ser_Rasp = serial_conf.Serial('/dev/ttyS0', 9600, timeout=0)
ser_Rasp.reset_input_buffer()
ser_Sensor = serial_conf.Serial('/dev/ttyACM0', 115200, timeout=0)
ser_Sensor.reset_input_buffer()

arquivo = "logger.json"

file = open(arquivo,"a")


while True:
    time.sleep(0.01)
    try:
        if ser_Sensor.is_open:
            if ser_Sensor.inWaiting() > 0:
                sensor_data = ser_Sensor.readline().decode("utf-8")
                print(sensor_data)
                file.write(sensor_data)
    except:
        #pass
        print('pass')