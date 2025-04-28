# student_grade = {}

# # Add a new student
# def add_student(name, grade):
#     student_grade[name] = grade
#     print(f"Added {name} with a grade of {grade}")

# # Update a student
# def update_student(name, grade):
#     if name in student_grade:
#         student_grade[name] = grade
#         print(f"{name}'s grade updated to {grade}")
#     else:
#         print(f"{name} is not found!")

# # Delete a student
# def delete_student(name):
#     if name in student_grade:
#         del student_grade[name]
#         print(f"{name} has been successfully deleted")
#     else:
#         print(f"{name} is not found!")

# # View all students
# def view_all():
#     if student_grade:
#         for name, grade in student_grade.items():
#             print(f"{name}: {grade}")
#     else:
#         print("No students found/added")

# # Validate grade input (optional, assumes numeric grades)
# def validate_grade(grade):
#     try:
#         grade = float(grade)  # Convert to float to allow decimals
#         if 0 <= grade <= 100:  # Assuming grades are between 0 and 100
#             return str(grade)  # Store as string for simplicity
#         else:
#             return None
#     except ValueError:
#         return None

# def main():
#     while True:
#         print("\nStudent Grades Management System")
#         print("1. Add Student")
#         print("2. Update Student")
#         print("3. Delete Student")
#         print("4. View Students")
#         print("5. Exit")

#         try:
#             choice = int(input("Enter Your Choice: "))
#         except ValueError:
#             print("Invalid input! Please enter a number.")
#             continue

#         if choice == 1:
#             name = input("Enter Student Name: ").strip()
#             if not name:
#                 print("Name cannot be empty!")
#                 continue
#             grade = input("Enter Student Grade: ").strip()
#             validated_grade = validate_grade(grade)
#             if validated_grade:
#                 add_student(name, validated_grade)
#             else:
#                 print("Invalid grade! Please enter a number between 0 and 100.")

#         elif choice == 2:
#             name = input("Enter Student Name: ").strip()
#             if not name:
#                 print("Name cannot be empty!")
#                 continue
#             grade = input("Enter Student Grade: ").strip()
#             validated_grade = validate_grade(grade)
#             if validated_grade:
#                 update_student(name, validated_grade)
#             else:
#                 print("Invalid grade! Please enter a number between 0 and 100.")

#         elif choice == 3:
#             name = input("Enter Student Name: ").strip()
#             if not name:
#                 print("Name cannot be empty!")
#                 continue
#             delete_student(name)

#         elif choice == 4:
#             view_all()

#         elif choice == 5:
#             print("Closing the program...")
#             break
#         else:
#             print("Invalid choice, please try again!")

# # Run the program
# if __name__ == "__main__":
#     main()


import sqlite3
from contextlib import contextmanager
import tkinter as tk
from tkinter import ttk, messagebox

# Database setup
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade REAL,
                email TEXT
            )
        ''')
        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('students.db')
    try:
        yield conn
    finally:
        conn.close()

# Add a new student
def add_student(id, name, grade, email):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (id, name, grade, email)
                VALUES (?, ?, ?, ?)
            ''', (id, name, grade, email))
            conn.commit()
            return True, f"Added {name} with ID {id}"
    except sqlite3.IntegrityError:
        return False, f"Error: Student ID {id} already exists!"

# Update a student
def update_student(id, name, grade, email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM students WHERE id = ?
        ''', (id,))
        if cursor.fetchone():
            cursor.execute('''
                UPDATE students
                SET name = ?, grade = ?, email = ?
                WHERE id = ?
            ''', (name, grade, email, id))
            conn.commit()
            return True, f"Updated student with ID {id}"
        else:
            return False, f"Student ID {id} not found!"

# Delete a student
def delete_student(id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM students WHERE id = ?
        ''', (id,))
        if cursor.fetchone():
            cursor.execute('''
                DELETE FROM students WHERE id = ?
            ''', (id,))
            conn.commit()
            return True, f"Student ID {id} has been successfully deleted"
        else:
            return False, f"Student ID {id} not found!"

# View all students
def get_all_students():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, grade, email FROM students')
        return cursor.fetchall()

# Validate inputs
def validate_grade(grade):
    try:
        grade = float(grade)
        if 0 <= grade <= 100:
            return True, grade
        return False, "Grade must be between 0 and 100!"
    except ValueError:
        return False, "Grade must be a number!"

def validate_email(email):
    if "@" in email and "." in email:
        return True, email
    return False, "Invalid email format!"

# GUI Application
class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Data Management System")
        self.root.geometry("800x600")

        # Initialize database
        init_db()

        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Student Details", padding=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        # Input Fields
        ttk.Label(input_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = ttk.Entry(input_frame)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Grade (0-100):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.grade_entry = ttk.Entry(input_frame)
        self.grade_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(input_frame)
        self.email_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Add Student", command=self.add_student).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Student", command=self.update_student).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Student", command=self.delete_student).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side="left", padx=5)

        # Table Frame
        table_frame = ttk.LabelFrame(self.root, text="Student Records", padding=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Treeview for displaying students
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Grade", "Email"), show="headings")
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Grade", text="Grade")
        self.tree.heading("Email", text="Email")
        self.tree.column("ID", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Grade", width=100)
        self.tree.column("Email", width=200)
        self.tree.pack(fill="both", expand=True)

        # Load initial data
        self.refresh_table()

        # Bind double-click to load data into fields
        self.tree.bind("<Double-1>", self.load_selected)

    def refresh_table(self):
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Load data from database
        students = get_all_students()
        for student in students:
            self.tree.insert("", "end", values=student)

    def clear_fields(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def validate_inputs(self):
        id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        email = self.email_entry.get().strip()

        if not id:
            return False, "Student ID cannot be empty!"
        if not name:
            return False, "Name cannot be empty!"
        grade_valid, grade_result = validate_grade(grade)
        if not grade_valid:
            return False, grade_result
        email_valid, email_result = validate_email(email)
        if not email_valid:
            return False, email_result
        return True, (id, name, grade_result, email_result)

    def add_student(self):
        valid, result = self.validate_inputs()
        if not valid:
            messagebox.showerror("Error", result)
            return
        id, name, grade, email = result
        success, message = add_student(id, name, grade, email)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_table()
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)

    def update_student(self):
        valid, result = self.validate_inputs()
        if not valid:
            messagebox.showerror("Error", result)
            return
        id, name, grade, email = result
        success, message = update_student(id, name, grade, email)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_table()
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)

    def delete_student(self):
        id = self.id_entry.get().strip()
        if not id:
            messagebox.showerror("Error", "Student ID cannot be empty!")
            return
        success, message = delete_student(id)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_table()
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)

    def load_selected(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.clear_fields()
            self.id_entry.insert(0, values[0])
            self.name_entry.insert(0, values[1])
            self.grade_entry.insert(0, values[2])
            self.email_entry.insert(0, values[3])

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()