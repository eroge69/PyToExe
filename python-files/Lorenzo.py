import vlc
import time

video_path = "C:\Users\deang\Videos\VirusLorenzosus.mp4"

player = vlc.MediaPlayer(video_path)
player.play()

# Attendi la fine del video (approssimato, o usa durata reale)
time.sleep(60)
