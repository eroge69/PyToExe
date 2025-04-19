import os
import random
import time
import re
from tkinter import *
from tkinter import messagebox, scrolledtext
from datetime import datetime

# Configuration
EXERCISES = [
    "Write a function that calculates the factorial of a number.",
    "Write a function that checks if a string is a palindrome.",
    "Write a function that returns the Fibonacci sequence up to n terms.",
    "Write a function that sorts a list of numbers in ascending order without using built-in sort functions.",
    "Write a function that counts the occurrences of each word in a string.",
    "Write a function that converts a decimal number to binary.",
    "Write a function that finds the maximum number in a list.",
    "Write a function that reverses a string without using built-in reverse functions.",
    "Write a function that checks if a number is prime.",
    "Write a function that calculates the sum of all even numbers in a list.",
]

TIMER_DURATION = 900  # 15 minutes in seconds
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
SUBMISSION_LOG = os.path.join(DESKTOP_PATH, "submission_log.txt")

# Syntax highlighting for text zone
PYTHON_KEYWORDS = [
    'False', 'True', 'and', 'break', 'continue', 'def', 'elif', 'in','else', 'for', 'if', 'import', 'lambda', 'not', 'or', 'return', 'while']

PYTHON_BUILTINS = [
    'bool', 'float', 'input', 'int', 'len','max', 'min', 'print', 'range','round', 'slice', 'str', 'tuple', 'type']

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.configure_tags()
        
    def configure_tags(self):
        # Tag colors
        self.text_widget.tag_config('keyword', foreground='blue')
        self.text_widget.tag_config('builtin', foreground='purple')
        self.text_widget.tag_config('string', foreground='green')
        self.text_widget.tag_config('comment', foreground='gray')
        self.text_widget.tag_config('number', foreground='orange')
        
    def highlight(self):
        # Remove all previous tags
        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, '1.0', 'end')
            
        # Get the text content
        text = self.text_widget.get('1.0', 'end-1c')
        
        # Highlight keywords
        for word in PYTHON_KEYWORDS:
            self.highlight_pattern(r'\b%s\b' % word, 'keyword')
            
        # Highlight builtins
        for word in PYTHON_BUILTINS:
            self.highlight_pattern(r'\b%s\b' % word, 'builtin')
            
        # Highlight strings
        self.highlight_pattern(r'"[^"]*"', 'string')
        self.highlight_pattern(r"'[^']*'", 'string')
        self.highlight_pattern(r'""".*?"""', 'string', flags=re.DOTALL)
        self.highlight_pattern(r"'''.*?'''", 'string', flags=re.DOTALL)
        
        # Highlight comments
        self.highlight_pattern(r'#.*$', 'comment', flags=re.MULTILINE)
        
        # Highlight numbers
        self.highlight_pattern(r'\b[0-9]+\b', 'number')
        self.highlight_pattern(r'\b[0-9]+\.[0-9]+\b', 'number')
        
    def highlight_pattern(self, pattern, tag, flags=0):
        text = self.text_widget.get('1.0', 'end-1c')
        matches = re.finditer(pattern, text, flags)
        
        for match in matches:
            start = match.start()
            end = match.end()
            
            # Convert character offset to Tkinter line.column format
            start_index = self.text_widget.index(f'1.0 + {start}c')
            end_index = self.text_widget.index(f'1.0 + {end}c')
            
            self.text_widget.tag_add(tag, start_index, end_index)

class StudentAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Coding Assessment")
        self.root.geometry("900x700")  
        
        # Fonts
        self.large_font = ('Arial', 14)
        self.medium_font = ('Arial', 12)
        self.small_font = ('Arial', 10)
        
        # Student details
        self.first_name = StringVar()
        self.last_name = StringVar()
        self.subscription_number = StringVar()
        self.group = StringVar()
        
        # Timer 
        self.time_left = TIMER_DURATION
        self.timer_running = False
        self.timer_id = None
        self.solution_submitted = False
        
        # Initial form
        self.create_student_form()

    def create_student_form(self):
        """Create the form for student details"""
        self.clear_window()
        
        # Main frame with padding
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text="Student Details", font=self.large_font).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Form fields 
        Label(main_frame, text="First Name:", font=self.medium_font).grid(row=1, column=0, padx=10, pady=10, sticky=E)
        Entry(main_frame, textvariable=self.first_name, font=self.medium_font).grid(row=1, column=1, padx=10, pady=10, sticky=W)
        
        Label(main_frame, text="Last Name:", font=self.medium_font).grid(row=2, column=0, padx=10, pady=10, sticky=E)
        Entry(main_frame, textvariable=self.last_name, font=self.medium_font).grid(row=2, column=1, padx=10, pady=10, sticky=W)
        
        Label(main_frame, text="Subscription Number:", font=self.medium_font).grid(row=3, column=0, padx=10, pady=10, sticky=E)
        Entry(main_frame, textvariable=self.subscription_number, font=self.medium_font).grid(row=3, column=1, padx=10, pady=10, sticky=W)
        
        Label(main_frame, text="Group:", font=self.medium_font).grid(row=4, column=0, padx=10, pady=10, sticky=E)
        Entry(main_frame, textvariable=self.group, font=self.medium_font).grid(row=4, column=1, padx=10, pady=10, sticky=W)
        
        Button(main_frame, text="Start Assessment", command=self.validate_student_details, 
              font=self.medium_font, bg='#4CAF50', fg='white').grid(row=5, column=0, columnspan=2, pady=20)

    def validate_student_details(self):
        """Validate the student details before proceeding"""
        if not all([self.first_name.get(), self.last_name.get(), 
                   self.subscription_number.get(), self.group.get()]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Check if student has already submitted
        if self.has_student_submitted():
            messagebox.showerror("Assessment Completed", 
                               "You have already completed this assessment.")
            return
        
        self.create_assessment_interface()

    def has_student_submitted(self):
        """Check if student has already submitted a solution"""
        if not os.path.exists(SUBMISSION_LOG):
            return False
            
        student_id = f"{self.first_name.get().strip()} {self.last_name.get().strip()}"
        group = self.group.get().strip()
        
        try:
            with open(SUBMISSION_LOG, 'r') as f:
                for line in f:
                    if student_id in line and group in line:
                        return True
        except:
            pass
            
        return False

    def create_assessment_interface(self):
        """Create the assessment interface with exercise and code editor"""
        self.clear_window()
        
        # Main frame with padding
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Student info display
        student_info = f"Student: {self.first_name.get()} {self.last_name.get()} | Group: {self.group.get()}"
        Label(main_frame, text=student_info, font=self.medium_font).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Exercise display (automatically generated)
        self.current_exercise = random.choice(EXERCISES)
        Label(main_frame, text="Your Exercise:", font=self.medium_font).grid(row=1, column=0, sticky=NW, pady=5)
        
        exercise_frame = Frame(main_frame, borderwidth=1, relief="solid", padx=10, pady=10)
        exercise_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.exercise_label = Label(exercise_frame, text=self.current_exercise, 
                                  font=self.small_font, wraplength=800, justify=LEFT)
        self.exercise_label.pack(anchor="w")
        
        # Solution editor with syntax highlighting
        Label(main_frame, text="Your Solution:", font=self.medium_font).grid(row=3, column=0, sticky=NW, pady=5)
        
        self.code_editor = scrolledtext.ScrolledText(main_frame, width=80, height=20, 
                                                   font=('Courier New', 12),
                                                   wrap=WORD, bg='#f5f5f5')
        self.code_editor.grid(row=4, column=0, columnspan=2, sticky="nsew")
        
        # Create syntax highlighter
        self.highlighter = SyntaxHighlighter(self.code_editor)
        
        # Bind key release to syntax highlighting
        self.code_editor.bind('<KeyRelease>', lambda event: self.highlight_code())
        
        # Timer and submit button
        bottom_frame = Frame(main_frame)
        bottom_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.timer_label = Label(bottom_frame, text="Time left: 15:00", 
                               font=('Arial', 14, 'bold'), fg="red")
        self.timer_label.pack(side=LEFT, padx=10)
        
        self.submit_button = Button(bottom_frame, text="Submit Solution", 
                                  command=self.submit_solution,
                                  font=self.medium_font, bg='#4CAF50', fg='white')
        self.submit_button.pack(side=RIGHT, padx=10)
        
        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Start the timer
        self.start_timer()
        
        # Initial highlighting
        self.highlight_code()

    def highlight_code(self):
        """Trigger syntax highlighting"""
        self.highlighter.highlight()

    def start_timer(self):
        """Start the countdown timer"""
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        """Update the timer display and handle timeout"""
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Time left: {minutes:02d}:{seconds:02d}")
        
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.timer_running = False
            messagebox.showinfo("Time's up!", "Your time has expired. Your solution has been submitted automatically.")
            self.submit_solution()

    def submit_solution(self):
        """Submit the student's solution"""
        if self.solution_submitted:
            return
            
        if self.timer_running:
            self.root.after_cancel(self.timer_id)
            self.timer_running = False
        
        # Get student details
        first_name = self.first_name.get().strip()
        last_name = self.last_name.get().strip()
        group = self.group.get().strip()
        solution = self.code_editor.get("1.0", END).strip()
        
        # Create group folder if it doesn't exist
        group_folder = os.path.join(DESKTOP_PATH, group)
        os.makedirs(group_folder, exist_ok=True)
        
        # Create solution file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{first_name}_{last_name}_{timestamp}.py"
        filepath = os.path.join(group_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# Exercise: {self.current_exercise}\n")
            f.write(f"# Student: {first_name} {last_name}\n")
            f.write(f"# Group: {group}\n")
            f.write(f"# Submission Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(solution)
        
        # Log the submission
        self.log_submission(first_name, last_name, group, filepath)
        
        messagebox.showinfo("Submission Successful", 
                          f"Your solution has been saved to:\n{filepath}\n\nYou cannot submit again.")
        
        # Disable further editing
        self.solution_submitted = True
        self.code_editor.config(state=DISABLED)
        self.submit_button.config(state=DISABLED, bg='grey')

    def log_submission(self, first_name, last_name, group, filepath):
        """Log the submission to prevent resubmission"""
        with open(SUBMISSION_LOG, 'a') as f:
            f.write(f"{first_name} {last_name} | {group} | {filepath} | {datetime.now()}\n")

    def reset_application(self):
        """Reset the application to its initial state"""
        self.first_name.set("")
        self.last_name.set("")
        self.subscription_number.set("")
        self.group.set("")
        self.time_left = TIMER_DURATION
        self.solution_submitted = False
        self.create_student_form()

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = Tk()
    app = StudentAssessmentApp(root)
    root.mainloop()