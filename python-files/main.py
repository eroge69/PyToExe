import sqlite3

# Database Connection
def connect_db():
    conn = sqlite3.connect('student_marks.db')
    return conn

# Database Table Creation
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            max_ospe REAL,
            obtained_ospe REAL,
            max_viva REAL,
            obtained_viva REAL,
            max_internal_practical REAL,
            obtained_internal_practical REAL,
            max_theory REAL,
            obtained_theory REAL,
            max_mcqs REAL,
            obtained_mcqs REAL,
            max_internal_theory REAL,
            obtained_internal_theory REAL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()

# Student Management Functions
def add_student(name, roll_number, course):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO students (name, roll_number, course)
            VALUES (?, ?, ?)
        ''', (name, roll_number, course))
        conn.commit()
        print("Student added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Roll number already exists.")
    conn.close()

def edit_student(student_id, name, roll_number, course):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE students
            SET name = ?, roll_number = ?, course = ?
            WHERE id = ?
        ''', (name, roll_number, course, student_id))
        conn.commit()
        if cursor.rowcount > 0:
            print("Student updated successfully!")
        else:
            print("Student not found.")
    except sqlite3.IntegrityError:
        print("Error: Roll number already exists.")
    conn.close()

def delete_student(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM students
        WHERE id = ?
    ''', (student_id,))
    conn.commit()
    if cursor.rowcount > 0:
        print("Student deleted successfully!")
    else:
        print("Student not found.")
    conn.close()

def view_students():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    if not students:
        print("No students found.")
    else:
        print("Student List:")
        for student in students:
            print(f"ID: {student[0]}, Name: {student[1]}, Roll Number: {student[2]}, Course: {student[3]}")
    conn.close()

# Marks Management Functions
def add_marks(student_id, subject, max_ospe, max_viva, max_internal_practical, max_theory, max_mcqs, max_internal_theory):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO marks (student_id, subject, max_ospe, max_viva, max_internal_practical, max_theory, 
                           max_mcqs, max_internal_theory)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, subject, max_ospe, max_viva, max_internal_practical, max_theory, max_mcqs, max_internal_theory))
    conn.commit()
    print("Marks entry created (Max Marks Added). Now you can add obtained marks")
    conn.close()

def edit_obtained_marks(student_id, subject, obtained_ospe, obtained_viva, obtained_internal_practical, obtained_theory, obtained_mcqs, obtained_internal_theory):
     conn = connect_db()
     cursor = conn.cursor()
     cursor.execute('''
         UPDATE marks
         SET obtained_ospe = ?, obtained_viva = ?, obtained_internal_practical = ?, 
             obtained_theory = ?, obtained_mcqs = ?, obtained_internal_theory = ?
         WHERE student_id = ? AND subject = ?
     ''', (obtained_ospe, obtained_viva, obtained_internal_practical, obtained_theory, obtained_mcqs, obtained_internal_theory, student_id, subject))
     conn.commit()
     if cursor.rowcount > 0:
         print("Obtained marks updated successfully!")
     else:
         print("Marks entry not found for this student and subject.")
     conn.close()

def view_marks(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM marks
        WHERE student_id = ?
    ''', (student_id,))
    marks = cursor.fetchall()
    if not marks:
        print("No marks found for this student.")
    else:
        print("Marks for Student ID:", student_id)
        for mark in marks:
            print(f"Subject: {mark[2]}")
            print(f"  OSPE: Max={mark[3]}, Obtained={mark[4]}")
            print(f"  Viva: Max={mark[5]}, Obtained={mark[6]}")
            print(f"  Internal (Practical): Max={mark[7]}, Obtained={mark[8]}")
            print(f"  Theory: Max={mark[9]}, Obtained={mark[10]}")
            print(f"  MCQs: Max={mark[11]}, Obtained={mark[12]}")
            print(f"  Internal (Theory): Max={mark[13]}, Obtained={mark[14]}")
    conn.close()

# Main Menu
def main_menu():
    create_table() # Ensure tables exist
    while True:
        print("\nStudent and Marks Management System")
        print("1. Student Management")
        print("2. Marks Management")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            student_menu()
        elif choice == '2':
            marks_menu()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def student_menu():
    while True:
        print("\nStudent Management")
        print("1. Add Student")
        print("2. Edit Student")
        print("3. Delete Student")
        print("4. View Students")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter student name: ")
            roll_number = input("Enter roll number: ")
            course = input("Enter course: ")
            add_student(name, roll_number, course)
        elif choice == '2':
            student_id = int(input("Enter student ID to edit: "))
            name = input("Enter new name: ")
            roll_number = input("Enter new roll number: ")
            course = input("Enter new course: ")
            edit_student(student_id, name, roll_number, course)
        elif choice == '3':
            student_id = int(input("Enter student ID to delete: "))
            delete_student(student_id)
        elif choice == '4':
            view_students()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def marks_menu():
    while True:
        print("\nMarks Management")
        print("1. Add Marks (Max Marks)")
        print("2. Edit Obtained Marks")
        print("3. View Marks")
        print("4. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            student_id = int(input("Enter student ID: "))
            subject = input("Enter subject name: ")
            max_ospe = float(input("Enter maximum marks for OSPE: "))
            max_viva = float(input("Enter maximum marks for Viva: "))
            max_internal_practical = float(input("Enter maximum marks for Internal (Practical): "))
            max_theory = float(input("Enter maximum marks for Theory: "))
            max_mcqs = float(input("Enter maximum marks for MCQs: "))
            max_internal_theory = float(input("Enter maximum marks for Internal (Theory): "))
            add_marks(student_id, subject, max_ospe, max_viva, max_internal_practical, max_theory, max_mcqs, max_internal_theory)
        elif choice == '2':
             student_id = int(input("Enter student ID: "))
             subject = input("Enter subject name: ")
             obtained_ospe = float(input("Enter obtained marks for OSPE: "))
             obtained_viva = float(input("Enter obtained marks for Viva: "))
             obtained_internal_practical = float(input("Enter obtained marks for Internal (Practical): "))
             obtained_theory = float(input("Enter obtained marks for Theory: "))
             obtained_mcqs = float(input("Enter obtained marks for MCQs: "))
             obtained_internal_theory = float(input("Enter obtained marks for Internal (Theory): "))
             edit_obtained_marks(student_id, subject, obtained_ospe, obtained_viva, obtained_internal_practical, obtained_theory, obtained_mcqs, obtained_internal_theory)
        elif choice == '3':
            student_id = int(input("Enter student ID to view marks: "))
            view_marks(student_id)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()