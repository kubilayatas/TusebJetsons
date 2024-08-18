from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time 
import sys 
import numpy as np
import math
import smbus2 as smbus
import glob
from tkinter import filedialog
import tkinter as tk
from PIL import ImageTk, Image


def convert_data(data):
    sensor_list = []
    for i in range(0,24,2):
        sensor_reading = (data[i] << 8) + data[i+1]
        sensor_list.append(sensor_reading)
    return sensor_list


class ReadCellValueThread(QThread):
    data = pyqtSignal(list)
    update = pyqtSignal()

    def __init__(self,channel=1, parent=None):
        super(ReadCellValueThread, self).__init__(parent)
        self.bus = smbus.SMBus(channel)
        self.buffer = [[0 for j in range(0, 12)] for i in range(0, 34)]

    def run(self):
        while True:
            for addr in range(1,34+1):
                self.update.emit()
                try:
                    data = self.bus.read_i2c_block_data(addr+7, 0, 24, force=None)
                    time.sleep(0.1)
                    self.buffer[addr-1] = convert_data(data)
                    print("{}\n".format(self.buffer[addr-1]))
                except:
                    self.buffer[addr-1] = [None for n in range(0,12)]
                self.data.emit(self.buffer)
                #print("{}\n".format(self.buffer[addr-1]))
            


class User_Interface(QWidget):
    def __init__(self):
        super().__init__()

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
        self.ReadCellValueThread.update.connect(self.update_values)
        
    def update_values(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        for i in range(0,34):
            for k in range(0,4):
                fsr_degeri = sensorVal_list[i][k]
                if fsr_degeri == None:
                    color = QColor(163, 73, 164) # RGB
                    self.label_list[i * 4 + k].setStyleSheet(f"background-color: {color.name()};")
                    self.label_list[i * 4 + k].setText(f"{i+1:02d}##")
                    self.label_list[i * 4 + k].setAlignment(Qt.AlignCenter)
                else:
                    scaled_value = int((fsr_degeri/1023)*255)
                    color = QColor(scaled_value, 40, 255 - scaled_value) # RGB
                    self.label_list[i * 4 + k].setStyleSheet(f"background-color: {color.name()};")
                    self.label_list[i * 4 + k].setText(f"{fsr_degeri:04d}")
                    self.label_list[i * 4 + k].setAlignment(Qt.AlignCenter)

#############################################################################

class ImageViewer(object):
    def __init__(self):
        self.ReadCellValueThread = ReadCellValueThread()
        self.ReadCellValueThread.start()
        self.root = tk.Tk()
        #self.root.state('zoomed')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.images = None

        img, wh, ht = self.open_file()
        self.canvas = tk.Canvas(self.root, width=wh, height=ht, bg='black')
        self.canvas.pack(expand=tk.YES)
        self.image_on_canvas = self.canvas.create_image(self.width/2, self.height/2, anchor=tk.CENTER, image=img)
        self.ReadCellValueThread.update.connect(self.next_image)
        self.root.mainloop()

    def open_file(self):
        base_width = 150
        img = Image.new('RGB', [4*2,9*2], 255)
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        data = img.load()
        sensorVal_list = self.ReadCellValueThread.buffer
        for x in range(img.size[0]):
            for y in range(img.size[1]-2):
                addr = int(y/2)*4+int(x/2)
                sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                if sens_val==None:
                    data[x,y] = (159,122,36)
                else:
                    sens_val = int((sens_val/1023)*255)
                    data[x,y] = (sens_val,100,255-sens_val)
        img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        return img, self.width, self.height

    def next_image(self):

        img, wh, ht = self.open_file()
        img = ImageTk.PhotoImage(img)

        self.canvas.itemconfigure(self.image_on_canvas, image=img)
        self.canvas.config(width=self.width, height=self.height)
        try:
            self.canvas.wait_visibility()
        except tk.TclError:
            pass

#############################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #window = User_Interface()
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())
