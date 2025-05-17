import tkinter as tk
import os, sys
from PIL import Image, ImageTk
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TokenGeneratorApp(tk.Tk):
    button_pressable = True
    def __init__(self):
        super().__init__()

        # Configuration parameters
        self.INIT_WIDTH   = 900
        self.INIT_HEIGHT  = 900
        self.CHAR_SET     = string.ascii_uppercase + string.digits
        self.TOKEN_LENGTH = 8
        self.BG_PATH  = self.resource_path("resources/images/empire_wall.jpg")
        self.BTN_PATH = self.resource_path("resources/images/button_asset_sized.png")

        self.title("Goodgame Empire Token Generator")
        self.geometry(f"{self.INIT_WIDTH}x{self.INIT_HEIGHT}")
        self.resizable(True, True)

        # --- Canvas + Background ---
        bg = (Image.open(self.BG_PATH)
                 .resize((self.INIT_WIDTH, self.INIT_HEIGHT), Image.LANCZOS))
        self.bg_photo = ImageTk.PhotoImage(bg)
        self.original_bg = Image.open(self.BG_PATH)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 3) Draw an initial background
        self.bg_photo = ImageTk.PhotoImage(
            self.original_bg.resize((self.INIT_WIDTH, self.INIT_HEIGHT), Image.LANCZOS)
        )
        self.bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # 4) Now bind the configure event so we redraw on resize
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # --- Title Banner ---
      
        # --- Instructions Box (centered) ---
        instr_w, instr_h = 450, 220
        cx, cy = self.INIT_WIDTH/2, self.INIT_HEIGHT/2

      

        # text settings
        common_opts = dict(
            font=("Serif", 14),
            fill="#F5EBD7",
            width=instr_w - 20,
            justify="center"
        )

        # 2) Instruction box rectangle
        instr_w, instr_h = 450, 220
        self.instr_box_id = self.canvas.create_rectangle(0, 0, 0, 0,
                                                         fill="#32281E", stipple="gray50",
                                                         outline="#D4AF37", width=2)

        # 3) Instruction texts
        self.instr_heading_id = self.canvas.create_text(0, 0,
            text="Please note:", font=("Serif",16,"bold"), fill="#F5EBD7")
        common_opts = dict(font=("Serif",14), fill="#F5EBD7",
                           width=instr_w-20, justify="center")
        self.instr1_id = self.canvas.create_text(0, 0,
            text=("After you click Generate Token, your browser will launch and "
                "automatically complete the reCAPTCHA challenge to obtain the token. "
                "Once generated, the token is copied directly to your clipboard."),
            **common_opts)
        self.instr2_id = self.canvas.create_text(0, 0,
            text=( "Next, open Discord and paste the token into the token parameter when "
                "starting the bot (e.g. Ctrl+V). We recommend entering all other startup "
                "parameters before generating your token, as it remains valid for only two minutes."),
            **common_opts)

        # 4) Button image
        raw_btn = Image.open(self.BTN_PATH).resize((400,300), Image.LANCZOS)
        cx, cy = self.INIT_WIDTH/2, self.INIT_HEIGHT/2 + 100
        instr_h = 180
        btn_x, btn_y = cx, cy + instr_h/2 + 100

# draw the image on the canvas
      
        self.btn_img = ImageTk.PhotoImage(raw_btn)
        self.btn_id = self.canvas.create_image(btn_x, btn_y, image=self.btn_img)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        # change cursor on hover
        self.canvas.tag_bind(self.btn_id, "<Enter>",  lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(self.btn_id, "<Leave>",  lambda e: self.canvas.config(cursor=""))

# bind click to your generate_token method
        self.canvas.tag_bind(self.btn_id, "<Button-1>", lambda e: self.generate_token())

        # Do one initial layout pass without a fake event
        self.update_idletasks()
        self._on_canvas_resize()  
    def resource_path(self, rel_path):

        
        base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        return os.path.join(base, rel_path)

    def get_token(self, game_url):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)

        driver.get(game_url)
        wait = WebDriverWait(driver, 30, poll_frequency=0.01)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#game')))
        iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#game')
        driver.switch_to.frame(iframe)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.grecaptcha-badge')))

        result = driver.execute_script("""
            return new Promise((resolve) => {
                window.grecaptcha.ready(() => {
                    window.grecaptcha.execute('6Lc7w34oAAAAAFKhfmln41m96VQm4MNqEdpCYm-k', { action: 'submit' }).then(resolve);
                });
            });
        """)
        driver.quit()
        return result
    def _show_popup(self, message, duration=5000):
        # Create a borderless popup
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg="#221E19")             # match your dark parchment
        popup.attributes("-topmost", True)

        # Position it centered over the main window
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 100
        y = self.winfo_rooty() + 50
        popup.geometry(f"250x50+{x}+{y}")

        # Message label
        lbl = tk.Label(popup,
                       text=message,
                       font=("Serif", 12),
                       fg="#F5EBD7",
                       bg="#221E19")
        lbl.pack(expand=True, fill="both", padx=10, pady=10)

        # Destroy after `duration` milliseconds
        popup.after(duration, popup.destroy)

    def generate_token(self):
        if (self.button_pressable == False):
            return
        
        self.button_pressable = False
        token = self.get_token("https://empire.goodgamestudios.com")
        self.clipboard_clear()
        self.clipboard_append(token)
        self.update()
        self.button_pressable = True
        self._show_popup("Token copied to clipboard")
        # copy to clipboard
          # ensure clipboard is updated
        # you could also flash a message or pop-up here

    def _on_canvas_resize(self, event=None):
        # 1) Determine new size
        if event:
            w, h = event.width, event.height
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

        # 2) Redraw background
        resized = self.original_bg.resize((w, h), resample=Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized)
        self.canvas.itemconfig(self.bg_id, image=self.bg_photo)

        # 3) Recompute centers
        cx, cy = w/2, h/2
        instr_w, instr_h = 450, 220

        # 4) Move each item by its stored ID
        self.canvas.coords(self.instr_box_id,
                           cx-instr_w/2, cy-instr_h/2,
                           cx+instr_w/2, cy+instr_h/2)
        self.canvas.coords(self.instr_heading_id, cx, cy-instr_h/2+20)
        self.canvas.coords(self.instr1_id,         cx, cy-30)
        self.canvas.coords(self.instr2_id,         cx, cy+50)
        self.canvas.coords(self.btn_id,  cx, cy+instr_h/2+100)


if __name__ == "__main__":
    # requires Pillow: pip install pillow
    app = TokenGeneratorApp()
    app.mainloop()


