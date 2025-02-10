import smbus2 as smbus
import threading
import time
import struct
import platform
import subprocess
import csv
import datetime
import asyncio
import websockets
import cv2
import nest_asyncio
import websocket_config
import numpy as np
import os
import io

nest_asyncio.apply()
BytesWholeBed = []
saveCsvFlag = False

class ReadCellValueThread(threading.Thread):
    def __init__(self, channel=1, data_callback=None, filename="i2c_sensorveri.csv", dirname = "out_datas"):
        super().__init__()
        self.bus = smbus.SMBus(channel)
        self.buffer = [[0 for _ in range(12)] for _ in range(32)]
        self.dataRailBytes = []
        self.data_callback = data_callback
        self.running = True
        self.csv_filename = filename
        self.dirname = dirname
        #self.init_csv_file()

    def init_csv_file(self):
        os.makedirs(self.dirname, exist_ok=True)
        filname = "./"+self.dirname+"/"+self.csv_filename
        with open(filname, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['Timestamp', 'FSR1', 'FSR2', 'FSR3', 'FSR4',
                       'HMD1_raw', 'TMP1_raw', 'HMD2_raw', 'TMP2_raw',
                       'HMD3_raw', 'TMP3_raw', 'HMD4_raw', 'TMP4_raw']
            csv_writer.writerow(headers)

    def run(self):
        global saveCsvFlag
        while self.running:
            for addr in range(1, 32 + 1):
                try:
                    data = self.bus.read_i2c_block_data(addr + 7, 0, 24)
                    time.sleep(0.1)
                    self.buffer[addr - 1] = self.convert_data(data)
                except Exception as e:
                    self.buffer[addr - 1] = [65535 for _ in range(12)]
                if(saveCsvFlag):self.save_to_csv(self.buffer[addr - 1])

            byte_data = b''.join(struct.pack('12H', *cell_data) if cell_data[0] is not None else b'\x00' * 24 for cell_data in self.buffer)
            self.dataRailBytes = byte_data

            if self.data_callback:
                self.data_callback(self.dataRailBytes)

    def convert_data(self, data):
        return [int.from_bytes(data[i:i + 2], byteorder='big') for i in range(0, len(data), 2)]

    def stop(self):
        self.running = False

    def save_to_csv(self, cell_data):
        filname = "./"+self.dirname+"/"+self.csv_filename
        with open(filname, mode='a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            csv_writer.writerow([timestamp] + cell_data)

async def receive_data(websocket):
    global saveCsvFlag
    while True:
        try:
            message = await websocket.recv()
            print("Sunucudan gelen mesaj:", message)
            if message.split('#')[0] == "Update System Time":
                await update_system_time(message.split('#')[1])
                await websocket.send(b'\x01' + bytes("System Date Updated".encode('utf-8')))
                
            elif message == "start_send_sensorData":
                saveCsvFlag = True
                asyncio.ensure_future(send_sensor_data(websocket))
                i2c_thread.init_csv_file()
            elif message == "start_send_camData":
                await send_camera_data(websocket)
            else:print("mesaj bekleniyor")
        except websockets.ConnectionClosed:
            print("Bağlantı kapandı.")
            break

async def send_sensor_data(websocket):
    await websocket.send(b'\x01' + bytes("Sensor Data Started".encode('utf-8')))
    while True:
        normal_data = bytes(i2c_thread.dataRailBytes)
        normal_data = b'\x03' + normal_data  # Başlığı ekleyin
        await websocket.send(normal_data)
        print("Sensor verileri server'a gönderildi")
        await asyncio.sleep(1)  # Sensor verilerini 1 saniyede bir gönderir

async def send_camera_data(websocket):
    await websocket.send(b'\x01' + bytes("Cam Data Started".encode('utf-8')))
    cmd = ["ffmpeg", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    process_gphoto2 = subprocess.Popen(["gphoto2", "--capture-movie", "--stdout"], stdout=subprocess.PIPE)
    process_ffmpeg = subprocess.Popen(cmd, stdin=process_gphoto2.stdout, stdout=subprocess.PIPE, bufsize=10**8)
    width, height = 1024, 576

    while True:
        try:
            raw_frame = process_ffmpeg.stdout.read(width * height * 3)
            if len(raw_frame) != width * height * 3:
                print("Frame boyutu eşleşmedi, video akışı sona erdi.")
                break

            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((height, width, 3))
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = b'\x02' + img_encoded.tobytes()
            await websocket.send(img_bytes)
            filname = "./" + i2c_thread.dirname + "/" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S.png')
            cv2.imwrite(filname, frame)
            #await save_camera_data(img_encoded.tobytes())
            print("Görüntü server'a gönderildi")
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Görüntü gönderilemedi: {e}")
            break

    process_ffmpeg.terminate()
    process_gphoto2.terminate()

async def connect_server():
    uri = f"ws://{websocket_config.ip}:{websocket_config.host}"
    client_id = websocket_config.client_id
    while True:
        try:
            async with websockets.connect(uri, timeout=10) as websocket:
                print(f"Bağlantı kuruldu. Client ID: {client_id}")
                await websocket.send(client_id)
                await receive_data(websocket)
        except (websockets.ConnectionClosedError, ConnectionRefusedError, OSError) as e:
            print("Sunucuya bağlanılamadı, 10 saniye sonra tekrar denenecek...", e)
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")
            break
        finally:
            cv2.destroyAllWindows()

async def update_system_time(new_time):
    os_type = platform.system()
    if os_type == "Windows":
        subprocess.run(["powershell", "-Command", f"Set-Date -Date \"{new_time}\""], shell=True)
    elif os_type == "Linux":
        subprocess.run(["timedatectl", "set-time", new_time])
        #subprocess.run(["sudo", "timedatectl", "set-time", new_time])
    elif os_type == "Darwin":
        subprocess.run(["sudo", "date", new_time])
    else:
        print("Bu işletim sistemi için desteklenmiyor.")
    

def handle_data(data):
    global BytesWholeBed
    BytesWholeBed = data

if __name__ == "__main__":
    timee = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S.csv')
    dirname = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    i2c_thread = ReadCellValueThread(channel=1, data_callback=handle_data, filename=timee, dirname = dirname)
    i2c_thread.start()
    #asyncio.run(send_data())
    asyncio.run(connect_server())

