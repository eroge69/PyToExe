import tkinter as tk
from tkinter import ttk, scrolledtext
import sounddevice as sd
import numpy as np
import random
import time
from pynput.mouse import Controller, Button
import threading # For running the bot in a separate thread
import math

# --- Configuration (can be adjusted or later moved to GUI elements) ---
# Audio Settings
SAMPLERATE = 44100
CHANNELS = 1
BLOCK_DURATION_MS = 50
BLOCK_SIZE = int(SAMPLERATE * BLOCK_DURATION_MS / 1000)

# Fishing Logic
DEFAULT_SPLASH_THRESHOLD = 0.05
CLICK_DELAY_BASE_MS = (120, 380)
REACTION_TIME_VARIABILITY_FACTOR = 0.3
OCCASIONAL_EXTREME_DELAY_CHANCE = 0.03
EXTREME_DELAY_MS_RANGE = (1000, 3000)
RECAST_DELAY_BASE_S = (1.8, 3.0)
FUMBLE_RECAST_CHANCE = 0.08
FUMBLE_RECAST_EXTRA_DELAY_S = (0.5, 1.5)
POST_CAST_COOLDOWN_S = (1.8, 2.8)

# Humanization / Anti-AFK
SKIP_SPLASH_CHANCE = (0.07, 0.22)
MOUSE_WIGGLE_INTERVAL_S = (20, 60)
MOUSE_WIGGLE_DELTA_PX = (-8, 8)
MOUSE_LOOK_AROUND_CHANCE = 0.15
MOUSE_LOOK_AROUND_DIST_PX = (30, 100)
MOUSE_MOVE_STEPS = 10

# Session Management
MAX_SESSION_DURATION_S = (1.5 * 60 * 60, 3 * 60 * 60) # Fish for 1.5 to 3 hours

class FishingBotGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("🎣 Minecraft Auto-Fisher")
        self.root.geometry("450x400") # Adjusted size

        self.mouse_controller = Controller()
        self.fishing_thread = None
        self.stop_event = threading.Event()

        # Bot state variables
        self.is_rod_cast = False
        self.last_cast_time = 0
        self.bot_start_time = 0
        self.current_session_duration = 0
        self.last_mouse_action_time = 0
        self.next_mouse_action_interval = 0
        self.splash_threshold = DEFAULT_SPLASH_THRESHOLD # Allow modification later

        self.audio_devices = self._get_audio_devices()
        self.selected_device_id = tk.IntVar(value=-1) # Default to no selection or first valid

        self._setup_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing) # Handle window close

    def _get_audio_devices(self):
        devices = sd.query_devices()
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({"id": i, "name": device['name']})
        return input_devices

    def _setup_widgets(self):
        # Frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Audio Device Selection
        ttk.Label(control_frame, text="Audio Device:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        device_names = [f"{dev['name']} (ID: {dev['id']})" for dev in self.audio_devices]
        if not device_names:
            device_names = ["No input devices found"]
        self.audio_device_dropdown = ttk.Combobox(control_frame, values=device_names, state="readonly", width=40)
        if self.audio_devices:
            self.audio_device_dropdown.current(0) # Select first device by default
            self.selected_device_id.set(self.audio_devices[0]['id']) # Store ID
            self.audio_device_dropdown.bind("<<ComboboxSelected>>", self._on_device_select)
        else:
            self.audio_device_dropdown.config(state=tk.DISABLED)
        self.audio_device_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Splash Threshold
        ttk.Label(control_frame, text="Splash Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.threshold_entry = ttk.Entry(control_frame, width=10)
        self.threshold_entry.insert(0, str(DEFAULT_SPLASH_THRESHOLD))
        self.threshold_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Calibration Help Button
        self.calibrate_button = ttk.Button(control_frame, text="Help Calibrate", command=self._show_calibration_help)
        self.calibrate_button.grid(row=1, column=1, padx=(100,5), pady=5, sticky=tk.W)


        # Start and Stop Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        self.start_button = ttk.Button(button_frame, text="Start Fishing", command=self._start_fishing_clicked)
        self.start_button.pack(side=tk.LEFT, expand=True, padx=5)
        if not self.audio_devices:
            self.start_button.config(state=tk.DISABLED)

        self.stop_button = ttk.Button(button_frame, text="Stop Fishing", command=self._stop_fishing_clicked, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Status Area
        ttk.Label(self.root, text="Status:").pack(pady=(10,0), anchor=tk.W, padx=10)
        self.status_text = scrolledtext.ScrolledText(self.root, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.status_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self._update_status("Ready. Select audio device and click Start.")
        if not self.audio_devices:
            self._update_status("ERROR: No audio input devices detected!\nPlease check:\n1. System audio settings\n2. Microphone permissions\n3. Audio device connections")


    def _on_device_select(self, event):
        selected_index = self.audio_device_dropdown.current()
        if 0 <= selected_index < len(self.audio_devices):
            self.selected_device_id.set(self.audio_devices[selected_index]['id'])
            self._update_status(f"Selected audio device: {self.audio_devices[selected_index]['name']}")


    def _show_calibration_help(self):
        self._update_status("\n--- CALIBRATION HELP ---")
        self._update_status("1. Run the separate calibration script (or use a 'print volume' loop).")
        self._update_status("2. In Minecraft, make fish splash sounds near your bobber.")
        self._update_status("3. Observe the 'Volume Norm' values printed.")
        self._update_status("4. Set 'Splash Threshold' here to slightly LOWER than typical splash values.")
        self._update_status("   (Ensure it's higher than background noise).")
        self._update_status("--- END HELP ---")


    def _update_status(self, message):
        def append_text():
            self.status_text.config(state=tk.NORMAL)
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END) # Scroll to the end
            self.status_text.config(state=tk.DISABLED)
        # Ensure GUI updates are done in the main thread
        self.root.after(0, append_text)


    def _start_fishing_clicked(self):
        try:
            self.splash_threshold = float(self.threshold_entry.get())
            if self.splash_threshold <= 0:
                raise ValueError("Threshold must be positive.")
        except ValueError:
            self._update_status("ERROR: Invalid Splash Threshold. Must be a positive number.")
            return

        device_idx = self.audio_device_dropdown.current()
        if not self.audio_devices or device_idx < 0:
            self._update_status("ERROR: No audio device selected or available.")
            return

        actual_device_id = self.audio_devices[device_idx]['id']

        self._update_status(f"Starting bot with device ID {actual_device_id} and threshold {self.splash_threshold}...")
        self._update_status("Ensure Minecraft is the active window!")

        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.audio_device_dropdown.config(state=tk.DISABLED)
        self.threshold_entry.config(state=tk.DISABLED)
        self.calibrate_button.config(state=tk.DISABLED)

        self.fishing_thread = threading.Thread(target=self._fishing_worker_thread, args=(actual_device_id,))
        self.fishing_thread.daemon = True # Allows main program to exit even if thread is running
        self.fishing_thread.start()


    def _stop_fishing_clicked(self):
        self._update_status("Stopping bot...")
        self.stop_event.set()
        # GUI update will be handled by _reset_gui_on_thread_stop or on_closing

    def _reset_gui_on_thread_stop(self):
        """Called when the fishing thread actually stops."""
        self.start_button.config(state=tk.NORMAL if self.audio_devices else tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.audio_device_dropdown.config(state=tk.NORMAL if self.audio_devices else tk.DISABLED)
        self.threshold_entry.config(state=tk.NORMAL)
        self.calibrate_button.config(state=tk.NORMAL)
        if self.fishing_thread and self.fishing_thread.is_alive():
            self.fishing_thread.join(timeout=1.0) # Give it a moment to exit
        self.fishing_thread = None
        self._update_status("Bot stopped.")


    def _on_closing(self):
        if self.fishing_thread and self.fishing_thread.is_alive():
            self._update_status("Window closed. Attempting to stop fishing thread...")
            self.stop_event.set()
            # Don't join here in a blocking way, or GUI might hang.
            # Daemon thread will exit if main exits, or let it finish.
            # Or, show a "stopping..." message and disable close for a bit.
            # For now, just set event and close.
        self.root.destroy()

    # --- Core Bot Logic (moved into methods of the class) ---
    def _smooth_mouse_move(self, dx, dy, steps=MOUSE_MOVE_STEPS):
        for i in range(1, steps + 1):
            if self.stop_event.is_set(): return
            step_dx = int(dx * (i / steps) - dx * ((i - 1) / steps))
            step_dy = int(dy * (i / steps) - dy * ((i - 1) / steps))
            self.mouse_controller.move(step_dx, step_dy)
            time.sleep(random.uniform(0.005, 0.015))

    def _perform_mouse_action(self):
        if random.random() < MOUSE_LOOK_AROUND_CHANCE:
            self._update_status("[HUMANIZE] Performing a 'look around'.")
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(MOUSE_LOOK_AROUND_DIST_PX[0], MOUSE_LOOK_AROUND_DIST_PX[1])
            dx = int(distance * math.cos(angle))
            dy = int(distance * math.sin(angle))
            self._smooth_mouse_move(dx, dy, steps=random.randint(10, 20))
        else:
            dx = random.randint(*MOUSE_WIGGLE_DELTA_PX)
            dy = random.randint(*MOUSE_WIGGLE_DELTA_PX)
            self._smooth_mouse_move(dx, dy, steps=random.randint(3, 7))
        self.last_mouse_action_time = time.time()
        self.next_mouse_action_interval = random.uniform(*MOUSE_WIGGLE_INTERVAL_S)

    def _cast_rod_from_thread(self):
        recast_base_wait = random.uniform(*RECAST_DELAY_BASE_S)
        self._update_status(f"[ACTION] Base wait {recast_base_wait:.2f}s to recast...")

        # Allow interruption during sleep
        sleep_end_time = time.time() + recast_base_wait
        while time.time() < sleep_end_time:
            if self.stop_event.is_set(): return
            time.sleep(0.05) # Shorter sleeps to check stop_event

        if self.stop_event.is_set(): return

        if random.random() < FUMBLE_RECAST_CHANCE:
            fumble_type = random.choice(["miss", "double_tap", "hesitate"])
            self._update_status(f"[HUMANIZE] Fumbling recast ({fumble_type})...")
            extra_fumble_delay = random.uniform(*FUMBLE_RECAST_EXTRA_DELAY_S)

            if fumble_type == "miss":
                self._update_status(f"[HUMANIZE] ...missed, waiting {extra_fumble_delay:.2f}s.")
                sleep_end_time = time.time() + extra_fumble_delay
                while time.time() < sleep_end_time:
                    if self.stop_event.is_set(): return
                    time.sleep(0.05)
                return # Will try to cast again in main loop if rod not cast

            elif fumble_type == "double_tap":
                self.mouse_controller.click(Button.right)
                time.sleep(random.uniform(0.05, 0.15))
                if self.stop_event.is_set(): return
                self.mouse_controller.click(Button.right)
                self._update_status(f"[HUMANIZE] ...double tapped.")
                time.sleep(random.uniform(0.1, 0.3) + extra_fumble_delay / 2) # simplified wait

            elif fumble_type == "hesitate":
                self._update_status(f"[HUMANIZE] ...hesitating for {extra_fumble_delay:.2f}s.")
                sleep_end_time = time.time() + extra_fumble_delay
                while time.time() < sleep_end_time:
                    if self.stop_event.is_set(): return
                    time.sleep(0.05)
                if self.stop_event.is_set(): return
                self.mouse_controller.click(Button.right)
                self._update_status(f"[ACTION] Casting (after hesitation).")
        else:
            self._update_status("[ACTION] Casting rod...")
            self.mouse_controller.click(Button.right)

        if not self.stop_event.is_set(): # Only set if cast was successful and not interrupted
            self.is_rod_cast = True
            self.last_cast_time = time.time()
            self._update_status(f"[INFO] Rod cast. Cooldown: ~{POST_CAST_COOLDOWN_S[0]:.1f}s.")


    def _audio_callback_for_thread(self, indata, frames, time_info, status):
        if self.stop_event.is_set(): # Check if we should stop processing
            raise sd.CallbackStop # Stop the audio stream

        if status:
            self._update_status(f"[WARNING] Audio stream: {status}")
        if not self.is_rod_cast:
            return

        cooldown = random.uniform(*POST_CAST_COOLDOWN_S)
        if time.time() - self.last_cast_time < cooldown:
            return

        volume_norm = np.linalg.norm(indata)

        if volume_norm > self.splash_threshold:
            self._update_status(f"[SOUND] Potential splash! Vol: {volume_norm:.4f} (Thresh: {self.splash_threshold:.4f})")

            if random.random() < random.uniform(*SKIP_SPLASH_CHANCE):
                self._update_status(f"[HUMANIZE] Decided to miss/skip splash.")
                self.is_rod_cast = False # Needs recast
                return

            delay_ms = random.uniform(*CLICK_DELAY_BASE_MS)
            if random.random() < REACTION_TIME_VARIABILITY_FACTOR:
                variation = delay_ms * random.uniform(-REACTION_TIME_VARIABILITY_FACTOR, REACTION_TIME_VARIABILITY_FACTOR)
                delay_ms += variation
            if random.random() < OCCASIONAL_EXTREME_DELAY_CHANCE:
                extreme_delay = random.uniform(*EXTREME_DELAY_MS_RANGE)
                delay_ms += extreme_delay
            delay_ms = max(50, delay_ms)

            self._update_status(f"[ACTION] Confirmed! Waiting {delay_ms:.0f}ms to reel in...")

            sleep_end_time = time.time() + (delay_ms / 1000.0)
            while time.time() < sleep_end_time:
                if self.stop_event.is_set(): return
                time.sleep(0.01) # Shorter sleeps for responsiveness

            if self.stop_event.is_set(): return # Check again before click

            self.mouse_controller.click(Button.right)
            self._update_status("[ACTION] Reeled in!")
            self.is_rod_cast = False # Needs recast


    def _fishing_worker_thread(self, device_id_to_use):
        self.bot_start_time = time.time()
        self.current_session_duration = random.uniform(*MAX_SESSION_DURATION_S)
        self.last_mouse_action_time = time.time()
        self.next_mouse_action_interval = random.uniform(*MOUSE_WIGGLE_INTERVAL_S)
        self.is_rod_cast = False # Ensure fresh state for bot run

        try:
            self._update_status("Audio stream starting...")
            with sd.InputStream(device=device_id_to_use, samplerate=SAMPLERATE,
                                 blocksize=BLOCK_SIZE, channels=CHANNELS,
                                 callback=self._audio_callback_for_thread, dtype='float32'):
                while not self.stop_event.is_set():
                    if time.time() - self.bot_start_time > self.current_session_duration:
                        self._update_status(f"[SESSION] Max duration ({self.current_session_duration/3600:.2f} hrs) reached.")
                        break 

                    if not self.is_rod_cast:
                        self._cast_rod_from_thread()
                        if self.stop_event.is_set(): break # If cast was interrupted

                    current_time = time.time()
                    if self.is_rod_cast and current_time - self.last_mouse_action_time >= self.next_mouse_action_interval:
                        if not self.stop_event.is_set():
                            self._perform_mouse_action()

                    # Check stop event frequently, sleep for short interval
                    if self.stop_event.wait(0.1): # Wait for 0.1s or until event is set
                        break
        except Exception as e:
            self._update_status(f"ERROR: {str(e)}")
            # Log the full traceback to a file instead of UI
            with open("error.log", "a") as f:
                import traceback
                f.write(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(traceback.format_exc())
        finally:
            self._update_status("Fishing thread has finished processing.")
            # Schedule GUI update to be done from main thread
            self.root.after(0, self._reset_gui_on_thread_stop)


if __name__ == "__main__":
    main_root = tk.Tk()
    app = FishingBotGUI(main_root)
    main_root.mainloop()