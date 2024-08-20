import subprocess
import cv2
import numpy as np

def stream_camera():
    # gphoto2 ile kameradan video akışı başlat
    cmd = ["gphoto2", "--capture-image-and-download", "--stdout"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)

    # Sürekli olarak stdout'tan veri al ve görüntü olarak işle
    while True:
        # Video akışından bir frame oku
        raw_image = process.stdout.read(1024*576*3)
        if len(raw_image) == 0:
            break

        # Eğer frame boyutunda veri aldıysak, işleyelim
        #frame = np.frombuffer(raw_image, dtype=np.uint8).reshape((1024, 576, 3))

        # Görüntüyü ekrana bastır
        cv2.imshow("Live View", raw_image)

        # 'q' tuşuna basarak çıkış yap
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # İşlem bittiğinde pencereleri kapat
    cv2.destroyAllWindows()
    process.terminate()

if __name__ == "__main__":
    stream_camera()

