import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, messagebox

def draw_sketch_with_total_height(circle_radius, chord_height, arc_radius):
    """Draws the sketch and calculates the total height."""
    if circle_radius <= 0 or arc_radius <= 0:
        messagebox.showerror("Error", "Radii must be positive values.")
        return
    if chord_height < 0 or chord_height > 2 * circle_radius:
        messagebox.showerror("Error", "Chord height must be within the range of the circle's diameter.")
        return

    # --- Draw the main circle ---
    theta_circle = np.linspace(0, 2 * np.pi, 100)
    x_circle = circle_radius * np.cos(theta_circle)
    y_circle = circle_radius * np.sin(theta_circle)

    # --- Calculate chord endpoints ---
    y_chord_center = chord_height - circle_radius
    if abs(y_chord_center) >= circle_radius:
        messagebox.showerror("Error", "Chord height is outside or at the edge of the circle.")
        return
    x_chord_endpoints = np.array([-np.sqrt(circle_radius**2 - y_chord_center**2),
                                    np.sqrt(circle_radius**2 - y_chord_center**2)])
    y_chord_endpoints = np.array([y_chord_center, y_chord_center])
    x_chord_line = np.linspace(x_chord_endpoints[0], x_chord_endpoints[1], 50)
    y_chord_line = np.full_like(x_chord_line, y_chord_center)

    # --- Calculate the center of the arc (below the chord and circle center) ---
    x_c = 0
    y_c = -(np.sqrt(arc_radius**2 - x_chord_endpoints[0]**2) - y_chord_center)
    arc_center = (x_c, y_c)

    # --- Calculate the angles for the arc ---
    angle1 = np.arctan2(y_chord_endpoints[0] - arc_center[1], x_chord_endpoints[0] - arc_center[0])
    angle2 = np.arctan2(y_chord_endpoints[1] - arc_center[1], x_chord_endpoints[1] - arc_center[0])

    # Ensure consistent angle direction (counter-clockwise for arc above with center below)
    if angle2 < angle1:
        angle1, angle2 = angle2, angle1

    theta_arc = np.linspace(angle1, angle2, 100)
    x_arc = arc_radius * np.cos(theta_arc) + arc_center[0]
    y_arc = arc_radius * np.sin(theta_arc) + arc_center[1]

    # --- Calculate the top of the arc along the vertical center line (x=0) ---
    top_of_arc_y = arc_center[1] + arc_radius

    # --- Calculate the total height from bottom of circle to top of arc ---
    total_height = circle_radius + top_of_arc_y

    # --- Create the plot ---
    plt.figure(figsize=(8, 8))
    plt.plot(x_circle, y_circle, label=f'Circle (R={circle_radius})', color='blue')
    plt.plot(x_chord_line, y_chord_line, label=f'Chord (h={chord_height})', color='red')
    plt.plot(x_arc, y_arc, label=f'Arc (R={arc_radius:.0f})', color='green')

    # Mark the center of the main circle
    plt.plot(0, 0, 'k.', label='Circle Center')
    # Mark the center of the arc
    plt.plot(arc_center[0], arc_center[1], 'm+', label='Arc Center')
    # Mark the top of the arc along the vertical center line
    plt.plot(0, top_of_arc_y, 'go', label='Top of Arc')

    # Add a vertical line along the center
    plt.axvline(0, color='gray', linestyle='--')

    # Add labels and title
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(f"Circle, Chord, Arc (Total Height: {total_height:.2f})")

    # Set aspect ratio to make the circle appear as a circle
    plt.gca().set_aspect('equal', adjustable='box')

    # Add a legend
    plt.legend()
    plt.grid(True)
    plt.show()

    return total_height

def get_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    circle_radius_input = simpledialog.askfloat("Input", "Enter the radius of the circle:")
    if circle_radius_input is None:
        return

    chord_height_input = simpledialog.askfloat("Input", "Enter the height of the chord from the bottom:")
    if chord_height_input is None:
        return

    arc_radius_input = simpledialog.askfloat("Input", "Enter the radius of the arc:")
    if arc_radius_input is None:
        return

    total_height = draw_sketch_with_total_height(circle_radius_input, chord_height_input, arc_radius_input)
    if total_height is not None:
        messagebox.showinfo("Total Height", f"The total height from the bottom of the circle to the top of the arc along the vertical center line is: {total_height:.2f}")

if __name__ == "__main__":
    get_input()
