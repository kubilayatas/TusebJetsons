




şu kodla mjpg oluşturabilirsin bashta direkt çalışır
gphoto2 --capture-movie --stdout > test_output.mjpg



mjpg sıkıştırılmış jpg framelerini mp4 formatına dönüştürmek için
ffmpeg -i input.mjpg -c:v libx264 -crf 23 -preset fast -pix_fmt yuv420p output.mp4
