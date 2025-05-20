import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading

BAUD_RATE = 115200
ser = None

# Initial parameters
minX, maxX = 20.0, 120.0
minY, maxY = 50.0, 100.0
minJaw, maxJaw = 0, 180

CANVAS_SIZE = 300


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def connect_serial():
    global ser
    selected_port = port_var.get()
    if not selected_port:
        print("No COM port selected.")
        return

    try:
        ser = serial.Serial(selected_port, BAUD_RATE)
        print(f"Connected to {selected_port}")
        connect_button.config(state='disabled')
        port_combo.config(state='disabled')
    except Exception as e:
        print(f"Error connecting: {e}")


def send_serial(x, y, jaw):
    if ser and ser.is_open:
        try:
            message = f"${x:.2f},{y:.2f},{jaw:.0f};\n"
            ser.write(message.encode())
        except Exception as e:
            print(f"Error sending serial data: {e}")


# === GUI SETUP ===
root = tk.Tk()
root.title("Skully Eye Control")
root.geometry("620x480")
root.resizable(False, False)

# Serial Port Selector
frameTop = ttk.Frame(root, padding="10")
frameTop.grid(row=0, column=0, columnspan=3, sticky="ew")

ttk.Label(frameTop, text="Select COM Port:").grid(row=0, column=0)
port_var = tk.StringVar()
port_combo = ttk.Combobox(frameTop, textvariable=port_var, width=10)
port_combo['values'] = list_serial_ports()
port_combo.grid(row=0, column=1)
connect_button = ttk.Button(frameTop, text="Connect", command=lambda: threading.Thread(target=connect_serial, daemon=True).start())
connect_button.grid(row=0, column=2)

# Entry Boxes
frameInputs = ttk.Frame(root, padding="10")
frameInputs.grid(row=1, column=0, columnspan=2, sticky="ew")

# X range
ttk.Label(frameInputs, text="X Min").grid(row=0, column=0)
entryMinX = ttk.Entry(frameInputs, width=6)
entryMinX.insert(0, str(minX))
entryMinX.grid(row=0, column=1)

ttk.Label(frameInputs, text="X Max").grid(row=0, column=2)
entryMaxX = ttk.Entry(frameInputs, width=6)
entryMaxX.insert(0, str(maxX))
entryMaxX.grid(row=0, column=3)

# Y range
ttk.Label(frameInputs, text="Y Min").grid(row=1, column=0)
entryMinY = ttk.Entry(frameInputs, width=6)
entryMinY.insert(0, str(minY))
entryMinY.grid(row=1, column=1)

ttk.Label(frameInputs, text="Y Max").grid(row=1, column=2)
entryMaxY = ttk.Entry(frameInputs, width=6)
entryMaxY.insert(0, str(maxY))
entryMaxY.grid(row=1, column=3)

# Jaw min/max
ttk.Label(frameInputs, text="Jaw Min").grid(row=2, column=0)
entryMinJaw = ttk.Entry(frameInputs, width=6)
entryMinJaw.insert(0, str(minJaw))
entryMinJaw.grid(row=2, column=1)

ttk.Label(frameInputs, text="Jaw Max").grid(row=2, column=2)
entryMaxJaw = ttk.Entry(frameInputs, width=6)
entryMaxJaw.insert(0, str(maxJaw))
entryMaxJaw.grid(row=2, column=3)

# Canvas
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="lightgray")
canvas.grid(row=2, column=0, rowspan=2, padx=10, pady=10)
canvas.create_line(CANVAS_SIZE / 2, 0, CANVAS_SIZE / 2, CANVAS_SIZE, fill="black")
canvas.create_line(0, CANVAS_SIZE / 2, CANVAS_SIZE, CANVAS_SIZE / 2, fill="black")

# Jaw Slider
frameSlider = ttk.Frame(root)
frameSlider.grid(row=2, column=1, sticky="ns")

labelOpen = ttk.Label(frameSlider, text="Open", font=("TkDefaultFont", 10, "bold"))
labelOpen.pack(side='top', pady=(5,0))

jaw_slider = ttk.Scale(frameSlider, from_=100, to=0, orient='vertical')
jaw_slider.set(50)
jaw_slider.pack()

labelClose = ttk.Label(frameSlider, text="Close", font=("TkDefaultFont", 10, "bold"))
labelClose.pack(pady=(0,5))

labelValJaw = ttk.Label(frameSlider, text="Jaw:  50    Scaled:  90", width=20, anchor="center")
labelValJaw.pack(pady=5)

# Output labels for X and Y side by side
labelValX = ttk.Label(root, text="X: 50.00")
labelValX.grid(row=4, column=0, sticky='e')
labelValY = ttk.Label(root, text="Y: 50.00")
labelValY.grid(row=4, column=1, sticky='w')

# Now define update_from_canvas AFTER labelValJaw exists, so no NameError
def update_from_canvas(event):
    try:
        mnx, mxx = float(entryMinX.get()), float(entryMaxX.get())
        mny, mxy = float(entryMinY.get()), float(entryMaxY.get())

        # Clamp coordinates within canvas
        if event:
            x = min(max(0, event.x), CANVAS_SIZE)
            y = min(max(0, event.y), CANVAS_SIZE)

            # Clear previous crosshair and label
            canvas.delete("crosshair")
            canvas.delete("raw_text")

            # Draw red circle (radius 20 for double size)
            radius = 20
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red", tags="crosshair")

            # Map canvas position to input values (raw)
            inputX = mnx + (mxx - mnx) * x / CANVAS_SIZE
            inputY = mny + (mxy - mny) * (CANVAS_SIZE - y) / CANVAS_SIZE  # Invert Y axis

            # Output scaled from 0 to 100
            outputX = 100 * (inputX - mnx) / (mxx - mnx)
            outputY = 100 * (inputY - mny) / (mxy - mny)

            labelValX.config(text=f"X: {outputX:.2f}")
            labelValY.config(text=f"Y: {outputY:.2f}")

            # Prepare raw input values text
            raw_text = f"({inputX:.1f}, {inputY:.1f})"

            # Position the text above the circle initially
            text_x = x
            text_y = y - radius - 10  # 10 pixels above the circle

            # Get approximate width of text (estimate: 7 pixels per char)
            approx_text_width = len(raw_text) * 7

            # Adjust horizontal position if text goes outside canvas
            if text_x - approx_text_width / 2 < 0:
                text_x = approx_text_width / 2
            elif text_x + approx_text_width / 2 > CANVAS_SIZE:
                text_x = CANVAS_SIZE - approx_text_width / 2

            # Adjust vertical position if text goes above the top edge
            if text_y < 0:
                # place below the circle instead
                text_y = y + radius + 15

            canvas.create_text(text_x, text_y, text=raw_text, fill="black", font=("TkDefaultFont", 10), tags="raw_text")

        currentJaw = jaw_slider.get()
        try:
            minJ = float(entryMinJaw.get())
            maxJ = float(entryMaxJaw.get())
        except ValueError:
            minJ, maxJ = 0, 180  # fallback defaults

        scaledJaw = int(minJ + (maxJ - minJ) * currentJaw / 100)

        labelValJaw.config(text=f"Jaw: {int(currentJaw):3d}    Scaled: {scaledJaw:3d}")

        send_serial(outputX if event else 50, outputY if event else 50, scaledJaw)

    except ValueError:
        print("Invalid input in min/max fields")


# Bind events after function is defined
canvas.bind("<B1-Motion>", update_from_canvas)
canvas.bind("<Button-1>", update_from_canvas)
jaw_slider.config(command=lambda v: update_from_canvas(None))

root.mainloop()
