import cv2
import os
from deepface import DeepFace

# === Configurar cámara ===
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# === Variables globales ===
face_match = False
matched_name = "Desconocido"

# === Cargar imágenes de referencia desde la carpeta 'referencias' ===
reference_faces = []
reference_names = []
reference_folder = "referencias"

if os.path.exists(reference_folder):
    for filename in os.listdir(reference_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(reference_folder, filename)
            img = cv2.imread(img_path)
            if img is not None:
                reference_faces.append(img)
                reference_names.append(os.path.splitext(filename)[0])
            else:
                print(f"Error al cargar {filename}")
else:
    print(f"La carpeta '{reference_folder}' no existe.")

# === Cargar el clasificador de rostros de OpenCV ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === Función de verificación ===
def check_face(face_crop, x, y, w, h):
    global face_match, matched_name
    face_match = False
    matched_name = "Desconocido"

    for i, ref_img in enumerate(reference_faces):
        try:
            result = DeepFace.verify(face_crop, ref_img, detector_backend='opencv')
            if result.get("verified", False):
                face_match = True
                matched_name = reference_names[i]
                break
        except Exception as e:
            print(f"Error con {reference_names[i]}: {e}")

    # Devolver la información para el rectángulo
    return (x, y, w, h, matched_name)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Analizar todas las caras detectadas
    for (x, y, w, h) in faces:
        face_crop = frame[y:y + h, x:x + w]

        # Llamar a la función de verificación en cada cara, sin usar hilos (más sencillo)
        (rect_x, rect_y, rect_w, rect_h, name) = check_face(face_crop, x, y, w, h)

        # Dibuja rectángulo y nombre
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (255, 255, 0), 2)

        if face_match:
            cv2.putText(frame, f"MATCH: {name}", (rect_x, rect_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "NO MATCH", (rect_x, rect_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Mostrar la imagen con las caras detectadas
    cv2.imshow("Reconocimiento Facial", frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()