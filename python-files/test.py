import cv2
import numpy as np
import screeninfo
import sys

# Initialize camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Cannot open webcam")
    sys.exit()

# Set resolution to 1080p (Full HD)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Create a named window
window_name = "Webcam"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Get the primary screen dimensions
try:
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width
    screen_height = screen.height
    cv2.moveWindow(window_name, screen.x, screen.y)
    cv2.resizeWindow(window_name, screen_width, screen_height)
except IndexError:
    print("Warning: Could not detect screen information. Running in a normal window.")

# Initial rotation, zoom, and translation parameters
angle = 0
zoom = 1.0
dx, dy = 0, 0
mouse_x, mouse_y = -1, -1 # Store mouse coordinates for zoom center

# Mouse callback for zoom and focus
def mouse_callback(event, x, y, flags, param):
    global zoom, mouse_x, mouse_y
    mouse_x, mouse_y = x, y # Update mouse coordinates

    if event == cv2.EVENT_MOUSEWHEEL:
        zoom_factor = 0.1
        if flags > 0: # Scroll Up (zoom in)
            zoom += zoom_factor
        else: # Scroll Down (zoom out)
            zoom = max(0.1, zoom - zoom_factor)
    elif event == cv2.EVENT_LBUTTONDOWN:
        # Attempt to trigger autofocus (if supported)
        if cap.set(cv2.CAP_PROP_FOCUS, 0):
            print("Attempted to trigger autofocus.")
        else:
            print("Failed to set focus property.")

# Set the mouse callback
cv2.setMouseCallback(window_name, mouse_callback)

# Function to rotate, zoom, and move the image
def rotate_zoom_translate(frame, angle, zoom, dx, dy, center_x=None, center_y=None):
    (h, w) = frame.shape[:2]
    if center_x is None:
        center_x = w // 2
    if center_y is None:
        center_y = h // 2

    M = cv2.getRotationMatrix2D((center_x, center_y), angle, zoom)
    M[0, 2] += dx - center_x * (zoom - 1)
    M[1, 2] += dy - center_y * (zoom - 1)
    transformed = cv2.warpAffine(frame, M, (w, h))
    return transformed

# Movement speed for arrow keys
move_speed = 20

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Apply rotation, zoom, and translation centered on the mouse
    frame_transformed = rotate_zoom_translate(frame, angle, zoom, dx, dy, mouse_x, mouse_y)
    cv2.imshow(window_name, frame_transformed)

    key = cv2.waitKeyEx(1)

    # print(f"Key pressed: {key}") # For debugging key codes

    if key == ord("q") or key == 27:
        break
    elif key == ord("r"):
        angle = (angle + 90) % 360
    elif key == ord("t"):
        angle = (angle + 180) % 360
    elif key == 65361: # Left arrow key (VK_LEFT)
        dx -= move_speed
    elif key == 65363: # Right arrow key (VK_RIGHT)
        dx += move_speed
    elif key == 65362: # Up arrow key (VK_UP)
        dy -= move_speed
    elif key == 65364: # Down arrow key (VK_DOWN)
        dy += move_speed
    elif cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
