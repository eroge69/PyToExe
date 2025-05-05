import cv2
import mediapipe as mp
from time import sleep

# Asansör parametreleri
current_floor = 1
min_floor = 1
max_floor = 3
movement_delay = 3  # Katlar arası geçiş süresi (saniye)

# MediaPipe el tanıma ayarları
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Kamera ayarları
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Genişlik
cap.set(4, 480)  # Yükseklik

# Hareket tespiti parametreleri
y_threshold = 30  # Piksel cinsinden minimum hareket miktarı
cooldown = 0  # Hareketler arası bekleme süresi

def control_elevator(direction):
    global current_floor, cooldown
    if cooldown > 0:
        return
    
    if direction == "up" and current_floor < max_floor:
        current_floor += 1
        print(f"Yukarı çıkılıyor... Kat {current_floor}")
        cooldown = movement_delay
    elif direction == "down" and current_floor > min_floor:
        current_floor -= 1
        print(f"Aşağı iniliyor... Kat {current_floor}")
        cooldown = movement_delay

prev_y = 0
while cap.isOpened():
    success, img = cap.read()
    if not success:
        continue
    
    img = cv2.flip(img, 1)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_img)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # İşaret parmağı ucu pozisyonu
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, c = img.shape
            current_y = int(index_tip.y * h)
            
            # Yön tespiti
            if abs(current_y - prev_y) > y_threshold:
                if current_y < prev_y:
                    control_elevator("up")
                else:
                    control_elevator("down")
                prev_y = current_y
            
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Cooldown sayacı
    if cooldown > 0:
        cooldown -= 1
    
    # Arayüz bilgileri
    cv2.putText(img, f"Current Floor: {current_floor}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("El Kontrollü Asansör", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()