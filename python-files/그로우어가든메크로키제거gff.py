import keyboard
import time

is_running = True

def toggle():
    global is_running
    is_running = not is_running
    if is_running:
        print("다시 시작이 됐습니다")
    else:
        print("중지 됐습니다")

# Insert 키를 누르면 toggle 함수 실행,
keyboard.add_hotkey('insert', toggle)

print("자동 수확이 시작되었어요! Ins 키로 중지/재개 종료는 창을 닫아주세요!")

try:
    while True:
        if is_running:
            keyboard.press_and_release('e')
            time.sleep(0.1)
        else:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n종료됨.")