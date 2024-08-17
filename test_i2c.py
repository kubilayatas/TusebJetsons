from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time 
import sys 
import numpy as np
import math
import smbus2 as smbus

bus = smbus.SMBus(1)

def convert_data(data):
    fsr_list = []
    for i in range(0,7):
        fsr_reading = (data[i] << 8) + data[i+1]
        fsr_list.append(fsr_reading)

    return fsr_list

buffer = [[i*j for j in range(1, 8)] for i in range(1, 32)]

for addr in range(0,34):
    data = bus.read_i2c_block_data(addr+8, 0, 24)
    data = convert_data(data)
    buffer[addr] = data
    print("adres:{addr};data:{data}\n")