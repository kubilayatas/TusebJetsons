import subprocess
import cv2
import os

def capture_image():
    try:
        # Fotoğrafı geçici olarak kaydetmek için bir dosya adı oluştur
        result = subprocess.run(["gphoto2", "--capture-image-and-download", "--filename", "live.jpg"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Gphoto2 error:", result.stderr)
            return None

        # Kaydedilen görüntüyü oku
        if os.path.exists("live.jpg"):
            image = cv2.imread("live.jpg")
            return image
        else:
            print("Görüntü dosyası bulunamadı.")
            return None
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None

def live_view():
    while True:
        # Kameradan görüntü al
        frame = capture_image()

        if frame is not None:
            # Görüntüyü göster
            cv2.imshow("Live View", frame)
            print("Görüntü gösteriliyor.")
        else:
            print("Görüntü alınamadı.")

        # 'q' tuşuna basarak çıkış yap
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Tüm pencereleri kapat
    cv2.destroyAllWindows()

if __name__ == "__main__":
    live_view()

