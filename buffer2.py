from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time 
import sys 
import numpy as np
import math
import smbus2 as smbus
import threading

def convert_data(data):
    sensor_list = []
    for i in range(0,24,2):
        sensor_reading = (data[i] << 8) + data[i+1]
        sensor_list.append(sensor_reading)
    return sensor_list

c = threading.Condition()
thread_flag = 0
buffer = [[0 for j in range(0, 12)] for i in range(0, 34)]

class ReadCellValueThread(threading.Thread):

    def __init__(self,channel=1):
        threading.Thread.__init__(self)
        self.bus = smbus.SMBus(channel)


    def run(self):
        global thread_flag
        global buffer
        while True:
            c.acquire()
            if thread_flag == 0:
                thread_flag = 1
                for addr in range(1,34+1):
                    try:
                        data = self.bus.read_i2c_block_data(addr+7, 0, 24, force=None)
                        time.sleep(0.1)
                        buffer[addr-1] = convert_data(data)
                        print("{}\n".format(buffer[addr-1]))
                    
                    except:
                        buffer[addr-1] = [None for n in range(0,12)]
                c.notify_all()
            else:
                c.wait()
            c.release()
                    


class User_Interface(QWidget,threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)
        self.ReadCellValueThread = ReadCellValueThread()
        self.ReadCellValueThread.start()

        self.setGeometry(200, 200, 1000, 800) 
        self.setWindowTitle("FSR Arayüzü")
        

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)

        self.label_list = [QLabel(f"FSR{i+1:03d}") for i in range(0, 144)]
        for i in range(0,144):
            self.label_list[i].setStyleSheet("border: 1px solid black;")
        
        for cell in range(0,36):
            cell_column = cell%4
            cell_row = math.floor(cell/4)
            first_fsr = cell_row*16 + cell_column*4
            row = cell_row*2
            col = cell_column*2
            grid_layout.addWidget(self.label_list[first_fsr], row, col)
            grid_layout.addWidget(self.label_list[first_fsr + 1], row, col+1)
            grid_layout.addWidget(self.label_list[first_fsr + 2], row+1, col)
            grid_layout.addWidget(self.label_list[first_fsr + 3], row+1, col+1)
            
        self.setLayout(grid_layout)
        #self.ReadCellValueThread.data_received.connect(self.update_values)
        
    def run(self):
        global thread_flag
        global buffer
        while True:
            c.acquire()
            if thread_flag == 1:
                for i in range(0,34):
                    for k in range(0,4):
                        fsr_degeri = buffer[i][k]
                        if fsr_degeri:
                            fsr_degeri = int(fsr_degeri) 
                            scaled_value = int((fsr_degeri/1023)*255)
                            color = QColor(scaled_value, 0, 255 - scaled_value) # RGB
                            self.label_list[i * 4 + k].setStyleSheet(f"background-color: {color.name()};")
                            self.label_list[i * 4 + k].setAlignment(Qt.AlignCenter)
                c.notify_all()
            else:
                c.wait()
            c.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = User_Interface()
    window.show()
    sys.exit(app.exec_())
