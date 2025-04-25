
import json
import subprocess
import os
from pathlib import Path

# Optimierte Konfiguration
data = {
    "click_down_button": 4,
    "games": [
        {"name": "Coinclick",     "max_lvl": 6, "position": 1},
        {"name": "Coin-match",    "max_lvl": 7, "position": 2},
        {"name": "Coin-Flip",     "max_lvl": 8, "position": 3},
        {"name": "Dr.Hamster",    "max_lvl": 6, "position": 4},
        {"name": "Surfer",        "max_lvl": 5, "position": 5},
        {"name": "Flappy Rocket", "max_lvl": 6, "position": 6},
        {"name": "Climber",       "max_lvl": 6, "position": 7},
        {"name": "2048 Coins",    "max_lvl": 5, "position": 8},
        {"name": "Cryptonoid",    "max_lvl": 5, "position": 9},
        {"name": "Lambo",         "max_lvl": 5, "position": 10}
    ]
}

# Speicherort definieren
config_path = Path("config.txt")
exe_path = Path("tiset_2_9_4_y.exe")

# config.txt schreiben
with open(config_path, "w") as f:
    json.dump(data, f, indent=2)

# EXE starten
if exe_path.exists():
    subprocess.Popen([str(exe_path)])
else:
    print("Fehler: tiset_2_9_4_y.exe nicht gefunden.")
