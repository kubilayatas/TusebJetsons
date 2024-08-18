from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time 
import sys 
import numpy as np
import math
import smbus2 as smbus
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
            

class MyCanvas(QWidget):
    def __init__(self):
        super().__init__()
        # creating canvas
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.black)
        
class User_Interface(QWidget):
    def __init__(self):
        super().__init__()

        self.ReadCellValueThread = ReadCellValueThread()
        self.ReadCellValueThread.start()

        self.setGeometry(200, 200, 1000, 800) 
        self.setWindowTitle("FSR Arayüzü")
        box = QHBoxLayout()
        self.label = QLabel()
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)
        
        box.addWidget(self.label)
        
        self.setLayout(box)
        self.ReadCellValueThread.update.connect(self.next_())
    
    def update_img(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        base_width = 150
        img = Image.new('RGB', [4*2,9*2], 255)
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        data = img.load()
        for x in range(img.size[0]):
            for y in range(img.size[1]-2):
                addr = int(y/2)*4+int(x/2)
                sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                if sens_val==None:
                    data[x,y] = (159,122,36)
                else:
                    sens_val = int((sens_val/1023)*255)
                    data[x,y] = (sens_val,100,255-sens_val)
        img = img.resize((base_width, hsize), resample=Image.BICUBIC)
        img = ImageTk.PhotoImage(img)
        return img, self.width, self.height     
     
# =============================================================================
#     def update_values(self):
#         sensorVal_list = self.ReadCellValueThread.buffer
#         for i in range(0,34):
#             for k in range(0,4):
#                 fsr_degeri = sensorVal_list[i][k]
#                 if fsr_degeri == None:
#                     color = QColor(163, 73, 164) # RGB
#                     self.label_list[i * 4 + k].setStyleSheet(f"background-color: {color.name()};")
#                     self.label_list[i * 4 + k].setText(f"{i+1:02d}##")
#                     self.label_list[i * 4 + k].setAlignment(Qt.AlignCenter)
#                 else:
#                     scaled_value = int((fsr_degeri/1023)*255)
#                     color = QColor(scaled_value, 40, 255 - scaled_value) # RGB
#                     self.label_list[i * 4 + k].setStyleSheet(f"background-color: {color.name()};")
#                     self.label_list[i * 4 + k].setText(f"{fsr_degeri:04d}")
#                     self.label_list[i * 4 + k].setAlignment(Qt.AlignCenter)
# =============================================================================
    
    def next_(self):
        img, wh, ht = self.update_img()
        self.pixmap = QPixmap(img)
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = User_Interface()
    window.show()
    sys.exit(app.exec_())

            


# =============================================================================
# class User_Interface(object):
#     def __init__(self):
#         super().__init__()
#         global shared_data
#         self.data = shared_data
#         self.ReadCellValueThread = ReadCellValueThread()
#         self.ReadCellValueThread.start()
#         self.root = tk.Tk()
#         self.width = 800
#         self.height = 600
#         self.images = None
#         img, wh, ht = self.update_img()
#         self.canvas = tk.Canvas(self.root, width=wh, height=ht, bg='black')
#         self.canvas.pack(expand=tk.YES)
#         self.image_on_canvas = self.canvas.create_image(self.width/2, self.height/2, anchor=tk.CENTER, image=img)
#         #self.ReadCellValueThread.update.connect(self.next_)
#         self.root.mainloop()
#         
#         
#         
#     def update_img(self):
#         #sensorVal_list = self.ReadCellValueThread.buffer
#         sensorVal_list = self.data[-1]
#         shared_data.clear()
#         base_width = 150
#         img = Image.new('RGB', [4*2,9*2], 255)
#         wpercent = (base_width / float(img.size[0]))
#         hsize = int((float(img.size[1]) * float(wpercent)))
#         data = img.load()
#         for x in range(img.size[0]):
#             for y in range(img.size[1]-2):
#                 addr = int(y/2)*4+int(x/2)
#                 sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
#                 if sens_val==None:
#                     data[x,y] = (159,122,36)
#                 else:
#                     sens_val = int((sens_val/1023)*255)
#                     data[x,y] = (sens_val,100,255-sens_val)
#         img = img.resize((base_width, hsize), resample=Image.BICUBIC)
#         img = ImageTk.PhotoImage(img)
#         return img, self.width, self.height
#     
#     def next_(self):
# 
#         img, wh, ht = self.update_img()
#         self.canvas.itemconfigure(self.image_on_canvas, image=img)
#         self.canvas.config(width=self.width, height=self.height)
#         try:
#             self.canvas.wait_visibility()
#         except tk.TclError:
#             pass
# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = User_Interface()
    window.show()
    sys.exit(app.exec_())
