
import PySimpleGUI as sg

def calculate_price(cena_zakupu, zysk_po_prowizji, prowizja=0.092):
    return round((cena_zakupu + zysk_po_prowizji) / (1 - prowizja), 2)

sg.theme('SystemDefault')

layout = [
    [sg.Text('Cena zakupu:'), sg.Input(key='cena')],
    [sg.Text('Zysk po prowizji:'), sg.Input(key='zysk')],
    [sg.Button('Oblicz')],
    [sg.Text('Cena wystawienia:'), sg.Text('', key='wynik', size=(20,1))]
]

window = sg.Window('Kalkulator ceny', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == 'Oblicz':
        try:
            cena = float(values['cena'])
            zysk = float(values['zysk'])
            wynik = calculate_price(cena, zysk)
            window['wynik'].update(f'{wynik} zł')
        except:
            window['wynik'].update('Błąd danych!')

window.close()
