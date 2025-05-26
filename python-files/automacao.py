import pandas
import time
import pyautogui
import os
import math
from datetime import date

time.sleep(3)

path = os.getcwd()

for file in os.listdir(path):
    if file.endswith(".xlsx"):
        excel = pandas.read_excel(file)

"""ordem = (excel["Tipo"][0] + " " + excel["Raya"][0])[0:10]"""

leng = len(excel.index)

for index, row in excel.iterrows():
    pyautogui.PAUSE = 0.1
    pyautogui.press("enter")
    time.sleep(0.4)
    pyautogui.write(str(row["Codigo"]))
    try:
         pyautogui.moveTo(fr"{path}\transference_error.png")
    except pyautogui.ImageNotFoundException:
        pass
    time.sleep(0.4)
    pyautogui.press("tab")
    time.sleep(0.4)
    pyautogui.press("right")
    pyautogui.press("right")
    time.sleep(0.4)
    pyautogui.press("enter")

    time.sleep(0.4)

    pyautogui.write(str(row["Requerido"]))
    
    pyautogui.press("enter")
    time.sleep(0.4)

    pyautogui.press("right")
    pyautogui.press("right")

    time.sleep(0.4)
    pyautogui.press("enter")
    pyautogui.write("0")
    pyautogui.write("0")
    pyautogui.write(str(row["OD ERP"]).replace(" ","").strip())
    pyautogui.write("01001")
    pyautogui.press("enter")
    time.sleep(0.4)
    pyautogui.press("right")
    time.sleep(0.4)
    pyautogui.press("enter")
    
    time.sleep(0.4)
    
    pyautogui.write(str(date.today().strftime('%d-%m-%Y')).replace("-","").replace("2025","25")) 

    time.sleep(0.4)

    pyautogui.press("enter")

    time.sleep(0.4)
    
    pyautogui.press("right")

    
    pyautogui.press("enter")

    time.sleep(0.4)
    
    pyautogui.write("0")
    pyautogui.write("3")

    time.sleep(0.4)

    pyautogui.press("enter")

    time.sleep(0.4)

    pyautogui.write("3")

    pyautogui.write("0")

    pyautogui.write("6")

    time.sleep(0.4)

    pyautogui.press("enter")

    time.sleep(0.5)

    with pyautogui.hold('alt'):
            time.sleep(0.4)
            pyautogui.press("down")
    
    time.sleep(0.4)

    pyautogui.press("right")

    time.sleep(0.4)
    pyautogui.press("right")

    time.sleep(1)
