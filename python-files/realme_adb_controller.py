
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

ADB_PATH = "adb"

def run_adb_command(command):
    try:
        result = subprocess.check_output([ADB_PATH] + command.split(), stderr=subprocess.STDOUT)
        return result.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8", errors="ignore")
    except FileNotFoundError:
        return "ADB غير موجود أو لم يتم إضافته إلى PATH."

def show_output(title, output):
    messagebox.showinfo(title, output if output else "لا توجد بيانات.")

def reboot_device():
    run_adb_command("reboot")
    messagebox.showinfo("إعادة التشغيل", "تم إرسال أمر إعادة التشغيل للهاتف.")

def reboot_recovery():
    run_adb_command("reboot recovery")
    messagebox.showinfo("وضع الريكفري", "تم إرسال أمر إعادة التشغيل إلى الريكفري.")

def reboot_bootloader():
    run_adb_command("reboot bootloader")
    messagebox.showinfo("وضع الفاست بوت", "تم إرسال أمر إعادة التشغيل إلى الفاست بوت.")

def toggle_airplane_mode(on):
    val = "1" if on else "0"
    state = "true" if on else "false"
    run_adb_command(f"shell settings put global airplane_mode_on {val}")
    run_adb_command(f"shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state {state}")
    messagebox.showinfo("وضع الطيران", "تم " + ("تفعيله" if on else "تعطيله"))

def toggle_wifi(on):
    cmd = "shell svc wifi enable" if on else "shell svc wifi disable"
    run_adb_command(cmd)
    messagebox.showinfo("الوايفاي", "تم " + ("تشغيل الوايفاي" if on else "إيقاف الوايفاي"))

def toggle_bluetooth(on):
    cmd = "shell service call bluetooth_manager 6 i32 1" if on else "shell service call bluetooth_manager 8 i32 1"
    run_adb_command(cmd)
    messagebox.showinfo("البلوتوث", "تم " + ("تشغيل البلوتوث" if on else "إيقاف البلوتوث"))

def uninstall_app():
    package = simpledialog.askstring("حذف تطبيق", "ادخل اسم الحزمة (package name) للتطبيق:")
    if package:
        output = run_adb_command(f"shell pm uninstall --user 0 {package}")
        messagebox.showinfo("حذف تطبيق", output)

def disable_app():
    package = simpledialog.askstring("تعطيل تطبيق", "ادخل اسم الحزمة (package name) للتطبيق:")
    if package:
        output = run_adb_command(f"shell pm disable-user --user 0 {package}")
        messagebox.showinfo("تعطيل تطبيق", output)

def enable_app():
    package = simpledialog.askstring("تفعيل تطبيق", "ادخل اسم الحزمة (package name) للتطبيق:")
    if package:
        output = run_adb_command(f"shell pm enable {package}")
        messagebox.showinfo("تفعيل تطبيق", output)

def clear_cache():
    package = simpledialog.askstring("مسح الكاش", "ادخل اسم الحزمة (package name) للتطبيق:")
    if package:
        output = run_adb_command(f"shell pm clear {package}")
        messagebox.showinfo("مسح الكاش", output)

def show_battery():
    output = run_adb_command("shell dumpsys battery")
    show_output("معلومات البطارية", output)

def main():
    root = tk.Tk()
    root.title("أداة تحكم Realme - عبر ADB")
    root.geometry("350x550")

    tk.Label(root, text="أداة تحكم وإدارة الهاتف عبر ADB", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="إعادة تشغيل الجهاز", width=30, command=reboot_device).pack(pady=5)
    tk.Button(root, text="إعادة تشغيل لوضع الريكفري", width=30, command=reboot_recovery).pack(pady=5)
    tk.Button(root, text="إعادة تشغيل لوضع الفاست بوت", width=30, command=reboot_bootloader).pack(pady=5)

    tk.Button(root, text="تفعيل وضع الطيران", width=30, command=lambda: toggle_airplane_mode(True)).pack(pady=5)
    tk.Button(root, text="تعطيل وضع الطيران", width=30, command=lambda: toggle_airplane_mode(False)).pack(pady=5)

    tk.Button(root, text="تشغيل الوايفاي", width=30, command=lambda: toggle_wifi(True)).pack(pady=5)
    tk.Button(root, text="إيقاف الوايفاي", width=30, command=lambda: toggle_wifi(False)).pack(pady=5)

    tk.Button(root, text="تشغيل البلوتوث", width=30, command=lambda: toggle_bluetooth(True)).pack(pady=5)
    tk.Button(root, text="إيقاف البلوتوث", width=30, command=lambda: toggle_bluetooth(False)).pack(pady=5)

    tk.Button(root, text="حذف تطبيق", width=30, command=uninstall_app).pack(pady=5)
    tk.Button(root, text="تعطيل تطبيق", width=30, command=disable_app).pack(pady=5)
    tk.Button(root, text="تفعيل تطبيق", width=30, command=enable_app).pack(pady=5)
    tk.Button(root, text="مسح الكاش لتطبيق", width=30, command=clear_cache).pack(pady=5)

    tk.Button(root, text="عرض معلومات البطارية", width=30, command=show_battery).pack(pady=5)

    tk.Label(root, text="\nملاحظة: يجب تفعيل تصحيح USB على الهاتف\nوأن يكون الهاتف متصلاً بالكمبيوتر عبر USB", fg="red").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
