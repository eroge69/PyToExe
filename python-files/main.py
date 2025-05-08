import customtkinter as ctk
import sqlite3
import os
import base64
import qrcode
from PIL import Image
from datetime import datetime, timedelta
import uuid
from PIL import ImageTk
from tkinter import filedialog
import cv2
from pyzbar.pyzbar import decode
import threading
import time
import numpy as np
from queue import Queue

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class LibraryApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("ระบบห้องสมุดโรงเรียน")
        self.app.geometry("800x600")
        
        # Initialize database
        self.init_database()
        
        # Start with login window
        self.show_login()
        
    def init_database(self):
        # Create database directory if it doesn't exist
        if not os.path.exists('db'):
            os.makedirs('db')
            
        # Create QR codes directory if it doesn't exist
        if not os.path.exists('assets/qrcodes'):
            os.makedirs('assets/qrcodes')
            
        # Connect to SQLite database
        self.conn = sqlite3.connect('db/library.db')
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                name TEXT,
                grade TEXT,
                number TEXT,
                register_date TEXT,
                expire_date TEXT,
                qrcode_data TEXT,
                qrcode_path TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                code TEXT,
                title TEXT,
                author TEXT,
                category TEXT,
                status TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrow_log (
                id INTEGER PRIMARY KEY,
                member_id INTEGER,
                book_id INTEGER,
                borrow_date TEXT,
                return_due TEXT,
                returned INTEGER,
                FOREIGN KEY (member_id) REFERENCES members (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT * FROM admin_users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO admin_users VALUES (?, ?)", ('admin', 'admin123'))
            
        self.conn.commit()
        
    def show_login(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create login frame
        login_frame = ctk.CTkFrame(self.app)
        login_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Login title
        title_label = ctk.CTkLabel(login_frame, text="เข้าสู่ระบบห้องสมุด", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Username entry
        username_entry = ctk.CTkEntry(login_frame, placeholder_text="ชื่อผู้ใช้")
        username_entry.pack(pady=10, padx=20)
        
        # Password entry
        password_entry = ctk.CTkEntry(login_frame, placeholder_text="รหัสผ่าน", show="*")
        password_entry.pack(pady=10, padx=20)
        
        # Login button
        login_button = ctk.CTkButton(login_frame, text="เข้าสู่ระบบ", 
                                   command=lambda: self.login(username_entry.get(), password_entry.get()))
        login_button.pack(pady=20)
        
    def login(self, username, password):
        self.cursor.execute("SELECT * FROM admin_users WHERE username = ? AND password = ?", 
                          (username, password))
        if self.cursor.fetchone():
            self.show_dashboard()
        else:
            # Show error message
            error_label = ctk.CTkLabel(self.app, text="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", 
                                     text_color="red")
            error_label.pack(pady=10)
            self.app.after(2000, error_label.destroy)
            
    def show_dashboard(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create dashboard frame
        dashboard_frame = ctk.CTkFrame(self.app)
        dashboard_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Dashboard title
        title_label = ctk.CTkLabel(dashboard_frame, text="หน้าหลัก", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Create buttons for each function
        buttons = [
            ("จัดการสมาชิก", self.show_member_management),
            ("จัดการหนังสือ", self.show_book_management),
            ("ยืมหนังสือ", self.show_borrow),
            ("คืนหนังสือ", self.show_return),
            ("ประวัติการยืม-คืน", self.show_history),
            ("ออกจากระบบ", self.show_login)
        ]
        
        for text, command in buttons:
            button = ctk.CTkButton(dashboard_frame, text=text, command=command)
            button.pack(pady=10, padx=20)
            
    def show_member_management(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create member management frame
        member_frame = ctk.CTkFrame(self.app)
        member_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(member_frame, text="จัดการสมาชิก", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Create form frame
        form_frame = ctk.CTkFrame(member_frame)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # Form fields
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="ชื่อ-นามสกุล")
        name_entry.pack(pady=5, padx=20, fill="x")
        
        grade_entry = ctk.CTkEntry(form_frame, placeholder_text="ชั้น")
        grade_entry.pack(pady=5, padx=20, fill="x")
        
        number_entry = ctk.CTkEntry(form_frame, placeholder_text="เลขที่")
        number_entry.pack(pady=5, padx=20, fill="x")
        
        # Add member button
        add_button = ctk.CTkButton(form_frame, text="เพิ่มสมาชิก", 
                                 command=lambda: self.add_member(
                                     name_entry.get(),
                                     grade_entry.get(),
                                     number_entry.get()
                                 ))
        add_button.pack(pady=10)
        
        # Back button
        back_button = ctk.CTkButton(member_frame, text="กลับ", 
                                  command=self.show_dashboard)
        back_button.pack(pady=10)
        
        # Display existing members
        self.display_members(member_frame)
        
    def add_member(self, name, grade, number):
        if not all([name, grade, number]):
            self.show_error("กรุณากรอกข้อมูลให้ครบ")
            return
            
        # Generate QR code data
        register_date = datetime.now().strftime("%Y-%m-%d")
        expire_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        qr_data = f"{name}|{grade}|{number}|{register_date}|{expire_date}"
        encoded_data = base64.b64encode(qr_data.encode()).decode()
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(encoded_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_filename = f"assets/qrcodes/{uuid.uuid4()}.png"
        qr_image.save(qr_filename)
        
        # Add to database
        try:
            self.cursor.execute('''
                INSERT INTO members (name, grade, number, register_date, expire_date, qrcode_data, qrcode_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, grade, number, register_date, expire_date, encoded_data, qr_filename))
            self.conn.commit()
            
            # Show QR code window
            self.show_qr_code_window(qr_image, name, grade, number, register_date, expire_date)
            
            # Refresh member list
            self.show_member_management()
            
        except sqlite3.Error as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
            
    def show_qr_code_window(self, qr_image, name, grade, number, register_date, expire_date):
        # Create new window
        qr_window = ctk.CTkToplevel(self.app)
        qr_window.title("QR Code บัตรสมาชิก")
        qr_window.geometry("400x600")
        
        # Create frame
        qr_frame = ctk.CTkFrame(qr_window)
        qr_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Member info
        info_text = f"""
ชื่อ-นามสกุล: {name}
ชั้น: {grade}
เลขที่: {number}
วันที่สมัคร: {register_date}
วันหมดอายุ: {expire_date}
        """
        info_label = ctk.CTkLabel(qr_frame, text=info_text, font=("Helvetica", 14))
        info_label.pack(pady=10)
        
        # Convert QR code to PhotoImage
        qr_ctk_image = ctk.CTkImage(light_image=qr_image, dark_image=qr_image, size=(256, 256))
        qr_label = ctk.CTkLabel(qr_frame, image=qr_ctk_image, text="")
        qr_label.image = qr_ctk_image
        qr_label.pack(pady=10)
        
        # Save button
        save_button = ctk.CTkButton(qr_frame, text="บันทึก QR Code", 
                                  command=lambda: self.save_qr_code(qr_image, name))
        save_button.pack(pady=10)
        
        # Close button
        close_button = ctk.CTkButton(qr_frame, text="ปิด", 
                                   command=qr_window.destroy)
        close_button.pack(pady=10)
        
    def save_qr_code(self, qr_image, name):
        # Create save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f"qrcode_{name}.png"
        )
        
        if file_path:
            qr_image.save(file_path)
            self.show_success(f"บันทึก QR Code เรียบร้อยแล้ว: {file_path}")
            
    def display_members(self, parent_frame):
        # Create scrollable frame for members
        scroll_frame = ctk.CTkScrollableFrame(parent_frame)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Get all members
        self.cursor.execute("SELECT * FROM members ORDER BY id DESC")
        members = self.cursor.fetchall()
        
        # Display each member
        for member in members:
            member_frame = ctk.CTkFrame(scroll_frame)
            member_frame.pack(pady=5, padx=10, fill="x")
            
            # Member info with complete details
            info_text = f"""
ชื่อ-นามสกุล: {member[1]}
ชั้น: {member[2]}
เลขที่: {member[3]}
วันที่สมัคร: {member[4]}
วันหมดอายุ: {member[5]}
QR Code: {os.path.basename(member[7])}
            """
            info_label = ctk.CTkLabel(member_frame, text=info_text, justify="left")
            info_label.pack(side="left", padx=10)
            
            # Buttons frame
            button_frame = ctk.CTkFrame(member_frame)
            button_frame.pack(side="right", padx=5)
            
            # View QR Code button
            view_qr_button = ctk.CTkButton(button_frame, text="ดู QR Code", 
                                         command=lambda m=member: self.view_member_qr(m))
            view_qr_button.pack(side="left", padx=2)
            
            # Delete button
            delete_button = ctk.CTkButton(button_frame, text="ลบ", 
                                        command=lambda m=member: self.delete_member(m))
            delete_button.pack(side="left", padx=2)
            
    def view_member_qr(self, member):
        try:
            # Load QR code image
            qr_image = Image.open(member[7])
            
            # Show QR code window
            self.show_qr_code_window(qr_image, member[1], member[2], member[3], 
                                   member[4], member[5])
        except Exception as e:
            self.show_error(f"ไม่สามารถเปิด QR Code ได้: {str(e)}")
            
    def delete_member(self, member):
        try:
            # Delete QR code file
            if os.path.exists(member[7]):  # qrcode_path
                os.remove(member[7])
                
            # Delete from database
            self.cursor.execute("DELETE FROM members WHERE id = ?", (member[0],))
            self.conn.commit()
            
            self.show_success("ลบสมาชิกสำเร็จ")
            self.show_member_management()  # Refresh the view
        except Exception as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
            
    def show_error(self, message):
        error_label = ctk.CTkLabel(self.app, text=message, text_color="red")
        error_label.pack(pady=10)
        self.app.after(2000, error_label.destroy)
        
    def show_success(self, message):
        success_label = ctk.CTkLabel(self.app, text=message, text_color="green")
        success_label.pack(pady=10)
        self.app.after(2000, success_label.destroy)
        
    def show_book_management(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create book management frame
        book_frame = ctk.CTkFrame(self.app)
        book_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(book_frame, text="จัดการหนังสือ", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Create form frame
        form_frame = ctk.CTkFrame(book_frame)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # Form fields
        code_entry = ctk.CTkEntry(form_frame, placeholder_text="รหัสหนังสือ")
        code_entry.pack(pady=5, padx=20, fill="x")
        
        title_entry = ctk.CTkEntry(form_frame, placeholder_text="ชื่อเรื่อง")
        title_entry.pack(pady=5, padx=20, fill="x")
        
        author_entry = ctk.CTkEntry(form_frame, placeholder_text="ผู้แต่ง")
        author_entry.pack(pady=5, padx=20, fill="x")
        
        category_entry = ctk.CTkEntry(form_frame, placeholder_text="หมวดหมู่")
        category_entry.pack(pady=5, padx=20, fill="x")
        
        # Add book button
        add_button = ctk.CTkButton(form_frame, text="เพิ่มหนังสือ", 
                                 command=lambda: self.add_book(
                                     code_entry.get(),
                                     title_entry.get(),
                                     author_entry.get(),
                                     category_entry.get()
                                 ))
        add_button.pack(pady=10)
        
        # Back button
        back_button = ctk.CTkButton(book_frame, text="กลับ", 
                                  command=self.show_dashboard)
        back_button.pack(pady=10)
        
        # Display existing books
        self.display_books(book_frame)
        
    def add_book(self, code, title, author, category):
        if not all([code, title, author, category]):
            self.show_error("กรุณากรอกข้อมูลให้ครบ")
            return
            
        try:
            self.cursor.execute('''
                INSERT INTO books (code, title, author, category, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (code, title, author, category, "ว่าง"))
            self.conn.commit()
            self.show_success("เพิ่มหนังสือสำเร็จ")
            self.show_book_management()  # Refresh the view
        except sqlite3.Error as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
            
    def display_books(self, parent_frame):
        # Create scrollable frame for books
        scroll_frame = ctk.CTkScrollableFrame(parent_frame)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Get all books
        self.cursor.execute("SELECT * FROM books ORDER BY id DESC")
        books = self.cursor.fetchall()
        
        # Display each book
        for book in books:
            book_frame = ctk.CTkFrame(scroll_frame)
            book_frame.pack(pady=5, padx=10, fill="x")
            
            # Book info
            info_text = f"รหัส: {book[1]} | ชื่อ: {book[2]} | ผู้แต่ง: {book[3]} | หมวดหมู่: {book[4]} | สถานะ: {book[5]}"
            info_label = ctk.CTkLabel(book_frame, text=info_text)
            info_label.pack(side="left", padx=10)
            
            # Delete button
            delete_button = ctk.CTkButton(book_frame, text="ลบ", 
                                        command=lambda b=book: self.delete_book(b))
            delete_button.pack(side="right", padx=5)
            
    def delete_book(self, book):
        try:
            # Check if book is borrowed
            self.cursor.execute("SELECT * FROM borrow_log WHERE book_id = ? AND returned = 0", (book[0],))
            if self.cursor.fetchone():
                self.show_error("ไม่สามารถลบหนังสือที่กำลังถูกยืมอยู่ได้")
                return
                
            # Delete from database
            self.cursor.execute("DELETE FROM books WHERE id = ?", (book[0],))
            self.conn.commit()
            
            self.show_success("ลบหนังสือสำเร็จ")
            self.show_book_management()  # Refresh the view
        except Exception as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
            
    def show_borrow(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create borrow frame
        borrow_frame = ctk.CTkFrame(self.app)
        borrow_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(borrow_frame, text="ยืมหนังสือ", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Member info frame
        member_frame = ctk.CTkFrame(borrow_frame)
        member_frame.pack(pady=10, padx=20, fill="x")
        
        # Scan button only (no QR entry)
        scan_button = ctk.CTkButton(member_frame, text="สแกน QR Code", command=self.start_scan)
        scan_button.pack(pady=5)
        
        # Member info display
        self.member_info_label = ctk.CTkLabel(member_frame, text="กรุณาสแกน QR Code สมาชิก")
        self.member_info_label.pack(pady=5)
        
        # Book selection frame
        book_frame = ctk.CTkFrame(borrow_frame)
        book_frame.pack(pady=10, padx=20, fill="x")
        
        # Book selection dropdown
        self.book_var = ctk.StringVar(value="เลือกหนังสือ")
        self.book_dropdown = ctk.CTkOptionMenu(book_frame, variable=self.book_var)
        self.book_dropdown.pack(pady=5, padx=20, fill="x")
        self.update_book_dropdown()
        
        # Due date selection
        due_date_frame = ctk.CTkFrame(borrow_frame)
        due_date_frame.pack(pady=10, padx=20, fill="x")
        
        due_date_label = ctk.CTkLabel(due_date_frame, text="กำหนดคืน:")
        due_date_label.pack(side="left", padx=10)
        
        self.due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        due_date_entry = ctk.CTkEntry(due_date_frame, placeholder_text=self.due_date)
        due_date_entry.pack(side="left", padx=10)
        
        # Borrow button (no qr_data param)
        borrow_button = ctk.CTkButton(borrow_frame, text="ยืมหนังสือ", 
                                    command=lambda: self.borrow_book(
                                        self.book_var.get(),
                                        due_date_entry.get() or self.due_date
                                    ))
        borrow_button.pack(pady=10)
        
        # Back button
        back_button = ctk.CTkButton(borrow_frame, text="กลับ", command=self.show_dashboard)
        back_button.pack(pady=10)
        
    def start_scan(self, mode="borrow"):
        # Create new window for scanning
        scan_window = ctk.CTkToplevel(self.app)
        scan_window.title("สแกน QR Code")
        scan_window.geometry("800x600")
        
        # Create frame for video
        video_frame = ctk.CTkFrame(scan_window)
        video_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Create label for video
        video_label = ctk.CTkLabel(video_frame, text="")
        video_label.pack(fill="both", expand=True)
        
        # Add instruction label
        instruction_label = ctk.CTkLabel(scan_window, 
            text="นำ QR Code มาวางตรงกล้อง\nรอสักครู่ระบบจะสแกนอัตโนมัติ",
            font=("Helvetica", 16))
        instruction_label.pack(pady=10)
        
        # Add status label
        status_label = ctk.CTkLabel(scan_window,
            text="กำลังรอสแกน...",
            font=("Helvetica", 14),
            text_color="yellow")
        status_label.pack(pady=5)
        
        # Start webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.show_error("ไม่สามารถเปิดกล้องได้")
            scan_window.destroy()
            return
            
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Create a queue for thread communication
        qr_queue = Queue()
        
        def scan_qr():
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to grab frame")
                        break
                        
                    # Resize frame for better display
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert frame to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Apply threshold to make QR code more visible
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # Try to decode QR code from both original and thresholded image
                    decoded_objects = decode(frame)
                    if not decoded_objects:
                        decoded_objects = decode(thresh)
                    
                    for obj in decoded_objects:
                        try:
                            # Draw rectangle around QR code
                            points = obj.polygon
                            if len(points) > 4:
                                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                                cv2.polylines(frame, [hull], True, (0, 255, 0), 2)
                            else:
                                cv2.polylines(frame, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 2)
                            
                            # Decode QR data
                            qr_data = obj.data.decode('utf-8')
                            decoded_data = base64.b64decode(qr_data).decode()
                            name, grade, number, register_date, expire_date = decoded_data.split("|")
                            
                            # Update status
                            status_label.configure(text="✓ สแกนสำเร็จ!", text_color="green")
                            
                            # Put data in queue for main thread to process
                            qr_queue.put((name, grade, number))
                            
                            # Close scan window after a short delay
                            scan_window.after(1000, lambda: [scan_window.destroy(), cap.release()])
                            return
                            
                        except Exception as e:
                            print(f"Error decoding QR: {str(e)}")
                            status_label.configure(text="❌ ไม่สามารถอ่าน QR Code ได้", text_color="red")
                    
                    # Convert frame to CTkImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_ctk = ctk.CTkImage(light_image=frame_pil, dark_image=frame_pil, size=(640, 480))
                    
                    # Update video label
                    video_label.configure(image=frame_ctk)
                    
                except Exception as e:
                    print(f"Error in scan loop: {str(e)}")
                    break
                    
                # Check if window is closed
                if not scan_window.winfo_exists():
                    break
                    
                time.sleep(0.03)  # 30 FPS
                
            # Clean up
            cap.release()
                
        # Start scanning in separate thread
        scan_thread = threading.Thread(target=scan_qr)
        scan_thread.daemon = True
        scan_thread.start()
        
        def process_qr_data():
            try:
                if not qr_queue.empty():
                    name, grade, number = qr_queue.get()
                    self.cursor.execute("""
                        SELECT id, register_date, expire_date FROM members 
                        WHERE name = ? AND grade = ? AND number = ?
                    """, (name, grade, number))
                    member = self.cursor.fetchone()
                    if member:
                        member_id, register_date, expire_date = member
                        if mode == "return":
                            self.return_member_info_label.configure(
                                text=f"สมาชิก: {name}\nชั้น: {grade}\nเลขที่: {number}"
                            )
                            self.display_borrowed_books(member_id)
                        else:
                            self.scanned_member = (name, grade, number, register_date, expire_date)
                            # แสดงข้อมูลสมาชิกทันที
                            self.member_info_label.configure(
                                text=f"สมาชิก: {name}\nชั้น: {grade}\nเลขที่: {number}"
                            )
                            # Show success notification (popup)
                            success_window = ctk.CTkToplevel(self.app)
                            success_window.title("พบข้อมูลสมาชิก")
                            success_window.geometry("300x200")
                            success_window.update_idletasks()
                            width = success_window.winfo_width()
                            height = success_window.winfo_height()
                            x = (success_window.winfo_screenwidth() // 2) - (width // 2)
                            y = (success_window.winfo_screenheight() // 2) - (height // 2)
                            success_window.geometry(f'{width}x{height}+{x}+{y}')
                            success_label = ctk.CTkLabel(success_window, 
                                text="✓ พบข้อมูลสมาชิกในระบบ",
                                text_color="green",
                                font=("Helvetica", 16))
                            success_label.pack(pady=20)
                            info_label = ctk.CTkLabel(success_window,
                                text=f"ชื่อ: {name}\nชั้น: {grade}\nเลขที่: {number}",
                                font=("Helvetica", 14))
                            info_label.pack(pady=10)
                            close_button = ctk.CTkButton(success_window,
                                text="ตกลง",
                                command=success_window.destroy)
                            close_button.pack(pady=10)
                    if scan_window.winfo_exists():
                        scan_window.after(100, process_qr_data)
            except Exception as e:
                print(f"Error processing QR data: {str(e)}")
        
        # Start processing QR data
        scan_window.after(100, process_qr_data)
        
        # Handle window close
        def on_closing():
            cap.release()
            scan_window.destroy()
            
        scan_window.protocol("WM_DELETE_WINDOW", on_closing)
        
    def update_book_dropdown(self):
        self.cursor.execute("SELECT id, code, title FROM books WHERE status = 'ว่าง'")
        books = self.cursor.fetchall()
        self.book_options = {f"{book[1]} - {book[2]}": book[0] for book in books}
        if hasattr(self, 'book_dropdown'):
            self.book_dropdown.configure(values=list(self.book_options.keys()))
            if list(self.book_options.keys()):
                self.book_dropdown.set(list(self.book_options.keys())[0])
            else:
                self.book_dropdown.set("เลือกหนังสือ")
            
    def borrow_book(self, book_text, due_date):
        print("เลือก:", book_text)
        print("ตัวเลือก:", list(self.book_options.keys()))
        if not hasattr(self, 'scanned_member') or not self.scanned_member:
            self.show_error("กรุณาสแกน QR Code สมาชิกก่อน")
            return
        if book_text == "เลือกหนังสือ":
            self.show_error("กรุณาเลือกหนังสือ")
            return
        if book_text not in self.book_options:
            self.show_error("ไม่พบหนังสือในระบบ กรุณาลองใหม่")
            return
        try:
            name, grade, number, register_date, expire_date = self.scanned_member
            self.cursor.execute("SELECT id FROM members WHERE name = ? AND grade = ? AND number = ?", (name, grade, number))
            member = self.cursor.fetchone()
            if not member:
                self.show_error("ไม่พบข้อมูลสมาชิก")
                return
            member_id = member[0]
            book_id = self.book_options[book_text]
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                INSERT INTO borrow_log (member_id, book_id, borrow_date, return_due, returned)
                VALUES (?, ?, ?, ?, ?)
            ''', (member_id, book_id, borrow_date, due_date, 0))
            self.cursor.execute("UPDATE books SET status = 'ยืมแล้ว' WHERE id = ?", (book_id,))
            self.conn.commit()
            self.show_success("ยืมหนังสือสำเร็จ")
            self.show_dashboard()
        except Exception as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
            
    def show_return(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create return frame
        return_frame = ctk.CTkFrame(self.app)
        return_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(return_frame, text="คืนหนังสือ", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Member info frame
        member_frame = ctk.CTkFrame(return_frame)
        member_frame.pack(pady=10, padx=20, fill="x")
        
        # QR code entry frame
        qr_frame = ctk.CTkFrame(member_frame)
        qr_frame.pack(pady=5, padx=20, fill="x")
        
        # QR code entry
        qr_entry = ctk.CTkEntry(qr_frame, placeholder_text="สแกน QR Code หรือวางข้อมูล")
        qr_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Scan button
        scan_button = ctk.CTkButton(qr_frame, text="สแกน QR Code", 
                                    command=lambda: self.start_scan(mode="return"))
        scan_button.pack(side="right", padx=5)
        
        # Member info display
        self.return_member_info_label = ctk.CTkLabel(member_frame, text="")
        self.return_member_info_label.pack(pady=5)
        
        # Borrowed books frame
        self.borrowed_books_frame = ctk.CTkFrame(return_frame)
        self.borrowed_books_frame.pack(pady=10, padx=20, fill="x")
        
        # Back button
        back_button = ctk.CTkButton(return_frame, text="กลับ", 
                                  command=self.show_dashboard)
        back_button.pack(pady=10)
        
    def display_borrowed_books(self, member_id):
        # Clear existing books
        for widget in self.borrowed_books_frame.winfo_children():
            widget.destroy()
            
        # Get borrowed books
        self.cursor.execute('''
            SELECT b.id, b.code, b.title, bl.borrow_date, bl.return_due
            FROM books b
            JOIN borrow_log bl ON b.id = bl.book_id
            WHERE bl.member_id = ? AND bl.returned = 0
        ''', (member_id,))
        books = self.cursor.fetchall()
        
        if not books:
            no_books_label = ctk.CTkLabel(self.borrowed_books_frame, text="ไม่มีหนังสือที่ยืมอยู่")
            no_books_label.pack(pady=10)
            return
            
        # Display each book
        for book in books:
            book_frame = ctk.CTkFrame(self.borrowed_books_frame)
            book_frame.pack(pady=5, padx=10, fill="x")
            
            # Book info
            info_text = f"รหัส: {book[1]} | ชื่อ: {book[2]} | ยืม: {book[3]} | คืน: {book[4]}"
            info_label = ctk.CTkLabel(book_frame, text=info_text)
            info_label.pack(side="left", padx=10)
            
            # Return button
            return_button = ctk.CTkButton(book_frame, text="คืน", 
                                        command=lambda b=book: self.return_book(b[0], member_id))
            return_button.pack(side="right", padx=5)
            
    def return_book(self, book_id, member_id):
        try:
            self.cursor.execute('''
                UPDATE borrow_log 
                SET returned = 1 
                WHERE book_id = ? AND returned = 0
            ''', (book_id,))
            self.cursor.execute("UPDATE books SET status = 'ว่าง' WHERE id = ?", (book_id,))
            self.conn.commit()
            self.show_success("คืนหนังสือสำเร็จ")
            self.display_borrowed_books(member_id)  # Refresh list
        except Exception as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
        
    def show_history(self):
        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
            
        # Create history frame
        history_frame = ctk.CTkFrame(self.app)
        history_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(history_frame, text="ประวัติการยืม-คืน", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(history_frame)
        search_frame.pack(pady=10, padx=20, fill="x")
        
        # Search fields
        member_entry = ctk.CTkEntry(search_frame, placeholder_text="ค้นหาตามชื่อสมาชิก")
        member_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        book_entry = ctk.CTkEntry(search_frame, placeholder_text="ค้นหาตามรหัสหนังสือ")
        book_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        date_entry = ctk.CTkEntry(search_frame, placeholder_text="ค้นหาตามวันที่ (YYYY-MM-DD)")
        date_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Search button
        search_button = ctk.CTkButton(search_frame, text="ค้นหา", 
                                    command=lambda: self.search_history(
                                        member_entry.get(),
                                        book_entry.get(),
                                        date_entry.get()
                                    ))
        search_button.pack(side="left", padx=5)
        
        # Export button
        export_button = ctk.CTkButton(search_frame, text="Export PDF", 
                                    command=self.export_history)
        export_button.pack(side="left", padx=5)
        
        # History display frame
        self.history_display_frame = ctk.CTkScrollableFrame(history_frame)
        self.history_display_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Back button
        back_button = ctk.CTkButton(history_frame, text="กลับ", 
                                  command=self.show_dashboard)
        back_button.pack(pady=10)
        
        # Display initial history
        self.display_history()
        
    def display_history(self, member_filter="", book_filter="", date_filter=""):
        # Clear existing history
        for widget in self.history_display_frame.winfo_children():
            widget.destroy()
            
        # Build query
        query = '''
            SELECT m.name, m.grade, m.number, b.code, b.title, bl.borrow_date, bl.return_due, bl.returned
            FROM borrow_log bl
            JOIN members m ON bl.member_id = m.id
            JOIN books b ON bl.book_id = b.id
            WHERE 1=1
        '''
        params = []
        
        if member_filter:
            query += " AND (m.name LIKE ? OR m.grade LIKE ? OR m.number LIKE ?)"
            params.extend([f"%{member_filter}%"] * 3)
            
        if book_filter:
            query += " AND (b.code LIKE ? OR b.title LIKE ?)"
            params.extend([f"%{book_filter}%"] * 2)
            
        if date_filter:
            query += " AND (bl.borrow_date = ? OR bl.return_due = ?)"
            params.extend([date_filter] * 2)
            
        query += " ORDER BY bl.borrow_date DESC"
        
        # Execute query
        self.cursor.execute(query, params)
        records = self.cursor.fetchall()
        
        if not records:
            no_records_label = ctk.CTkLabel(self.history_display_frame, text="ไม่พบประวัติ")
            no_records_label.pack(pady=10)
            return
            
        # Display each record
        for record in records:
            record_frame = ctk.CTkFrame(self.history_display_frame)
            record_frame.pack(pady=5, padx=10, fill="x")
            
            # Record info
            status = "คืนแล้ว" if record[7] else "ยังไม่คืน"
            info_text = (f"สมาชิก: {record[0]} ({record[1]}/{record[2]}) | "
                        f"หนังสือ: {record[3]} - {record[4]} | "
                        f"ยืม: {record[5]} | คืน: {record[6]} | "
                        f"สถานะ: {status}")
            info_label = ctk.CTkLabel(record_frame, text=info_text)
            info_label.pack(pady=5, padx=10)
            
    def search_history(self, member_filter, book_filter, date_filter):
        self.display_history(member_filter, book_filter, date_filter)
        
    def export_history(self):
        try:
            # Get all history records
            self.cursor.execute('''
                SELECT m.name, m.grade, m.number, b.code, b.title, 
                       bl.borrow_date, bl.return_due, bl.returned
                FROM borrow_log bl
                JOIN members m ON bl.member_id = m.id
                JOIN books b ON bl.book_id = b.id
                ORDER BY bl.borrow_date DESC
            ''')
            records = self.cursor.fetchall()
            
            # Create PDF file
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib.units import inch
            
            filename = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            
            # Create table data
            data = [["ชื่อสมาชิก", "ชั้น", "เลขที่", "รหัสหนังสือ", "ชื่อหนังสือ", "วันที่ยืม", "วันที่คืน", "สถานะ"]]
            for record in records:
                status = "คืนแล้ว" if record[7] else "ยังไม่คืน"
                data.append([
                    record[0], record[1], record[2], record[3], record[4],
                    record[5], record[6], status
                ])
            
            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            # Build PDF
            elements = []
            elements.append(table)
            doc.build(elements)
            
            self.show_success(f"Export สำเร็จ: {filename}")
        except Exception as e:
            self.show_error(f"เกิดข้อผิดพลาด: {str(e)}")
        
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = LibraryApp()
    app.run() 