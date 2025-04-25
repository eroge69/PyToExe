import cv2
import mediapipe as mp
import math
import subprocess


camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Не вдалося відкрити камеру")
    exit()

hands = mp.solutions.hands.Hands(max_num_hands=2)
draw = mp.solutions.drawing_utils

isPlay = False

while True:
    success, image = camera.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    imageProc = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(imageProc)
    flag1, flag2, flag3, flag4, flag5 = False, False, False, False, False

    lmList = []
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))
                if len(lmList) >=21:
                    thumb_x1, thumb_y1 = lmList[4][1], lmList[4][2]
                    thumb_x2, thumb_y2 = lmList[1][1], lmList[1][2]
                    thumb_x3, thumb_y3 = lmList[3][1], lmList[3][2]

                    if math.hypot(thumb_x2 - thumb_x1, thumb_y2 - thumb_y1) < math.hypot(thumb_x3 - thumb_x2, thumb_y3 - thumb_y2):
                        flag1 = True


                    index_x1, index_y1 = lmList[8][1], lmList[8][2]
                    index_x2, index_y2 = lmList[5][1], lmList[5][2]
                    index_x3, index_y3 = lmList[7][1], lmList[7][2]
                    if math.hypot(index_x2 - index_x1, index_y2 - index_y1) < math.hypot(index_x3 - index_x2, index_y3 - index_y2):
                        flag2 = True

                    middle_x1, middle_y1 = lmList[12][1], lmList[12][2]
                    middle_x2, middle_y2 = lmList[9][1], lmList[9][2]
                    middle_x3, middle_y3 = lmList[11][1], lmList[11][2]
                    if math.hypot(middle_x2 - middle_x1, middle_y2 - middle_y1) > math.hypot(middle_x3 - middle_x2, middle_y3 - middle_y2):
                        flag3 = True

                    ring_x1, ring_y1 = lmList[16][1], lmList[16][2]
                    ring_x2, ring_y2 = lmList[13][1], lmList[13][2]
                    ring_x3, ring_y3 = lmList[15][1], lmList[15][2]
                    if math.hypot(ring_x2 - ring_x1, ring_y2 - ring_y1) < math.hypot(ring_x3 - ring_x2, ring_y3 - ring_y2):
                        flag4 = True

                    pinky_x1, pinky_y1 = lmList[20][1], lmList[20][2]
                    pinky_x2, pinky_y2 = lmList[17][1], lmList[17][2]
                    pinky_x3, pinky_y3 = lmList[19][1], lmList[19][2]
                    if math.hypot(pinky_x2 - pinky_x1, pinky_y2 - pinky_y1) < math.hypot(pinky_x3 - pinky_x2, pinky_y3 - pinky_y2):
                        flag5 = True

                    if flag5 and flag4 and flag2 and flag3 and not isPlay:
                        print("MIDDLE FINGER UP")
                        subprocess.run("shutdown /s /t 1", shell=True)
                        isPlay = True



            draw.draw_landmarks(image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracking", image)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()