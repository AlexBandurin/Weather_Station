import socket
#import numpy as np
#import encodings
import Adafruit_DHT
import Adafruit_MCP3008
import time
import bme280
import smbus2

HOST = '192.168.4.65'  # Standard loopback interface address (localhost)
PORT = 65431        # Port to listen on (non-privileged ports are > 1023)
pin = 4
sensor = Adafruit_DHT.DHT22
start_time = time.time()

# BME280 setup
port = 1
address = 0x76 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

mcp = Adafruit_MCP3008.MCP3008(clk=18, cs=25, miso=23,mosi=24)
TEMP_PIN = 0
WIND_PIN = 1
#start_time = time.time()
#duration = 60
weather_data = []
zeroWindAdjustment = 0.35


def sensor_data():
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    temperature = bme280_data.temperature
    
    TMP_ADunits = mcp.read_adc(TEMP_PIN)
    Wind_ADunits = mcp.read_adc(WIND_PIN)
    Wind_Volts = (Wind_ADunits * 0.0048828125)
    TempCtimes100 = (0.005 * (float(TMP_ADunits) * float(TMP_ADunits))) - (16.862 * float(TMP_ADunits)) + 9075.4
    zeroWind_ADunits = -0.0006 * (float(TMP_ADunits) * float(TMP_ADunits)) + 1.0727 * float(TMP_ADunits) + 47.172
    zeroWind_volts = (zeroWind_ADunits * 0.0048828125) - zeroWindAdjustment
    try:
        WindSpeed_MPH =  pow(((Wind_Volts - zeroWind_volts) /.2300) , 2.7265)
        W = (WindSpeed_MPH*0.44704)
    except Exception as e:
        W = None
        print(e)
    
    if humidity is not None and TempCtimes100 is not None and W is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        print("data was written on database T{} H{}".format(temperature,humidity))
        print("WindSpeed_MPH: ", W, "Temperature: ",TempCtimes100/100, "Pressure: ", pressure)
        print(type(W))
        print(type(TempCtimes100))
        #if TempCtimes100 is None:
        #    TempCtimes100 = '0'
        data = '{},{},{}'.format(humidity, W, TempCtimes100/100)
        print('sent a batch')
    else:
        print("Sensor failure.")        
        data = 'error,error,error,error,error'
    return data

def my_server():
    duration = 6000
    ungoing = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Server Started waiting for client to connect ")
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")  
        conn, addr = s.accept()             
        print(f"Connection from {addr}")
        with conn:
            print('Connected by', addr)
            while ungoing:
                my_data = sensor_data()
                x_encoded_data = my_data.encode('utf-8')
                conn.send(x_encoded_data)                    
                current_time = time.time()
                time_elapsed = current_time - start_time
                if (time_elapsed) >= duration:
                    ungoing = False
                print("Time elapsed: ", round(time_elapsed, 1), "s")
                time.sleep(1)

if __name__ == '__main__':
    my_server()