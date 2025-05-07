
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2, decode_predictions, preprocess_input
)
from tensorflow.keras.preprocessing import image
import numpy as np
import tkinter as tk
from tkinter import filedialog, Label, Button
from PIL import Image, ImageTk

# Cargar modelo preentrenado
model = MobileNetV2(weights="imagenet")

# Función de predicción
def es_perro(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    decoded = decode_predictions(preds, top=3)[0]
    for _, label, prob in decoded:
        if "dog" in label.lower():
            return f"✅ Es un perro (confianza: {prob:.2%}, clase: {label})"
    return f"❌ No es un perro (mejor predicción: {decoded[0][1]}, confianza: {decoded[0][2]:.2%})"

# Función para cargar imagen
def cargar_imagen():
    archivo = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Imágenes", "*.jpg *.jpeg *.png")]
    )
    if archivo:
        img = Image.open(archivo)
        img = img.resize((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk
        resultado = es_perro(archivo)
        resultado_label.config(text=resultado)

# Ventana principal
ventana = tk.Tk()
ventana.title("¿Es un perro?")
ventana.geometry("400x450")

btn_cargar = Button(ventana, text="Seleccionar imagen", command=cargar_imagen)
btn_cargar.pack(pady=10)

panel = Label(ventana)
panel.pack()

resultado_label = Label(ventana, text="", font=("Arial", 12), wraplength=350)
resultado_label.pack(pady=10)

ventana.mainloop()
