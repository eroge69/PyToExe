import webbrowser
import time

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rickroll-Link

# Vorsicht: 100 Tabs sind viel! Hier zum Beispiel nur 5.
for _ in range(100):
    webbrowser.open_new_tab(url)
    time.sleep(0.5)  # kleine Pause, um den Browser nicht zu überlasten