import subprocess
import cv2
import numpy as np

def capture_image():
    # Fotoğrafı geçici olarak kaydetmek için bir dosya adı oluştur
    subprocess.run(["gphoto2", "--capture-image-and-download", "--filename", "live.jpg"])

    # Kaydedilen görüntüyü oku
    image = cv2.imread("live.jpg")
    
    return image

def live_view():
    while True:
        # Kameradan görüntü al
        frame = capture_image()

        if frame is not None:
            # Görüntüyü göster
            cv2.imshow("Live View", frame)
        
        # 'q' tuşuna basarak çıkış yap
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Tüm pencereleri kapat
    cv2.destroyAllWindows()

if __name__ == "__main__":
    live_view()

