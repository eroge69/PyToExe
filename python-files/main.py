import PySimpleGUI as sg
from math import floor
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

height = 1300
width = 1680

dfont = ("Comic Sans MS", 30)

curr_inp = sg.Input(key="currWC", focus=True, enable_events=True, expand_y=True, font=dfont, size=(5, 0), pad=(0,0))
max_inp = sg.Input(key="maxWC", enable_events=True, expand_y=True, font=dfont, size=(5, 0), pad=(0,0))

cols = []
rows = []
for i in range(10): # i = column
    for j in range(10): # j = row
        rows.append([sg.Button(button_color="white", key=(j * 10) + i, size=(10, 3), pad=(0, 0), disabled=True)])
    cols.append(sg.Column(rows, expand_x=True, pad=(0, 0)))
    rows.clear()

layout = [
    [sg.Column([[curr_inp, sg.Text(" / ", font=dfont, background_color="gray"), max_inp]], background_color="gray")],
    [sg.Column([cols])]
]
    
def color_calc(square):
    if square < 10:
        return "#be2f25"
    elif square < 20:
        return "#d87d1d"
    elif square < 30:
        return "#FFD31F"  #yellow
    elif square < 40:
        return "#d5ff1f"  #lime
    elif square < 50:
        return "#3FFF1F"   #bright green
    elif square < 60:
        return "#22c3cb"
    elif square < 70:
        return "#2287cb"
    elif square < 80:
        return "#2252cb"
    elif square < 90:
        return "#5722cb"
    return "#8c22cb"

window = sg.Window("Essay progress", layout, background_color="gray", size=(width, height))

while True:
    event, values = window.read()
    if event==sg.WIN_CLOSED or event=="Cancel": 
        break
    elif event=="currWC" or event=="maxWC":
        try:
            max_wc = int(values["maxWC"])
            curr_wc = int(values["currWC"])
        except:
            max_wc = 0
            curr_wc = 0
        squares = 0 if max_wc == 0 else min(100, floor((curr_wc*100)/max_wc))
        print(squares)
        for i in range(100):
            if i < squares:
                window[i].update(button_color=color_calc(i))
            else:
                window[i].update(button_color="white")

window.close()