import smbus2 as smbus
import threading
import time
import struct

import asyncio
import websockets
import cv2
import nest_asyncio
import websocket_config

nest_asyncio.apply()
BytesWholeBed = []
wholeBedDataFlag = False

class ReadCellValueThread(threading.Thread):
    def __init__(self, channel=1, data_callback=None):
        super().__init__()
        self.bus = smbus.SMBus(channel)
        self.buffer = [[0 for _ in range(12)] for _ in range(32)]
        self.dataRailBytes = []
        self.data_callback = data_callback  # Yeni veri olduğunda çağrılacak fonksiyon
        self.running = True  # Döngüyü kontrol etmek için bayrak

    def run(self):
        while self.running:
            for addr in range(1, 32 + 1):
                try:
                    # I2C veri okuma
                    data = self.bus.read_i2c_block_data(addr + 7, 0, 24, force=None)
                    time.sleep(0.1)
                    self.buffer[addr - 1] = self.convert_data(data)
                    print(f"{self.buffer[addr - 1]}\n")
                except Exception as e:
                    print(f"Adres {addr} için veri alınamadı: {e}")
                    self.buffer[addr - 1] = [None for _ in range(12)]
            
            # Veriyi byte formatına dönüştürme
            byte_data = b''.join(struct.pack('12H', *cell_data) if cell_data[0] is not None else b'\x00' * 24 for cell_data in self.buffer)
            self.dataRailBytes = byte_data

            # Yeni veri geldiğinde data_callback'i çağır
            if self.data_callback:
                self.data_callback("dataR")

    def convert_data(self, data):
        # I2C verisini 12 adet 2-byte uzunluğunda değerlere çevir
        return [int.from_bytes(data[i:i + 2], byteorder='big') for i in range(0, len(data), 2)]

    def stop(self):
        self.running = False  # Döngüyü durdur
###############################################################################
async def receive_data(websocket):
    while True:
        try:
            # Sunucudan gelen mesajı al
            message = await websocket.recv()
            print("Sunucudan gelen mesaj:", message)
        except websockets.ConnectionClosed:
            print("Bağlantı kapandı.")
            break

async def send_data():
    uri = "ws://{}:{}".format(websocket_config.ip,websocket_config.host)  # C# server adresi
    client_id = websocket_config.client_id  # Sabit bir client ID
    cap = None

   

    while True:
        try:
            # Sunucuya bağlanmayı dene
            async with websockets.connect(uri, timeout= 10) as websocket:
                print(f"Bağlantı kuruldu. Client ID: {client_id}")

                # İlk olarak sunucuya client_id'yi gönder
                await websocket.send(client_id)

                # Sunucudan gelen mesajları dinlemek için ayrı bir görev başlat
                #asyncio.create_task(receive_data(websocket))
                asyncio.ensure_future(receive_data(websocket))
                
                # Kamera başlat
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("Kamera açılamadı.")
                    return
                global wholeBedDataFlag
                # Veri gönderme döngüsü
                while True:
                    # 24 byte'lık normal veri gönderme
                    #normal_data = struct.pack('24B', *[random.randint(0, 255) for _ in range(24)])
                    while not(wholeBedDataFlag):
                        print("i2c verisi bekleniyor")
                    normal_data = BytesWholeBed
                    normal_data = b'\x01' + normal_data  # 0x01 başlık ekle
                    wholeBedDataFlag = False
                    await websocket.send(normal_data)
                    print("Sensor verileri server'a gönderildi")

                    # Görüntü gönderme
                    ret, frame = cap.read()
                    if not ret:
                        print("Kamera görüntüsü alınamadı.")
                        #break
                    else:
                        _, img_encoded = cv2.imencode('.jpg', frame)
                        img_bytes = img_encoded.tobytes()
                        img_bytes = b'\x02' + img_bytes  # 0x02 başlık ekle
                        await websocket.send(img_bytes)
                        print("Görüntü server'a gönderildi")

                    await asyncio.sleep(0.1)  # 1 saniye bekleyin
        except (websockets.ConnectionClosedError, ConnectionRefusedError, OSError) as e:
            # Bağlantı hatası durumunda 10 saniye bekle ve yeniden bağlanmayı dene
            print("Sunucuya bağlanılamadı, 10 saniye sonra tekrar denenecek...", e)
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")
            break
        finally:
            # Kamera bağlantısını serbest bırak
            if cap is not None and cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()

def handle_data():
    global wholeBedDataFlag
    global BytesWholeBed
    wholeBedDataFlag = False
    BytesWholeBed = i2c_thread.dataRailBytes
    wholeBedDataFlag = True

if __name__ == "__main__":
    i2c_thread = ReadCellValueThread(channel=1, data_callback=handle_data)
    i2c_thread.start()
    asyncio.run(send_data())               
