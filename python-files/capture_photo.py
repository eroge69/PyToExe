import cv2

# Открываем доступ к камере (0 - это индекс камеры, обычно 0 - это фронтальная камера)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Не удалось открыть камеру")
    exit()

# Читаем один кадр из потока
ret, frame = cap.read()

if ret:
    # Сохраняем изображение в файл
    cv2.imwrite('photo.png', frame)
    print("Фото сохранено как photo.png")
else:
    print("Не удалось сделать фото")

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows() 