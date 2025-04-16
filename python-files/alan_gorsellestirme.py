import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, TextBox

WIDTH = 120
HEIGHT = 250
GRID_RESOLUTION = 1

usage_grid = np.zeros((HEIGHT, WIDTH), dtype=int)

def get_color_map(grid):
    norm = np.clip(grid / grid.max(), 0, 1) if grid.max() > 0 else grid
    return plt.cm.Blues(norm)

def draw_grid():
    plt.clf()
    plt.imshow(get_color_map(usage_grid), origin='lower')
    used_percent = 100 * np.count_nonzero(usage_grid) / (WIDTH * HEIGHT)
    plt.title(f"Kullanılan Alan: %{used_percent:.2f}")
    plt.axis('off')
    plt.draw()

def submit(event):
    try:
        x_dim = int(textbox_dim_x.text)
        y_dim = int(textbox_dim_y.text)
        x_pos = int(textbox_pos_x.text)
        y_pos = int(textbox_pos_y.text)

        if (x_pos + x_dim > WIDTH) or (y_pos + y_dim > HEIGHT):
            print("⚠️ Hata: Alan dışına çıkıyor.")
            return

        usage_grid[y_pos:y_pos + y_dim, x_pos:x_pos + x_dim] += 1
        draw_grid()
    except ValueError:
        print("⚠️ Geçersiz giriş.")

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)

axbox1 = plt.axes([0.1, 0.25, 0.15, 0.05])
textbox_dim_x = TextBox(axbox1, 'x:')

axbox2 = plt.axes([0.3, 0.25, 0.15, 0.05])
textbox_dim_y = TextBox(axbox2, 'y:')

axbox3 = plt.axes([0.1, 0.15, 0.15, 0.05])
textbox_pos_x = TextBox(axbox3, 'X:')

axbox4 = plt.axes([0.3, 0.15, 0.15, 0.05])
textbox_pos_y = TextBox(axbox4, 'Y:')

submit_ax = plt.axes([0.5, 0.2, 0.15, 0.1])
button = Button(submit_ax, 'İşaretle')
button.on_clicked(submit)

draw_grid()
plt.show()
