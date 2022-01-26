'''
import serial.tools.list_ports as port_list
ports = list(port_list.comports())
for p in ports:
    print(p)
'''

import serial
import serial.tools.list_ports as port_list

BD_SENSOR = 115200
BD_CONVERSOR_SERIAL = 9600

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