import serial
import json
import time
from serial_config import*

flag_comunicacao_sensor = False
flag_configuracao_ok = False
flag_parar_loop_envio_distancia = False
cont_estado = 0

def envia_comando_sensor(comando):
    ser_sensor.write(comando)
    time.sleep(0.1)
    sensor_data = ser_sensor.readline().decode("utf-8")
    return json.loads(sensor_data)

while not flag_configuracao_ok:
    time.sleep(0.01)
    if flag_comunicacao_sensor == False:
        try:
            ser_sensor = serial.Serial(portas_usb_encontradas[0], 115200, timeout=0)
            ser_sensor.reset_input_buffer()
            print('Sensor conectado')
            flag_comunicacao_sensor = True
        except serial.SerialException as e:
            print('Erro de conexão serial do tipo: ', e)
    print(cont_estado)
    if cont_estado == 0:
        while not flag_parar_loop_envio_distancia:
            try:
                dicionario_json = envia_comando_sensor(b'Od')
                if dicionario_json['SpeedOutputFeature'] == 'd':          
                    print('envio de distância a todo momento parada com sucesso')
                    cont_estado+=1
                    flag_parar_loop_envio_distancia = True
                else:
                    dicionario_json = {}
                    dicionario_json = envia_comando_sensor(b'Od')
            except json.JSONDecodeError as e:
                print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 1:
        try:
            dicionario_json = envia_comando_sensor(b'uM')
            if dicionario_json['RangeUnit'] == 'm':
                print('distância em "m" configurada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 2:
        try:
            dicionario_json = envia_comando_sensor(b'UK')
            if dicionario_json['SpeedUnit'] == 'kmph':
                print('velocidade em "km/h" configurada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 3:
        try:
            dicionario_json = envia_comando_sensor(b'S2')
            if dicionario_json['DopplerSampleRateHz'] == 20000:
                print('sample hate de 20000 amostras/s configurada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 4:
        try:
            dicionario_json = envia_comando_sensor(b'K+')
            if dicionario_json['DopplerPeakDetect'] == 'Enabled':
                print('cálculo da velocidade pela média dos picos configurada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 5:
        try:
            dicionario_json = envia_comando_sensor(b'OJ')
            if dicionario_json['SpeedOutputFeature'] == 'J':
                print('dados em formato Json habilitado com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 6:
        try:
            dicionario_json = envia_comando_sensor(b'OS')
            if dicionario_json['SpeedOutputFeature'] == 'S':
                print('envio de velocidade habilitada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 7:
        try:
            dicionario_json = envia_comando_sensor(b'OM')
            if dicionario_json['SpeedOutputFeature'] == 'M':
                print('envio das magnitudes de detecção de velocidade habilitadas com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 8:
        try:
            dicionario_json = envia_comando_sensor(b'oM')
            if dicionario_json['RangeOutputFeature'] == 'M':
                print('envio das magnitudes de detecção de distância habilitadas com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 9:
        try:
            dicionario_json = envia_comando_sensor(b'OY')
            if dicionario_json['SpeedOutputFeature'] == 'Y':
                print('envio de velocidade + distância habilitada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 10:
        try: 
            dicionario_json = envia_comando_sensor(b'OD')
            if dicionario_json['SpeedOutputFeature'] == 'D':
                print('envio de distância habilitada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 11:
        try:
            dicionario_json = envia_comando_sensor(b'IG')
            if dicionario_json['Interface'] == 'Enable Object Sensor on GPIO':
                print('envio dos dados somente dentro da zona de detecção habilitado com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 12:
        try:
            dicionario_json = envia_comando_sensor(b'R+')
            if dicionario_json['RequiredDirection'] == 'Towards Only':
                print('captura de objetos apenas na aproximação configurada com sucesso')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 13:
        try:
            dicionario_json = envia_comando_sensor(b'F0')
            if dicionario_json['FormatDigits'] == 0:
                print('magnitudes e velocidades configuradas sem casa decimal')
                cont_estado+=1
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
    elif cont_estado == 14:
        try:
            ser_sensor.write(b'A!')  
            time.sleep(1)    
            sensor_data = ser_sensor.readline().decode("utf-8")
            dicionario_json = json.loads(sensor_data)
            if dicionario_json['INFO'] == 'Saving current values to Persistent Settings':
                print('Sensor configurado com sucesso')
                cont_estado = 0
                flag_configuracao_ok = True
        except KeyError as e:
            print("ERRO DO TIPO: ", e)
        except json.JSONDecodeError as e:
            print("ERRO JSON DO TIPO: ", e)
        



