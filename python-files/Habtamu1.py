import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# Developer Information
DEVELOPER = "Habtamu Mesele"
CONTACT_PHONE = "+251985819921"
CONTACT_EMAIL = "habtamumesele@example.com"  # Replace with actual email

def show_developer_info():
    info = f"Developer: {DEVELOPER}\nContact Phone: {CONTACT_PHONE}\nEmail: {CONTACT_EMAIL}"
    messagebox.showinfo("Developer Information", info)

def list_devices():
    try:
        output = os.popen("adb devices").read()
        device_output.delete(1.0, tk.END)
        device_output.insert(tk.END, output)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def factory_reset(device_type):
    try:
        if device_type == "iphone":
            messagebox.showwarning("Not Supported", "Factory reset for iPhone requires iTunes")
        else:
            os.system("adb shell am broadcast -a android.intent.action.MASTER_CLEAR")
            messagebox.showinfo("Success", f"Factory reset command sent to {device_type} device.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def unlock_device(device_type):
    try:
        if device_type == "iphone":
            messagebox.showwarning("Not Supported", "iPhone unlocking requires different tools")
        elif device_type == "huawei":
            os.system("adb shell oem unlock")
        elif device_type in ["samsung", "realme", "nokia", "techno", "itel"]:
            os.system("adb shell pm uninstall --user 0 com.android.locksettings")
        messagebox.showinfo("Success", f"Unlock command sent to {device_type} device.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def flash_firmware(device_type):
    firmware_path = filedialog.askopenfilename(
        title=f"Select Firmware File for {device_type}",
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
    )
    if firmware_path:
        try:
            if device_type == "iphone":
                messagebox.showwarning("Not Supported", "iPhone requires iTunes for firmware restore")
            else:
                os.system(f"adb sideload {firmware_path}")
                messagebox.showinfo("Success", f"Firmware flashing started for {device_type}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def repair_imei(device_type):
    imei = imei_entry.get()
    if imei:
        try:
            if device_type == "iphone":
                messagebox.showwarning("Not Supported", "IMEI repair not supported for iPhone")
            else:
                os.system(f"adb shell service call iphonesubinfo 1 {imei}")
                messagebox.showinfo("Success", f"IMEI repair command sent to {device_type} device.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "Please enter an IMEI number.")

def unlock_frp(device_type):
    try:
        if device_type == "iphone":
            messagebox.showwarning("Not Supported", "FRP unlock not applicable for iPhone")
        elif device_type == "huawei":
            os.system(r"adb shell am start -n com.android.settings/.Settings\$SecuritySettingsActivity")
        elif device_type == "samsung":
            os.system("adb shell am start -a android.settings.SECURITY_SETTINGS")
        else:
            os.system("adb shell am broadcast -a android.intent.action.MASTER_CLEAR")
        messagebox.showinfo("Success", f"FRP unlock attempted for {device_type} device.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_device_specific_buttons(frame, device_type):
    tk.Label(frame, text=f"{device_type.upper()} Tools", font=('Courier', 12, 'bold'), bg='#111111', fg='lime').pack(pady=5)
    
    tk.Button(frame, text="Factory Reset", 
             command=lambda: factory_reset(device_type),
             bg='black', fg='lime', font=('Courier', 10),
             relief=tk.RAISED, borderwidth=2).pack(pady=5, fill=tk.X)
    
    tk.Button(frame, text="Unlock Device", 
             command=lambda: unlock_device(device_type),
             bg='black', fg='lime', font=('Courier', 10),
             relief=tk.RAISED, borderwidth=2).pack(pady=5, fill=tk.X)
    
    tk.Button(frame, text="Flash Firmware", 
             command=lambda: flash_firmware(device_type),
             bg='black', fg='lime', font=('Courier', 10),
             relief=tk.RAISED, borderwidth=2).pack(pady=5, fill=tk.X)
    
    tk.Button(frame, text="Unlock FRP", 
             command=lambda: unlock_frp(device_type),
             bg='black', fg='lime', font=('Courier', 10),
             relief=tk.RAISED, borderwidth=2).pack(pady=5, fill=tk.X)

# Create the main window
root = tk.Tk()
root.title("Universal Mobile Tool")
root.configure(bg='black')

# Create banner frame
banner_frame = tk.Frame(root, bg='black', padx=10, pady=10)
banner_frame.pack(fill=tk.X)

# Title label
title_label = tk.Label(
    banner_frame, 
    text="UNIVERSAL MOBILE TOOL", 
    fg='lime', 
    bg='black', 
    font=('Courier', 18, 'bold')
)
title_label.pack(side=tk.LEFT, expand=True)

# Developer contact info
contact_label = tk.Label(
    banner_frame,
    text=f"Dev: {DEVELOPER}\nPhone: {CONTACT_PHONE}\nEmail: {CONTACT_EMAIL}",
    fg='cyan',
    bg='black',
    font=('Courier', 10),
    justify=tk.RIGHT
)
contact_label.pack(side=tk.RIGHT)

# Main content frame
main_frame = tk.Frame(root, bg='#111111')
main_frame.pack(fill=tk.BOTH, expand=True)

# Device List Button
list_button = tk.Button(
    main_frame, 
    text="List Connected Devices", 
    command=list_devices,
    bg='black',
    fg='lime',
    font=('Courier', 10),
    relief=tk.RAISED,
    borderwidth=3
)
list_button.pack(pady=10)

# Device Output
device_output = scrolledtext.ScrolledText(
    main_frame, 
    width=70, 
    height=10,
    bg='black',
    fg='lime',
    insertbackground='lime',
    font=('Courier', 10),
    relief=tk.SUNKEN,
    borderwidth=3
)
device_output.pack(pady=10)

# Configure Notebook Style
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook', background='black', bordercolor='green')
style.configure('TNotebook.Tab', background='black', foreground='lime',
               padding=[10, 5], font=('Courier', 10, 'bold'))
style.map('TNotebook.Tab', background=[('selected', '#003300')],
         foreground=[('selected', 'white')])

# Create Notebook for device tabs
notebook = ttk.Notebook(main_frame)
notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Create tabs for each device type
devices = ["huawei", "samsung", "realme", "iphone", "nokia", "techno", "itel"]
for device in devices:
    frame = tk.Frame(notebook, bg='#111111')
    notebook.add(frame, text=device.upper())
    create_device_specific_buttons(frame, device)

    # IMEI Repair Section (only for Android devices)
    if device != "iphone":
        tk.Label(
            frame, 
            text="IMEI Repair:", 
            bg='#111111', 
            fg='lime',
            font=('Courier', 10)
        ).pack(pady=5)
        
        imei_entry = tk.Entry(
            frame, 
            bg='black', 
            fg='lime',
            insertbackground='lime',
            font=('Courier', 10),
            relief=tk.SUNKEN
        )
        imei_entry.pack(pady=5)
        
        tk.Button(
            frame, 
            text="Repair IMEI", 
            command=lambda d=device: repair_imei(d),
            bg='black',
            fg='lime',
            font=('Courier', 10),
            relief=tk.RAISED,
            borderwidth=2
        ).pack(pady=5)

# Run the application
root.mainloop()
