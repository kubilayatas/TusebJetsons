import asyncio
import websockets
import struct
import random
import cv2
import nest_asyncio
import websocket_config

# nest_asyncio ile mevcut döngüyü yeniden başlatılabilir hale getir
nest_asyncio.apply()

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
                
                # Veri gönderme döngüsü
                while True:
                    # 24 byte'lık normal veri gönderme
                    normal_data = struct.pack('24B', *[random.randint(0, 255) for _ in range(24)])
                    normal_data = b'\x01' + normal_data  # 0x01 başlık ekle
                    await websocket.send(normal_data)
                    print("Normal veri gönderildi")

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
                        print("Görüntü gönderildi")

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

# asyncio.run() ile sürekli veri gönderimini başlat
asyncio.run(send_data())
