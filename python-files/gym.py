import customtkinter as ctk
from tkinter import messagebox, filedialog
import time

# Theme setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ----------------------------
# Data class
# ----------------------------
class Exercise:
    def __init__(self, name, duration, muscle_group):
        self.name = name
        self.duration = duration
        self.muscle_group = muscle_group

exercise_list = [
    Exercise("Push-ups", 10, "chest"),
    Exercise("Squats", 15, "legs"),
    Exercise("Pull-ups", 10, "back"),
    Exercise("Lunges", 10, "legs"),
    Exercise("Plank", 5, "core"),
    Exercise("Crunches", 5, "core"),
    Exercise("Deadlifts", 15, "back"),
    Exercise("Bench Press", 10, "chest")
]

# ----------------------------
# Core Algorithm (with logging)
# ----------------------------
def generate_workout_plan(exercises, total_time, priority_order, debug_callback):
    priority_map = {muscle: i for i, muscle in enumerate(priority_order)}
    sorted_exercises = sorted(exercises, key=lambda x: (priority_map.get(x.muscle_group, float('inf')), x.duration))
    
    plan = []
    time_used = 0
    skipped = 0

    for ex in sorted_exercises:
        debug_callback(f"Checking: {ex.name} ({ex.muscle_group}, {ex.duration} min)")
        if time_used + ex.duration <= total_time:
            plan.append(ex)
            time_used += ex.duration
            debug_callback(f"✔ Added: {ex.name} | Total Time: {time_used}/{total_time} min\n")
        else:
            skipped += 1
            debug_callback(f"✘ Skipped: {ex.name} | Would exceed time\n")
    
    debug_callback(f"\nSummary: {len(plan)} exercises added, {skipped} skipped.\nTotal time used: {time_used} min")
    return plan

# Horspool search
def horspool_search(text, pattern):
    m, n = len(pattern), len(text)
    if m > n: return -1
    shift = {c: m for c in set(text)}
    for i in range(m - 1):
        shift[pattern[i]] = m - 1 - i
    i = m - 1
    while i < n:
        k = 0
        while k < m and pattern[m - 1 - k] == text[i - k]:
            k += 1
        if k == m:
            return i - m + 1
        i += shift.get(text[i], m)
    return -1

# ----------------------------
# GUI Functions
# ----------------------------
def log_debug(message):
    debug_text.insert("end", message + "\n")
    debug_text.see("end")

def generate_plan():
    try:
        total_time = int(time_entry.get())
        priorities = priority_entry.get().split(',')
        priorities = [p.strip().lower() for p in priorities]
        result_text.delete("1.0", "end")
        debug_text.delete("1.0", "end")

        start = time.perf_counter()
        plan = generate_workout_plan(exercise_list, total_time, priorities, log_debug)
        end = time.perf_counter()

        elapsed = end - start
        log_debug(f"\n⚡ Algorithm runtime: {elapsed:.6f} seconds\n")

        if not plan:
            result_text.insert("end", "No exercises fit within the available time.")
        else:
            result_text.insert("end", "Workout Plan:\n")
            for ex in plan:
                result_text.insert("end", f"{ex.name} - {ex.duration} min ({ex.muscle_group})\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_exercise():
    query = search_entry.get().lower()
    result_text.delete("1.0", "end")
    found = False
    for ex in exercise_list:
        if horspool_search(ex.name.lower(), query) != -1:
            result_text.insert("end", f"Found: {ex.name} ({ex.muscle_group}, {ex.duration} min)\n")
            found = True
    if not found:
        result_text.insert("end", "No matching exercise found.")

def add_exercise():
    name, duration, muscle = name_entry.get(), duration_entry.get(), muscle_entry.get()
    if not name or not duration or not muscle:
        messagebox.showwarning("Input Error", "All fields must be filled.")
        return
    try:
        duration = int(duration)
        exercise_list.append(Exercise(name, duration, muscle.lower()))
        messagebox.showinfo("Success", f"Added: {name}")
    except ValueError:
        messagebox.showerror("Error", "Duration must be a number.")

def delete_exercise():
    name = name_entry.get().lower()
    global exercise_list
    exercise_list = [ex for ex in exercise_list if ex.name.lower() != name]
    messagebox.showinfo("Deleted", f"Exercise '{name}' removed (if existed).")

def save_plan():
    text = result_text.get("1.0", "end").strip()
    if not text:
        messagebox.showwarning("Empty", "No workout plan to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Saved to {file_path}")

def show_all_exercises():
    result_text.delete("1.0", "end")
    result_text.insert("end", "All Exercises:\n")
    for ex in exercise_list:
        result_text.insert("end", f"{ex.name} - {ex.duration} min ({ex.muscle_group})\n")

# ----------------------------
# GUI Layout
# ----------------------------
root = ctk.CTk()
root.title("🏋️ Gym Workout Scheduler")
root.geometry("580x750")

frame = ctk.CTkFrame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

ctk.CTkLabel(frame, text="Available Time (minutes):").pack()
time_entry = ctk.CTkEntry(frame)
time_entry.pack()

ctk.CTkLabel(frame, text="Muscle Group Priority (comma separated):").pack()
priority_entry = ctk.CTkEntry(frame)
priority_entry.pack()

ctk.CTkButton(frame, text="Generate Workout Plan", command=generate_plan).pack(pady=5)

ctk.CTkLabel(frame, text="Search Exercise:").pack()
search_entry = ctk.CTkEntry(frame)
search_entry.pack()
ctk.CTkButton(frame, text="Search", command=search_exercise).pack(pady=5)

ctk.CTkLabel(frame, text="Add/Delete Exercise:").pack(pady=2)
name_entry = ctk.CTkEntry(frame, placeholder_text="Exercise Name")
name_entry.pack()
duration_entry = ctk.CTkEntry(frame, placeholder_text="Duration (min)")
duration_entry.pack()
muscle_entry = ctk.CTkEntry(frame, placeholder_text="Muscle Group")
muscle_entry.pack()

ctk.CTkButton(frame, text="Add Exercise", command=add_exercise).pack(pady=2)
ctk.CTkButton(frame, text="Delete Exercise", command=delete_exercise).pack(pady=2)

ctk.CTkButton(frame, text="Show All Exercises", command=show_all_exercises).pack(pady=5)
ctk.CTkButton(frame, text="Save Workout Plan", command=save_plan).pack(pady=5)

ctk.CTkLabel(frame, text="📋 Generated Workout Plan:").pack(pady=(10, 0))
result_text = ctk.CTkTextbox(frame, height=150)
result_text.pack(fill="both", expand=True)

ctk.CTkLabel(frame, text="🔍 Algorithm Debug Log:").pack(pady=(10, 0))
debug_text = ctk.CTkTextbox(frame, height=180)
debug_text.pack(fill="both", expand=True)

root.mainloop()
