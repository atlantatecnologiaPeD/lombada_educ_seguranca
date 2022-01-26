from crc_16bits import*
import serial
import serial.tools.list_ports as port_list

#Constantes do protocolo do display
CABECALHO = 0xAB 
COMANDO = 0x81
ID_FAIXA = 0x10
RODAPE = 0xCD
BD_SENSOR = 115200
BD_CONVERSOR_SERIAL = 9600
COMANDO_ENVIA_VEL_REG = 0x83
COMANDO_ESTADO_DIGITO = 0x86

#CRC configuração
formato_CRC = crc_16("HEX")

#Definicção das Funções
#Função de listar portas seriais ativas e conectar ao sensor
def get_porta_sensor():
    porta_sensor_doppler = None
    porta_conversor_serial = None
    ports = list(port_list.comports())
    for p in ports:
        if "IFX CDC" in p.description:
            porta_sensor_doppler = p.device
        if "FT232R USB UART" in p.description:
            porta_conversor_serial = p.device
    return str(porta_sensor_doppler), str(porta_conversor_serial)


#Conexões seriais e suas confogurações 
portas_usb_encontradas = get_porta_sensor()



if portas_usb_encontradas[0] == 'None':
    print('Sensor não encontrado')
else:
    print('O sensor foi encontrado na porta: ', portas_usb_encontradas[0])

if portas_usb_encontradas[1] == 'None':
    print('Conversor USB/Serial não encontrado')
else:
    print('O conversor USB/Serial foi encontrado na porta: ', portas_usb_encontradas[1])

try:
    ser_sensor = serial.Serial(portas_usb_encontradas[0], BD_SENSOR, timeout=0)
    ser_sensor.reset_input_buffer()

    ser_conversor_display = serial.Serial(portas_usb_encontradas[1], BD_CONVERSOR_SERIAL, timeout=0)
    ser_conversor_display.reset_input_buffer()
except Exception as e:
    print('Erro do tipo: ', e)

#Função de envio de dados para display de velocidade
def send_vel(vel, crc16_alta, crc16_baixa):
    ser_conversor_display.write(serial.to_bytes([CABECALHO,COMANDO,ID_FAIXA,vel,crc16_alta, crc16_baixa,RODAPE])) 
    

#Função que cria o pacote de dados de velocidade para ser enviado ao display de velocidade
def display_protocolo(velocidade_sensor):
    #Escreve protocolo em formato HEX e o dado (velocidade) com duas casas decimais ex:0F ou 0A...
    protocolo = f'{COMANDO:x}{ID_FAIXA:x}{velocidade_sensor:0{2}x}'
    #print('Protocolo a ser enviado', protocolo)
    CRC_16_bits = (formato_CRC.crc16_CCITT(str(protocolo))) 
    msb_CRC = (CRC_16_bits[0:1])
    lsb_CRC = (CRC_16_bits[1:4])
    msb_CRC_hex = int.from_bytes(msb_CRC, 'big', signed=False)
    lsb_CRC_hex= int.from_bytes(lsb_CRC, 'big', signed=False) 
    return msb_CRC_hex, lsb_CRC_hex


def requisita_estado_digitos():
    ser_conversor_display.write(serial.to_bytes(
        [CABECALHO, COMANDO_ESTADO_DIGITO, ID_FAIXA, 0xBE, 0x00, RODAPE]))

def avalia_estado_digitos():
    lista_de_dados = []
    lista_unidade = []
    lista_dezena = []
    status_dezena = ''
    status_unidade = ''
    while(len(lista_dezena) < 7):
        if ser_conversor_display.inWaiting() > 0:
            sensor_data = ser_conversor_display.read(1)
            hex_string = binascii.hexlify(sensor_data).decode('utf-8')
            lista_de_dados.append(hex_string)
            lista_unidade = lista_de_dados[3:10]
            lista_dezena = lista_de_dados[10:17]
    if 'ff' in lista_unidade:
         print('Unidade com defeito')
         status_unidade = 'Unidade com defeito'
    else:
        print('Unidade OK')
        status_unidade = 'Unidade OK'
    if 'ff' in lista_dezena:
        print('Dezena com defeito')
        status_dezena = 'Dezena com defeito'
    else:
        print('Dezena OK')
        status_dezena = 'Dezena OK'
    return status_dezena, status_unidade
    

def display_protocolo_envia_vel_reg(velocidade_display_regulamentada):
    # Escreve protocolo em formato HEX e o dado (velocidade) com duas casas decimais ex:0F ou 0A...
    protocolo = f'{COMANDO_ENVIA_VEL_REG:x}{ID_FAIXA:x}{velocidade_display_regulamentada:0{2}x}'
    print('Protocolo a ser enviado', protocolo)
    CRC_16_bits = (formato_CRC.crc16_CCITT(str(protocolo)))
    msb_CRC = (CRC_16_bits[0:1])
    lsb_CRC = (CRC_16_bits[1:4])
    msb_CRC_hex = int.from_bytes(msb_CRC, 'big', signed=False)
    lsb_CRC_hex = int.from_bytes(lsb_CRC, 'big', signed=False)
    print('MSB ', msb_CRC_hex)
    print('LSB ', lsb_CRC_hex)
    ser_conversor_display.write(serial.to_bytes(
        [CABECALHO, COMANDO_ENVIA_VEL_REG, ID_FAIXA, velocidade_display_regulamentada, msb_CRC_hex, lsb_CRC_hex, RODAPE]))
    print('cabecalho', CABECALHO)
    print('cmd', COMANDO_ENVIA_VEL_REG)
    print('faixa', ID_FAIXA)
    print('dado', velocidade_display_regulamentada)
    print('msb', msb_CRC_hex)
    print('lsb', lsb_CRC_hex)
    print('rodape', RODAPE)