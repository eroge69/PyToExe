# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 12:45:44 2025

@author: hasim
"""

import psutil
import time
import winsound

# Alarm sesi ayarları
def play_alarm():
    duration = 1000  # ms
    freq = 1000      # Hz
    for _ in range(3):
        winsound.Beep(freq, duration)
        time.sleep(0.5)
play_alarm()
# Ana döngü
def battery_monitor():
    alarm_low_triggered = False
    alarm_high_triggered = False

    while True:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged

        print(f"Batarya Seviyesi: {percent}%, Şarjda: {plugged}")

        # %10'un altı alarmı
        if percent < 10 and not plugged and not alarm_low_triggered:
            print("⚠️ Düşük batarya seviyesi! Alarm çalıyor.")
            play_alarm()
            alarm_low_triggered = True
            alarm_high_triggered = False

        # %90 üzeri alarmı
        elif percent > 90 and plugged and not alarm_high_triggered:
            print("🔌 Batarya %90'ın üzerinde! Alarm çalıyor.")
            play_alarm()
            alarm_high_triggered = True
            alarm_low_triggered = False

        # Seviyeler normale döndüğünde alarmları sıfırla
        if 10 <= percent <= 90:
            alarm_low_triggered = False
            alarm_high_triggered = False

        time.sleep(60)  # Her 60 saniyede bir kontrol et

if __name__ == "__main__":
    battery_monitor()
