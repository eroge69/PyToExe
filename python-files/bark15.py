import tkinter as tk
import random
import os  # A gép leállításához szükséges modul

# Ablak méretek
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 100

# Bővített színlista
def random_color():
    colors = [
        'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'cyan', 'white', 'gray',
        'brown', 'violet', 'indigo', 'turquoise', 'magenta', 'lime', 'teal', 'mintcream', 
        'salmon', 'gold', 'crimson', 'beige', 'orchid', 'plum', 'navy', 'darkgreen', 'darkblue', 
        'saddlebrown', 'seashell', 'peachpuff', 'chartreuse', 'dodgerblue', 'darkviolet', 'skyblue'
    ]
    return random.choice(colors)

# Felugró ablakok mozgatása
def move_popup(popup, text, canvas, width, height, dx, dy):
    # Jelenlegi koordináták
    x1, y1, x2, y2 = canvas.coords(popup)
    
    # Új koordináták, folyamatos mozgás
    new_x1 = x1 + dx
    new_y1 = y1 + dy
    new_x2 = x2 + dx
    new_y2 = y2 + dy
    
    # Ha elérte a képernyő szélét, irányt váltunk
    if new_x1 < 0 or new_x2 > width:
        dx = -dx  # Irányváltás vízszintesen
    if new_y1 < 0 or new_y2 > height:
        dy = -dy  # Irányváltás függőlegesen

    # Téglalap és szöveg új pozíciója
    canvas.coords(popup, new_x1, new_y1, new_x2, new_y2)
    canvas.coords(text, new_x1 + WINDOW_WIDTH / 2, new_y1 + WINDOW_HEIGHT / 2)  # Szöveg középre igazítása

    # Mozgás újraindítása, animációs sebesség beállítása
    canvas.after(10, move_popup, popup, text, canvas, width, height, dx, dy)  # Gyors animáció

# Ablakok létrehozása kattintásra
def on_click(event, canvas, screen_width, screen_height, popups, texts, click_count):
    # Ha ez az első kattintás, piros ablakot hozunk létre, különben véletlenszerű színt választunk
    if click_count == 0:
        color = 'red'  # Első ablak piros
    else:
        color = random_color()  # Minden más ablak véletlenszerű színű
    
    # Téglalap létrehozása a megfelelő színnel
    popup = canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=color)
    
    # Szöveg hozzáadása a felugró ablakhoz, fekete színnel
    text = canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, text="BARK", font=('Arial', 12, 'bold'), fill="black")
    
    # Ablakok és szövegek tárolása
    popups.append(popup)
    texts.append(text)
    
    # Ellenőrzés, hogy a felugró ablakok száma meghaladja-e a 30-at
    if len(popups) > 30:
        show_shutdown_message()  # Üzenet megjelenítése
        canvas.config(cursor="arrow")  # Kurzor visszaállítása

    # Sebesség beállítása
    dx = random.choice([15, -15])  # Sebesség: vízszintesen 15 pixel mozgás
    dy = random.choice([15, -15])  # Sebesség: függőlegesen 15 pixel mozgás
    
    # Mozgatás
    move_popup(popup, text, canvas, screen_width, screen_height, dx, dy)

# Leállító üzenet megjelenítése
def show_shutdown_message():
    shutdown_window = tk.Toplevel()  # Új ablak
    shutdown_window.title("System Overloaded")  # Ablak cím
    shutdown_window.geometry("300x150")  # Ablak méret
    shutdown_window.configure(bg='blue')  # Kék háttér
    
    # Üzenet szöveg
    message_label = tk.Label(shutdown_window, text="The system is overloaded", font=('Arial', 14, 'bold'), fg='white', bg='blue')
    message_label.pack(pady=20)

    # Gomb a gép leállításához (Shut Down PC)
    shutdown_button = tk.Button(shutdown_window, text="Shut Down PC", font=('Arial', 12), command=shutdown_computer)
    shutdown_button.pack(pady=10)

    # Bezárás és minimizálás letiltása
    shutdown_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Az X gomb blokkolása
    shutdown_window.protocol("WM_ICONIFY", lambda: None)  # A - gomb letiltása

# Gép leállítása
def shutdown_computer():
    os.system("shutdown /s /f /t 1")  # Windows gépen az azonnali leállításhoz (1 másodpercen belül)

# Alkalmazás indítása
def create_fullscreen_popup():
    root = tk.Tk()
    root.attributes("-fullscreen", True)  # Teljes képernyős mód
    root.configure(bg='black')  # Háttérszín beállítása

    # Képernyő méretek
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Alapértelmezett kurzor elrejtése
    root.config(cursor="none")  # Eltüntetjük a kurzort

    canvas = tk.Canvas(root, bg='black', bd=0, highlightthickness=0, relief='ridge')
    canvas.pack(fill="both", expand=True)

    # Kezdeti pop-up
    popups = []
    texts = []
    click_count = [0]  # Lista, hogy változtatható legyen a kattintások száma

    # Az első ablak automatikus megjelenítése
    on_click(None, canvas, screen_width, screen_height, popups, texts, click_count[0])
    click_count[0] += 1  # Az első kattintás számának növelése

    # Kattintás esemény
    def handle_click(event):
        # Az első kattintáskor piros ablak, minden második kattintásnál véletlen szín
        on_click(event, canvas, screen_width, screen_height, popups, texts, click_count[0])
        click_count[0] += 1  # Növeljük a kattintás számot

    canvas.bind("<Button-1>", handle_click)

    root.mainloop()

# Futtatjuk a programot
if __name__ == "__main__":
    create_fullscreen_popup()
