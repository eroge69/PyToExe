import tkinter as tk
from tkinter import filedialog, messagebox
import json

class VaayuVoltLabsApp:
    def __init__(self, master):
        self.master = master
        master.title("VaayuVoltLabs - FPV Drone Tuning App")

        # Variables to store uploaded file paths
        self.cli_dump_path = None
        self.blackbox_log_path = None

        # Input fields
        self.create_label_and_entry("Drone Size (cm):")
        self.drone_size_entry = self.last_entry

        self.create_label_and_entry("Drone Weight (g):")
        self.drone_weight_entry = self.last_entry

        self.create_label_and_entry("Prop Size (inches):")
        self.prop_size_entry = self.last_entry

        self.create_label_and_entry("Motor KV:")
        self.motor_kv_entry = self.last_entry

        self.create_label_and_entry("Motor Size (mm):")
        self.motor_size_entry = self.last_entry

        self.create_label_and_entry("Battery Voltage (V):")
        self.battery_voltage_entry = self.last_entry

        self.create_label_and_entry("Battery Capacity (mAh):")
        self.battery_mah_entry = self.last_entry

        # Upload buttons
        self.upload_cli_button = tk.Button(master, text="Upload CLI Dump (.txt)", command=self.upload_cli)
        self.upload_cli_button.pack(pady=5)

        self.upload_blackbox_button = tk.Button(master, text="Upload Blackbox Log (.bbl)", command=self.upload_blackbox)
        self.upload_blackbox_button.pack(pady=5)

        # Calculate button
        self.calculate_button = tk.Button(master, text="Calculate PID & Filters", command=self.calculate_settings)
        self.calculate_button.pack(pady=10)

        # Output
        self.output_text = tk.Text(master, height=15, width=60)
        self.output_text.pack(pady=10)

    def create_label_and_entry(self, text):
        label = tk.Label(self.master, text=text)
        label.pack()
        entry = tk.Entry(self.master)
        entry.pack()
        self.last_entry = entry

    def upload_cli(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.cli_dump_path = file_path
            messagebox.showinfo("Upload Success", f"✅ CLI Dump uploaded:\n{file_path}")

    def upload_blackbox(self):
        file_path = filedialog.askopenfilename(filetypes=[("Blackbox Log files", "*.bbl")])
        if file_path:
            self.blackbox_log_path = file_path
            messagebox.showinfo("Upload Success", f"✅ Blackbox Log uploaded:\n{file_path}")

    def calculate_settings(self):
        try:
            drone_size = float(self.drone_size_entry.get())
            drone_weight = float(self.drone_weight_entry.get())
            prop_size = float(self.prop_size_entry.get())
            motor_kv = float(self.motor_kv_entry.get())
            motor_size = float(self.motor_size_entry.get())
            battery_voltage = float(self.battery_voltage_entry.get())
            battery_mah = float(self.battery_mah_entry.get())

            if not self.cli_dump_path or not self.blackbox_log_path:
                messagebox.showwarning("Missing Upload", "Please upload both CLI Dump and Blackbox Log files.")
                return

            # --- AI LOGIC ---
            if drone_weight < 250:
                p_gain = 45
                i_gain = 50
                d_gain = 30
            elif drone_weight < 500:
                p_gain = 50
                i_gain = 55
                d_gain = 35
            else:
                p_gain = 55
                i_gain = 60
                d_gain = 40

            if motor_kv > 2500:
                d_gain += 5
                p_gain -= 2
            elif motor_kv < 1600:
                i_gain += 3

            if battery_voltage > 22:
                p_gain += 2
                d_gain += 2

            pid_settings = {
                "Roll": {"P": p_gain, "I": i_gain, "D": d_gain},
                "Pitch": {"P": p_gain, "I": i_gain, "D": d_gain},
                "Yaw": {"P": int(p_gain * 0.6), "I": int(i_gain * 0.7), "D": 0}
            }

            filter_settings = {
                "D-Term Low Pass": "90Hz" if prop_size < 5 else "60Hz",
                "Gyro Low Pass": "150Hz" if motor_kv > 2000 else "100Hz"
            }

            result = f"=== AI PID SETTINGS ===\n{json.dumps(pid_settings, indent=2)}\n\n=== AI FILTER SETTINGS ===\n{json.dumps(filter_settings, indent=2)}"

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, result)
            messagebox.showinfo("Tuning Complete", "✅ PID & Filter settings calculated!")

        except ValueError:
            messagebox.showerror("Input Error", "❗ Please enter valid numeric values.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VaayuVoltLabsApp(root)
    root.mainloop()
