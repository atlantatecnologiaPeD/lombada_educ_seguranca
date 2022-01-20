from fastapi import FastAPI
from threading import Thread
from serial_config import*
from main import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
from fastapi.responses import HTMLResponse




#Start das threads        
mainThread = Thread(target=main_code)
mainThread.daemon = True
mainThread.start()

'''
sensorThread = Thread(target=sensor_data)
sensorThread.daemon = True
sensorThread.start()
'''

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
        except serial.SerialException as e:
            print("NÃO FOI POSSIVEL A COMUNICAÇÃO COM O SENSOR, POR FAVOR, VERIFICAR SE  PORTA ESTA CORRETA OU SE ESTA PLUGADO")
            return ("NULL")


dopplerSensor = DopplerSensor(portas_usb_encontradas[0],BD_SENSOR)

description = """
DESCRICAO DA LOMBADA
"""

app = FastAPI(
    debug=False,
    title="ATL-LOMBADA",
    description=description,
    version="1.0.10",
    contact={
        "name": "Ari",
        "url": "https://www.atlantatecnologia.com.br",
        "email": "arimateia.carvalho@atlantatecnologia.com.br",
    },
    license_info={
        "name": "Atlanta Tecnologia © ",
    },
)


security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """
    Endereço raiz do WS
    """   
    return  "<strong>ATLANTA TECNOLOGIA DA INFORMAÇÃO</strong> <br> API de integração<br>"

@app.get("/version")
async def versao():
    """
    Retorna a versão deste WEB Service
    """
    return {"versao": "1.0.10"}
    
@app.get("/getstatus")
async def getstatus():
    """
    Retorna o status do sensor
    """
    json_value  = dopplerSensor.getStatus()
    return {"status": json_value}

@app.get("/gettime")
async def gettime():
    """
    Retorna o status do sensor
    """
    json_value  = dopplerSensor.getTime()
    return {"status": json_value}

@app.get("/habilitaenvioveldisp/{dado}")
async def habilita_envio_vel_disp(dado):
    """
    Habilita ou desabilita o envio de velocidade para o display de velocidade
    """
    habilita_envio_vel_display(dado)
    return {"status": dado}

@app.get("/requisitaestadodisplay")
async def requisita_estado_disp():
    """
    Requisita estado dos dígitos do display
    """
    requisita_estado_digitos()
    avalia_digitos = avalia_estado_digitos()
    return {"status": avalia_digitos}

@app.get("/velregulamentada/{dado}")
async def vel_regulamentada(dado):
    """
    Envia velocidade regulamentada para o display
    """
    display_protocolo_envia_vel_reg(int(dado))
    return {"status": 'Ok'}