from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time 
import sys 
import numpy as np
import math
import smbus2 as smbus
from PIL import ImageTk, Image
from PIL.ImageQt import ImageQt


def convert_data(data):
    sensor_list = []
    for i in range(0,24,2):
        sensor_reading = (data[i] << 8) + data[i+1]
        sensor_list.append(sensor_reading)
    return sensor_list


class ReadCellValueThread(QThread):
    data_r = pyqtSignal(str)

    def __init__(self,channel=1, parent=None):
        super(ReadCellValueThread, self).__init__(parent)
        self.bus = smbus.SMBus(channel)
        self.buffer = [[0 for j in range(0, 12)] for i in range(0, 34)]

    def run(self):
        while True:
            for addr in range(1,34+1):
                try:
                    data = self.bus.read_i2c_block_data(addr+7, 0, 24, force=None)
                    time.sleep(0.1)
                    self.buffer[addr-1] = convert_data(data)
                    print("{}\n".format(self.buffer[addr-1]))
                except:
                    self.buffer[addr-1] = [None for n in range(0,12)]
                self.data_r.emit("dataR")
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
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        ###############################################
        self.label_fsr = QLabel()
        self.label_fsr_text = QLabel()
        canvas_fsr = QPixmap(150, 340)
        canvas_fsr.fill(Qt.white)
        
        self.label_fsr.setPixmap(canvas_fsr)
        self.label_fsr.setStyleSheet("border: 1px solid black;")
        
        self.label_fsr_text.setText("Basınç Haritası")
        self.label_fsr_text.setStyleSheet("border: 1px solid black;")
        ###############################################
        self.label_heat = QLabel()
        self.label_heat_text = QLabel()
        canvas_heat = QPixmap(150, 340)
        canvas_heat.fill(Qt.white)
        
        self.label_heat.setPixmap(canvas_heat)
        self.label_heat.setStyleSheet("border: 1px solid black;")
        
        self.label_heat_text.setText("Sıcaklık Haritası")
        self.label_heat_text.setStyleSheet("border: 1px solid black;")
        ###############################################
        self.label_humid = QLabel()
        self.label_humid_text = QLabel()
        canvas_humid = QPixmap(150, 340)
        canvas_humid.fill(Qt.white)
        
        self.label_humid.setPixmap(canvas_humid)
        self.label_humid.setStyleSheet("border: 1px solid black;")
        
        self.label_humid_text.setText("% Bağıl Nem Haritası")
        self.label_humid_text.setStyleSheet("border: 1px solid black;")
        ###############################################
        grid_layout.addWidget(self.label_fsr_text, 0, 0)
        grid_layout.addWidget(self.label_fsr, 1, 0)
        
        grid_layout.addWidget(self.label_heat_text, 0, 1)
        grid_layout.addWidget(self.label_heat, 1, 1)
        
        grid_layout.addWidget(self.label_humid_text, 0, 2)
        grid_layout.addWidget(self.label_humid, 1, 2)
        
        self.setLayout(grid_layout)
        self.ReadCellValueThread.data_r.connect(self.update_img)
##############################################################################    
    def create_img_FSR(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        base_width = 150
        not_connected_color = (159,122,36)
        img = Image.new('RGB', [4*2,9*2], 255)
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        data = img.load()
        for x in range(img.size[0]):
            for y in range(img.size[1]-2):
                addr = int(y/2)*4+int(x/2)
                sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                if sens_val==None:
                    data[x,y+2] = not_connected_color
                else:
                    sens_val = int((sens_val/1023)*255)
                    data[x,y+2] = (sens_val,100,255-sens_val)
        ###
        for x in range(img.size[0]):
            for y in range(2):
                addr = int(y/2)*4+int(x/2)+31
                if (addr==31 or addr==34):
                    data[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                    if sens_val==None:
                        data[x,y] = not_connected_color
                    else:
                        sens_val = int((sens_val/1023)*255)
                        data[x,y] = (sens_val,100,255-sens_val)
        ###
        img = img.resize((base_width, hsize), resample=Image.BICUBIC)
        #img = ImageTk.PhotoImage(img)
        return img, self.width, self.height
###############################################################################    
    def create_img_HEAT(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        base_width = 150
        not_connected_color = (159,122,36)
        img2 = Image.new('RGB', [4,9], 255)
        wpercent = (base_width / float(img2.size[0]))
        hsize = int((float(img2.size[1]) * float(wpercent)))
        data2 = img2.load()
        for x in range(img2.size[0]):
            for y in range(img2.size[1]-1):
                addr = y*4+x
                sens_val = sensorVal_list[addr][7]
                sens_val2 = sensorVal_list[addr][9]
                if sens_val==None:
                    data2[x,y+1] = not_connected_color
                elif sens_val2==None:
                    data2[x,y+1] = not_connected_color
                else:
                    if(sens_val == 1001+addr):sens_val = sens_val2
                    if(sens_val2 == 1001+addr):sens_val2 = sens_val
                    sens_val = int((sens_val+sens_val2)/2)
                    if(sens_val == 1001+addr):data2[x,y+1] = not_connected_color
                    else:
                        sens_val = int((sens_val/65535)*255)
                        data2[x,y+1] = (sens_val,100,255-sens_val)
        ###
        for x in range(img2.size[0]):
            for y in range(1):
                addr = y*4+x+31
                if (addr==31 or addr==34):
                    data2[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][7]
                    if sens_val==None:
                        data2[x,y] = not_connected_color
                    else:
                        sens_val += sensorVal_list[addr][9]
                        sens_val = int(sens_val/2)
                        sens_val = int((sens_val/65535)*255)
                        data2[x,y] = (sens_val,100,255-sens_val)
        ###
        img2 = img2.resize((base_width, hsize), resample=Image.BICUBIC)
        #img = ImageTk.PhotoImage(img)
        return img2, self.width, self.height
     
###############################################################################
    def create_img_HUMID(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        base_width = 150
        not_connected_color = (159,122,36)
        img3 = Image.new('RGB', [4,9], 255)
        wpercent = (base_width / float(img3.size[0]))
        hsize = int((float(img3.size[1]) * float(wpercent)))
        data3 = img3.load()
        for x in range(img3.size[0]):
            for y in range(img3.size[1]-1):
                addr = y*4+x
                if (addr == 4):print("addr 4")
                sens_val = sensorVal_list[addr][6]
                sens_val2 = sensorVal_list[addr][8]
                if sens_val==None:
                    data3[x,y+1] = not_connected_color
                elif sens_val2==None:
                    data3[x,y+1] = not_connected_color
                else:
                    if(sens_val == 1001+addr):sens_val = sens_val2
                    if(sens_val2 == 1001+addr):sens_val2 = sens_val
                    sens_val = int((sens_val + sens_val2)/2)
                    if(sens_val == 1001+addr):data3[x,y+1] = not_connected_color
                    else:
                        sens_val = int((sens_val/65535)*255)
                        data3[x,y+1] = (sens_val,100,255-sens_val)
        ###
        for x in range(img3.size[0]):
            for y in range(1):
                addr = y*4+x+31
                if (addr==31 or addr==34):
                    data3[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][6]
                    if sens_val==None:
                        data3[x,y] = not_connected_color
                    else:
                        sens_val += sensorVal_list[addr][8]
                        sens_val = int(sens_val/2)
                        sens_val = int((sens_val/65535)*255)
                        data3[x,y] = (sens_val,100,255-sens_val)
        ###
        img3 = img3.resize((base_width, hsize), resample=Image.BICUBIC)
        #img = ImageTk.PhotoImage(img)
        return img3, self.width, self.height
     
###############################################################################
    def create_img(self):
        sensorVal_list = self.ReadCellValueThread.buffer
        base_width = 150
        not_connected_color = (159,122,36)
        img1 = Image.new('RGB', [4*2,9*2], 255)
        wpercent1 = (base_width / float(img1.size[0]))
        hsize1 = int((float(img1.size[1]) * float(wpercent1)))
        data1 = img1.load()
        for x in range(img1.size[0]):
            for y in range(img1.size[1]-2):
                addr = int(y/2)*4+int(x/2)
                sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                if sens_val==None:
                    data1[x,y+2] = not_connected_color
                else:
                    sens_val = int((sens_val/1023)*255)
                    data1[x,y+2] = (sens_val,100,255-sens_val)
        ###
        for x in range(img1.size[0]):
            for y in range(2):
                addr = int(y/2)*4+int(x/2)+31
                if (addr==31 or addr==34):
                    data1[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][(x%2)+(y%2)*2]
                    if sens_val==None:
                        data1[x,y] = not_connected_color
                    else:
                        sens_val = int((sens_val/1023)*255)
                        data1[x,y] = (sens_val,100,255-sens_val)
        ###
        img1 = img1.resize((base_width, hsize1), resample=Image.BICUBIC)
        #img = ImageTk.PhotoImage(img)
        img2 = Image.new('RGB', [4,9], 255)
        wpercent2 = (base_width / float(img2.size[0]))
        hsize2 = int((float(img2.size[1]) * float(wpercent2)))
        data2 = img2.load()
        for x in range(img2.size[0]):
            for y in range(img2.size[1]-1):
                addr = y*4+x
                sens_val = sensorVal_list[addr][7]
                if sens_val==None:
                    data2[x,y+1] = not_connected_color
                else:
                    sens_val += sensorVal_list[addr][9]
                    sens_val = int(sens_val/2)
                    sens_val = int((sens_val/65535)*255)
                    data2[x,y+1] = (sens_val,100,255-sens_val)
        ###
        for x in range(img2.size[0]):
            for y in range(1):
                addr = y*4+x+31
                if (addr==31 or addr==34):
                    data2[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][7]
                    if sens_val==None:
                        data2[x,y] = not_connected_color
                    else:
                        sens_val += sensorVal_list[addr][9]
                        sens_val = int(sens_val/2)
                        sens_val = int((sens_val/65535)*255)
                        data2[x,y] = (sens_val,100,255-sens_val)
        ###
        img2 = img2.resize((base_width, hsize2), resample=Image.BICUBIC)
        
        img3 = Image.new('RGB', [4,9], 255)
        wpercent3 = (base_width / float(img3.size[0]))
        hsize3 = int((float(img3.size[1]) * float(wpercent3)))
        data3 = img3.load()
        for x in range(img3.size[0]):
            for y in range(img3.size[1]-1):
                addr = y*4+x
                sens_val = sensorVal_list[addr][6]
                if sens_val==None:
                    data3[x,y+1] = not_connected_color
                else:
                    sens_val += sensorVal_list[addr][8]
                    sens_val = int(sens_val/2)
                    sens_val = int((sens_val/65535)*255)
                    data3[x,y+1] = (sens_val,100,255-sens_val)
        ###
        for x in range(img3.size[0]):
            for y in range(1):
                addr = y*4+x+31
                if (addr==31 or addr==34):
                    data3[x,y] = not_connected_color
                else:
                    sens_val = sensorVal_list[addr][6]
                    if sens_val==None:
                        data3[x,y] = not_connected_color
                    else:
                        sens_val += sensorVal_list[addr][8]
                        sens_val = int(sens_val/2)
                        sens_val = int((sens_val/65535)*255)
                        data3[x,y] = (sens_val,100,255-sens_val)
        ###
        img3 = img3.resize((base_width, hsize3), resample=Image.BICUBIC)
        #img = ImageTk.PhotoImage(img)
        return img1,img2,img3, self.width, self.height
###############################################################################
    def update_img_FSR(self):
        img1, wh1, ht1 = self.create_img_FSR()
        qimage1 = ImageQt(img1)
        self.label_fsr.setPixmap(QPixmap.fromImage(qimage1))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
    def update_img_HEAT(self):
        img2, wh2, ht2 = self.create_img_HEAT()
        qimage2 = ImageQt(img2)
        self.label_heat.setPixmap(QPixmap.fromImage(qimage2))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
    def update_img_HUMID(self):
        img3, wh3, ht3 = self.create_img_HUMID()
        qimage3 = ImageQt(img3)
        self.label_humid.setPixmap(QPixmap.fromImage(qimage3))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
        
#################################
    def update_img(self):
        img1,img2,img3, wh, ht = self.create_img()
        qimage1 = ImageQt(img1)
        self.label_fsr.setPixmap(QPixmap.fromImage(qimage1))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
        qimage2 = ImageQt(img2)
        self.label_heat.setPixmap(QPixmap.fromImage(qimage2))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
        qimage3 = ImageQt(img3)
        self.label_humid.setPixmap(QPixmap.fromImage(qimage3))
        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = User_Interface()
    window.show()
    sys.exit(app.exec_())
