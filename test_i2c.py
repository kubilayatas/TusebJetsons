import time
import smbus2 as smbus

bus = smbus.SMBus(1)
time.sleep(1)

def convert_data(data):
    sensor_list = []
    for i in range(0,24,2):
        sensor_reading = (data[i] << 8) + data[i+1]
        sensor_list.append(sensor_reading)
    return sensor_list


while(1):
    data = bus.read_i2c_block_data(39, 0, 24, force=None)
    listt = convert_data(data)
    print(listt)