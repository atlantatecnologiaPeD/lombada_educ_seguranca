import serial
import json


class DopplerSensor:
    def __init__(self, porta, baudrate):
        self.baudrate = baudrate
        self.porta = porta

    def getStatus(self):
        try:
            with serial.Serial(self.porta, self.baudrate) as porta:
                porta.write(b'??')
                dados = porta.readline()
                x = json.loads(dados)
                print("o produto", x["Product"], "esta vivo na porta", porta.name)
                return(x)
        except serial.SerialException as e:
            print("NÃO FOI POSSIVEL A COMUNICAÇÃO COM O SENSOR, POR FAVOR, VERIFICAR SE  PORTA ESTA CORRETA OU SE ESTA PLUGADO")
            return("NULL")
            

    def getTime(self):
        try:
            with serial.Serial(self.porta, self.baudrate) as porta:
                porta.write(b'C?')
                dados = porta.readline()
                x = json.loads(dados)
                return(x["Clock"])
                print(x["Clock"],"segundos")
        except serial.SerialException as e:
            print("NÃO FOI POSSIVEL A COMUNICAÇÃO COM O SENSOR, POR FAVOR, VERIFICAR SE  PORTA ESTA CORRETA OU SE ESTA PLUGADO")
            return ("NULL")

