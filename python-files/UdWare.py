import sys
import time
import platform
import os
import hashlib
from time import sleep
from datetime import datetime
import mss
import cv2
import time
import numpy as np
import serial
import keyboard
import win32api
import win32con
import os
import configparser
import sys
import requests
import datetime
import subprocess
import re
import socket
import wmi
import pyttsx3
import ctypes
from struct import pack
from math import *
from colorama import just_fix_windows_console
from termcolor import colored
import socket
import struct
from mouse_instruct import MouseInstruct, DeviceNotFoundError
from colorama import Fore, Style
from pystyle import Write, System, Colors, Colorate, Anime
red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pink = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.CYAN
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET
config = configparser.ConfigParser()
config1 = configparser.ConfigParser()
just_fix_windows_console()
config.read('settings.ini')
config_section0 = 'ScreenResolution'
config_section1 = 'Settings'
config_section2 = 'HotKey/Rage'
config_section4 = 'Hotkey/Legit'
config_section3 = 'License'
config_section5 = 'Extras'

def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Python Example')
    elif platform.system() == 'Linux':
        os.system('clear')
        sys.stdout.write('\x1b]0;Python Example\x07')
    elif platform.system() == 'Darwin':
        os.system("clear && printf '\\e[3J'")
        os.system('echo - n - e "\x1b]0;Python Example\x07"')

os.system('mode con: cols=56 lines=23')
os.system('title UdWare')
os.system('color 4')
os.system('cls')
print('Connecting...')


def main():
    ascii_art = '''
          __  __    ___       __              
         / / / /___/ / |     / /___ _________ 
        / / / / __  /| | /| / / __ `/ ___/ _ \\
       / /_/ / /_/ / | |/ |/ / /_/ / /  /  __/
       /____/\\__,_/  |__/|__/\\__,_/_/   \\___/ 
     [https://dsc.gg/Xe27V4rrCh   Dev: 28.4.Simjid]
'''

    os.system('mode con: cols=56 lines=23')
    os.system('title UdWare')
    os.system('color 4')
    os.system('cls')
    monitor_width = float(config.get(config_section0, 'MonitorWidth', fallback=''))
    monitor_height = float(config.get(config_section0, 'MonitorHeight', fallback=''))
    profile = config.get(config_section1, 'Config', fallback='')
    modes = config.get(config_section1, 'ToggleMode', fallback='')
    color_choice = config.get(config_section1, 'Color', fallback='')
    perm_del = float(config.get(config_section1, 'Performance_Boost', fallback=''))
    perboost = config.get(config_section1, 'PerformanceBoost', fallback='')
    aim1_toggle = '0x73'
    aimtoggle1 = int(aim1_toggle, 16)
    aim2_toggle = '0x74'
    aimtoggle2 = int(aim2_toggle, 16)
    tb_toggle = '0x75'
    tbtoggle = int(tb_toggle, 16)
    aim_key1 = config.get(config_section4, 'AimAssist1Key', fallback='')
    aim_key2 = config.get(config_section4, 'AimAssist2Key', fallback='')
    trig_key = config.get(config_section4, 'TriggerBotKey', fallback='')
    aimkey1 = int(aim_key1, 16)
    aimkey2 = int(aim_key2, 16)
    trigkey = int(trig_key, 16)
    aimassist1 = False
    aimass1 = False
    aimassist2 = False
    aimass2 = False
    triggerbot = False
    trigb = False
    exit_key = 'F8'
    config1.read(profile)
    config1_section = 'Rage'
    config1_section1 = 'Legit'
    fov = int(config1.get(config1_section1, 'AimAssistFov', fallback=''))
    fovt = int(config1.get(config1_section1, 'TriggerBotFov', fallback=''))
    speed_x = float(config1.get(config1_section1, 'X_Speed', fallback=''))
    smoothness = float(config1.get(config1_section1, 'Smoothness', fallback='0.1'))
    speed_y = float(config1.get(config1_section1, 'Y_Speed', fallback=''))
    speed_x1 = float(config1.get(config1_section1, 'XSpeed', fallback=''))
    speed_y1 = float(config1.get(config1_section1, 'YSpeed', fallback=''))
    tb_delay = float(config1.get(config1_section1, 'TriggerBotDelay', fallback=''))
    offset1 = int(config1.get(config1_section1, 'AimAssist1Offset', fallback=''))
    offset2 = int(config1.get(config1_section1, 'AimAssist2Offset', fallback=''))
    ingame_sens = float(config1.get(config1_section1, 'InGameSens', fallback=''))
    os.system('mode con: cols=56 lines=23')
    os.system('title UdWare')
    os.system('color 4')
    os.system('cls')
    print()
    print('Getting CONFIGS...')
    print('')
    time.sleep(0.5)
    sct = mss.mss()
    screenshot = sct.monitors[1]
    screenshot['left'] = int(monitor_width / 2 - fov / 2)
    screenshot['top'] = int(monitor_height / 2 - fov / 2)
    screenshot['width'] = fov
    screenshot['height'] = fov
    center_x = fov / 2
    center_y = fov / 2
    sct = mss.mss()
    screenshot2 = sct.monitors[1]
    screenshot2['left'] = int(monitor_width / 2 - fovt / 2)
    screenshot2['top'] = int(monitor_height / 2 - fovt / 2)
    screenshot2['width'] = fovt
    screenshot2['height'] = fovt
    console_width = os.get_terminal_size().columns
    os.system('mode con: cols=56 lines=23')
    os.system('title UdWare')
    os.system('color 4')
    os.system('cls')
    print()
    Write.Print(f'''{ascii_art}''', Colors.purple_to_blue, 0)
    print('\n\t----------------------------------------')
    Write.Print('\t[F8] QUIT LOADER\n', Colors.purple_to_blue, interval=0.1)
    print('\t----------------------------------------\n')
    if color_choice == 'P1':
        top = np.array([
            164,
            255,
            255])
        bot = np.array([
            133,
            40,
            84])
    elif color_choice == 'P2':
        top = np.array([
            140,
            110,
            150])
        bot = np.array([
            150,
            195,
            255])
    elif color_choice == 'P3':
        top = np.array([
            140,
            110,
            160])
        bot = np.array([
            140,
            150,
            194])
    elif color_choice == 'Y1':
        top = np.array([
            31,
            255,
            255])
        bot = np.array([
            29,
            150,
            160])
    elif color_choice == 'Y2':
        top = np.array([
            30,
            150,
            200])
        bot = np.array([
            30,
            255,
            255])
    elif color_choice == 'R1':
        top = np.array([
            0,
            80,
            240])
        bot = np.array([
            30,
            255,
            252])
    elif color_choice == 'R2':
        top = np.array([
            30,
            150,
            220])
        bot = np.array([
            190,
            190,
            250])
    else:
        print('Invalid choice.')
    vendor = config.get(config_section1, 'VID', fallback='')
    product = config.get(config_section1, 'PID', fallback='')
    vid = int(vendor, 16)
    pid = int(product, 16)
    import mouse_instruct
    
    def getMouse():
        return MouseInstruct.getMouse(vid, pid)
    try:
        m = getMouse()
    except DeviceNotFoundError:
        print('ERROR: Mouse not found. Please check your VID and PID!')
        sys.exit()    

    
    def ionc_status():
        if modes == 'Toggle':
            print(f'''\t{Fore.MAGENTA}[F4]{Fore.RED}{Fore.CYAN} AIM ASSIST 1''') if aimassist1 else print(f'''\t{Fore.LIGHTBLACK_EX}[F4]{Fore.RED}{Fore.CYAN} AIM ASSIST 1''')
            print(f'''\t{Fore.MAGENTA}[F5]{Fore.RED}{Fore.CYAN} AIM ASSIST 2''') if aimassist2 else print(f'''\t{Fore.LIGHTBLACK_EX}[F5]{Fore.RED}{Fore.CYAN} AIM ASSIST 2''')
            print(f'''\t{Fore.MAGENTA}[F6]{Fore.RED}{Fore.CYAN} TRIGGER BOT''') if triggerbot else print(f'''\t{Fore.LIGHTBLACK_EX}[F6]{Fore.RED}{Fore.CYAN} TRIGGER BOT''')
            print()
            print('\x1b[A\x1b[A\x1b[A\x1b[A', end='')
        elif modes == 'TogglePlusHold':
            print(f'''\t{Fore.MAGENTA}[F4]{Fore.CYAN}{Fore.CYAN} AIM ASSIST 1''') if aimass1 else print(f'''\t{Fore.LIGHTBLACK_EX}[F4]{Fore.MAGENTA}{Fore.CYAN} AIM ASSIST 1''')
            print(f'''\t{Fore.MAGENTA}[F5]{Fore.CYAN}{Fore.CYAN} AIM ASSIST 2''') if aimass2 else print(f'''\t{Fore.LIGHTBLACK_EX}[F5]{Fore.MAGENTA}{Fore.CYAN} AIM ASSIST 2''')
            print(f'''\t{Fore.MAGENTA}[F6]{Fore.CYAN}{Fore.CYAN} TRIGGER BOT''') if trigb else print(f'''\t{Fore.LIGHTBLACK_EX}[F6]{Fore.MAGENTA}{Fore.CYAN} TRIGGER BOT''')
            print()
            print('\x1b[A\x1b[A\x1b[A\x1b[A', end='')
        else:
            print('Invalid choice.')

    ionc_status()


    while True:
        
        if modes == 'Toggle':
            if win32api.GetAsyncKeyState(aimtoggle1) & 0x8000:
                aimassist1 = not aimassist1
                ionc_status()
                time.sleep(0.2)
            if win32api.GetAsyncKeyState(aimtoggle2) & 0x8000:
                aimassist2 = not aimassist2
                ionc_status()
                time.sleep(0.2)
            if win32api.GetAsyncKeyState(tbtoggle) & 0x8000:
                triggerbot = not triggerbot
                ionc_status()
                time.sleep(0.2)
        elif modes == 'TogglePlusHold':
            if win32api.GetAsyncKeyState(aimtoggle1) & 0x8000:
                aimass1 = not aimass1
                ionc_status()
                time.sleep(0.2)
            if win32api.GetAsyncKeyState(aimtoggle2) & 0x8000:
                aimass2 = not aimass2
                ionc_status()
                time.sleep(0.2)
            if win32api.GetAsyncKeyState(tbtoggle) & 0x8000:
                trigb = not trigb
                ionc_status()
                time.sleep(0.2)

        aimassist1 = win32api.GetAsyncKeyState(aimkey1) < 0 and aimass1
        aimassist2 = win32api.GetAsyncKeyState(aimkey2) < 0 and aimass2
        triggerbot = win32api.GetAsyncKeyState(trigkey) < 0 and trigb
    
        if aimassist1:
            img = np.array(sct.grab(screenshot))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, top, bot)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(mask, kernel, iterations=5)
            thresh = cv2.threshold(dilated, 30, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(max_contour)
                aim_x = x + w // 2
                aim_y = y + offset1
                screen_center = (img.shape[1] // 2, img.shape[0] // 2)
                delta_x = aim_x - screen_center[0]
                delta_y = aim_y - screen_center[1]

                
                def bezier_curve(p0, p1, p2, t):
                    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

                move_x = bezier_curve(0, delta_x * 0.5, delta_x, smoothness)
                move_y = bezier_curve(0, delta_y * 0.5, delta_y, smoothness)

                m.move(int(move_x * (speed_x / ingame_sens)), int(move_y * (speed_y / ingame_sens)), 0)

        if aimassist2:
            img = np.array(sct.grab(screenshot))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, top, bot)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(mask, kernel, iterations=5)
            thresh = cv2.threshold(dilated, 30, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(max_contour)
                aim_x = x + w // 2
                aim_y = y + offset2

                diff_x = (aim_x - center_x) * (speed_x1 / ingame_sens)
                diff_y = (aim_y - center_y) * (speed_y1 / ingame_sens)

                m.move(int(diff_x / 4), int(diff_y / 4), 0)

        if triggerbot:
            img = np.array(sct.grab(screenshot2))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, top, bot)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(mask, kernel, iterations=5)
            thresh = cv2.threshold(dilated, 30, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                m.move(0, 0, 1)  
                m.move(0, 0, 0)  
                time.sleep(tb_delay)

        if keyboard.is_pressed(exit_key):
            sys.exit()  


main()