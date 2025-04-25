import re
import time
from datetime import datetime
from datetime import date
import os
import pyautogui as pg
import pyperclip
import pandas as pd
import json

jsonVar = open('extractor_variables.json')
variables = json.load(jsonVar)


#screenWidth, screenHeight = pg.size()
#currentMouseX, currentMouseY = pg.position()
#pg.click(variables["reportBtn"][0], variables["reportBtn"][1])
#time.sleep(4)
#pg.click(variables["statisticsBtn"][0], variables["statisticsBtn"][1])
#time.sleep(4)
#pg.click(variables["statisticsBtn"][0], variables["statisticsBtn"][1])
#time.sleep(2)
#pg.click(variables["randomClickOnText"][0], variables["randomClickOnText"][1])

#pg.hotkey('ctrl', 'a')
#pg.hotkey('ctrl', 'c')

#f = open("test.txt", "w")
#text = pyperclip.paste()
#f.write(text)
#f.close()

data = []
lines = open("test.txt", "r")
for line in lines:
    if line is not None and line != "":
        findName = re.search("] (.*) /", line)
        name = ""
        if findName is not None:
            name = findName.groups()[0]
        if name is not None and name != "":
            findDepartment = re.search(" /(.*)", line)
            department = findDepartment.groups()[0]
            findTime = re.search("(\d+:\d+:\d+)", line)
            time = findTime.groups()[0]
            entExitFind = re.search("(Вход|Виход)", line)
            entExit = entExitFind.groups()[0]
            if entExit == "Вход":
                entExit = "Вхід"
            if entExit == "Виход":
                entExit = "Вихід"

            dateToday = str(date.today())
            dataLine = {"name": name, "department": department, "time": time, "type": entExit, "date": dateToday}
            data.append(dataLine)

diskPath = fr"\\{variables['folderPathIp']}\{variables['folderPathFolderWork']}\{variables['folderPathFolderProhidna']}"
year = datetime.now().year
path = diskPath + fr"\{year}"
if not os.path.exists(path):
    os.makedirs(path)
dataFrame = pd.DataFrame(data)
with open(fr"{path}\{str(date.today())}.xlsx", "wb") as f1:
    dataFrame.to_excel(f1, index=False)
f1.close()

pg.click(variables["ExitBtn"][0], variables["ExitBtn"][0])
