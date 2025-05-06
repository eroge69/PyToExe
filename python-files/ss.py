from pynput import mouse, keyboard
import time
import threading

exit_flag = False # Flag to indicate when to exit the loop

def on_click(x, y, button, pressed):
if button == mouse.Button.x1 and pressed:
press_keys()

def on_press(key):
global exit_flag
if key == keyboard.Key.esc:
exit_flag = True

def press_keys():
controller = keyboard.Controller()

# Press Space key
controller.press(keyboard.Key.space)
controller.release(keyboard.Key.space)

# Introduce a delay between pressing Space and Ctrl
time.sleep(0.005) # Adjust this value based on your needs

# Press Ctrl key
controller.press(keyboard.Key.ctrl)

# Schedule the release of Ctrl key after 300 milliseconds
threading.Timer(0.3, controller.release, args=[keyboard.Key.ctrl]).start()

# Create mouse listener in a separate thread
listener = mouse.Listener(on_click=on_click)
listener_thread = threading.Thread(target=listener.start)

# Create keyboard listener in a separate thread
k_listener = keyboard.Listener(on_press=on_press)
k_listener_thread = threading.Thread(target=k_listener.start)

# Start both threads
listener_thread.start()
k_listener_thread.start()

# Keep the program running until the 'esc' key is pressed
while not exit_flag:
time.sleep(0.1) # Adjust this value based on your needs

# Stop the listeners
listener.stop()
k_listener.stop()