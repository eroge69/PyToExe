import tkinter as tk
import soundfile as sf
import sounddevice as sd
import numpy as np

# MU1000 장치 인덱스
DEVICE_INDEX = 4

# 음악 파일 경로
music_files = [
    "C:/Users/iceci/Downloads/안내방송/1.wav",
    "C:/Users/iceci/Downloads/안내방송/2.wav",
    "C:/Users/iceci/Downloads/안내방송/3.wav",
    "C:/Users/iceci/Downloads/안내방송/4.wav",
    "C:/Users/iceci/Downloads/안내방송/5.wav",
    "C:/Users/iceci/Downloads/안내방송/6.wav",
    "C:/Users/iceci/Downloads/안내방송/7.wav",
    "C:/Users/iceci/Downloads/안내방송/8.wav",
    "C:/Users/iceci/Downloads/안내방송/9.wav",
    "C:/Users/iceci/Downloads/안내방송/10.wav",
    "C:/Users/iceci/Downloads/안내방송/11.wav",
    "C:/Users/iceci/Downloads/안내방송/12.wav",
    "C:/Users/iceci/Downloads/안내방송/13.wav",
]

# 버튼 라벨
button_labels = [
    "이용감사",
    "이동자제",
    "화재발생",
    "노약자석",
    "터널진입",
    "카드태그",
    "승차안내",
    "하차벨",
    "기후위기",
    "안전벨트",
    "임산부석",
    "차임업",
    "차임다운",
]

def play_music(index):
    try:
        filename = music_files[index]
        data, fs = sf.read(filename, dtype='float32')
        
        # 모노 → 스테레오 변환
        if data.ndim == 1:
            data = np.stack((data, data), axis=-1)

        sd.play(data, fs, device=DEVICE_INDEX)
    except Exception as e:
        print("재생 오류:", e)

# GUI 생성
root = tk.Tk()
root.title("MU1000 안내 방송 재생기")

for i, label in enumerate(button_labels):
    btn = tk.Button(root, text=label, width=20, command=lambda i=i: play_music(i))
    btn.grid(row=i, column=0, padx=10, pady=4)

root.mainloop()
