import tkinter as tk
from tkinter import messagebox
import base64
import hashlib

# --- Account Obfuscation Utilities ---
def encode_account(username, password):
    user_bytes = username.encode('utf-8')
    pass_bytes = password.encode('utf-8')
    user_b64 = base64.b64encode(user_bytes).decode('utf-8')
    pass_hash = hashlib.sha256(pass_bytes).hexdigest()
    return f"{user_b64}:{pass_hash}"

def decode_username(obf):
    user_b64 = obf.split(":", 1)[0]
    return base64.b64decode(user_b64.encode('utf-8')).decode('utf-8')

def verify_login(obf, username, password):
    try:
        user_b64, pass_hash = obf.split(":", 1)
        user = base64.b64decode(user_b64.encode('utf-8')).decode('utf-8')
        pass_hash_input = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return user == username and pass_hash == pass_hash_input
    except Exception:
        return False

# --- Obfuscated accounts list ---
accounts_obf = [
    # These are the obfuscated accounts for Lyric/Lyric123, Maybachelis/maybachelis123, Cursed/Cursed123
    encode_account("Lyric", "Lyric123"),
    encode_account("Maybachelis", "maybachelis123"),
    encode_account("Cursed", "Cursed123")
]

theme = {
    'bg': "#181825",
    'tab_bg': "#232135",
    'frame_bg': "#232135",
    'accent': "#8f44fd",
    'fg': "#ffffff",
    'fg_dim': "#b5b5c9",
    'slider_trough': "#8f44fd",
    'tab_fg_active': "#e0b3ff",
    'tab_fg_inactive': "#b48fd7",
    'button_bg': "#8f44fd",
    'button_fg': "#ffffff"
}

class Overlay:
    def __init__(self):
        self.overlay = None
        self.canvas = None
        self.size = 350

    def show(self, fov=None, crosshair=False, box=False, health=False, name=False):
        size = self.size
        if self.overlay is None:
            self.overlay = tk.Toplevel()
            self.overlay.overrideredirect(True)
            self.overlay.attributes("-topmost", True)
            self.overlay.wm_attributes("-transparentcolor", "white")
            self.overlay.attributes("-alpha", 0.5)
            self.overlay.configure(bg="white")
            self.canvas = tk.Canvas(self.overlay, width=size, height=size, bg="white", highlightthickness=0)
            self.canvas.pack()
        else:
            self.overlay.attributes("-alpha", 0.5)
            self.canvas.config(width=size, height=size)
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        x = screen_width // 2 - size // 2
        y = screen_height // 2 - size // 2
        self.overlay.geometry(f"{size}x{size}+{x}+{y}")
        self.draw(fov, crosshair, box, health, name)
        self.overlay.deiconify()

    def draw(self, fov, crosshair, box, health, name):
        self.canvas.delete("all")
        center = self.size // 2
        if fov:
            d = fov
            thickness = 4
            self.canvas.create_oval(
                center-d//2+thickness//2, center-d//2+thickness//2,
                center+d//2-thickness//2, center+d//2-thickness//2,
                outline="#8f44fd", width=thickness, fill=""
            )
        if crosshair:
            ch_len = 24
            ch_thick = 2
            self.canvas.create_line(center, center-ch_len//2, center, center+ch_len//2, fill="#ffffff", width=ch_thick)
            self.canvas.create_line(center-ch_len//2, center, center+ch_len//2, center, fill="#ffffff", width=ch_thick)
        if box:
            box_size = 120
            bx0 = center - box_size//2
            by0 = center - box_size//2
            bx1 = center + box_size//2
            by1 = center + box_size//2
            self.canvas.create_rectangle(bx0, by0, bx1, by1, outline="#00ff00", width=2)
        if name:
            self.canvas.create_text(center, center-70, text="PlayerName", fill="#ffb347", font=("Consolas", 14, "bold"))
        if health:
            health_perc = 0.7
            bar_w = 80
            bar_h = 10
            bar_x = center - bar_w//2
            bar_y = center + 70
            self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w, bar_y+bar_h, fill="#444", outline="#000")
            self.canvas.create_rectangle(bar_x, bar_y, bar_x+int(bar_w*health_perc), bar_y+bar_h, fill="#27e627", outline="")
            self.canvas.create_text(center, bar_y+bar_h//2, text="HP", fill="#fff", font=("Consolas", 9))

    def hide(self):
        if self.overlay:
            self.overlay.withdraw()

    def destroy(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.canvas = None

overlay = Overlay()
active_labels = []

def check_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    for obf in accounts_obf:
        if verify_login(obf, username, password):
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            root.withdraw()
            open_cheat_menu(username)
            return
    messagebox.showerror("Login Failed", "Incorrect username or password.")

def on_register():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if not username or not password:
        messagebox.showerror("Registration Failed", "Please enter a username and password.")
        return
    for obf in accounts_obf:
        if decode_username(obf) == username:
            messagebox.showerror("Registration Failed", f"Username '{username}' already exists.")
            return
    accounts_obf.append(encode_account(username, password))
    messagebox.showinfo("Registration Success", f"Account '{username}' registered!")
    root.withdraw()
    open_cheat_menu(username)

def open_cheat_menu(username):
    cheat_win = tk.Toplevel()
    cheat_win.title("Among Us - Rust Cheat UI | v2.0")
    cheat_win.geometry("600x400")
    cheat_win.configure(bg=theme['bg'])
    cheat_win.resizable(False, False)
    cheat_win.attributes("-alpha", 0.94)

    def on_closing():
        cheat_win.destroy()
        root.deiconify()
        overlay.destroy()
        for label in active_labels:
            label.destroy()

    cheat_win.protocol("WM_DELETE_WINDOW", on_closing)

    font_title = ("Consolas", 13, "bold")
    font_section = ("Consolas", 11, "bold")
    font_feature = ("Consolas", 10)
    slider_length = 250

    tab_buttons = {}
    tab_frames = {}
    tabs = ["Visual", "Gameplay", "Misc"]

    def show_tab(tab):
        for name, btn in tab_buttons.items():
            btn.config(bg=theme['tab_bg'] if name==tab else theme['bg'],
                       fg=theme['tab_fg_active'] if name==tab else theme['tab_fg_inactive'],
                       relief="flat")
        for name, frame in tab_frames.items():
            if name == tab:
                frame.lift()

    tab_frame = tk.Frame(cheat_win, bg=theme['tab_bg'])
    tab_frame.pack(fill="x")
    for tab in tabs:
        btn = tk.Label(tab_frame, text=tab, font=font_section, fg=theme['tab_fg_active'] if tab=="Visual" else theme['tab_fg_inactive'],
                       bg=theme['tab_bg'] if tab=="Visual" else theme['bg'], padx=24, pady=8, cursor="hand2")
        btn.pack(side="left")
        tab_buttons[tab] = btn

    stack_frame = tk.Frame(cheat_win, bg=theme['bg'])
    stack_frame.pack(fill="both", expand=True)

    # Visual Tab
    visual_frame = tk.Frame(stack_frame, bg=theme['frame_bg'])
    visual_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tab_frames["Visual"] = visual_frame

    tk.Label(visual_frame, text="VISUAL", font=font_title, fg=theme['accent'], bg=theme['frame_bg']).pack(anchor="w", padx=18, pady=(16,2))
    tk.Frame(visual_frame, bg=theme['accent'], height=2).pack(fill="x", padx=16, pady=(0, 12))

    esp_var = tk.BooleanVar(value=True)
    chams_var = tk.BooleanVar(value=False)
    crosshair_visual_var = tk.BooleanVar(value=True)
    box_esp_var = tk.BooleanVar(value=False)
    name_esp_var = tk.BooleanVar(value=True)
    health_bar_var = tk.BooleanVar(value=False)

    def make_checkbox(parent, text, var, command=None):
        return tk.Checkbutton(parent, text=text, variable=var, font=font_feature,
                              fg=theme['fg'], bg=theme['frame_bg'], activebackground=theme['frame_bg'],
                              selectcolor=theme['accent'], activeforeground=theme['fg'],
                              highlightthickness=0, bd=0, pady=2, anchor="w", command=command)

    features_v = [
        ("ESP", esp_var),
        ("Chams", chams_var),
        ("Crosshair", crosshair_visual_var),
        ("Box ESP", box_esp_var),
        ("Name ESP", name_esp_var),
        ("Health Bar", health_bar_var),
    ]
    for text, var in features_v:
        make_checkbox(visual_frame, text, var, command=lambda: update_overlay_and_labels()).pack(anchor="w", padx=28, pady=2)

    # Gameplay Tab
    gameplay_frame = tk.Frame(stack_frame, bg=theme['frame_bg'])
    gameplay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tab_frames["Gameplay"] = gameplay_frame

    tk.Label(gameplay_frame, text="GAMEPLAY", font=font_title, fg=theme['accent'], bg=theme['frame_bg']).pack(anchor="w", padx=18, pady=(16,2))
    tk.Frame(gameplay_frame, bg=theme['accent'], height=2).pack(fill="x", padx=16, pady=(0, 12))

    silent_aim_var = tk.BooleanVar(value=True)
    hitbox_override_var = tk.BooleanVar(value=False)
    no_recoil_var = tk.BooleanVar(value=True)
    rapid_fire_var = tk.BooleanVar(value=False)
    crosshair_gameplay_var = tk.BooleanVar(value=False)

    features_g = [
        ("Silent Aim", silent_aim_var),
        ("Hitbox Override", hitbox_override_var),
        ("No Recoil", no_recoil_var),
        ("Rapid Fire", rapid_fire_var),
        ("Crosshair", crosshair_gameplay_var),
    ]
    for text, var in features_g:
        make_checkbox(gameplay_frame, text, var, command=lambda: update_overlay_and_labels()).pack(anchor="w", padx=28, pady=2)

    silent_aim_fov_var = tk.DoubleVar(value=90.0)
    smooth_var = tk.DoubleVar(value=3.5)
    def make_slider(parent, label, var, frm, to, resolution=0.01, command=None):
        row = tk.Frame(parent, bg=theme['frame_bg'])
        row.pack(fill="x", padx=24, pady=2)
        tk.Label(row, text=label, font=font_feature, fg=theme['fg_dim'], bg=theme['frame_bg']).pack(anchor="w")
        s = tk.Scale(row, from_=frm, to=to, resolution=resolution, orient="horizontal", length=250,
                     variable=var, bg=theme['frame_bg'], fg=theme['fg'], troughcolor=theme['slider_trough'],
                     highlightthickness=0, bd=0, sliderrelief="flat", font=("Consolas", 9), command=command)
        s.pack(anchor="w")
        return s
    make_slider(gameplay_frame, "Silent Aim FOV", silent_aim_fov_var, 10, 180, command=lambda x: update_overlay_and_labels())
    make_slider(gameplay_frame, "Aimbot Smooth", smooth_var, 1, 10)

    # Misc Tab
    misc_frame = tk.Frame(stack_frame, bg=theme['frame_bg'])
    misc_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tab_frames["Misc"] = misc_frame

    tk.Label(misc_frame, text="MISC", font=font_title, fg=theme['accent'], bg=theme['frame_bg']).pack(anchor="w", padx=18, pady=(16,2))
    tk.Frame(misc_frame, bg=theme['accent'], height=2).pack(fill="x", padx=16, pady=(0, 12))

    bunnyhop_var = tk.BooleanVar(value=True)
    speedhack_var = tk.BooleanVar(value=False)
    unlock_skins_var = tk.BooleanVar(value=False)
    fake_lag_var = tk.BooleanVar(value=False)
    auto_vote_var = tk.BooleanVar(value=False)

    features_m = [
        ("Coming Soon", bunnyhop_var),
        ("Speed Hack", speedhack_var),
        ("Skin Changer", unlock_skins_var),
        ("Fake Lag", fake_lag_var),
        ("Coming Soon", auto_vote_var),
    ]
    for text, var in features_m:
        make_checkbox(misc_frame, text, var, command=lambda: update_overlay_and_labels()).pack(anchor="w", padx=28, pady=2)

    buttons_frame = tk.Frame(cheat_win, bg=theme['bg'])
    buttons_frame.pack(side="bottom", pady=8)

    def on_save():
        messagebox.showinfo("Save", "Settings saved!")

    def on_load():
        messagebox.showinfo("Load", "Settings loaded!")

    save_btn = tk.Button(buttons_frame, text="Save", width=12, bg=theme['button_bg'], fg=theme['button_fg'],
                         relief="flat", font=font_feature, command=on_save, activebackground=theme['accent'])
    save_btn.pack(side="left", padx=5)
    load_btn = tk.Button(buttons_frame, text="Load", width=12, bg=theme['button_bg'], fg=theme['button_fg'],
                         relief="flat", font=font_feature, command=on_load, activebackground=theme['accent'])
    load_btn.pack(side="left", padx=5)

    def update_overlay_and_labels(*_):
        fov = None
        if silent_aim_var.get():
            fov_val = silent_aim_fov_var.get()
            min_px = 30
            max_px = 300
            fov = int(min_px + (max_px - min_px) * ((fov_val - 10) / (180 - 10)))
        overlay.show(
            fov=fov,
            crosshair=crosshair_visual_var.get() or crosshair_gameplay_var.get(),
            box=box_esp_var.get(),
            health=health_bar_var.get(),
            name=name_esp_var.get()
        )
        for label in active_labels:
            label.destroy()
        active_labels.clear()
        msg_features = [
            (esp_var, "ESP enabled"),
            (chams_var, "Chams enabled"),
            (hitbox_override_var, "Hitbox Override enabled"),
            (no_recoil_var, "No Recoil enabled"),
            (rapid_fire_var, "Rapid Fire enabled"),
            (bunnyhop_var, "Bunny Hop enabled"),
            (speedhack_var, "Speed Hack enabled"),
            (unlock_skins_var, "Unlock Skins enabled"),
            (fake_lag_var, "Fake Lag enabled"),
            (auto_vote_var, "Auto Vote enabled"),
        ]
        y = 320
        for var, text in msg_features:
            if var.get():
                lbl = tk.Label(cheat_win, text=text, font=("Consolas", 9), fg="#8f44fd", bg=theme['bg'])
                lbl.place(x=325, y=y)
                active_labels.append(lbl)
                y += 18
        if smooth_var.get() > 1:
            lbl = tk.Label(cheat_win, text=f"Aimbot Smooth: {smooth_var.get():.2f}", font=("Consolas", 9), fg="#8f44fd", bg=theme['bg'])
            lbl.place(x=325, y=y)
            active_labels.append(lbl)

    def on_tab_switch(tab):
        show_tab(tab)
        update_overlay_and_labels()
    for tab in tabs:
        tab_buttons[tab].bind("<Button-1>", lambda e, t=tab: on_tab_switch(t))

    silent_aim_var.trace_add("write", update_overlay_and_labels)
    silent_aim_fov_var.trace_add("write", update_overlay_and_labels)
    crosshair_visual_var.trace_add("write", update_overlay_and_labels)
    crosshair_gameplay_var.trace_add("write", update_overlay_and_labels)
    box_esp_var.trace_add("write", update_overlay_and_labels)
    name_esp_var.trace_add("write", update_overlay_and_labels)
    health_bar_var.trace_add("write", update_overlay_and_labels)
    esp_var.trace_add("write", update_overlay_and_labels)
    chams_var.trace_add("write", update_overlay_and_labels)
    hitbox_override_var.trace_add("write", update_overlay_and_labels)
    no_recoil_var.trace_add("write", update_overlay_and_labels)
    rapid_fire_var.trace_add("write", update_overlay_and_labels)
    bunnyhop_var.trace_add("write", update_overlay_and_labels)
    speedhack_var.trace_add("write", update_overlay_and_labels)
    unlock_skins_var.trace_add("write", update_overlay_and_labels)
    fake_lag_var.trace_add("write", update_overlay_and_labels)
    auto_vote_var.trace_add("write", update_overlay_and_labels)
    smooth_var.trace_add("write", update_overlay_and_labels)

    show_tab("Visual")
    update_overlay_and_labels()

def toggle_colors():
    global dark_mode, colors
    dark_mode = not dark_mode
    if dark_mode:
        colors = {
            'bg': "#181825",
            'fg': "#ffffff",
            'entry_bg': "#232135",
            'entry_fg': "#ffffff",
            'button_bg': "#8f44fd",
            'button_fg': "#ffffff"
        }
    else:
        colors = {
            'bg': "#dddddd",
            'fg': "#000000",
            'entry_bg': "#ffffff",
            'entry_fg': "#000000",
            'button_bg': "#cccccc",
            'button_fg': "#000000"
        }
    apply_colors()

def apply_colors():
    root.configure(bg=colors['bg'])
    username_label.config(bg=colors['bg'], fg=colors['fg'])
    password_label.config(bg=colors['bg'], fg=colors['fg'])
    username_entry.config(bg=colors['entry_bg'], fg=colors['entry_fg'], insertbackground=colors['entry_fg'])
    password_entry.config(bg=colors['entry_bg'], fg=colors['entry_fg'], insertbackground=colors['entry_fg'])
    button_frame.config(bg=colors['bg'])
    change_btn.config(bg=colors['button_bg'], fg=colors['button_fg'])
    login_btn.config(bg=colors['button_bg'], fg=colors['button_fg'])
    register_btn.config(bg=colors['button_bg'], fg=colors['button_fg'])

colors = {
    'bg': "#181825",
    'fg': "#ffffff",
    'entry_bg': "#232135",
    'entry_fg': "#ffffff",
    'button_bg': "#8f44fd",
    'button_fg': "#ffffff"
}

dark_mode = True

root = tk.Tk()
root.title("LunarCheats")
root.geometry("320x144")
root.resizable(False, False)
root.configure(bg=colors['bg'])
root.attributes("-alpha", 0.95)

font_label = ("Consolas", 10)
font_entry = ("Consolas", 10)
font_button = ("Consolas", 10)

username_label = tk.Label(root, text="Username:", font=font_label, bg=colors['bg'], fg=colors['fg'])
username_label.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
username_entry = tk.Entry(root, font=font_entry, bg=colors['entry_bg'], fg=colors['entry_fg'],
                          insertbackground=colors['entry_fg'], relief="flat", width=30)
username_entry.grid(row=0, column=1, padx=10, pady=(10, 2))

password_label = tk.Label(root, text="Password:", font=font_label, bg=colors['bg'], fg=colors['fg'])
password_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
password_entry = tk.Entry(root, font=font_entry, bg=colors['entry_bg'], fg=colors['entry_fg'],
                          insertbackground=colors['entry_fg'], show="*", relief="flat", width=30)
password_entry.grid(row=1, column=1, padx=10, pady=2)

button_frame = tk.Frame(root, bg=colors['bg'])
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

change_btn = tk.Button(button_frame, text="Change colors", font=font_button,
                       bg=colors['button_bg'], fg=colors['button_fg'],
                       relief="flat", width=12, command=toggle_colors)
change_btn.pack(side="left", padx=5)

login_btn = tk.Button(button_frame, text="Login", font=font_button,
                      bg=colors['button_bg'], fg=colors['button_fg'],
                      relief="flat", width=8, command=check_login)
login_btn.pack(side="left", padx=5)

register_btn = tk.Button(button_frame, text="Register", font=font_button,
                         bg=colors['button_bg'], fg=colors['button_fg'],
                         relief="flat", width=8, command=on_register)
register_btn.pack(side="left", padx=5)

root.mainloop()