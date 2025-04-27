import threading
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import firebase_admin
from firebase_admin import credentials, db
import uuid
from datetime import datetime, timedelta
from fpdf import FPDF
import os
import webbrowser
import openai
import speech_recognition as sr
from PIL import Image, ImageTk
import io
import google.generativeai as genai
import numpy as np
import pyttsx3

# Initialize Firebase with your credentials
cred = credentials.Certificate("projectfirebasecrm-firebase-adminsdk-fbsvc-dffba1017c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://projectfirebasecrm-default-rtdb.firebaseio.com/'
})

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("ASVAT")

        # Current user data
        self.current_user = None
        self.current_role = None
       
        # Set window icon
        self.iconbitmap("5.ico")
        # Color scheme
        self.primary_color = "#6C63FF"
        self.accent_color = "#F5F5F5"
        self.text_color = "#333333"
        self.secondary_text = "#666666"
        self.danger_color = "#FF4D4D"
        self.success_color = "#4CAF50"
       
        # Menu items based on role
        self.admin_menu = ["Dashboard", "Manage Employees", "Inventory", "Billing", "Reports", "Help Center", "Task Management", "Notice", "Chatbot", "Recommendations", "Settings"]
        self.employee_menu = ["Dashboard", "Tasks", "Help Center", "Inventory", "Billing", "Updates", "Settings"]
        self.customer_menu = [
            "Dashboard",
            "Products",
            "Voice Bot",
            "Tasks",
            "Suggestion",
            "Help Center",
            "Settings"
        ]
       
        # Company settings
        self.company_logo = None
        self.company_signature = None
        self.company_settings = {
            'name': 'Global Leaders Inc.',
            'address': '123 Business Ave, New York, NY 10001',
            'phone': '+1 (555) 123-4567',
            'email': 'info@globalleaders.com',
            'website': 'www.globalleaders.com',
            'tax_rate': 10,
            'logo': None,
            'signature': None,
            'about_us': {
                'introduction': "Meet our dynamic team and discover the meaning to success as we will let you know how we work.",
                'history': "Founded in 2016, we've grown from a small startup to a global leader with offices in multiple countries.",
                'mission': "To provide innovative solutions that transform businesses and create lasting value for our clients.",
                'vision': "To be the most trusted partner for businesses worldwide by 2030.",
                'values': "Quality, Integrity, Innovation, Collaboration, Customer Focus",
                'team': "Our team consists of industry experts with decades of combined experience in business transformation.",
                'achievements': "Global Leader 2023, 1st Class Award, 4.9 Star Rating",
                'locations': "New York, London, Tokyo, Sydney",
                'images': {
                    'team_photo': None,
                    'office_photo': None,
                    'achievements_photo': None
                }
            }
        }
       
        # Load company settings
        self.load_company_settings()
       
        # Check if default admin exists
        self.ensure_default_admin()
        self.show_login_page()
    
    def load_company_settings(self):
        try:
            ref = db.reference('company_settings')
            settings = ref.get()
            if settings:
                self.company_settings.update(settings)
           
            # Try to load logo and signature
            logo_ref = db.reference('company_logo')
            logo_data = logo_ref.get()
            if logo_data:
                self.company_logo = logo_data
           
            signature_ref = db.reference('company_signature')
            signature_data = signature_ref.get()
            if signature_data:
                self.company_signature = signature_data
        except:
            pass

    def ensure_default_admin(self):
        ref = db.reference('users')
        users = ref.get() or {}
       
        # Check if default admin exists
        admin_exists = any(user.get('username') == 'admin' for user in users.values())
       
        if not admin_exists:
            # Create default admin
            admin_data = {
                'username': 'admin',
                'password': 'admin',
                'name': 'Default Admin',
                'phone': '1234567890',
                'address': 'Admin Address',
                'role': 'admin',
                'designation': 'System Administrator',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'email': 'admin@example.com'
            }
            ref.push(admin_data)

    def show_login_page(self):
        self.clear_window()
        self.current_user = None
        self.current_role = None

        # Login UI
        login_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        login_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        ctk.CTkLabel(login_frame, text="Welcome Back!", font=("Roboto", 28, "bold"), text_color=self.text_color).pack(pady=(200, 10))
        ctk.CTkLabel(login_frame, text="Enter your credentials to continue", font=("Roboto", 14), text_color=self.secondary_text).pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=10)

        login_btn = ctk.CTkButton(login_frame, text="Log In", command=self.check_login, fg_color=self.primary_color, text_color="white")
        login_btn.pack(pady=20)
       
        register_btn = ctk.CTkButton(login_frame, text="Register", command=self.show_register_page, fg_color="transparent", border_color=self.primary_color, text_color=self.primary_color, border_width=1)
        register_btn.pack(pady=5)

        design_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.primary_color)
        design_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        ctk.CTkLabel(design_frame, text="ASVAT", font=("Roboto", 102, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
       
    def show_register_page(self):
        self.clear_window()

        register_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        register_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        ctk.CTkLabel(register_frame, text="Create Account", font=("Roboto", 28, "bold"), text_color=self.text_color).pack(pady=(150, 10))
       
        self.reg_name = ctk.CTkEntry(register_frame, placeholder_text="Full Name", width=250)
        self.reg_name.pack(pady=5)
       
        self.reg_username = ctk.CTkEntry(register_frame, placeholder_text="Username", width=250)
        self.reg_username.pack(pady=5)
       
        self.reg_email = ctk.CTkEntry(register_frame, placeholder_text="Email", width=250)
        self.reg_email.pack(pady=5)
       
        self.reg_phone = ctk.CTkEntry(register_frame, placeholder_text="Phone Number", width=250)
        self.reg_phone.pack(pady=5)
       
        self.reg_address = ctk.CTkEntry(register_frame, placeholder_text="Address", width=250)
        self.reg_address.pack(pady=5)
       
        self.reg_password = ctk.CTkEntry(register_frame, placeholder_text="Password", show="*", width=250)
        self.reg_password.pack(pady=5)
       
        self.reg_confirm_password = ctk.CTkEntry(register_frame, placeholder_text="Confirm Password", show="*", width=250)
        self.reg_confirm_password.pack(pady=5)

        register_btn = ctk.CTkButton(register_frame, text="Register", command=self.register_customer, fg_color=self.primary_color, text_color="white")
        register_btn.pack(pady=20)
       
        back_btn = ctk.CTkButton(register_frame, text="Back to Login", command=self.show_login_page, fg_color="transparent", border_color=self.primary_color, text_color=self.primary_color, border_width=1)
        back_btn.pack(pady=5)

        design_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.primary_color)
        design_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        ctk.CTkLabel(design_frame, text="ASVAT", font=("Roboto", 102, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def register_customer(self):
        # Validation
        if self.reg_password.get() != self.reg_confirm_password.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
           
        if not all([self.reg_name.get(), self.reg_username.get(), self.reg_password.get(), self.reg_email.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
           
        # Check if username already exists
        ref = db.reference('users')
        users = ref.get() or {}
       
        for user_id, user_data in users.items():
            if user_data.get('username') == self.reg_username.get():
                messagebox.showerror("Error", "Username already taken")
                return
            if user_data.get('email') == self.reg_email.get():
                messagebox.showerror("Error", "Email already registered")
                return
               
        # Create new user
        user_data = {
            'username': self.reg_username.get(),
            'name': self.reg_name.get(),
            'email': self.reg_email.get(),
            'phone': self.reg_phone.get(),
            'address': self.reg_address.get(),
            'password': self.reg_password.get(),
            'role': 'customer',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
       
        new_user_ref = ref.push(user_data)
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.show_login_page()

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
       
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
           
        ref = db.reference('users')
        users = ref.get() or {}
       
        for user_id, user_data in users.items():
            if user_data.get('username') == username and user_data.get('password') == password:
                self.current_user = user_data
                self.current_user['id'] = user_id
                self.current_role = user_data.get('role')
                self.slide_transition(self.show_dashboard)
                return
               
        messagebox.showerror("Login Failed", "Invalid username or password")

    def slide_transition(self, target_page_func):
        width = self.winfo_width()

        overlay = ctk.CTkFrame(self, fg_color=self.primary_color)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        for i in range(width, 0, -20):
            overlay.place(x=i)
            self.update()
            time.sleep(0.005)

        target_page_func()

    def show_dashboard(self):
        self.clear_window()

        self.sidebar = ctk.CTkFrame(self, fg_color=self.primary_color, corner_radius=0)
        self.sidebar.place(relx=0, rely=0, relwidth=0.2, relheight=1)

        # Profile Section
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color=self.primary_color)
        profile_frame.pack(fill="x", pady=(20, 10))

        ctk.CTkLabel(profile_frame, text=f"👤 {self.current_user.get('name', 'User')}",
                    font=("Roboto", 14, "bold"), text_color="white").pack(pady=5)
        ctk.CTkLabel(profile_frame, text=f"({self.current_role.capitalize()})",
                    font=("Roboto", 12), text_color="white").pack()
       
        # Menu Items based on role
        menu_items = []
        if self.current_role == "admin":
            menu_items = self.admin_menu
        elif self.current_role == "employee":
            menu_items = self.employee_menu
        else:
            menu_items = self.customer_menu
           
        for item in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=item, command=lambda i=item: self.navigate(i),
                                fg_color=self.primary_color, text_color="white",
                                hover_color="#544DC6", anchor="w")
            btn.pack(fill="x", pady=5, padx=10)

        # Logout Button
        logout_btn = ctk.CTkButton(self.sidebar, text="🚪 Logout", command=self.show_login_page,
                                  fg_color=self.danger_color, hover_color="#FF6666", text_color="white")
        logout_btn.pack(side="bottom", pady=20, padx=10, fill="x")

        self.content_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.content_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

        # Show appropriate dashboard content
        if hasattr(self, f"show_{self.current_role}_dashboard"):
            getattr(self, f"show_{self.current_role}_dashboard")()
        else:
            self.show_dashboard_content()
   
   
    def show_admin_dashboard(self):
        # Admin-specific dashboard
        ctk.CTkLabel(self.content_frame, text="Admin Dashboard", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Quick stats frame
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color=self.accent_color)
        stats_frame.pack(fill="x", padx=20, pady=10)
       
        # Get user counts from Firebase
        ref = db.reference('users')
        users = ref.get() or {}
       
        admin_count = sum(1 for user in users.values() if user.get('role') == 'admin')
        employee_count = sum(1 for user in users.values() if user.get('role') == 'employee')
        customer_count = sum(1 for user in users.values() if user.get('role') == 'customer')
        total_users = len(users)
       
        # Get product counts
        products_ref = db.reference('products')
        products = products_ref.get() or {}
        total_products = len(products)
        low_stock = sum(1 for p in products.values() if int(p.get('quantity', 0)) < 10)
       
        ctk.CTkLabel(stats_frame, text="System Statistics", font=("Roboto", 16, "bold")).pack(pady=10)
       
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=10)
       
        ctk.CTkLabel(stats_grid, text=f"Total Users: {total_users}", font=("Roboto", 14)).grid(row=0, column=0, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Admins: {admin_count}", font=("Roboto", 14)).grid(row=0, column=1, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Employees: {employee_count}", font=("Roboto", 14)).grid(row=1, column=0, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Customers: {customer_count}", font=("Roboto", 14)).grid(row=1, column=1, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Total Products: {total_products}", font=("Roboto", 14)).grid(row=2, column=0, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Low Stock Items: {low_stock}", font=("Roboto", 14)).grid(row=2, column=1, padx=20, pady=5)
       
        # Add user button for admin
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
       
        add_user_btn = ctk.CTkButton(btn_frame, text="+ Add New User", command=self.show_add_user_form,
                                    fg_color=self.primary_color, text_color="white")
        add_user_btn.pack(side="left", padx=5)
       
        add_employee_btn = ctk.CTkButton(btn_frame, text="+ Add Employee", command=self.show_add_employee_form,
                                       fg_color=self.success_color, text_color="white")
        add_employee_btn.pack(side="left", padx=5)
       
        # User table
        self.show_user_table()
   

    def show_employee_dashboard(self):
        # Employee-specific dashboard
        ctk.CTkLabel(self.content_frame, text="Employee Dashboard", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Quick stats frame
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color=self.accent_color)
        stats_frame.pack(fill="x", padx=20, pady=10)
       
        # Get data from Firebase
        ref = db.reference('users')
        users = ref.get() or {}
       
        customer_count = sum(1 for user in users.values() if user.get('role') == 'customer')
       
        # Get product counts
        products_ref = db.reference('products')
        products = products_ref.get() or {}
        total_products = len(products)
        low_stock = sum(1 for p in products.values() if int(p.get('quantity', 0)) < 10)
       
        ctk.CTkLabel(stats_frame, text="Your Statistics", font=("Roboto", 16, "bold")).pack(pady=10)
       
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=10)
       
        ctk.CTkLabel(stats_grid, text=f"Customers: {customer_count}", font=("Roboto", 14)).grid(row=0, column=0, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Designation: {self.current_user.get('designation', 'Employee')}",
                    font=("Roboto", 14)).grid(row=0, column=1, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Products: {total_products}", font=("Roboto", 14)).grid(row=1, column=0, padx=20, pady=5)
        ctk.CTkLabel(stats_grid, text=f"Low Stock: {low_stock}", font=("Roboto", 14)).grid(row=1, column=1, padx=20, pady=5)
       
        # Customer table
        self.show_customer_table()

    def show_customer_dashboard(self):
        # Customer-specific dashboard
        ctk.CTkLabel(self.content_frame, text=f"Welcome, {self.current_user.get('name', 'Customer')}",
                    font=("Roboto", 24, "bold"), text_color=self.text_color).pack(pady=20)
       
        # Profile info frame
        info_frame = ctk.CTkFrame(self.content_frame, fg_color=self.accent_color)
        info_frame.pack(fill="x", padx=20, pady=10)
       
        ctk.CTkLabel(info_frame, text="Your Profile Information", font=("Roboto", 16, "bold")).pack(pady=10)
       
        info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_grid.pack(pady=10)
       
        ctk.CTkLabel(info_grid, text=f"Username: {self.current_user.get('username', '')}",
                    font=("Roboto", 14)).grid(row=0, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(info_grid, text=f"Email: {self.current_user.get('email', '')}",
                    font=("Roboto", 14)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(info_grid, text=f"Phone: {self.current_user.get('phone', '')}",
                    font=("Roboto", 14)).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(info_grid, text=f"Address: {self.current_user.get('address', '')}",
                    font=("Roboto", 14)).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(info_grid, text=f"Member Since: {self.current_user.get('created_at', '')}",
                    font=("Roboto", 14)).grid(row=4, column=0, padx=20, pady=5, sticky="w")

        # Button frame for actions
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Add suggestion button
        suggestion_btn = ctk.CTkButton(button_frame, text="Submit Suggestion",
                                     command=self.show_suggestion_form,
                                     fg_color=self.primary_color,
                                     text_color="white")
        suggestion_btn.pack(side="left", padx=10)
        
        # Add voice bot button
        voice_bot_btn = ctk.CTkButton(button_frame, text="Voice Assistant",
                                     command=self.show_voice_bot,
                                     fg_color=self.primary_color,
                                     text_color="white")
        voice_bot_btn.pack(side="left", padx=10)

        # Show user's suggestions
        self.show_user_suggestions()

    def show_suggestion_form(self):
        # Create a new window for the suggestion form
        suggestion_window = ctk.CTkToplevel(self)
        suggestion_window.title("Submit Suggestion")
        suggestion_window.geometry("600x400")
        suggestion_window.resizable(False, False)

        # Title
        ctk.CTkLabel(suggestion_window, text="Submit Your Suggestion",
                    font=("Roboto", 20, "bold")).pack(pady=20)

        # Suggestion text area
        ctk.CTkLabel(suggestion_window, text="Your Suggestion:",
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w", padx=20)
       
        self.suggestion_text = ctk.CTkTextbox(suggestion_window, height=150)
        self.suggestion_text.pack(fill="x", padx=20, pady=5)

        # Submit button
        submit_btn = ctk.CTkButton(suggestion_window, text="Submit",
                                  command=lambda: self.save_suggestion(suggestion_window),
                                  fg_color=self.primary_color,
                                  text_color="white")
        submit_btn.pack(pady=20)

    def save_suggestion(self, window):
        suggestion_text = self.suggestion_text.get("1.0", "end-1c").strip()
       
        if not suggestion_text:
            messagebox.showerror("Error", "Please enter your suggestion")
            return

        # Save to Firebase
        ref = db.reference('suggestions')
        suggestion_data = {
            'user_id': self.current_user['id'],
            'username': self.current_user['username'],
            'user_name': self.current_user['name'],
            'suggestion': suggestion_text,
            'status': 'pending',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'admin_reply': ''
        }
       
        ref.push(suggestion_data)
        messagebox.showinfo("Success", "Your suggestion has been submitted successfully!")
        window.destroy()
        self.show_user_suggestions()

    def show_user_suggestions(self):
        # Create a frame for suggestions
        suggestions_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        suggestions_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(suggestions_frame, text="Your Suggestions",
                    font=("Roboto", 16, "bold")).pack(pady=10)

        # Get suggestions from Firebase
        ref = db.reference('suggestions')
        suggestions = ref.get() or {}
       
        # Filter suggestions for current user
        user_suggestions = {k: v for k, v in suggestions.items()
                          if v.get('user_id') == self.current_user['id']}

        if not user_suggestions:
            ctk.CTkLabel(suggestions_frame, text="No suggestions submitted yet",
                        font=("Roboto", 14)).pack(pady=10)
            return

        # Create a scrollable frame for suggestions
        scroll_frame = ctk.CTkScrollableFrame(suggestions_frame)
        scroll_frame.pack(fill="both", expand=True)

        for suggestion_id, suggestion_data in user_suggestions.items():
            suggestion_card = ctk.CTkFrame(scroll_frame, fg_color=self.accent_color)
            suggestion_card.pack(fill="x", pady=5, padx=10)

            # Suggestion text
            ctk.CTkLabel(suggestion_card, text=suggestion_data['suggestion'],
                        font=("Roboto", 14), wraplength=500).pack(pady=10, padx=10)

            # Status and date
            status_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
            status_frame.pack(fill="x", padx=10, pady=5)

            status_color = self.success_color if suggestion_data['status'] == 'replied' else self.danger_color
            ctk.CTkLabel(status_frame, text=f"Status: {suggestion_data['status'].capitalize()}",
                        font=("Roboto", 12), text_color=status_color).pack(side="left")

            ctk.CTkLabel(status_frame, text=f"Submitted: {suggestion_data['created_at']}",
                        font=("Roboto", 12)).pack(side="right")

            # Admin reply if available
            if suggestion_data.get('admin_reply'):
                reply_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
                reply_frame.pack(fill="x", padx=10, pady=5)
               
                ctk.CTkLabel(reply_frame, text="Admin Reply:",
                            font=("Roboto", 12, "bold")).pack(anchor="w")
                ctk.CTkLabel(reply_frame, text=suggestion_data['admin_reply'],
                            font=("Roboto", 12), wraplength=500).pack(anchor="w")

    def show_inventory_page(self):
        self.clear_content()
       
        ctk.CTkLabel(self.content_frame, text="Inventory Management", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Add product button
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
       
        add_btn = ctk.CTkButton(btn_frame, text="+ Add Product", command=self.show_add_product_form,
                               fg_color=self.success_color, text_color="white")
        add_btn.pack(side="left", padx=5)
       
        # Product table
        self.show_product_table()

    def show_add_product_form(self):
        self.clear_content()
       
        ctk.CTkLabel(self.content_frame, text="Add New Product", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        form_frame = ctk.CTkFrame(self.content_frame, fg_color=self.accent_color)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Form fields
        ctk.CTkLabel(form_frame, text="Product Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w", padx=20)
       
        self.product_name = ctk.CTkEntry(form_frame, placeholder_text="Product Name")
        self.product_name.pack(pady=5, padx=20, fill="x")
       
        self.product_description = ctk.CTkTextbox(form_frame, height=80)
        self.product_description.pack(pady=5, padx=20, fill="x")
       
        self.product_price = ctk.CTkEntry(form_frame, placeholder_text="Price")
        self.product_price.pack(pady=5, padx=20, fill="x")
       
        self.product_quantity = ctk.CTkEntry(form_frame, placeholder_text="Quantity")
        self.product_quantity.pack(pady=5, padx=20, fill="x")
       
        self.product_category = ctk.CTkEntry(form_frame, placeholder_text="Category")
        self.product_category.pack(pady=5, padx=20, fill="x")
       
        # Image upload
        ctk.CTkLabel(form_frame, text="Product Image", font=("Roboto", 14)).pack(pady=5, padx=20, anchor="w")
       
        self.product_image_path = None
        self.product_image_label = ctk.CTkLabel(form_frame, text="No image selected")
        self.product_image_label.pack(pady=5, padx=20, anchor="w")
       
        upload_btn = ctk.CTkButton(form_frame, text="Upload Image", command=self.upload_product_image)
        upload_btn.pack(pady=5, padx=20, anchor="w")
       
        # Save button
        save_btn = ctk.CTkButton(form_frame, text="Save Product", command=self.save_product,
                                fg_color=self.primary_color)
        save_btn.pack(pady=20, padx=20, fill="x")

    def upload_product_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.product_image_path = file_path
            self.product_image_label.configure(text=file_path.split("/")[-1])

    def save_product(self):
        # Validation
        if not all([self.product_name.get(), self.product_price.get(), self.product_quantity.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
           
        try:
            price = float(self.product_price.get())
            quantity = int(self.product_quantity.get())
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and quantity must be an integer")
            return
           
        # Prepare product data
        product_data = {
            'name': self.product_name.get(),
            'description': self.product_description.get("1.0", "end-1c"),
            'price': price,
            'quantity': quantity,
            'category': self.product_category.get(),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': self.current_user['username']
        }
       
        # Handle image upload if exists
        if self.product_image_path:
            try:
                with open(self.product_image_path, "rb") as image_file:
                    image_data = image_file.read()
                    product_data['image'] = image_data.hex()
            except:
                messagebox.showerror("Error", "Failed to read image file")
                return
       
        # Save to Firebase
        ref = db.reference('products')
        new_product_ref = ref.push(product_data)
       
        messagebox.showinfo("Success", "Product added successfully!")
        self.show_inventory_page()

    def show_product_table(self):
        # Create a frame for the table and search
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Search bar
        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
       
        self.product_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search products...", textvariable=self.product_search_var)
        search_entry.pack(side="left", fill="x", expand=True)
       
        search_btn = ctk.CTkButton(search_frame, text="Search", command=self.search_products, width=80)
        search_btn.pack(side="left", padx=5)
       
        # Treeview for product table
        self.product_tree = ttk.Treeview(table_frame, columns=("name", "price", "quantity", "category", "created_at"), show="headings")
       
        # Style the treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                       background="#FFFFFF",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading",
                       background=self.primary_color,
                       foreground="white",
                       font=('Roboto', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#E1E1E1')])
       
        # Configure columns
        self.product_tree.heading("name", text="Name")
        self.product_tree.heading("price", text="Price")
        self.product_tree.heading("quantity", text="Quantity")
        self.product_tree.heading("category", text="Category")
        self.product_tree.heading("created_at", text="Added On")
       
        self.product_tree.column("name", width=200)
        self.product_tree.column("price", width=100)
        self.product_tree.column("quantity", width=80)
        self.product_tree.column("category", width=120)
        self.product_tree.column("created_at", width=120)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
       
        self.product_tree.pack(fill="both", expand=True)
       
        # Action buttons frame
        action_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
       
        edit_btn = ctk.CTkButton(action_frame, text="Edit", command=self.edit_selected_product,
                                fg_color=self.primary_color, width=80)
        edit_btn.pack(side="left", padx=5)
       
        delete_btn = ctk.CTkButton(action_frame, text="Delete", command=self.delete_selected_product,
                                  fg_color=self.danger_color, width=80)
        delete_btn.pack(side="left", padx=5)
       
        view_btn = ctk.CTkButton(action_frame, text="View", command=self.view_product_details,
                                fg_color=self.success_color, width=80)
        view_btn.pack(side="left", padx=5)
       
        refresh_btn = ctk.CTkButton(action_frame, text="Refresh", command=self.load_product_data,
                                  fg_color=self.secondary_text, width=80)
        refresh_btn.pack(side="right", padx=5)
       
        # Load data from Firebase
        self.load_product_data()
       
        # Bind double click event
        self.product_tree.bind("<Double-1>", self.view_product_details)

    def load_product_data(self):
        # Clear existing data
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
           
        # Get data from Firebase
        ref = db.reference('products')
        products = ref.get() or {}
       
        # Add data to treeview
        for product_id, product_data in products.items():
            self.product_tree.insert("", "end",
                                   values=(
                                       product_data.get('name', ''),
                                       f"{self.company_settings['currency']} {product_data.get('price', 0):.2f}",
                                       product_data.get('quantity', 0),
                                       product_data.get('category', ''),
                                       product_data.get('created_at', '')
                                   ),
                                   tags=(product_id,))

    def search_products(self):
        query = self.product_search_var.get().lower()
       
        # Get all products from Firebase
        ref = db.reference('products')
        products = ref.get() or {}
       
        # Clear current data
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
           
        # Filter and add matching products
        for product_id, product_data in products.items():
            if (query in product_data.get('name', '').lower() or
                query in product_data.get('category', '').lower() or
                query in product_data.get('description', '').lower() or
                str(product_data.get('price', '')).lower().startswith(query)):
               
                self.product_tree.insert("", "end",
                                      values=(
                                          product_data.get('name', ''),
                                          f"{self.company_settings['currency']} {product_data.get('price', 0):.2f}",
                                          product_data.get('quantity', 0),
                                          product_data.get('category', ''),
                                          product_data.get('created_at', '')
                                      ),
                                      tags=(product_id,))

    def view_product_details(self, event=None):
        selected_item = self.product_tree.selection()
        if not selected_item:
            return
           
        product_id = self.product_tree.item(selected_item)['tags'][0]
       
        # Get product data from Firebase
        ref = db.reference(f'products/{product_id}')
        product_data = ref.get()
       
        # Create details window
        details_window = ctk.CTkToplevel(self)
        details_window.title("Product Details")
        details_window.geometry("600x500")
       
        # Details frame
        details_frame = ctk.CTkFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
       
        ctk.CTkLabel(details_frame, text="Product Details", font=("Roboto", 20, "bold")).pack(pady=10)
       
        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(details_frame)
        scroll_frame.pack(fill="both", expand=True)
       
        # Display image if available
        if 'image' in product_data:
            try:
                image_data = bytes.fromhex(product_data['image'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                image_label = ctk.CTkLabel(scroll_frame, text="", image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack(pady=10)
            except:
                pass
       
        details_text = f"""
Name: {product_data.get('name', 'N/A')}
Price: {self.company_settings['currency']} {product_data.get('price', 0):.2f}
Quantity: {product_data.get('quantity', 0)}
Category: {product_data.get('category', 'N/A')}
Added On: {product_data.get('created_at', 'N/A')}
Added By: {product_data.get('created_by', 'N/A')}

Description:
{product_data.get('description', 'No description available')}
        """
       
        ctk.CTkLabel(scroll_frame, text=details_text, justify="left", font=("Roboto", 14)).pack(pady=10, anchor="w")
       
        # Close button
        close_btn = ctk.CTkButton(details_frame, text="Close", command=details_window.destroy)
        close_btn.pack(pady=10)

    def edit_selected_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
           
        product_id = self.product_tree.item(selected_item)['tags'][0]
       
        # Get product data from Firebase
        ref = db.reference(f'products/{product_id}')
        product_data = ref.get()
       
        # Create edit window
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Product")
        edit_window.geometry("600x600")
       
        # Edit frame
        edit_frame = ctk.CTkFrame(edit_window)
        edit_frame.pack(fill="both", expand=True, padx=20, pady=20)
       
        ctk.CTkLabel(edit_frame, text="Edit Product", font=("Roboto", 20, "bold")).pack(pady=10)
       
        # Form fields
        self.edit_product_name = ctk.CTkEntry(edit_frame, placeholder_text="Product Name")
        self.edit_product_name.insert(0, product_data.get('name', ''))
        self.edit_product_name.pack(pady=5, fill="x")
       
        self.edit_product_description = ctk.CTkTextbox(edit_frame, height=80)
        self.edit_product_description.insert("1.0", product_data.get('description', ''))
        self.edit_product_description.pack(pady=5, fill="x")
       
        self.edit_product_price = ctk.CTkEntry(edit_frame, placeholder_text="Price")
        self.edit_product_price.insert(0, str(product_data.get('price', '')))
        self.edit_product_price.pack(pady=5, fill="x")
       
        self.edit_product_quantity = ctk.CTkEntry(edit_frame, placeholder_text="Quantity")
        self.edit_product_quantity.insert(0, str(product_data.get('quantity', '')))
        self.edit_product_quantity.pack(pady=5, fill="x")
       
        self.edit_product_category = ctk.CTkEntry(edit_frame, placeholder_text="Category")
        self.edit_product_category.insert(0, product_data.get('category', ''))
        self.edit_product_category.pack(pady=5, fill="x")
       
        # Image section
        self.edit_product_image_path = None
        self.edit_product_image_label = ctk.CTkLabel(edit_frame, text="Current image will be kept" if 'image' in product_data else "No image available")
        self.edit_product_image_label.pack(pady=5)
       
        upload_btn = ctk.CTkButton(edit_frame, text="Change Image", command=self.edit_upload_product_image)
        upload_btn.pack(pady=5)
       
        # Save button
        save_btn = ctk.CTkButton(edit_frame, text="Save Changes",
                                command=lambda: self.save_product_changes(product_id, edit_window),
                                fg_color=self.primary_color)
        save_btn.pack(pady=10, fill="x")

    def edit_upload_product_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.edit_product_image_path = file_path
            self.edit_product_image_label.configure(text=file_path.split("/")[-1])

    def save_product_changes(self, product_id, window):
        # Validation
        if not all([self.edit_product_name.get(), self.edit_product_price.get(), self.edit_product_quantity.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
           
        try:
            price = float(self.edit_product_price.get())
            quantity = int(self.edit_product_quantity.get())
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and quantity must be an integer")
            return
           
        # Prepare update data
        update_data = {
            'name': self.edit_product_name.get(),
            'description': self.edit_product_description.get("1.0", "end-1c"),
            'price': price,
            'quantity': quantity,
            'category': self.edit_product_category.get(),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
       
        # Handle image upload if exists
        if self.edit_product_image_path:
            try:
                with open(self.edit_product_image_path, "rb") as image_file:
                    image_data = image_file.read()
                    update_data['image'] = image_data.hex()
            except:
                messagebox.showerror("Error", "Failed to read image file")
                return
       
        # Update in Firebase
        ref = db.reference(f'products/{product_id}')
        ref.update(update_data)
       
        messagebox.showinfo("Success", "Product updated successfully!")
        window.destroy()
        self.load_product_data()

    def delete_selected_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
           
        product_id = self.product_tree.item(selected_item)['tags'][0]
       
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            return
           
        # Delete from Firebase
        ref = db.reference(f'products/{product_id}')
        ref.delete()
       
        messagebox.showinfo("Success", "Product deleted successfully!")
        self.load_product_data()

    def show_billing_page(self):
        self.clear_content()
       
        # Main title
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(title_frame, text="Billing System", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(side="left")
       
        # Create a scrollable frame for the form
        scrollable_frame = ctk.CTkScrollableFrame(self.content_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)
       
        # Form frame inside scrollable area
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
       
        # Customer Information Section
        customer_section = ctk.CTkFrame(form_frame, fg_color=self.accent_color)
        customer_section.pack(fill="x", padx=5, pady=5)
       
        ctk.CTkLabel(customer_section, text="Customer Information",
                    font=("Roboto", 16, "bold")).pack(pady=5, anchor="w", padx=10)
       
        # Customer dropdown
        customer_row = ctk.CTkFrame(customer_section, fg_color="transparent")
        customer_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(customer_row, text="Customer:", width=100).pack(side="left")
       
        self.customer_var = ctk.StringVar()
        self.customer_dropdown = ctk.CTkComboBox(customer_row,
                                               variable=self.customer_var,
                                               dropdown_fg_color="white",
                                               dropdown_text_color="black")
        self.customer_dropdown.pack(side="left", fill="x", expand=True, padx=5)
        self.load_customers_for_billing()
       
        # Invoice Details Section
        invoice_section = ctk.CTkFrame(form_frame, fg_color=self.accent_color)
        invoice_section.pack(fill="x", padx=5, pady=5)
       
        ctk.CTkLabel(invoice_section, text="Invoice Details",
                    font=("Roboto", 16, "bold")).pack(pady=5, anchor="w", padx=10)
       
        # Invoice number
        inv_num_row = ctk.CTkFrame(invoice_section, fg_color="transparent")
        inv_num_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(inv_num_row, text="Invoice #:", width=100).pack(side="left")
       
        self.invoice_number = ctk.CTkEntry(inv_num_row)
        self.invoice_number.insert(0, str(uuid.uuid4().int)[:6])
        self.invoice_number.pack(side="left", fill="x", expand=True, padx=5)
       
        # Invoice date
        inv_date_row = ctk.CTkFrame(invoice_section, fg_color="transparent")
        inv_date_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(inv_date_row, text="Date:", width=100).pack(side="left")
       
        self.invoice_date = ctk.CTkEntry(inv_date_row)
        self.invoice_date.insert(0, datetime.now().strftime("%b %d, %Y"))
        self.invoice_date.pack(side="left", fill="x", expand=True, padx=5)
       
        # Due date
        due_date_row = ctk.CTkFrame(invoice_section, fg_color="transparent")
        due_date_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(due_date_row, text="Due Date:", width=100).pack(side="left")
       
        self.due_date = ctk.CTkEntry(due_date_row)
        self.due_date.insert(0, (datetime.now() + timedelta(days=30)).strftime("%b %d, %Y"))
        self.due_date.pack(side="left", fill="x", expand=True, padx=5)
       
        # Products Section
        products_section = ctk.CTkFrame(form_frame, fg_color=self.accent_color)
        products_section.pack(fill="x", padx=5, pady=5)
       
        ctk.CTkLabel(products_section, text="Add Products",
                    font=("Roboto", 16, "bold")).pack(pady=5, anchor="w", padx=10)
       
        # Product selection
        product_row = ctk.CTkFrame(products_section, fg_color="transparent")
        product_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(product_row, text="Product:", width=100).pack(side="left")
       
        self.product_var = ctk.StringVar()
        self.product_dropdown = ctk.CTkComboBox(product_row,
                                              variable=self.product_var,
                                              dropdown_fg_color="white",
                                              dropdown_text_color="black")
        self.product_dropdown.pack(side="left", fill="x", expand=True, padx=5)
        self.load_products_for_billing()
       
        # Quantity
        qty_row = ctk.CTkFrame(products_section, fg_color="transparent")
        qty_row.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(qty_row, text="Quantity:", width=100).pack(side="left")
       
        self.product_quantity_entry = ctk.CTkEntry(qty_row)
        self.product_quantity_entry.insert(0, "1")
        self.product_quantity_entry.pack(side="left", fill="x", expand=True, padx=5)
       
        add_btn = ctk.CTkButton(qty_row, text="Add to Invoice",
                               width=120, command=self.add_product_to_invoice)
        add_btn.pack(side="left", padx=10)
       
        # Invoice Items Table Section
        items_section = ctk.CTkFrame(form_frame, fg_color=self.accent_color)
        items_section.pack(fill="both", expand=True, padx=5, pady=5)
       
        ctk.CTkLabel(items_section, text="Invoice Items",
                    font=("Roboto", 16, "bold")).pack(pady=5, anchor="w", padx=10)
       
        # Table container with scrollbar
        table_container = ctk.CTkFrame(items_section, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=5)
       
        # Create the treeview with columns
        self.invoice_items_table = ttk.Treeview(
            table_container,
            columns=("product", "quantity", "price", "total"),
            show="headings",
            height=5,  # Show 5 rows by default
            selectmode="browse"
        )
       
        # Style configuration
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                      background="#FFFFFF",
                      foreground="black",
                      rowheight=25,
                      fieldbackground="#FFFFFF",
                      bordercolor="#DDDDDD",
                      borderwidth=1)
        style.configure("Treeview.Heading",
                      background=self.primary_color,
                      foreground="white",
                      font=('Roboto', 10, 'bold'),
                      relief="flat")
        style.map("Treeview",
                 background=[('selected', '#E1E1E1')],
                 foreground=[('selected', 'black')])
       
        # Configure columns
        columns = {
            "product": {"text": "Product", "width": 250, "anchor": "w"},
            "quantity": {"text": "Qty", "width": 80, "anchor": "center"},
            "price": {"text": "Price", "width": 100, "anchor": "e"},
            "total": {"text": "Total", "width": 100, "anchor": "e"}
        }
       
        for col, config in columns.items():
            self.invoice_items_table.heading(col, text=config["text"])
            self.invoice_items_table.column(col, width=config["width"], anchor=config["anchor"])
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.invoice_items_table.yview)
        self.invoice_items_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.invoice_items_table.pack(fill="both", expand=True)
       
        # Table action buttons
        action_frame = ctk.CTkFrame(items_section, fg_color="transparent")
        action_frame.pack(fill="x", pady=5, padx=10)
       
        remove_btn = ctk.CTkButton(action_frame, text="Remove Selected",
                                  width=120, command=self.remove_selected_item)
        remove_btn.pack(side="left", padx=5)
       
        clear_btn = ctk.CTkButton(action_frame, text="Clear All",
                                 width=120, command=self.clear_invoice_items)
        clear_btn.pack(side="left", padx=5)
       
        # Summary Section
        summary_section = ctk.CTkFrame(form_frame, fg_color=self.accent_color)
        summary_section.pack(fill="x", padx=5, pady=5)
       
        summary_frame = ctk.CTkFrame(summary_section, fg_color="transparent")
        summary_frame.pack(fill="x", padx=10, pady=10)
       
        # Subtotal
        ctk.CTkLabel(summary_frame, text="Subtotal:",
                    font=("Roboto", 14), width=100).pack(side="left")
        self.subtotal_label = ctk.CTkLabel(summary_frame,
                                         text=f"{self.company_settings['currency']} 0.00",
                                         font=("Roboto", 14, "bold"))
        self.subtotal_label.pack(side="left", padx=10)
       
        # Tax
        ctk.CTkLabel(summary_frame, text=f"Tax ({self.company_settings['tax_rate']}%):",
                    font=("Roboto", 14), width=100).pack(side="left", padx=(20, 0))
        self.tax_label = ctk.CTkLabel(summary_frame,
                                    text=f"{self.company_settings['currency']} 0.00",
                                    font=("Roboto", 14, "bold"))
        self.tax_label.pack(side="left", padx=10)
       
        # Total
        ctk.CTkLabel(summary_frame, text="Total:",
                    font=("Roboto", 14), width=100).pack(side="left", padx=(20, 0))
        self.total_label = ctk.CTkLabel(summary_frame,
                                      text=f"{self.company_settings['currency']} 0.00",
                                      font=("Roboto", 14, "bold"))
        self.total_label.pack(side="left", padx=10)
       
        # Generate Invoice Button (outside scrollable frame)
        generate_btn = ctk.CTkButton(self.content_frame,
                                    text="Generate Invoice",
                                    fg_color=self.success_color,
                                    text_color="white",
                                    font=("Roboto", 14, "bold"),
                                    height=40,
                                    command=self.generate_invoice_pdf)
        generate_btn.pack(fill="x", padx=20, pady=10)
       
        # Initialize invoice items
        self.invoice_items = []

    def load_customers_for_billing(self):
        ref = db.reference('users')
        users = ref.get() or {}
       
        customers = []
        for user_id, user_data in users.items():
            if user_data.get('role') == 'customer':
                customers.append(f"{user_data.get('name', '')} ({user_data.get('email', '')})")
       
        self.customer_dropdown.configure(values=customers)
        if customers:
            self.customer_var.set(customers[0])

    def load_products_for_billing(self):
        ref = db.reference('products')
        products = ref.get() or {}
       
        product_list = []
        for product_id, product_data in products.items():
            product_list.append(f"{product_data.get('name', '')} - {self.company_settings['currency']} {product_data.get('price', 0):.2f}")
       
        self.product_dropdown.configure(values=product_list)
        if product_list:
            self.product_var.set(product_list[0])

    def add_product_to_invoice(self):
        product_str = self.product_var.get()
        if not product_str:
            messagebox.showwarning("Warning", "Please select a product")
            return
           
        try:
            quantity = int(self.product_quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity (positive integer)")
            return
           
        # Extract product name and price from the dropdown string
        product_name = product_str.split(" - ")[0]
        price_str = product_str.split(" - ")[1].replace(self.company_settings['currency'], "").strip()
        price = float(price_str)
       
        # Check if product already in invoice
        for item in self.invoice_items:
            if item['name'] == product_name:
                item['quantity'] += quantity
                item['total'] = item['quantity'] * item['price']
                self.update_invoice_items_table()
                self.update_invoice_totals()
                return
               
        # Add new item
        self.invoice_items.append({
            'name': product_name,
            'quantity': quantity,
            'price': price,
            'total': quantity * price
        })
       
        self.update_invoice_items_table()
        self.update_invoice_totals()

    def update_invoice_items_table(self):
        # Clear existing items
        for item in self.invoice_items_table.get_children():
            self.invoice_items_table.delete(item)
           
        # Add current items
        for item in self.invoice_items:
            self.invoice_items_table.insert("", "end",
                                          values=(
                                              item['name'],
                                              item['quantity'],
                                              f"{self.company_settings['currency']} {item['price']:.2f}",
                                              f"{self.company_settings['currency']} {item['total']:.2f}"
                                          ))

    def update_invoice_totals(self):
        subtotal = sum(item['total'] for item in self.invoice_items)
        tax = subtotal * (self.company_settings['tax_rate'] / 100)
        total = subtotal + tax
       
        self.subtotal_label.configure(text=f"{self.company_settings['currency']} {subtotal:.2f}")
        self.tax_label.configure(text=f"{self.company_settings['currency']} {tax:.2f}")
        self.total_label.configure(text=f"{self.company_settings['currency']} {total:.2f}")

    def remove_selected_item(self):
        selected_item = self.invoice_items_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
           
        selected_index = self.invoice_items_table.index(selected_item[0])
        if 0 <= selected_index < len(self.invoice_items):
            self.invoice_items.pop(selected_index)
            self.update_invoice_items_table()
            self.update_invoice_totals()

    def clear_invoice_items(self):
        if not self.invoice_items:
            return
           
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all items from the invoice?"):
            self.invoice_items = []
            self.update_invoice_items_table()
            self.update_invoice_totals()

    def generate_invoice_pdf(self):
        if not self.invoice_items:
            messagebox.showerror("Error", "Cannot generate an empty invoice")
            return

        customer_str = self.customer_var.get()
        if not customer_str:
            messagebox.showerror("Error", "Please select a customer")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Roboto", size=12)

        # --- Add logo ---
        if self.company_logo:
            try:
                temp_logo_path = "images.jpg"
                with open(temp_logo_path, "wb") as logo_file:
                    logo_file.write(bytes.fromhex(self.company_logo))
                pdf.image(temp_logo_path, x=10, y=10, w=40)  # Adjusted width
                os.remove(temp_logo_path)
            except Exception as e:
                print(f"[ERROR] Failed to load logo: {e}")
                messagebox.showwarning("Logo Error", f"Could not add company logo.\n{e}")

        # --- Company Info ---
        pdf.set_font("Roboto", 'B', 16)
        pdf.cell(0, 10, self.company_settings['name'], ln=1, align='R')
        pdf.set_font("Roboto", size=12)
        pdf.cell(0, 7, self.company_settings['address'], ln=1, align='R')
        pdf.cell(0, 7, f"Phone: {self.company_settings['phone']}", ln=1, align='R')
        pdf.cell(0, 7, f"Email: {self.company_settings['email']}", ln=1, align='R')
        pdf.cell(0, 7, f"Website: {self.company_settings['website']}", ln=1, align='R')

        # --- Title ---
        pdf.ln(20)
        pdf.set_font("Roboto", 'B', 24)
        pdf.cell(0, 10, "INVOICE", ln=1, align='C')

        # --- From/To ---
        pdf.ln(10)
        pdf.set_font("Roboto", size=12)
        pdf.cell(95, 7, "From:", ln=0)
        pdf.cell(95, 7, "Bill To:", ln=1)

        pdf.set_font("Roboto", 'B', 12)
        pdf.cell(95, 7, self.company_settings['name'], ln=0)
        customer_name = customer_str.split(" (")[0]
        pdf.cell(95, 7, customer_name, ln=1)

        pdf.set_font("Roboto", size=12)
        pdf.cell(95, 7, self.company_settings['address'], ln=0)
        pdf.cell(95, 7, "Customer Address", ln=1)

        pdf.cell(95, 7, f"Phone: {self.company_settings['phone']}", ln=0)
        pdf.cell(95, 7, "Customer Phone", ln=1)

        # --- Invoice Info ---
        pdf.ln(10)
        pdf.cell(95, 7, f"Invoice #: {self.invoice_number.get()}", ln=0)
        pdf.cell(95, 7, f"Date: {self.invoice_date.get()}", ln=1)
        pdf.cell(95, 7, f"Due Date: {self.due_date.get()}", ln=1)

        # --- Items Header ---
        pdf.ln(15)
        pdf.set_font("Roboto", 'B', 12)
        pdf.cell(100, 10, "Description", border=1)
        pdf.cell(30, 10, "Qty", border=1, align='C')
        pdf.cell(30, 10, "Rate", border=1, align='R')
        pdf.cell(30, 10, "Amount", border=1, align='R', ln=1)

        # --- Items ---
        pdf.set_font("Roboto", size=12)
        subtotal = 0
        for item in self.invoice_items:
            pdf.cell(100, 10, item['name'], border=1)
            pdf.cell(30, 10, str(item['quantity']), border=1, align='C')
            pdf.cell(30, 10, f"{self.company_settings['currency']} {item['price']:.2f}", border=1, align='R')
            pdf.cell(30, 10, f"{self.company_settings['currency']} {item['total']:.2f}", border=1, align='R', ln=1)
            subtotal += item['total']

        # --- Summary ---
        tax = subtotal * (self.company_settings['tax_rate'] / 100)
        total = subtotal + tax

        pdf.cell(160, 10, "Subtotal:", border=1, align='R')
        pdf.cell(30, 10, f"{self.company_settings['currency']} {subtotal:.2f}", border=1, align='R', ln=1)

        pdf.cell(160, 10, f"Tax ({self.company_settings['tax_rate']}%):", border=1, align='R')
        pdf.cell(30, 10, f"{self.company_settings['currency']} {tax:.2f}", border=1, align='R', ln=1)

        pdf.set_font("Roboto", 'B', 12)
        pdf.cell(160, 10, "Total:", border=1, align='R')
        pdf.cell(30, 10, f"{self.company_settings['currency']} {total:.2f}", border=1, align='R', ln=1)

        # --- Payment Instructions ---
        pdf.ln(15)
        pdf.set_font("Roboto", 'B', 12)
        pdf.cell(0, 10, "Payment Instructions:", ln=1)

        pdf.set_font("Roboto", size=12)
        pdf.cell(0, 7, "Make checks payable to: " + self.company_settings['name'], ln=1)
        pdf.cell(0, 7, "Bank Transfer:", ln=1)
        pdf.cell(0, 7, "Account Name: " + self.company_settings['name'], ln=1)
        pdf.cell(0, 7, "Account Number: XXXX-XXXX-XXXX", ln=1)
        pdf.cell(0, 7, "Routing: 061120084", ln=1)

        # --- Notes ---
        pdf.ln(10)
        pdf.set_font("Roboto", 'B', 12)
        pdf.cell(0, 10, "Notes:", ln=1)
        pdf.set_font("Roboto", size=12)
        pdf.multi_cell(0, 7, "Thank you for your business. Please make payment by the due date to avoid late fees.")

        # --- Signature ---
        if self.company_signature:
            try:
                temp_sign_path = "images (1).png"
                with open(temp_sign_path, "wb") as sign_file:
                    sign_file.write(bytes.fromhex(self.company_signature))
                y_position = pdf.get_y() + 10
                pdf.image(temp_sign_path, x=160, y=y_position, w=30)
                os.remove(temp_sign_path)

                pdf.set_y(y_position + 20)
                pdf.cell(0, 7, "Authorized Signature", ln=1, align='R')
            except Exception as e:
                print(f"[ERROR] Failed to load signature: {e}")
                messagebox.showwarning("Signature Error", f"Could not add signature.\n{e}")

        # --- Save PDF ---
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Invoice_{self.invoice_number.get()}.pdf"
        )

        if file_path:
            pdf.output(file_path)
            self.update_inventory_quantities()
            self.save_invoice_to_db(file_path)
            if messagebox.askyesno("Success", "Invoice generated successfully! Would you like to open it now?"):
                webbrowser.open(file_path)
            self.clear_invoice_items()

    def update_inventory_quantities(self):
        ref = db.reference('products')
        products = ref.get() or {}
       
        for item in self.invoice_items:
            for product_id, product_data in products.items():
                if product_data.get('name') == item['name']:
                    new_quantity = int(product_data.get('quantity', 0)) - item['quantity']
                    if new_quantity < 0:
                        new_quantity = 0
                    ref.child(product_id).update({'quantity': new_quantity})
                    break

    def save_invoice_to_db(self, file_path):
        invoice_data = {
            'invoice_number': self.invoice_number.get(),
            'customer': self.customer_var.get(),
            'date': self.invoice_date.get(),
            'due_date': self.due_date.get(),
            'items': self.invoice_items,
            'subtotal': sum(item['total'] for item in self.invoice_items),
            'tax': self.company_settings['tax_rate'],
            'total': sum(item['total'] for item in self.invoice_items) * (1 + self.company_settings['tax_rate'] / 100),
            'created_by': self.current_user['username'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'pdf_path': file_path
        }
       
        ref = db.reference('invoices')
        ref.push(invoice_data)

    def show_customer_products_page(self):
        self.clear_content()
       
        # Create a container frame for the entire products page
        self.products_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.products_container.pack(fill="both", expand=True, padx=20, pady=20)
       
        # Title frame
        title_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
       
        ctk.CTkLabel(title_frame, text="Our Products", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(side="left")
       
        # Search and filter frame
        search_filter_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        search_filter_frame.pack(fill="x", pady=10)
       
        # Search bar
        self.customer_product_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_filter_frame,
                                  placeholder_text="Search products...",
                                  textvariable=self.customer_product_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_filter_frame,
                                  text="Search",
                                  command=self.search_customer_products,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Category filter
        ctk.CTkLabel(search_filter_frame,
                    text="Filter by Category:",
                    font=("Roboto", 14)).pack(side="left", padx=(0, 10))
       
        self.category_filter_var = ctk.StringVar(value="All")
        self.category_dropdown = ctk.CTkComboBox(search_filter_frame,
                                               variable=self.category_filter_var,
                                               width=150)
        self.category_dropdown.pack(side="left")
       
        # Load categories
        self.load_product_categories()
       
        # Create a scrollable frame for products
        self.products_scroll_frame = ctk.CTkScrollableFrame(self.products_container, fg_color="transparent")
        self.products_scroll_frame.pack(fill="both", expand=True)
       
        # Create a frame for the product grid
        self.products_grid_frame = ctk.CTkFrame(self.products_scroll_frame, fg_color="transparent")
        self.products_grid_frame.pack(fill="both", expand=True)
       
        # Load products
        self.load_customer_products()

    def load_product_categories(self):
        ref = db.reference('products')
        products = ref.get() or {}
       
        categories = set()
        for product_data in products.values():
            if 'category' in product_data and product_data['category']:
                categories.add(product_data['category'])
       
        category_list = ["All"] + sorted(list(categories))
        self.category_dropdown.configure(values=category_list)

    def load_customer_products(self):
        # Clear existing products
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()
           
        # Get data from Firebase
        ref = db.reference('products')
        products = ref.get() or {}
       
        # Filter by category if needed
        selected_category = self.category_filter_var.get()
        if selected_category != "All":
            products = {k: v for k, v in products.items()
                       if v.get('category') == selected_category}
       
        # Apply search filter if any
        search_query = self.customer_product_search_var.get().lower()
        if search_query:
            products = {k: v for k, v in products.items()
                       if (search_query in v.get('name', '').lower() or
                           search_query in v.get('description', '').lower() or
                           search_query in v.get('category', '').lower())}
       
        # Display products in a grid
        row, col = 0, 0
        for product_id, product_data in products.items():
            # Create a card for each product
            product_card = ctk.CTkFrame(self.products_grid_frame,
                                      width=200,
                                      height=300,
                                      border_width=1,
                                      border_color="#DDDDDD",
                                      corner_radius=10)
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            product_card.grid_propagate(False)
           
            # Configure grid to center the cards
            self.products_grid_frame.grid_columnconfigure(col, weight=1)
           
            # Display image if available
            image_frame = ctk.CTkFrame(product_card, fg_color="transparent", height=150)
            image_frame.pack(fill="x", pady=(10, 5), padx=10)
           
            if 'image' in product_data:
                try:
                    image_data = bytes.fromhex(product_data['image'])
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((180, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                   
                    image_label = ctk.CTkLabel(image_frame, text="", image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack()
                except Exception as e:
                    # If image fails to load, show a placeholder
                    ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
            else:
                ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
           
            # Product name
            name_label = ctk.CTkLabel(product_card,
                                    text=product_data.get('name', 'Product'),
                                    font=("Roboto", 14, "bold"),
                                    wraplength=180)
            name_label.pack(pady=(5, 0))
           
            # Price
            price_label = ctk.CTkLabel(product_card,
                                     text=f"{self.company_settings['currency']} {product_data.get('price', 0):.2f}",
                                     font=("Roboto", 12, "bold"),
                                     text_color=self.primary_color)
            price_label.pack(pady=2)
           
            # View details button
            view_btn = ctk.CTkButton(product_card,
                                    text="View Details",
                                    command=lambda pid=product_id: self.show_product_details(pid),
                                    width=120,
                                    fg_color=self.primary_color)
            view_btn.pack(pady=10)
           
            col += 1
            if col > 3:  # 4 products per row
                col = 0
                row += 1

    def show_product_details(self, product_id):
        # Clear the products grid to show details
        for widget in self.products_container.winfo_children():
            widget.destroy()
       
        # Create a back button frame
        back_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        back_frame.pack(fill="x", pady=(0, 10))
       
        back_btn = ctk.CTkButton(back_frame,
                                text="← Back to Products",
                                command=self.back_to_products_list,
                                fg_color="transparent",
                                text_color=self.primary_color,
                                hover_color=self.accent_color)
        back_btn.pack(side="left", anchor="w")
       
        # Create details frame
        details_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Get product data from Firebase
        ref = db.reference(f'products/{product_id}')
        product_data = ref.get()
       
        # Create a scrollable frame for details
        scroll_frame = ctk.CTkScrollableFrame(details_frame)
        scroll_frame.pack(fill="both", expand=True)
       
        # Main content frame
        content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Product image (larger)
        image_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        image_frame.pack(fill="x", pady=(0, 20))
       
        if 'image' in product_data:
            try:
                image_data = bytes.fromhex(product_data['image'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                image_label = ctk.CTkLabel(image_frame, text="", image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack()
            except:
                ctk.CTkLabel(image_frame, text="No Image Available", height=300,
                            font=("Roboto", 14)).pack()
        else:
            ctk.CTkLabel(image_frame, text="No Image Available", height=300,
                        font=("Roboto", 14)).pack()
       
        # Product details container
        details_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_container.pack(fill="both", expand=True)
       
        # Product name (large and bold)
        ctk.CTkLabel(details_container,
                    text=product_data.get('name', 'N/A'),
                    font=("Roboto", 24, "bold"),
                    anchor="w").pack(fill="x", pady=(0, 10))
       
        # Price (highlighted)
        price_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        price_frame.pack(fill="x", pady=(0, 15))
       
        ctk.CTkLabel(price_frame,
                    text="Price:",
                    font=("Roboto", 18)).pack(side="left")
       
        ctk.CTkLabel(price_frame,
                    text=f"{self.company_settings['currency']} {product_data.get('price', 0):.2f}",
                    font=("Roboto", 18, "bold"),
                    text_color=self.primary_color).pack(side="left", padx=5)
       
        # Key details in a grid
        details_grid = ctk.CTkFrame(details_container, fg_color="transparent")
        details_grid.pack(fill="x", pady=(0, 20))
       
        # Availability
        availability_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        availability_frame.grid(row=0, column=0, padx=(0, 20), sticky="w")
       
        ctk.CTkLabel(availability_frame,
                    text="Availability:",
                    font=("Roboto", 14, "bold")).pack(anchor="w")
       
        stock_status = "In Stock" if int(product_data.get('quantity', 0)) > 0 else "Out of Stock"
        stock_color = self.success_color if int(product_data.get('quantity', 0)) > 0 else self.danger_color
       
        ctk.CTkLabel(availability_frame,
                    text=f"{stock_status} ({product_data.get('quantity', 0)} available)",
                    font=("Roboto", 14),
                    text_color=stock_color).pack(anchor="w")
       
        # Category
        category_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        category_frame.grid(row=0, column=1, sticky="w")
       
        ctk.CTkLabel(category_frame,
                    text="Category:",
                    font=("Roboto", 14, "bold")).pack(anchor="w")
       
        ctk.CTkLabel(category_frame,
                    text=product_data.get('category', 'N/A'),
                    font=("Roboto", 14)).pack(anchor="w")
       
        # Added date
        date_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        date_frame.grid(row=1, column=0, padx=(0, 20), pady=(10, 0), sticky="w")
       
        ctk.CTkLabel(date_frame,
                    text="Added On:",
                    font=("Roboto", 14, "bold")).pack(anchor="w")
       
        ctk.CTkLabel(date_frame,
                    text=product_data.get('created_at', 'N/A'),
                    font=("Roboto", 14)).pack(anchor="w")
       
        # Added by
        added_by_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        added_by_frame.grid(row=1, column=1, pady=(10, 0), sticky="w")
       
        ctk.CTkLabel(added_by_frame,
                    text="Added By:",
                    font=("Roboto", 14, "bold")).pack(anchor="w")
       
        ctk.CTkLabel(added_by_frame,
                    text=product_data.get('created_by', 'N/A'),
                    font=("Roboto", 14)).pack(anchor="w")
       
        # Description section
        desc_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(20, 0))
       
        ctk.CTkLabel(desc_frame,
                    text="Description",
                    font=("Roboto", 18, "bold")).pack(anchor="w", pady=(0, 10))
       
        desc_text = product_data.get('description', 'No description available')
        desc_label = ctk.CTkLabel(desc_frame,
                                 text=desc_text,
                                 font=("Roboto", 14),
                                 wraplength=600,
                                 justify="left",
                                 anchor="w")
        desc_label.pack(fill="x")

    def back_to_products_list(self):
        # Clear the details view and show the products grid again
        for widget in self.products_container.winfo_children():
            widget.destroy()
       
        # Recreate the products view
        title_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
       
        ctk.CTkLabel(title_frame, text="Our Products", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(side="left")
       
        # Search and filter frame
        search_filter_frame = ctk.CTkFrame(self.products_container, fg_color="transparent")
        search_filter_frame.pack(fill="x", pady=10)
       
        # Search bar
        search_entry = ctk.CTkEntry(search_filter_frame,
                                  placeholder_text="Search products...",
                                  textvariable=self.customer_product_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_filter_frame,
                                  text="Search",
                                  command=self.search_customer_products,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Category filter
        ctk.CTkLabel(search_filter_frame,
                    text="Filter by Category:",
                    font=("Roboto", 14)).pack(side="left", padx=(0, 10))
       
        self.category_dropdown.pack(side="left")
       
        # Create a scrollable frame for products
        self.products_scroll_frame = ctk.CTkScrollableFrame(self.products_container, fg_color="transparent")
        self.products_scroll_frame.pack(fill="both", expand=True)
       
        # Create a frame for the product grid
        self.products_grid_frame = ctk.CTkFrame(self.products_scroll_frame, fg_color="transparent")
        self.products_grid_frame.pack(fill="both", expand=True)
       
        # Load products
        self.load_customer_products()

    def search_customer_products(self):
        self.load_customer_products()

    def show_settings_page(self):
        self.clear_content()
       
        ctk.CTkLabel(self.content_frame, text="Settings", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Create tabs for different settings
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Add tabs based on user role
        if self.current_role == "admin":
            tabview.add("General")
            tabview.add("Logo & Signature")
            tabview.add("Invoice Settings")
            tabview.add("Profile")
        else:
            tabview.add("Profile")
       
        # Profile Settings Tab (for all users)
        profile_frame = tabview.tab("Profile")
       
        ctk.CTkLabel(profile_frame, text="Profile Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
       
        # Name
        ctk.CTkLabel(profile_frame, text="Full Name:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_name = ctk.CTkEntry(profile_frame)
        self.profile_name.insert(0, self.current_user.get('name', ''))
        self.profile_name.pack(fill="x", pady=5)
       
        # Email
        ctk.CTkLabel(profile_frame, text="Email:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_email = ctk.CTkEntry(profile_frame)
        self.profile_email.insert(0, self.current_user.get('email', ''))
        self.profile_email.pack(fill="x", pady=5)
       
        # Phone
        ctk.CTkLabel(profile_frame, text="Phone:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_phone = ctk.CTkEntry(profile_frame)
        self.profile_phone.insert(0, self.current_user.get('phone', ''))
        self.profile_phone.pack(fill="x", pady=5)
       
        # Address
        ctk.CTkLabel(profile_frame, text="Address:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_address = ctk.CTkEntry(profile_frame)
        self.profile_address.insert(0, self.current_user.get('address', ''))
        self.profile_address.pack(fill="x", pady=5)
       
        # Password
        ctk.CTkLabel(profile_frame, text="New Password (leave blank to keep current):", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_password = ctk.CTkEntry(profile_frame, show="*")
        self.profile_password.pack(fill="x", pady=5)
       
        # Confirm Password
        ctk.CTkLabel(profile_frame, text="Confirm New Password:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.profile_confirm_password = ctk.CTkEntry(profile_frame, show="*")
        self.profile_confirm_password.pack(fill="x", pady=5)
       
        # Save Profile button
        save_profile_btn = ctk.CTkButton(profile_frame, text="Save Profile", command=self.save_profile_changes,
                                       fg_color=self.primary_color)
        save_profile_btn.pack(pady=20, fill="x")
       
        # Admin-specific settings
        if self.current_role == "admin":
            # General Settings Tab
            general_frame = tabview.tab("General")
           
            ctk.CTkLabel(general_frame, text="Company Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
           
            self.company_name_entry = ctk.CTkEntry(general_frame, placeholder_text="Company Name")
            self.company_name_entry.insert(0, self.company_settings['name'])
            self.company_name_entry.pack(pady=5, fill="x")
           
            self.company_address_entry = ctk.CTkEntry(general_frame, placeholder_text="Address")
            self.company_address_entry.insert(0, self.company_settings['address'])
            self.company_address_entry.pack(pady=5, fill="x")
           
            self.company_phone_entry = ctk.CTkEntry(general_frame, placeholder_text="Phone")
            self.company_phone_entry.insert(0, self.company_settings['phone'])
            self.company_phone_entry.pack(pady=5, fill="x")
           
            self.company_email_entry = ctk.CTkEntry(general_frame, placeholder_text="Email")
            self.company_email_entry.insert(0, self.company_settings['email'])
            self.company_email_entry.pack(pady=5, fill="x")
           
            self.company_website_entry = ctk.CTkEntry(general_frame, placeholder_text="Website")
            self.company_website_entry.insert(0, self.company_settings['website'])
            self.company_website_entry.pack(pady=5, fill="x")



            # Logo & Signature Tab
            logo_frame = tabview.tab("Logo & Signature")
           
            ctk.CTkLabel(logo_frame, text="Company Logo", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
            self.logo_btn = ctk.CTkButton(logo_frame, text="Upload Logo", command=self.upload_company_logo)
            self.logo_btn.pack(pady=5, fill="x")
           
            ctk.CTkLabel(logo_frame, text="Company Signature", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
            self.signature_btn = ctk.CTkButton(logo_frame, text="Upload Signature", command=self.upload_company_signature)
            self.signature_btn.pack(pady=5, fill="x")
           
            # Invoice Settings Tab
            invoice_frame = tabview.tab("Invoice Settings")
           
            ctk.CTkLabel(invoice_frame, text="Invoice Settings", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
           
            ctk.CTkLabel(invoice_frame, text="Tax Rate (%):", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.tax_rate_entry = ctk.CTkEntry(invoice_frame)
            self.tax_rate_entry.insert(0, str(self.company_settings['tax_rate']))
            self.tax_rate_entry.pack(pady=5, fill="x")
           
            ctk.CTkLabel(invoice_frame, text="Currency:", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.currency_entry = ctk.CTkEntry(invoice_frame)
            self.currency_entry.insert(0, self.company_settings['currency'])
            self.currency_entry.pack(pady=5, fill="x")
           
            # Save Company Settings button
            save_company_btn = ctk.CTkButton(invoice_frame, text="Save Company Settings", command=self.save_company_settings,
                                           fg_color=self.primary_color)
            save_company_btn.pack(pady=20, fill="x")

    def save_profile_changes(self):
        # Get the current user's data
        ref = db.reference('users')
        users = ref.get() or {}
       
        # Find the current user's data
        for user_id, user_data in users.items():
            if user_id == self.current_user['id']:
                # Update user data
                updated_data = {
                    'name': self.profile_name.get(),
                    'email': self.profile_email.get(),
                    'phone': self.profile_phone.get(),
                    'address': self.profile_address.get()
                }
               
                # Update password if provided
                if self.profile_password.get():
                    if self.profile_password.get() != self.profile_confirm_password.get():
                        messagebox.showerror("Error", "Passwords do not match")
                        return
                    updated_data['password'] = self.profile_password.get()
               
                # Update in Firebase
                ref.child(user_id).update(updated_data)
               
                # Update current user data
                self.current_user.update(updated_data)
               
                messagebox.showinfo("Success", "Profile updated successfully!")
                return
       
        messagebox.showerror("Error", "Failed to update profile")

    def upload_company_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            try:
                with open(file_path, "rb") as image_file:
                    image_data = image_file.read()
                    self.company_logo = image_data.hex()
               
                # Update preview
                image = Image.open(file_path)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                self.logo_preview_label.configure(image=photo, text="")
                self.logo_preview_label.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def upload_company_signature(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            try:
                with open(file_path, "rb") as image_file:
                    image_data = image_file.read()
                    self.company_signature = image_data.hex()
               
                # Update preview
                image = Image.open(file_path)
                image = image.resize((150, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                self.signature_preview_label.configure(image=photo, text="")
                self.signature_preview_label.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def save_company_settings(self):
        # Validate inputs
        try:
            tax_rate = float(self.tax_rate_entry.get())
            if tax_rate < 0 or tax_rate > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid tax rate between 0 and 100")
            return
           
        if not self.company_name_entry.get():
            messagebox.showerror("Error", "Company name cannot be empty")
            return
           
        # Prepare settings data
        settings_data = {
            'name': self.company_name_entry.get(),
            'address': self.company_address_entry.get(),
            'phone': self.company_phone_entry.get(),
            'email': self.company_email_entry.get(),
            'website': self.company_website_entry.get(),
            'tax_rate': tax_rate,
            'currency': self.currency_entry.get()
        }
       
        # Save to Firebase
        ref = db.reference('company_settings')
        ref.set(settings_data)
       
        # Save logo and signature if they exist
        if self.company_logo:
            logo_ref = db.reference('company_logo')
            logo_ref.set(self.company_logo)
           
        if self.company_signature:
            signature_ref = db.reference('company_signature')
            signature_ref.set(self.company_signature)
       
        # Update local settings
        self.company_settings.update(settings_data)
       
        messagebox.showinfo("Success", "Company settings saved successfully!")

    def show_placeholder_page(self, page_name):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text=page_name, font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
        ctk.CTkLabel(self.content_frame, text="This page is under development",
                    font=("Roboto", 16)).pack(pady=10)

    def show_help_center(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Help Center", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Create a container frame for the entire help center page
        self.help_center_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.help_center_container.pack(fill="both", expand=True, padx=20, pady=20)
       
        # Create a tabview for switching between view and add modes
        tabview = ctk.CTkTabview(self.help_center_container)
        tabview.pack(fill="both", expand=True)
       
        # Add tabs
        view_tab = tabview.add("View Help Centers")
        if self.current_role in ["admin", "employee"]:
            add_tab = tabview.add("Add Help Center")
       
        # View Help Centers Tab
        # Search and filter frame
        search_filter_frame = ctk.CTkFrame(view_tab, fg_color="transparent")
        search_filter_frame.pack(fill="x", pady=10)
       
        # Search bar
        self.help_center_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_filter_frame,
                                  placeholder_text="Search help centers...",
                                  textvariable=self.help_center_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_filter_frame,
                                  text="Search",
                                  command=self.search_help_centers,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Create a scrollable frame for help centers
        self.help_center_scroll_frame = ctk.CTkScrollableFrame(view_tab, fg_color="transparent")
        self.help_center_scroll_frame.pack(fill="both", expand=True)
       
        # Create a frame for the help center grid
        self.help_center_grid_frame = ctk.CTkFrame(self.help_center_scroll_frame, fg_color="transparent")
        self.help_center_grid_frame.pack(fill="both", expand=True)
       
        # Load help centers
        self.load_help_centers()
       
        # Add Help Center Tab (only for admin and employee)
        if self.current_role in ["admin", "employee"]:
            # Create a scrollable frame for the form
            form_scroll_frame = ctk.CTkScrollableFrame(add_tab)
            form_scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
           
            # Form frame
            form_frame = ctk.CTkFrame(form_scroll_frame)
            form_frame.pack(fill="both", expand=True)
           
            ctk.CTkLabel(form_frame, text="Add New Help Center", font=("Roboto", 20, "bold")).pack(pady=20)
           
            # Name
            ctk.CTkLabel(form_frame, text="Name:", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.help_center_name = ctk.CTkEntry(form_frame)
            self.help_center_name.pack(fill="x", pady=5)
           
            # Address
            ctk.CTkLabel(form_frame, text="Address:", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.help_center_address = ctk.CTkEntry(form_frame)
            self.help_center_address.pack(fill="x", pady=5)
           
            # Email
            ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.help_center_email = ctk.CTkEntry(form_frame)
            self.help_center_email.pack(fill="x", pady=5)
           
            # Description
            ctk.CTkLabel(form_frame, text="Description:", font=("Roboto", 14)).pack(pady=5, anchor="w")
            self.help_center_description = ctk.CTkTextbox(form_frame, height=100)
            self.help_center_description.pack(fill="x", pady=5)
           
            # Image upload section
            image_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            image_frame.pack(fill="x", pady=10)
           
            ctk.CTkLabel(image_frame, text="Image:", font=("Roboto", 14)).pack(pady=5, anchor="w")
           
            # Image preview frame
            self.help_center_image_preview = ctk.CTkFrame(image_frame, width=200, height=150)
            self.help_center_image_preview.pack(pady=5)
            self.help_center_image_preview.pack_propagate(False)
           
            self.help_center_image_label = ctk.CTkLabel(self.help_center_image_preview, text="No image selected")
            self.help_center_image_label.pack(expand=True)
           
            # Image upload button
            upload_btn = ctk.CTkButton(image_frame,
                                     text="Choose Image",
                                     command=self.upload_help_center_image,
                                     fg_color=self.primary_color)
            upload_btn.pack(pady=5)
           
            # Save button
            save_btn = ctk.CTkButton(form_frame,
                                   text="Save Help Center",
                                   command=self.save_help_center,
                                   fg_color=self.primary_color)
            save_btn.pack(pady=20, fill="x")

    def upload_help_center_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Help Center Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
       
        if file_path:
            try:
                # Read and resize the image
                image = Image.open(file_path)
                image = image.resize((200, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                # Update the preview
                self.help_center_image_label.configure(text="", image=photo)
                self.help_center_image_label.image = photo  # Keep a reference
               
                # Store the file path
                self.help_center_image_path = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def save_help_center(self):
        # Validation
        if not all([self.help_center_name.get(), self.help_center_address.get(),
                   self.help_center_email.get(), self.help_center_description.get("1.0", "end-1c")]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
       
        # Prepare help center data
        help_center_data = {
            'name': self.help_center_name.get(),
            'address': self.help_center_address.get(),
            'email': self.help_center_email.get(),
            'description': self.help_center_description.get("1.0", "end-1c"),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': self.current_user['username']
        }
       
        # Handle image upload if exists
        if self.help_center_image_path:
            try:
                with open(self.help_center_image_path, "rb") as image_file:
                    image_data = image_file.read()
                    help_center_data['image'] = image_data.hex()
            except:
                messagebox.showerror("Error", "Failed to read image file")
                return
       
        # Save to Firebase
        ref = db.reference('help_centers')
        new_help_center_ref = ref.push(help_center_data)
       
        messagebox.showinfo("Success", "Help center added successfully!")
       
        # Clear form fields
        self.help_center_name.delete(0, "end")
        self.help_center_address.delete(0, "end")
        self.help_center_email.delete(0, "end")
        self.help_center_description.delete("1.0", "end")
        self.help_center_image_path = None
        self.help_center_image_label.configure(text="No image selected")
       
        # Reload help centers
        self.load_help_centers()

    def load_help_centers(self):
        # Clear existing help centers
        for widget in self.help_center_grid_frame.winfo_children():
            widget.destroy()
       
        # Get data from Firebase
        ref = db.reference('help_centers')
        help_centers = ref.get() or {}
       
        # Apply search filter if any
        search_query = self.help_center_search_var.get().lower()
        if search_query:
            help_centers = {k: v for k, v in help_centers.items()
                          if (search_query in v.get('name', '').lower() or
                              search_query in v.get('description', '').lower())}
       
        # Display help centers in a grid
        row, col = 0, 0
        for help_center_id, help_center_data in help_centers.items():
            # Create a card for each help center
            help_center_card = ctk.CTkFrame(self.help_center_grid_frame,
                                          width=200,
                                          height=300,
                                          border_width=1,
                                          border_color="#DDDDDD",
                                          corner_radius=10)
            help_center_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            help_center_card.grid_propagate(False)
           
            # Configure grid to center the cards
            self.help_center_grid_frame.grid_columnconfigure(col, weight=1)
           
            # Display image if available
            image_frame = ctk.CTkFrame(help_center_card, fg_color="transparent", height=150)
            image_frame.pack(fill="x", pady=(10, 5), padx=10)
           
            if 'image' in help_center_data:
                try:
                    image_data = bytes.fromhex(help_center_data['image'])
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((180, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                   
                    image_label = ctk.CTkLabel(image_frame, text="", image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack()
                except:
                    ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
            else:
                ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
           
            # Help center name
            name_label = ctk.CTkLabel(help_center_card,
                                    text=help_center_data.get('name', 'Help Center'),
                                    font=("Roboto", 14, "bold"),
                                    wraplength=180)
            name_label.pack(pady=(5, 0))
           
            # Email
            email_label = ctk.CTkLabel(help_center_card,
                                     text=help_center_data.get('email', ''),
                                     font=("Roboto", 12),
                                     text_color=self.primary_color)
            email_label.pack(pady=2)
           
            # View details button
            view_btn = ctk.CTkButton(help_center_card,
                                    text="View Details",
                                    command=lambda hcid=help_center_id: self.show_help_center_details(hcid),
                                    width=120,
                                    fg_color=self.primary_color)
            view_btn.pack(pady=10)
           
            col += 1
            if col > 3:  # 4 help centers per row
                col = 0
                row += 1

    def show_help_center_details(self, help_center_id):
        # Clear the help centers grid to show details
        for widget in self.help_center_container.winfo_children():
            widget.destroy()
       
        # Create a back button frame
        back_frame = ctk.CTkFrame(self.help_center_container, fg_color="transparent")
        back_frame.pack(fill="x", pady=(0, 10))
       
        back_btn = ctk.CTkButton(back_frame,
                                text="← Back to Help Centers",
                                command=self.back_to_help_centers_list,
                                fg_color="transparent",
                                text_color=self.primary_color,
                                hover_color=self.accent_color)
        back_btn.pack(side="left", anchor="w")
       
        # Create details frame
        details_frame = ctk.CTkFrame(self.help_center_container, fg_color="transparent")
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Get help center data from Firebase
        ref = db.reference(f'help_centers/{help_center_id}')
        help_center_data = ref.get()
       
        # Create a scrollable frame for details
        scroll_frame = ctk.CTkScrollableFrame(details_frame)
        scroll_frame.pack(fill="both", expand=True)
       
        # Main content frame
        content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Help center image (larger)
        image_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        image_frame.pack(fill="x", pady=(0, 20))
       
        if 'image' in help_center_data:
            try:
                image_data = bytes.fromhex(help_center_data['image'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
               
                image_label = ctk.CTkLabel(image_frame, text="", image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack()
            except:
                ctk.CTkLabel(image_frame, text="No Image Available", height=300,
                            font=("Roboto", 14)).pack()
        else:
            ctk.CTkLabel(image_frame, text="No Image Available", height=300,
                        font=("Roboto", 14)).pack()
       
        # Help center details container
        details_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_container.pack(fill="both", expand=True)
       
        # Help center name (large and bold)
        ctk.CTkLabel(details_container,
                    text=help_center_data.get('name', 'N/A'),
                    font=("Roboto", 24, "bold"),
                    anchor="w").pack(fill="x", pady=(0, 10))
       
        # Contact information
        contact_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        contact_frame.pack(fill="x", pady=(0, 15))
       
        ctk.CTkLabel(contact_frame,
                    text="Contact Information",
                    font=("Roboto", 18, "bold")).pack(anchor="w", pady=(0, 10))
       
        ctk.CTkLabel(contact_frame,
                    text=f"Email: {help_center_data.get('email', 'N/A')}",
                    font=("Roboto", 14)).pack(anchor="w")
       
        ctk.CTkLabel(contact_frame,
                    text=f"Address: {help_center_data.get('address', 'N/A')}",
                    font=("Roboto", 14)).pack(anchor="w", pady=(5, 0))
       
        # Description section
        desc_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(20, 0))
       
        ctk.CTkLabel(desc_frame,
                    text="Description",
                    font=("Roboto", 18, "bold")).pack(anchor="w", pady=(0, 10))
       
        desc_text = help_center_data.get('description', 'No description available')
        desc_label = ctk.CTkLabel(desc_frame,
                                 text=desc_text,
                                 font=("Roboto", 14),
                                 wraplength=600,
                                 justify="left",
                                 anchor="w")
        desc_label.pack(fill="x")

    def back_to_help_centers_list(self):
        # Clear the details view and show the help centers grid again
        for widget in self.help_center_container.winfo_children():
            widget.destroy()
       
        # Recreate the help centers view
        title_frame = ctk.CTkFrame(self.help_center_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
       
        ctk.CTkLabel(title_frame, text="Help Center", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(side="left")
       
        # Add "Add Help Center" button for admin and employee roles
        if self.current_role in ["admin", "employee"]:
            add_btn = ctk.CTkButton(title_frame, text="+ Add Help Center",
                                  command=self.show_add_help_center_form,
                                  fg_color=self.success_color,
                                  text_color="white")
            add_btn.pack(side="right", padx=10)
       
        # Search and filter frame
        search_filter_frame = ctk.CTkFrame(self.help_center_container, fg_color="transparent")
        search_filter_frame.pack(fill="x", pady=10)
       
        # Search bar
        search_entry = ctk.CTkEntry(search_filter_frame,
                                  placeholder_text="Search help centers...",
                                  textvariable=self.help_center_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_filter_frame,
                                  text="Search",
                                  command=self.search_help_centers,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Create a scrollable frame for help centers
        self.help_center_scroll_frame = ctk.CTkScrollableFrame(self.help_center_container, fg_color="transparent")
        self.help_center_scroll_frame.pack(fill="both", expand=True)
       
        # Create a frame for the help center grid
        self.help_center_grid_frame = ctk.CTkFrame(self.help_center_scroll_frame, fg_color="transparent")
        self.help_center_grid_frame.pack(fill="both", expand=True)
       
        # Load help centers
        self.load_help_centers()

    def search_help_centers(self):
        self.load_help_centers()

    def navigate(self, page):
        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Manage Users" and self.current_role == "admin":
            self.show_admin_dashboard()
        elif page == "Manage Employees" and self.current_role == "admin":
            self.show_employee_management()
        elif page == "Notice" and self.current_role == "admin":
            self.show_notice_management()
        elif page == "Updates" and self.current_role == "employee":
            self.show_employee_updates()
        elif page == "Inventory":
            if self.current_role in ["admin", "employee"]:
                self.show_inventory_page()
            else:
                self.show_customer_inventory_view()
        elif page == "Billing" and self.current_role in ["admin", "employee"]:
            self.show_billing_page()
        elif page == "Products" and self.current_role == "customer":
            self.show_customer_products_page()
        elif page == "Help Center":
            self.show_help_center()
        elif page == "Settings":
            self.show_settings_page()
        elif page == "Recommendations" and self.current_role == "admin":
            self.show_recommendations()
        elif page == "Suggestion" and self.current_role == "customer":
            self.show_suggestion_page()
        elif page == "Reports" and self.current_role == "admin":
            self.show_task_reports()
        elif page == "Chatbot" and self.current_role == "admin":
            self.show_admin_chat()
        elif page == "Voice Bot" and self.current_role == "customer":
            self.show_voice_bot()
        elif page == "Task Management" and self.current_role == "admin":
            self.show_task_management()
        elif page == "Tasks":
            self.show_task_page()
        elif page == "About Us":
            if self.current_role == "admin":
                self.show_about_us_admin_page()
            else:
                self.show_about_us()
        else:
            self.show_placeholder_page(page)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_customer_inventory_view(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Product Catalog", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Search and filter frame
        search_filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_filter_frame.pack(fill="x", pady=10, padx=20)
       
        # Search bar
        self.customer_inventory_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_filter_frame,
                                  placeholder_text="Search products...",
                                  textvariable=self.customer_inventory_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_filter_frame,
                                  text="Search",
                                  command=self.search_customer_inventory,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Category filter
        ctk.CTkLabel(search_filter_frame,
                    text="Filter by Category:",
                    font=("Roboto", 14)).pack(side="left", padx=(0, 10))
       
        self.customer_category_filter_var = ctk.StringVar(value="All")
        self.customer_category_dropdown = ctk.CTkComboBox(search_filter_frame,
                                                       variable=self.customer_category_filter_var,
                                                       width=150)
        self.customer_category_dropdown.pack(side="left")
       
        # Load categories
        self.load_customer_categories()
       
        # Create a scrollable frame for products
        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Create a frame for the product grid
        self.customer_products_grid = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.customer_products_grid.pack(fill="both", expand=True)
       
        # Load products
        self.load_customer_inventory()

    def load_customer_categories(self):
        ref = db.reference('products')
        products = ref.get() or {}
       
        categories = set()
        for product_data in products.values():
            if 'category' in product_data and product_data['category']:
                categories.add(product_data['category'])
       
        category_list = ["All"] + sorted(list(categories))
        self.customer_category_dropdown.configure(values=category_list)

    def load_customer_inventory(self):
        # Clear existing products
        for widget in self.customer_products_grid.winfo_children():
            widget.destroy()
       
        # Get data from Firebase
        ref = db.reference('products')
        products = ref.get() or {}
       
        # Filter by category if needed
        selected_category = self.customer_category_filter_var.get()
        if selected_category != "All":
            products = {k: v for k, v in products.items()
                       if v.get('category') == selected_category}
       
        # Apply search filter if any
        search_query = self.customer_inventory_search_var.get().lower()
        if search_query:
            products = {k: v for k, v in products.items()
                       if (search_query in v.get('name', '').lower() or
                           search_query in v.get('description', '').lower() or
                           search_query in v.get('category', '').lower())}
       
        # Display products in a grid
        row, col = 0, 0
        for product_id, product_data in products.items():
            # Create a card for each product
            product_card = ctk.CTkFrame(self.customer_products_grid,
                                      width=200,
                                      height=300,
                                      border_width=1,
                                      border_color="#DDDDDD",
                                      corner_radius=10)
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            product_card.grid_propagate(False)
           
            # Configure grid to center the cards
            self.customer_products_grid.grid_columnconfigure(col, weight=1)
           
            # Display image if available
            image_frame = ctk.CTkFrame(product_card, fg_color="transparent", height=150)
            image_frame.pack(fill="x", pady=(10, 5), padx=10)
           
            if 'image' in product_data:
                try:
                    image_data = bytes.fromhex(product_data['image'])
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((180, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                   
                    image_label = ctk.CTkLabel(image_frame, text="", image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack()
                except:
                    ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
            else:
                ctk.CTkLabel(image_frame, text="No Image", height=150).pack()
           
            # Product name
            name_label = ctk.CTkLabel(product_card,
                                    text=product_data.get('name', 'Product'),
                                    font=("Roboto", 14, "bold"),
                                    wraplength=180)
            name_label.pack(pady=(5, 0))
           
            # Price
            price_label = ctk.CTkLabel(product_card,
                                     text=f"{self.company_settings['currency']} {product_data.get('price', 0):.2f}",
                                     font=("Roboto", 12, "bold"),
                                     text_color=self.primary_color)
            price_label.pack(pady=2)
           
            # Stock status
            stock_status = "In Stock" if int(product_data.get('quantity', 0)) > 0 else "Out of Stock"
            stock_color = self.success_color if int(product_data.get('quantity', 0)) > 0 else self.danger_color
           
            stock_label = ctk.CTkLabel(product_card,
                                     text=stock_status,
                                     font=("Roboto", 12),
                                     text_color=stock_color)
            stock_label.pack(pady=2)
           
            # View details button
            view_btn = ctk.CTkButton(product_card,
                                    text="View Details",
                                    command=lambda pid=product_id: self.show_product_details(pid),
                                    width=120,
                                    fg_color=self.primary_color)
            view_btn.pack(pady=10)
           
            col += 1
            if col > 3:  # 4 products per row
                col = 0
                row += 1

    def search_customer_inventory(self):
        self.load_customer_inventory()

    def show_add_user_form(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Add New User", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Create a scrollable frame for the form
        scrollable_frame = ctk.CTkScrollableFrame(self.content_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Form frame
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
       
        # User Information Section
        ctk.CTkLabel(form_frame, text="User Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
       
        # Name
        ctk.CTkLabel(form_frame, text="Full Name:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_name = ctk.CTkEntry(form_frame)
        self.new_user_name.pack(fill="x", pady=5)
       
        # Username
        ctk.CTkLabel(form_frame, text="Username:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_username = ctk.CTkEntry(form_frame)
        self.new_user_username.pack(fill="x", pady=5)
       
        # Email
        ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_email = ctk.CTkEntry(form_frame)
        self.new_user_email.pack(fill="x", pady=5)
       
        # Phone
        ctk.CTkLabel(form_frame, text="Phone:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_phone = ctk.CTkEntry(form_frame)
        self.new_user_phone.pack(fill="x", pady=5)
       
        # Address
        ctk.CTkLabel(form_frame, text="Address:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_address = ctk.CTkEntry(form_frame)
        self.new_user_address.pack(fill="x", pady=5)
       
        # Password
        ctk.CTkLabel(form_frame, text="Password:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_password = ctk.CTkEntry(form_frame, show="*")
        self.new_user_password.pack(fill="x", pady=5)
       
        # Confirm Password
        ctk.CTkLabel(form_frame, text="Confirm Password:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_confirm_password = ctk.CTkEntry(form_frame, show="*")
        self.new_user_confirm_password.pack(fill="x", pady=5)
       
        # Role
        ctk.CTkLabel(form_frame, text="Role:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_user_role = ctk.CTkComboBox(form_frame, values=["admin", "employee", "customer"])
        self.new_user_role.pack(fill="x", pady=5)
       
        # Save button
        save_btn = ctk.CTkButton(form_frame, text="Save User", command=self.save_new_user,
                                fg_color=self.primary_color)
        save_btn.pack(pady=20, fill="x")

    def save_new_user(self):
        # Validation
        if not all([self.new_user_name.get(), self.new_user_username.get(),
                   self.new_user_email.get(), self.new_user_password.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
       
        if self.new_user_password.get() != self.new_user_confirm_password.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
       
        # Check if username already exists
        ref = db.reference('users')
        users = ref.get() or {}
       
        for user_id, user_data in users.items():
            if user_data.get('username') == self.new_user_username.get():
                messagebox.showerror("Error", "Username already taken")
                return
            if user_data.get('email') == self.new_user_email.get():
                messagebox.showerror("Error", "Email already registered")
                return
       
        # Prepare user data
        user_data = {
            'name': self.new_user_name.get(),
            'username': self.new_user_username.get(),
            'email': self.new_user_email.get(),
            'phone': self.new_user_phone.get(),
            'address': self.new_user_address.get(),
            'password': self.new_user_password.get(),
            'role': self.new_user_role.get(),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': self.current_user['username']
        }
       
        # Save to Firebase
        new_user_ref = ref.push(user_data)
       
        messagebox.showinfo("Success", "User added successfully!")
        self.show_admin_dashboard()

    def show_user_table(self):
        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Create the treeview
        self.user_tree = ttk.Treeview(table_frame, columns=("name", "username", "email", "role", "created_at"), show="headings")
       
        # Configure columns
        self.user_tree.heading("name", text="Name")
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("email", text="Email")
        self.user_tree.heading("role", text="Role")
        self.user_tree.heading("created_at", text="Created At")
       
        self.user_tree.column("name", width=150)
        self.user_tree.column("username", width=100)
        self.user_tree.column("email", width=200)
        self.user_tree.column("role", width=100)
        self.user_tree.column("created_at", width=150)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
       
        self.user_tree.pack(fill="both", expand=True)
       
        # Load data
        self.load_user_data()

    def load_user_data(self):
        # Clear existing data
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
       
        # Get data from Firebase
        ref = db.reference('users')
        users = ref.get() or {}
       
        # Add data to treeview
        for user_id, user_data in users.items():
            self.user_tree.insert("", "end", values=(
                user_data.get('name', ''),
                user_data.get('username', ''),
                user_data.get('email', ''),
                user_data.get('role', ''),
                user_data.get('created_at', '')
            ), tags=(user_id,))

    def show_employee_management(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Employee Management", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Add employee button
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
       
        add_btn = ctk.CTkButton(btn_frame, text="+ Add Employee", command=self.show_add_employee_form,
                               fg_color=self.success_color, text_color="white")
        add_btn.pack(side="left", padx=5)
       
        # Employee table
        self.show_employee_table()

    def show_add_employee_form(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Add New Employee", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Create a scrollable frame for the form
        scrollable_frame = ctk.CTkScrollableFrame(self.content_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Form frame
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
       
        # Employee Information Section
        ctk.CTkLabel(form_frame, text="Employee Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
       
        # Name
        ctk.CTkLabel(form_frame, text="Full Name:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_employee_name = ctk.CTkEntry(form_frame)
        self.new_employee_name.pack(fill="x", pady=5)
       
        # Username
        ctk.CTkLabel(form_frame, text="Username:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_employee_username = ctk.CTkEntry(form_frame)
        self.new_employee_username.pack(fill="x", pady=5)
       
        # Phone
        ctk.CTkLabel(form_frame, text="Phone Number:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_employee_phone = ctk.CTkEntry(form_frame)
        self.new_employee_phone.pack(fill="x", pady=5)
       
        # Password
        ctk.CTkLabel(form_frame, text="Password:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_employee_password = ctk.CTkEntry(form_frame, show="*")
        self.new_employee_password.pack(fill="x", pady=5)
       
        # Confirm Password
        ctk.CTkLabel(form_frame, text="Confirm Password:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.new_employee_confirm_password = ctk.CTkEntry(form_frame, show="*")
        self.new_employee_confirm_password.pack(fill="x", pady=5)
       
        # Save button
        save_btn = ctk.CTkButton(form_frame, text="Save Employee", command=self.save_new_employee,
                                fg_color=self.primary_color)
        save_btn.pack(pady=20, fill="x")

    def save_new_employee(self):
        # Validation
        if not all([self.new_employee_name.get(), self.new_employee_username.get(),
                   self.new_employee_phone.get(), self.new_employee_password.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
       
        if self.new_employee_password.get() != self.new_employee_confirm_password.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
       
        # Check if username already exists
        ref = db.reference('users')
        users = ref.get() or {}
       
        for user_id, user_data in users.items():
            if user_data.get('username') == self.new_employee_username.get():
                messagebox.showerror("Error", "Username already taken")
                return
       
        # Prepare employee data
        employee_data = {
            'name': self.new_employee_name.get(),
            'username': self.new_employee_username.get(),
            'phone': self.new_employee_phone.get(),
            'password': self.new_employee_password.get(),
            'role': 'employee',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': self.current_user['username']
        }
       
        # Save to Firebase
        new_employee_ref = ref.push(employee_data)
       
        messagebox.showinfo("Success", "Employee added successfully!")
        self.show_employee_management()

    def show_employee_table(self):
        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Create the treeview
        self.employee_tree = ttk.Treeview(table_frame, columns=("name", "username", "phone", "created_at"), show="headings")
       
        # Configure columns
        self.employee_tree.heading("name", text="Name")
        self.employee_tree.heading("username", text="Username")
        self.employee_tree.heading("phone", text="Phone")
        self.employee_tree.heading("created_at", text="Created At")
       
        self.employee_tree.column("name", width=150)
        self.employee_tree.column("username", width=100)
        self.employee_tree.column("phone", width=150)
        self.employee_tree.column("created_at", width=150)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
       
        self.employee_tree.pack(fill="both", expand=True)
       
        # Load data
        self.load_employee_data()

    def load_employee_data(self):
        # Clear existing data
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
       
        # Get data from Firebase
        ref = db.reference('users')
        users = ref.get() or {}
       
        # Add data to treeview
        for user_id, user_data in users.items():
            if user_data.get('role') == 'employee':
                self.employee_tree.insert("", "end", values=(
                    user_data.get('name', ''),
                    user_data.get('username', ''),
                    user_data.get('phone', ''),
                    user_data.get('created_at', '')
                ), tags=(user_id,))

    def show_notice_management(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Notice Management", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Add notice button
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
       
        add_btn = ctk.CTkButton(btn_frame, text="+ Add Notice", command=self.show_add_notice_form,
                               fg_color=self.success_color, text_color="white")
        add_btn.pack(side="left", padx=5)
       
        # Notice table
        self.show_notice_table()

    def show_add_notice_form(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Add New Notice", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
       
        # Create a scrollable frame for the form
        scrollable_frame = ctk.CTkScrollableFrame(self.content_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Form frame
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
       
        # Notice Information Section
        ctk.CTkLabel(form_frame, text="Notice Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w")
       
        # Title
        ctk.CTkLabel(form_frame, text="Title:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.notice_title = ctk.CTkEntry(form_frame)
        self.notice_title.pack(fill="x", pady=5)
       
        # Description
        ctk.CTkLabel(form_frame, text="Description:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.notice_description = ctk.CTkTextbox(form_frame, height=100)
        self.notice_description.pack(fill="x", pady=5)
       
        # Target Employee
        ctk.CTkLabel(form_frame, text="Target Employee:", font=("Roboto", 14)).pack(pady=5, anchor="w")
        self.notice_target = ctk.CTkComboBox(form_frame, values=["All Employees"] + self.get_employee_list())
        self.notice_target.pack(fill="x", pady=5)
       
        # Save button
        save_btn = ctk.CTkButton(form_frame, text="Save Notice", command=self.save_new_notice,
                                fg_color=self.primary_color)
        save_btn.pack(pady=20, fill="x")

    def get_employee_list(self):
        ref = db.reference('users')
        users = ref.get() or {}
        return [user_data.get('username') for user_id, user_data in users.items()
                if user_data.get('role') == 'employee']

    def save_new_notice(self):
        # Validation
        if not all([self.notice_title.get(), self.notice_description.get("1.0", "end-1c")]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
       
        # Prepare notice data
        notice_data = {
            'title': self.notice_title.get(),
            'description': self.notice_description.get("1.0", "end-1c"),
            'target': self.notice_target.get(),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'created_by': self.current_user['username']
        }
       
        # Save to Firebase
        ref = db.reference('notices')
        new_notice_ref = ref.push(notice_data)
       
        messagebox.showinfo("Success", "Notice added successfully!")
        self.show_notice_management()

    def show_notice_table(self):
        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Create the treeview
        self.notice_tree = ttk.Treeview(table_frame, columns=("title", "target", "created_at"), show="headings")
       
        # Configure columns
        self.notice_tree.heading("title", text="Title")
        self.notice_tree.heading("target", text="Target")
        self.notice_tree.heading("created_at", text="Created At")
       
        self.notice_tree.column("title", width=200)
        self.notice_tree.column("target", width=150)
        self.notice_tree.column("created_at", width=150)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.notice_tree.yview)
        self.notice_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
       
        self.notice_tree.pack(fill="both", expand=True)
       
        # Load data
        self.load_notice_data()

    def load_notice_data(self):
        # Clear existing data
        for item in self.notice_tree.get_children():
            self.notice_tree.delete(item)
       
        # Get data from Firebase
        ref = db.reference('notices')
        notices = ref.get() or {}
       
        # Add data to treeview
        for notice_id, notice_data in notices.items():
            self.notice_tree.insert("", "end", values=(
                notice_data.get('title', ''),
                notice_data.get('target', ''),
                notice_data.get('created_at', '')
            ), tags=(notice_id,))

    def show_employee_updates(self):
        self.clear_content()
        
        # Main title
        ctk.CTkLabel(self.content_frame, text="Updates", font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
        
        # Create a scrollable frame for updates
        scrollable_frame = ctk.CTkScrollableFrame(self.content_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get notices from Firebase
        ref = db.reference('notices')
        notices = ref.get() or {}
        
        # Display notices
        for notice_id, notice_data in notices.items():
            # Check if notice is for this employee or all employees
            if notice_data.get('target') == "All Employees" or notice_data.get('target') == self.current_user['username']:
                # Create card frame
                card_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.accent_color)
                card_frame.pack(fill="x", pady=10, padx=5)
                
                # Card header
                header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=10)
                
                # Title with icon
                title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                title_frame.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(title_frame, text="📢",
                            font=("Roboto", 20)).pack(side="left", padx=(0, 5))
                ctk.CTkLabel(title_frame, text=notice_data.get('title', ''),
                            font=("Roboto", 16, "bold")).pack(side="left")
                
                # Date and author
                date_author = f"Posted by {notice_data.get('created_by', '')} on {notice_data.get('created_at', '')}"
                ctk.CTkLabel(header_frame, text=date_author,
                            font=("Roboto", 12), text_color=self.secondary_text).pack(side="right")
                
                # Description
                desc_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                desc_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                ctk.CTkLabel(desc_frame, text=notice_data.get('description', ''),
                            font=("Roboto", 14), wraplength=600, justify="left").pack(anchor="w")
                
                # Target info
                target_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                target_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                target_text = "For: " + ("All Employees" if notice_data.get('target') == "All Employees" 
                                       else f"Employee ({notice_data.get('target', '')})")
                ctk.CTkLabel(target_frame, text=target_text,
                            font=("Roboto", 12), text_color=self.secondary_text).pack(anchor="w")
    def show_recommendations(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Customer Recommendations",
                    font=("Roboto", 24, "bold"), text_color=self.text_color).pack(pady=20)
       
        # Create a container frame
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Search frame
        search_frame = ctk.CTkFrame(container, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
       
        # Search bar
        self.recommendation_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame,
                                  placeholder_text="Search suggestions...",
                                  textvariable=self.recommendation_search_var,
                                  width=300)
        search_entry.pack(side="left", padx=(0, 10))
       
        search_btn = ctk.CTkButton(search_frame,
                                  text="Search",
                                  command=self.search_recommendations,
                                  width=80)
        search_btn.pack(side="left", padx=(0, 20))
       
        # Status filter
        ctk.CTkLabel(search_frame,
                    text="Filter by Status:",
                    font=("Roboto", 14)).pack(side="left", padx=(0, 10))
       
        self.status_filter_var = ctk.StringVar(value="All")
        self.status_dropdown = ctk.CTkComboBox(search_frame,
                                             variable=self.status_filter_var,
                                             values=["All", "Pending", "Replied"],
                                             width=150)
        self.status_dropdown.pack(side="left")
       
        # Create a scrollable frame for recommendations
        self.recommendations_scroll_frame = ctk.CTkScrollableFrame(container)
        self.recommendations_scroll_frame.pack(fill="both", expand=True, pady=10)
       
        # Load recommendations
        self.load_recommendations()

    def load_recommendations(self):
        # Clear existing recommendations
        for widget in self.recommendations_scroll_frame.winfo_children():
            widget.destroy()
       
        # Get suggestions from Firebase
        ref = db.reference('suggestions')
        suggestions = ref.get() or {}
       
        # Apply filters
        status_filter = self.status_filter_var.get()
        search_query = self.recommendation_search_var.get().lower()
       
        filtered_suggestions = {}
        for suggestion_id, suggestion_data in suggestions.items():
            # Apply status filter
            if status_filter != "All" and suggestion_data['status'].capitalize() != status_filter:
                continue
           
            # Apply search filter
            if search_query:
                if (search_query not in suggestion_data['suggestion'].lower() and
                    search_query not in suggestion_data['user_name'].lower()):
                    continue
           
            filtered_suggestions[suggestion_id] = suggestion_data
       
        if not filtered_suggestions:
            ctk.CTkLabel(self.recommendations_scroll_frame,
                        text="No recommendations found",
                        font=("Roboto", 14)).pack(pady=20)
            return
       
        # Display recommendations
        for suggestion_id, suggestion_data in filtered_suggestions.items():
            suggestion_card = ctk.CTkFrame(self.recommendations_scroll_frame, fg_color=self.accent_color)
            suggestion_card.pack(fill="x", pady=5, padx=10)
           
            # User info
            user_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
            user_frame.pack(fill="x", padx=10, pady=5)
           
            ctk.CTkLabel(user_frame,
                        text=f"From: {suggestion_data['user_name']} ({suggestion_data['username']})",
                        font=("Roboto", 12, "bold")).pack(side="left")
           
            ctk.CTkLabel(user_frame,
                        text=f"Submitted: {suggestion_data['created_at']}",
                        font=("Roboto", 12)).pack(side="right")
           
            # Suggestion text
            ctk.CTkLabel(suggestion_card,
                        text=suggestion_data['suggestion'],
                        font=("Roboto", 14),
                        wraplength=500).pack(pady=10, padx=10)
           
            # Status and reply button
            action_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
            action_frame.pack(fill="x", padx=10, pady=5)
           
            status_color = self.success_color if suggestion_data['status'] == 'replied' else self.danger_color
            ctk.CTkLabel(action_frame,
                        text=f"Status: {suggestion_data['status'].capitalize()}",
                        font=("Roboto", 12),
                        text_color=status_color).pack(side="left")
           
            reply_btn = ctk.CTkButton(action_frame,
                                    text="Reply" if suggestion_data['status'] == 'pending' else "Edit Reply",
                                    command=lambda sid=suggestion_id: self.show_reply_form(sid),
                                    width=100,
                                    fg_color=self.primary_color)
            reply_btn.pack(side="right")
           
            # Show existing reply if any
            if suggestion_data.get('admin_reply'):
                reply_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
                reply_frame.pack(fill="x", padx=10, pady=5)
               
                ctk.CTkLabel(reply_frame,
                            text="Your Reply:",
                            font=("Roboto", 12, "bold")).pack(anchor="w")
                ctk.CTkLabel(reply_frame,
                            text=suggestion_data['admin_reply'],
                            font=("Roboto", 12),
                            wraplength=500).pack(anchor="w")

    def show_reply_form(self, suggestion_id):
        # Get suggestion data
        ref = db.reference('suggestions')
        suggestion_data = ref.child(suggestion_id).get()
        
        # Clear existing content
        self.clear_content()
        
        # Create container frame
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        ctk.CTkLabel(container,
                    text=f"Reply to {suggestion_data['user_name']}'s Suggestion",
                    font=("Roboto", 20, "bold")).pack(pady=20)
        
        # Show original suggestion
        ctk.CTkLabel(container,
                    text="Original Suggestion:",
                    font=("Roboto", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=20)
        
        suggestion_text = ctk.CTkLabel(container,
                                     text=suggestion_data['suggestion'],
                                     font=("Roboto", 14),
                                     wraplength=500)
        suggestion_text.pack(pady=5, padx=20)
        
        # Reply text area
        ctk.CTkLabel(container,
                    text="Your Reply:",
                    font=("Roboto", 14)).pack(pady=(20, 5), anchor="w", padx=20)
        
        self.reply_text = ctk.CTkTextbox(container, height=150)
        self.reply_text.pack(fill="x", padx=20, pady=5)
        
        # Insert existing reply if any
        if suggestion_data.get('admin_reply'):
            self.reply_text.insert("1.0", suggestion_data['admin_reply'])
        
        # Button frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Back button
        back_btn = ctk.CTkButton(button_frame,
                                text="Back",
                                command=self.show_recommendations,
                                fg_color=self.danger_color,
                                width=100)
        back_btn.pack(side="left", padx=5)
        
        # Submit button
        submit_btn = ctk.CTkButton(button_frame,
                                  text="Send Reply",
                                  command=lambda: self.save_reply(suggestion_id, None),
                                  fg_color=self.primary_color,
                                  text_color="white",
                                  width=100)
        submit_btn.pack(side="right", padx=5)

    def save_reply(self, suggestion_id, window):
        reply_text = self.reply_text.get("1.0", "end-1c").strip()
        
        if not reply_text:
            messagebox.showerror("Error", "Please enter your reply")
            return
        
        # Update Firebase
        ref = db.reference('suggestions')
        ref.child(suggestion_id).update({
            'admin_reply': reply_text,
            'status': 'replied',
            'replied_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        messagebox.showinfo("Success", "Reply submitted successfully!")
        
        # If there's a window, destroy it
        if window:
            window.destroy()
        
        # Return to recommendations view
        self.show_recommendations()

    def search_recommendations(self):
        self.load_recommendations()


    def show_suggestion_page(self):
        self.clear_content()
       
        # Main title
        ctk.CTkLabel(self.content_frame, text="Submit Your Suggestion",
                    font=("Roboto", 24, "bold"), text_color=self.text_color).pack(pady=20)
       
        # Create a container frame
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Suggestion form frame
        form_frame = ctk.CTkFrame(container, fg_color=self.accent_color)
        form_frame.pack(fill="x", pady=10)
       
        # Title
        ctk.CTkLabel(form_frame, text="New Suggestion",
                    font=("Roboto", 18, "bold")).pack(pady=10)
       
        # Suggestion text area
        ctk.CTkLabel(form_frame, text="Your Suggestion:",
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w", padx=20)
       
        self.suggestion_text = ctk.CTkTextbox(form_frame, height=150)
        self.suggestion_text.pack(fill="x", padx=20, pady=5)
       
        # Submit button
        submit_btn = ctk.CTkButton(form_frame, text="Submit Suggestion",
                                  command=self.save_suggestion,
                                  fg_color=self.primary_color,
                                  text_color="white")
        submit_btn.pack(pady=20)
       
        # Your suggestions section
        ctk.CTkLabel(container, text="Your Previous Suggestions",
                    font=("Roboto", 18, "bold")).pack(pady=(20, 10))
       
        # Create a scrollable frame for suggestions
        suggestions_scroll_frame = ctk.CTkScrollableFrame(container)
        suggestions_scroll_frame.pack(fill="both", expand=True)
       
        # Get suggestions from Firebase
        ref = db.reference('suggestions')
        suggestions = ref.get() or {}
       
        # Filter suggestions for current user
        user_suggestions = {k: v for k, v in suggestions.items()
                          if v.get('user_id') == self.current_user['id']}
       
        if not user_suggestions:
            ctk.CTkLabel(suggestions_scroll_frame,
                        text="No suggestions submitted yet",
                        font=("Roboto", 14)).pack(pady=10)
            return
       
        # Display suggestions
        for suggestion_id, suggestion_data in user_suggestions.items():
            suggestion_card = ctk.CTkFrame(suggestions_scroll_frame, fg_color=self.accent_color)
            suggestion_card.pack(fill="x", pady=5, padx=10)
           
            # Suggestion text
            ctk.CTkLabel(suggestion_card,
                        text=suggestion_data['suggestion'],
                        font=("Roboto", 14),
                        wraplength=500).pack(pady=10, padx=10)
           
            # Status and date
            status_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
            status_frame.pack(fill="x", padx=10, pady=5)
           
            status_color = self.success_color if suggestion_data['status'] == 'replied' else self.danger_color
            ctk.CTkLabel(status_frame,
                        text=f"Status: {suggestion_data['status'].capitalize()}",
                        font=("Roboto", 12),
                        text_color=status_color).pack(side="left")
           
            ctk.CTkLabel(status_frame,
                        text=f"Submitted: {suggestion_data['created_at']}",
                        font=("Roboto", 12)).pack(side="right")
           
            # Admin reply if available
            if suggestion_data.get('admin_reply'):
                reply_frame = ctk.CTkFrame(suggestion_card, fg_color="transparent")
                reply_frame.pack(fill="x", padx=10, pady=5)
               
                ctk.CTkLabel(reply_frame,
                            text="Admin Reply:",
                            font=("Roboto", 12, "bold")).pack(anchor="w")
                ctk.CTkLabel(reply_frame,
                            text=suggestion_data['admin_reply'],
                            font=("Roboto", 12),
                            wraplength=500).pack(anchor="w")

    def save_suggestion(self):
        suggestion_text = self.suggestion_text.get("1.0", "end-1c").strip()
       
        if not suggestion_text:
            messagebox.showerror("Error", "Please enter your suggestion")
            return
       
        # Save to Firebase
        ref = db.reference('suggestions')
        suggestion_data = {
            'user_id': self.current_user['id'],
            'username': self.current_user['username'],
            'user_name': self.current_user['name'],
            'suggestion': suggestion_text,
            'status': 'pending',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'admin_reply': ''
        }
       
        ref.push(suggestion_data)
        messagebox.showinfo("Success", "Your suggestion has been submitted successfully!")
       
        # Clear the text area
        self.suggestion_text.delete("1.0", "end")
       
        # Refresh the suggestions list
        self.show_suggestion_page()
       
    def show_task_page(self):
        self.clear_content()
        
        if self.current_role == "employee":
            title = "My Tasks"
        else:
            title = "Task Management"
        
        ctk.CTkLabel(self.content_frame, text=title, font=("Roboto", 24, "bold"), 
                    text_color=self.text_color).pack(pady=20)
        
        # Create a container frame for all task-related widgets
        task_container = ctk.CTkFrame(self.content_frame)
        task_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add a button to create new task (for customers and admins)
        if self.current_role in ["customer", "admin"]:
            btn_frame = ctk.CTkFrame(task_container, fg_color="transparent")
            btn_frame.pack(fill="x", pady=5)
            
            create_btn = ctk.CTkButton(btn_frame, text="+ Create Task", command=self.show_create_task_form, 
                                      fg_color=self.primary_color, text_color="white")
            create_btn.pack(side="left", padx=5)
        
        # Create a tab view for different task views
        self.task_tabview = ctk.CTkTabview(task_container)
        self.task_tabview.pack(fill="both", expand=True)
        
        # Add tabs based on user role
        if self.current_role == "employee":
            self.task_tabview.add("Assigned Tasks")
            self.show_employee_task_table(self.task_tabview.tab("Assigned Tasks"))
        elif self.current_role == "customer":
            self.task_tabview.add("My Tasks")
            self.show_my_task_table(self.task_tabview.tab("My Tasks"))
        else:
            self.task_tabview.add("All Tasks")
            self.task_tabview.add("My Tasks")
            self.show_task_table(self.task_tabview.tab("All Tasks"))
            self.show_my_task_table(self.task_tabview.tab("My Tasks"))
    
    def show_task_management(self):
        self.show_task_page()

    def show_create_task_form(self):
        # Clear the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Add back button
        back_btn = ctk.CTkButton(self.content_frame, text="← Back", command=self.show_task_page,
                                fg_color="transparent", text_color=self.primary_color)
        back_btn.pack(pady=10, anchor="w")
        
        ctk.CTkLabel(self.content_frame, text="Create New Task", font=("Roboto", 24, "bold"), 
                    text_color=self.text_color).pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.content_frame, fg_color=self.accent_color)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Task Information", font=("Roboto", 16, "bold")).pack(pady=10, anchor="w", padx=20)
        
        self.task_title = ctk.CTkEntry(form_frame, placeholder_text="Task Title*")
        self.task_title.pack(pady=5, padx=20, fill="x")
        
        self.task_description = ctk.CTkTextbox(form_frame, height=100)
        self.task_description.pack(pady=5, padx=20, fill="x")
        
        # Image upload section
        img_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        img_frame.pack(pady=5, padx=20, fill="x")
        
        self.task_image_path = None
        self.task_image_label = ctk.CTkLabel(img_frame, text="No image selected", width=100)
        self.task_image_label.pack(side="left", padx=5)
        
        upload_btn = ctk.CTkButton(img_frame, text="Upload Image", command=self.upload_task_image)
        upload_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(form_frame, text="Create Task", command=self.save_new_task, 
                                fg_color=self.primary_color)
        save_btn.pack(pady=20, padx=20, fill="x")

    def upload_task_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Task Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        
        if file_path:
            self.task_image_path = file_path
            self.task_image_label.configure(text=os.path.basename(file_path))

    def save_new_task(self):
        if not self.task_title.get():
            messagebox.showerror("Error", "Please enter a task title")
            return
            
        task_data = {
            'title': self.task_title.get(),
            'description': self.task_description.get("1.0", "end-1c"),
            'created_by_id': self.current_user['id'],
            'created_by_name': self.current_user['name'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Pending'
        }
        
        # Handle image upload
        if self.task_image_path:
            try:
                # Store the image path in the task data
                task_data['image_path'] = self.task_image_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")
                return
        
        ref = db.reference('tasks')
        new_task_ref = ref.push(task_data)
        
        messagebox.showinfo("Success", "Task created successfully!")
        self.show_task_page()

    def show_task_table(self, parent_frame):
        search_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
        
        self.task_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search tasks...", textvariable=self.task_search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        search_btn = ctk.CTkButton(search_frame, text="Search", command=lambda: self.search_tasks(self.task_tree), width=80)
        search_btn.pack(side="left", padx=5)
        
        self.task_tree = ttk.Treeview(parent_frame, columns=("title", "created_by", "assigned_to", "priority", "status", "deadline"), show="headings")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#FFFFFF", 
                       foreground="black", 
                       rowheight=25, 
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", 
                       background=self.primary_color, 
                       foreground="white", 
                       font=('Roboto', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#E1E1E1')])
        
        self.task_tree.heading("title", text="Title")
        self.task_tree.heading("created_by", text="Created By")
        self.task_tree.heading("assigned_to", text="Assigned To")
        self.task_tree.heading("priority", text="Priority")
        self.task_tree.heading("status", text="Status")
        self.task_tree.heading("deadline", text="Deadline")
        
        self.task_tree.column("title", width=200)
        self.task_tree.column("created_by", width=150)
        self.task_tree.column("assigned_to", width=150)
        self.task_tree.column("priority", width=100)
        self.task_tree.column("status", width=120)
        self.task_tree.column("deadline", width=120)
        
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.task_tree.pack(fill="both", expand=True)
        
        action_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        
        view_btn = ctk.CTkButton(action_frame, text="View Details", command=lambda: self.view_task_details(self.task_tree), 
                                fg_color=self.primary_color, width=100)
        view_btn.pack(side="left", padx=5)
        
        if self.current_role == "admin":
            assign_btn = ctk.CTkButton(action_frame, text="Assign Task", command=self.assign_selected_task, 
                                      fg_color=self.success_color, width=100)
            assign_btn.pack(side="left", padx=5)
            
            delete_btn = ctk.CTkButton(action_frame, text="Delete", command=lambda: self.delete_selected_task(self.task_tree), 
                                      fg_color=self.danger_color, width=80)
            delete_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(action_frame, text="Refresh", command=lambda: self.load_task_data(self.task_tree), 
                                  fg_color=self.secondary_text, width=80)
        refresh_btn.pack(side="right", padx=5)
        
        self.load_task_data(self.task_tree)
        self.task_tree.bind("<Double-1>", lambda e: self.view_task_details(self.task_tree))

    def show_employee_task_table(self, parent_frame):
        search_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
        
        self.employee_task_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search tasks...", textvariable=self.employee_task_search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        search_btn = ctk.CTkButton(search_frame, text="Search", command=lambda: self.search_employee_tasks(self.employee_task_tree), width=80)
        search_btn.pack(side="left", padx=5)
        
        self.employee_task_tree = ttk.Treeview(parent_frame, columns=("title", "created_by", "priority", "status", "deadline"), show="headings")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#FFFFFF", 
                       foreground="black", 
                       rowheight=25, 
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", 
                       background=self.primary_color, 
                       foreground="white", 
                       font=('Roboto', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#E1E1E1')])
        
        self.employee_task_tree.heading("title", text="Title")
        self.employee_task_tree.heading("created_by", text="Created By")
        self.employee_task_tree.heading("priority", text="Priority")
        self.employee_task_tree.heading("status", text="Status")
        self.employee_task_tree.heading("deadline", text="Deadline")
        
        self.employee_task_tree.column("title", width=250)
        self.employee_task_tree.column("created_by", width=150)
        self.employee_task_tree.column("priority", width=100)
        self.employee_task_tree.column("status", width=120)
        self.employee_task_tree.column("deadline", width=120)
        
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.employee_task_tree.yview)
        self.employee_task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.employee_task_tree.pack(fill="both", expand=True)
        
        action_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        
        view_btn = ctk.CTkButton(action_frame, text="View Details", command=lambda: self.view_task_details(self.employee_task_tree), 
                                fg_color=self.primary_color, width=100)
        view_btn.pack(side="left", padx=5)
        
        update_btn = ctk.CTkButton(action_frame, text="Update Status", command=self.update_task_status, 
                                  fg_color=self.success_color, width=120)
        update_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(action_frame, text="Refresh", command=lambda: self.load_employee_task_data(self.employee_task_tree), 
                                  fg_color=self.secondary_text, width=80)
        refresh_btn.pack(side="right", padx=5)
        
        self.load_employee_task_data(self.employee_task_tree)
        self.employee_task_tree.bind("<Double-1>", lambda e: self.view_task_details(self.employee_task_tree))

    def show_my_task_table(self, parent_frame):
        search_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
        
        self.my_task_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search tasks...", textvariable=self.my_task_search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        search_btn = ctk.CTkButton(search_frame, text="Search", command=lambda: self.search_my_tasks(self.my_task_tree), width=80)
        search_btn.pack(side="left", padx=5)
        
        self.my_task_tree = ttk.Treeview(parent_frame, columns=("title", "assigned_to", "priority", "status", "deadline"), show="headings")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#FFFFFF", 
                       foreground="black", 
                       rowheight=25, 
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", 
                       background=self.primary_color, 
                       foreground="white", 
                       font=('Roboto', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#E1E1E1')])
        
        self.my_task_tree.heading("title", text="Title")
        self.my_task_tree.heading("assigned_to", text="Assigned To")
        self.my_task_tree.heading("priority", text="Priority")
        self.my_task_tree.heading("status", text="Status")
        self.my_task_tree.heading("deadline", text="Deadline")
        
        self.my_task_tree.column("title", width=250)
        self.my_task_tree.column("assigned_to", width=150)
        self.my_task_tree.column("priority", width=100)
        self.my_task_tree.column("status", width=120)
        self.my_task_tree.column("deadline", width=120)
        
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.my_task_tree.yview)
        self.my_task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.my_task_tree.pack(fill="both", expand=True)
        
        action_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)
        
        view_btn = ctk.CTkButton(action_frame, text="View Details", command=lambda: self.view_task_details(self.my_task_tree), 
                                fg_color=self.primary_color, width=100)
        view_btn.pack(side="left", padx=5)
        
        if self.current_role == "admin":
            delete_btn = ctk.CTkButton(action_frame, text="Delete", command=lambda: self.delete_selected_task(self.my_task_tree), 
                                      fg_color=self.danger_color, width=80)
            delete_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(action_frame, text="Refresh", command=lambda: self.load_my_task_data(self.my_task_tree), 
                                  fg_color=self.secondary_text, width=80)
        refresh_btn.pack(side="right", padx=5)
        
        self.load_my_task_data(self.my_task_tree)
        self.my_task_tree.bind("<Double-1>", lambda e: self.view_task_details(self.my_task_tree))

    def load_task_data(self, tree):
        for item in tree.get_children():
            tree.delete(item)
            
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for task_id, task_data in tasks.items():
            tree.insert("", "end", 
                      values=(
                          task_data.get('title', ''),
                          task_data.get('created_by_name', ''),
                          task_data.get('assigned_to_name', 'Unassigned'),
                          task_data.get('priority', 'Medium'),
                          task_data.get('status', 'Pending'),
                          task_data.get('deadline', 'Not set')
                      ),
                      tags=(task_id,))

    def load_employee_task_data(self, tree):
        for item in tree.get_children():
            tree.delete(item)
            
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for task_id, task_data in tasks.items():
            if task_data.get('assigned_to_id') == self.current_user['id']:
                tree.insert("", "end", 
                          values=(
                              task_data.get('title', ''),
                              task_data.get('created_by_name', ''),
                              task_data.get('priority', 'Medium'),
                              task_data.get('status', 'Pending'),
                              task_data.get('deadline', 'Not set')
                          ),
                          tags=(task_id,))

    def load_my_task_data(self, tree):
        for item in tree.get_children():
            tree.delete(item)
            
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for task_id, task_data in tasks.items():
            if task_data.get('created_by_id') == self.current_user['id']:
                tree.insert("", "end", 
                          values=(
                              task_data.get('title', ''),
                              task_data.get('assigned_to_name', 'Unassigned'),
                              task_data.get('priority', 'Medium'),
                              task_data.get('status', 'Pending'),
                              task_data.get('deadline', 'Not set')
                          ),
                          tags=(task_id,))

    def search_tasks(self, tree):
        query = self.task_search_var.get().lower()
        
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for item in tree.get_children():
            tree.delete(item)
            
        for task_id, task_data in tasks.items():
            if (query in task_data.get('title', '').lower() or 
                query in task_data.get('created_by_name', '').lower() or 
                query in task_data.get('assigned_to_name', '').lower() or 
                query in task_data.get('status', '').lower() or 
                query in task_data.get('priority', '').lower()):
                
                tree.insert("", "end", 
                          values=(
                              task_data.get('title', ''),
                              task_data.get('created_by_name', ''),
                              task_data.get('assigned_to_name', 'Unassigned'),
                              task_data.get('priority', 'Medium'),
                              task_data.get('status', 'Pending'),
                              task_data.get('deadline', 'Not set')
                          ),
                          tags=(task_id,))

    def search_employee_tasks(self, tree):
        query = self.employee_task_search_var.get().lower()
        
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for item in tree.get_children():
            tree.delete(item)
            
        for task_id, task_data in tasks.items():
            if (task_data.get('assigned_to_id') == self.current_user['id'] and 
                (query in task_data.get('title', '').lower() or 
                 query in task_data.get('status', '').lower() or 
                 query in task_data.get('priority', '').lower())):
                
                tree.insert("", "end", 
                          values=(
                              task_data.get('title', ''),
                              task_data.get('created_by_name', ''),
                              task_data.get('priority', 'Medium'),
                              task_data.get('status', 'Pending'),
                              task_data.get('deadline', 'Not set')
                          ),
                          tags=(task_id,))

    def search_my_tasks(self, tree):
        query = self.my_task_search_var.get().lower()
        
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        for item in tree.get_children():
            tree.delete(item)
            
        for task_id, task_data in tasks.items():
            if (task_data.get('created_by_id') == self.current_user['id'] and 
                (query in task_data.get('title', '').lower() or 
                 query in task_data.get('status', '').lower() or 
                 query in task_data.get('priority', '').lower())):
                
                tree.insert("", "end", 
                          values=(
                              task_data.get('title', ''),
                              task_data.get('assigned_to_name', 'Unassigned'),
                              task_data.get('priority', 'Medium'),
                              task_data.get('status', 'Pending'),
                              task_data.get('deadline', 'Not set')
                          ),
                          tags=(task_id,))

    def view_task_details(self, tree, event=None):
        selected_item = tree.selection()
        if not selected_item:
            return
            
        task_id = tree.item(selected_item)['tags'][0]
        
        ref = db.reference(f'tasks/{task_id}')
        task_data = ref.get()
        
        details_window = ctk.CTkToplevel(self)
        details_window.title("Task Details")
        details_window.geometry("700x700")
        
        details_frame = ctk.CTkFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Make the details window scrollable
        canvas = ctk.CTkCanvas(details_frame)
        scrollbar = ctk.CTkScrollbar(details_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Task title
        ctk.CTkLabel(scrollable_frame, text=task_data.get('title', 'No Title'), 
                     font=("Roboto", 20, "bold")).pack(pady=10)
        
        # Status and priority
        info_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(info_frame, text=f"Status: {task_data.get('status', 'Pending')}", 
                     font=("Roboto", 14)).pack(side="left", padx=10)
        
        if task_data.get('priority'):
            ctk.CTkLabel(info_frame, text=f"Priority: {task_data.get('priority', 'Medium')}", 
                         font=("Roboto", 14)).pack(side="left", padx=10)
        
        # Display image if available
        if task_data.get('image_path'):
            try:
                img = Image.open(task_data['image_path'])
                img.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(img)
                
                img_frame = ctk.CTkFrame(scrollable_frame)
                img_frame.pack(pady=10)
                
                img_label = ctk.CTkLabel(img_frame, text="", image=photo)
                img_label.image = photo  # Keep reference
                img_label.pack()
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Description
        desc_frame = ctk.CTkFrame(scrollable_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(desc_frame, text="Description:", font=("Roboto", 14, "bold")).pack(anchor="w")
        desc_text = ctk.CTkTextbox(desc_frame, height=100, wrap="word")
        desc_text.insert("1.0", task_data.get('description', 'No description provided'))
        desc_text.configure(state="disabled")
        desc_text.pack(fill="x", pady=5)
        
        # Requirements (if available)
        if task_data.get('requirements'):
            req_frame = ctk.CTkFrame(scrollable_frame)
            req_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(req_frame, text="Requirements:", font=("Roboto", 14, "bold")).pack(anchor="w")
            req_text = ctk.CTkTextbox(req_frame, height=60, wrap="word")
            req_text.insert("1.0", task_data.get('requirements', ''))
            req_text.configure(state="disabled")
            req_text.pack(fill="x", pady=5)
        
        # Progress bar
        progress_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=10)
        
        status = task_data.get('status', 'Pending')
        progress_value = self.get_progress_value(status)
        progress_color = self.get_status_color(status)
        
        ctk.CTkLabel(progress_frame, text="Progress:", font=("Roboto", 14)).pack(side="left", padx=5)
        
        progress_bar = ctk.CTkProgressBar(progress_frame, orientation="horizontal")
        progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        progress_bar.set(progress_value)
        progress_bar.configure(progress_color=progress_color)
        
        ctk.CTkLabel(progress_frame, text=status, font=("Roboto", 14)).pack(side="left", padx=5)
        
        # Close button
        close_btn = ctk.CTkButton(scrollable_frame, text="Close", command=details_window.destroy)
        close_btn.pack(pady=10)

    def get_progress_value(self, status):
        if status == "Pending":
            return 0.0
        elif status == "Assigned":
            return 0.25
        elif status == "In Progress":
            return 0.5
        elif status == "Completed":
            return 1.0
        else:
            return 0.0

    def get_status_color(self, status):
        if status == "Completed":
            return self.success_color
        elif status == "In Progress":
            return self.warning_color
        elif status == "Assigned":
            return self.primary_color
        else:
            return self.secondary_text

    def assign_selected_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to assign")
            return
            
        task_id = self.task_tree.item(selected_item)['tags'][0]
        
        ref = db.reference(f'tasks/{task_id}')
        task_data = ref.get()
        
        if task_data.get('status') == 'Completed':
            messagebox.showerror("Error", "Cannot assign a completed task")
            return
            
        assign_window = ctk.CTkToplevel(self)
        assign_window.title("Assign Task")
        assign_window.geometry("400x400")
        
        # Create main frame
        main_frame = ctk.CTkFrame(assign_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(main_frame)
        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        # Configure canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        ctk.CTkLabel(scrollable_frame, text="Assign Task", font=("Roboto", 20, "bold")).pack(pady=10)
        
        user_ref = db.reference('users')
        users = user_ref.get() or {}
        employees = [(uid, user['name']) for uid, user in users.items() if user.get('role') == 'employee']
        
        if not employees:
            messagebox.showerror("Error", "No employees available to assign")
            assign_window.destroy()
            return
            
        # Employee selection
        ctk.CTkLabel(scrollable_frame, text="Select Employee:", font=("Roboto", 14)).pack(anchor="w", pady=(10,0))
        self.assign_employee = ctk.CTkOptionMenu(scrollable_frame, values=[name for uid, name in employees])
        self.assign_employee.pack(pady=5, fill="x")
        
        self.employee_mapping = {name: uid for uid, name in employees}
        
        # Priority selection
        ctk.CTkLabel(scrollable_frame, text="Select Priority:", font=("Roboto", 14)).pack(anchor="w", pady=(10,0))
        self.assign_priority = ctk.CTkOptionMenu(scrollable_frame, values=["Low", "Medium", "High"])
        self.assign_priority.pack(pady=5, fill="x")
        
        # Deadline entry
        ctk.CTkLabel(scrollable_frame, text="Enter Deadline:", font=("Roboto", 14)).pack(anchor="w", pady=(10,0))
        self.assign_deadline = ctk.CTkEntry(scrollable_frame, placeholder_text="YYYY-MM-DD")
        self.assign_deadline.pack(pady=5, fill="x")
        
        # Requirements
        ctk.CTkLabel(scrollable_frame, text="Requirements:", font=("Roboto", 14)).pack(anchor="w", pady=(10,0))
        self.assign_requirements = ctk.CTkTextbox(scrollable_frame, height=60)
        self.assign_requirements.pack(pady=5, fill="x")
        
        # Save button with more prominent styling
        save_btn = ctk.CTkButton(scrollable_frame, 
                                text="Save Assignment", 
                                command=lambda: self.save_task_assignment(task_id, assign_window),
                                fg_color=self.primary_color,
                                hover_color="#544DC6",
                                font=("Roboto", 14, "bold"),
                                height=40)
        save_btn.pack(pady=20, fill="x")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(scrollable_frame,
                                  text="Cancel",
                                  command=assign_window.destroy,
                                  fg_color="transparent",
                                  border_color=self.primary_color,
                                  border_width=1,
                                  text_color=self.primary_color)
        cancel_btn.pack(pady=5, fill="x")
        
        # Configure canvas scrolling
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def save_task_assignment(self, task_id, window):
        if not self.assign_deadline.get():
            messagebox.showerror("Error", "Please enter a deadline")
            return
            
        assigned_to_name = self.assign_employee.get()
        assigned_to_id = self.employee_mapping.get(assigned_to_name)
        
        update_data = {
            'assigned_to_id': assigned_to_id,
            'assigned_to_name': assigned_to_name,
            'priority': self.assign_priority.get(),
            'deadline': self.assign_deadline.get(),
            'requirements': self.assign_requirements.get("1.0", "end-1c"),
            'status': 'Assigned'
        }
        
        ref = db.reference(f'tasks/{task_id}')
        ref.update(update_data)
        
        messagebox.showinfo("Success", "Task assigned successfully!")
        window.destroy()
        self.load_task_data(self.task_tree)

    def update_task_status(self):
        selected_item = self.employee_task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to update")
            return
            
        task_id = self.employee_task_tree.item(selected_item)['tags'][0]
        
        ref = db.reference(f'tasks/{task_id}')
        task_data = ref.get()
        
        if task_data.get('status') == 'Completed':
            messagebox.showerror("Error", "Task is already completed")
            return
            
        status_window = ctk.CTkToplevel(self)
        status_window.title("Update Task Status")
        status_window.geometry("400x250")
        
        status_frame = ctk.CTkFrame(status_window)
        status_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(status_frame, text="Update Task Status", font=("Roboto", 20, "bold")).pack(pady=10)
        
        current_status = task_data.get('status', 'Assigned')
        
        self.task_status = ctk.CTkOptionMenu(status_frame, values=["Assigned", "In Progress", "Completed"])
        self.task_status.set(current_status)
        self.task_status.pack(pady=10, fill="x")
        
        update_btn = ctk.CTkButton(status_frame, text="Update", 
                                  command=lambda: self.save_task_status(task_id, status_window),
                                  fg_color=self.primary_color)
        update_btn.pack(pady=10, fill="x")

    def save_task_status(self, task_id, window):
        new_status = self.task_status.get()
        
        update_data = {
            'status': new_status
        }
        
        if new_status == 'Completed':
            update_data['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ref = db.reference(f'tasks/{task_id}')
        ref.update(update_data)
        
        messagebox.showinfo("Success", "Task status updated successfully!")
        window.destroy()
        self.load_employee_task_data(self.employee_task_tree)

    def delete_selected_task(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
            
        task_id = tree.item(selected_item)['tags'][0]
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            return
            
        ref = db.reference(f'tasks/{task_id}')
        ref.delete()
        
        messagebox.showinfo("Success", "Task deleted successfully!")
        
        if tree == self.task_tree:
            self.load_task_data(self.task_tree)
        elif tree == self.my_task_tree:
            self.load_my_task_data(self.my_task_tree)

    def show_task_reports(self):
        self.clear_content()
        
        # Main title
        ctk.CTkLabel(self.content_frame, text="Task Reports", 
                    font=("Roboto", 24, "bold")).pack(pady=10)
        
        # Month selection
        month_frame = ctk.CTkFrame(self.content_frame)
        month_frame.pack(pady=10)
        
        current_month = datetime.now().strftime("%B %Y")
        months = self._get_available_months()  # Implement this to fetch months with tasks
        
        ctk.CTkLabel(month_frame, text="Select Month:").grid(row=0, column=0, padx=5)
        self.month_var = ctk.StringVar(value=current_month)
        month_dropdown = ctk.CTkComboBox(month_frame, 
                                       values=months,
                                       variable=self.month_var,
                                       command=self.update_report_display)
        month_dropdown.grid(row=0, column=1, padx=5)
        
        # Report container
        self.report_container = ctk.CTkFrame(self.content_frame)
        self.report_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Generate PDF button
        pdf_btn = ctk.CTkButton(self.content_frame, 
                               text="Generate PDF Report",
                               command=self.generate_monthly_pdf,
                               fg_color=self.primary_color)
        pdf_btn.pack(pady=20)
        
        # Initial display
        self.update_report_display()
    def update_report_display(self, event=None):
        selected_month = self.month_var.get()
        month, year = selected_month.split()
        month_num = datetime.strptime(month, "%B").month
       
       # Clear previous content
        for widget in self.report_container.winfo_children():
            widget.destroy()
        
        # Get tasks for selected month
        ref = db.reference('tasks')
        all_tasks = ref.get() or {}
        
        # Filter tasks by month
        monthly_tasks = []
        for task_id, task in all_tasks.items():
            if 'created_at' in task:
                task_date = datetime.strptime(task['created_at'].split()[0], "%Y-%m-%d")
                if task_date.month == month_num and task_date.year == int(year):
                    monthly_tasks.append(task)
        
        if not monthly_tasks:
            ctk.CTkLabel(self.report_container, 
                        text=f"No tasks found for {selected_month}",
                        font=("Roboto", 14)).pack(pady=20)
            return
        
        # Get users data
        users_ref = db.reference('users')
        users = users_ref.get() or {}
        
        # Calculate statistics
        status_counts = {'Pending': 0, 'Assigned': 0, 'In Progress': 0, 'Completed': 0}
        for task in monthly_tasks:
            status = task.get('status', 'Pending')
            if status in status_counts:
                status_counts[status] += 1
        
        total_tasks = len(monthly_tasks)
        completed_tasks = status_counts['Completed']
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Employee statistics
        employee_stats = {}
        for task in monthly_tasks:
            if 'assigned_to_id' in task:
                emp_id = task['assigned_to_id']
                if emp_id not in employee_stats:
                    employee_stats[emp_id] = {'name': users.get(emp_id, {}).get('name', 'Unknown'),
                                            'completed': 0, 'total': 0}
                employee_stats[emp_id]['total'] += 1
                if task.get('status') == 'Completed':
                    employee_stats[emp_id]['completed'] += 1
        
        # Create tabs for different report views
        tabview = ctk.CTkTabview(self.report_container)
        tabview.pack(fill="both", expand=True)
        
        # Summary Tab
        summary_tab = tabview.add("Summary")
        
        # Statistics Frame
        stats_frame = ctk.CTkFrame(summary_tab)
        stats_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(stats_frame, text="Monthly Statistics", 
                    font=("Roboto", 16, "bold")).pack(pady=5)
        
        # Stats Grid
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=10)
        
        ctk.CTkLabel(stats_grid, text=f"Total Tasks: {total_tasks}", 
                    font=("Roboto", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_grid, text=f"Completed Tasks: {completed_tasks}", 
                    font=("Roboto", 14)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_grid, text=f"Completion Rate: {completion_rate:.1f}%", 
                    font=("Roboto", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Status Distribution Chart
        chart_frame = ctk.CTkFrame(summary_tab)
        chart_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        ctk.CTkLabel(chart_frame, text="Task Status Distribution", 
                    font=("Roboto", 16, "bold")).pack(pady=5)
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data for pie chart
        labels = [status for status in status_counts.keys() if status_counts[status] > 0]
        sizes = [status_counts[status] for status in labels]
        colors = ['#FF4D4D', '#6C63FF', '#FFC107', '#4CAF50']  # Red, Purple, Yellow, Green
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
        
        # Embed the matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Employee Performance Tab
        if employee_stats:
            employee_tab = tabview.add("Employee Performance")
            
            # Employee stats frame
            emp_stats_frame = ctk.CTkFrame(employee_tab)
            emp_stats_frame.pack(fill="both", expand=True, pady=10, padx=10)
            
             # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(emp_stats_frame)
            scroll_frame.pack(fill="both", expand=True)
            
            # Employee performance chart
            emp_chart_frame = ctk.CTkFrame(scroll_frame)
            emp_chart_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(emp_chart_frame, text="Employee Performance", 
                        font=("Roboto", 16, "bold")).pack(pady=5)
            
            # Prepare data for bar chart
            emp_names = []
            completion_rates = []
            for emp_id, stats in employee_stats.items():
                emp_names.append(stats['name'])
                rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                completion_rates.append(rate)
            
            # Create matplotlib figure
            fig2 = Figure(figsize=(6, 4), dpi=100)
            ax2 = fig2.add_subplot(111)
            
            y_pos = range(len(emp_names))
            bars = ax2.barh(y_pos, completion_rates, color=self.primary_color)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(emp_names)
            ax2.set_xlabel('Completion Rate (%)')
            ax2.set_title('Employee Task Completion Rates')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}%',
                        ha='center', va='center')
            
            # Embed the matplotlib figure
            canvas2 = FigureCanvasTkAgg(fig2, master=emp_chart_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
            
            # Employee details table
            emp_table_frame = ctk.CTkFrame(scroll_frame)
            emp_table_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(emp_table_frame, text="Employee Task Details", 
                        font=("Roboto", 16, "bold")).pack(pady=5)
            
            # Create treeview for employee stats
            emp_tree = ttk.Treeview(emp_table_frame, 
                                   columns=("employee", "completed", "total", "rate"), 
                                   show="headings")
            
            # Style the treeview
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Treeview", 
                           background="#FFFFFF", 
                           foreground="black", 
                           rowheight=25, 
                           fieldbackground="#FFFFFF")
            style.configure("Treeview.Heading", 
                           background=self.primary_color, 
                           foreground="white", 
                           font=('Roboto', 10, 'bold'))
            style.map("Treeview", background=[('selected', '#E1E1E1')])
            
            # Configure columns
            emp_tree.heading("employee", text="Employee")
            emp_tree.heading("completed", text="Completed")
            emp_tree.heading("total", text="Total Tasks")
            emp_tree.heading("rate", text="Completion Rate")
            
            emp_tree.column("employee", width=150)
            emp_tree.column("completed", width=100, anchor="center")
            emp_tree.column("total", width=100, anchor="center")
            emp_tree.column("rate", width=120, anchor="center")
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(emp_table_frame, orient="vertical", command=emp_tree.yview)
            emp_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            emp_tree.pack(fill="both", expand=True)
            
             # Add data
            for emp_id, stats in employee_stats.items():
                rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                emp_tree.insert("", "end", 
                            values=(stats['name'], 
                                    stats['completed'], 
                                    stats['total'],
                                    f"{rate:.1f}%"))

    def generate_monthly_pdf(self):
        selected_month = self.month_var.get()
        month, year = selected_month.split()
        month_num = datetime.strptime(month, "%B").month
        
         # Get tasks for selected month
        ref = db.reference('tasks')
        all_tasks = ref.get() or {}
         
         # Filter tasks by month
        monthly_tasks = []
        for task_id, task in all_tasks.items():
            if 'created_at' in task:
                task_date = datetime.strptime(task['created_at'].split()[0], "%Y-%m-%d")
                if task_date.month == month_num and task_date.year == int(year):
                    monthly_tasks.append(task)
        
        if not monthly_tasks:
            messagebox.showwarning("No Data", f"No tasks found for {selected_month}")
            return
        
         # Get users data
        users_ref = db.reference('users')
        users = users_ref.get() or {}
        
         # Calculate statistics
        status_counts = {'Pending': 0, 'Assigned': 0, 'In Progress': 0, 'Completed': 0}
        for task in monthly_tasks:
            status = task.get('status', 'Pending')
            if status in status_counts:
                status_counts[status] += 1
         
        total_tasks = len(monthly_tasks)
        completed_tasks = status_counts['Completed']
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
         
         # Employee statistics
        employee_stats = {}
        for task in monthly_tasks:
            if 'assigned_to_id' in task:
                emp_id = task['assigned_to_id']
                if emp_id not in employee_stats:
                    employee_stats[emp_id] = {'name': users.get(emp_id, {}).get('name', 'Unknown'),
                                            'completed': 0, 'total': 0}
                employee_stats[emp_id]['total'] += 1
                if task.get('status') == 'Completed':
                    employee_stats[emp_id]['completed'] += 1
         
         # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Roboto", size=12)
         
         # Header with logo
        if self.company_logo:
            try:
                temp_logo_path = "temp_logo.png"
                with open(temp_logo_path, "wb") as logo_file:
                    logo_file.write(bytes.fromhex(self.company_logo))
                pdf.image(temp_logo_path, x=10, y=10, w=30)
                os.remove(temp_logo_path)
            except:
                pass
         
        pdf.set_font("Roboto", 'B', 16)
        pdf.cell(0, 10, f"Task Report - {selected_month}", 0, 1, 'C')
        pdf.ln(15)
         
         # Summary Section
        pdf.set_font("Roboto", 'B', 14)
        pdf.cell(0, 10, "Monthly Summary", 0, 1)
        pdf.set_font("Roboto", size=12)
         
         # Summary stats
        pdf.cell(0, 7, f"Total Tasks: {total_tasks}", 0, 1)
        pdf.cell(0, 7, f"Completed Tasks: {completed_tasks}", 0, 1)
        pdf.cell(0, 7, f"Completion Rate: {completion_rate:.1f}%", 0, 1)
        pdf.ln(10)
         
         # Status Distribution Chart
        pdf.set_font("Roboto", 'B', 14)
        pdf.cell(0, 10, "Task Status Distribution", 0, 1)
         
         # Create a pie chart
        fig = Figure(figsize=(4, 3))
        ax = fig.add_subplot(111)
         
        labels = [status for status in status_counts.keys() if status_counts[status] > 0]
        sizes = [status_counts[status] for status in labels]
        colors = ['#FF4D4D', '#6C63FF', '#FFC107', '#4CAF50']  # Red, Purple, Yellow, Green
         
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Task Status Distribution')
         
         # Save the chart to a temporary file
        chart_path = "temp_chart.png"
        fig.savefig(chart_path, bbox_inches='tight', dpi=100)
        pdf.image(chart_path, x=50, w=100)
        os.remove(chart_path)
        pdf.ln(10)
         
         # Task Details Table
        pdf.set_font("Roboto", 'B', 14)
        pdf.cell(0, 10, "Task Details", 0, 1)
         
         # Table Header
        pdf.set_font("Roboto", 'B', 10)
        pdf.cell(60, 7, "Task", 1, 0)
        pdf.cell(40, 7, "Assigned To", 1, 0)
        pdf.cell(30, 7, "Status", 1, 0)
        pdf.cell(30, 7, "Due Date", 1, 1)
         
         # Table Rows
        pdf.set_font("Roboto", size=9)
        for task in monthly_tasks:
            assigned_to = "Unassigned"
            if 'assigned_to_id' in task:
                user = users.get(task['assigned_to_id'], {})
                assigned_to = user.get('name', 'Unknown')
            
            # Highlight completed tasks
            if task.get('status') == 'Completed':
                pdf.set_fill_color(220, 255, 220)
            else:
                pdf.set_fill_color(255, 255, 255)
             
            pdf.cell(60, 7, task.get('title', 'Untitled')[:30], 1, 0, 'L', 1)
            pdf.cell(40, 7, assigned_to[:20], 1, 0, 'L', 1)
            pdf.cell(30, 7, task.get('status', 'Pending'), 1, 0, 'C', 1)
            pdf.cell(30, 7, task.get('due_date', 'N/A'), 1, 1, 'C', 1)
         
         # Employee Performance Section
        if employee_stats:
            pdf.add_page()
            pdf.set_font("Roboto", 'B', 14)
            pdf.cell(0, 10, "Employee Performance", 0, 1)
            pdf.ln(5)
             
             # Create a bar chart
            fig2 = Figure(figsize=(6, 3))
            ax2 = fig2.add_subplot(111)
             
            emp_names = []
            completion_rates = []
            for emp_id, stats in employee_stats.items():
                emp_names.append(stats['name'])
                rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                completion_rates.append(rate)
             
            y_pos = range(len(emp_names))
            bars = ax2.barh(y_pos, completion_rates, color='#6C63FF')
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(emp_names)
            ax2.set_xlabel('Completion Rate (%)')
            ax2.set_title('Employee Task Completion Rates')
             
             # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}%',
                        ha='center', va='center')
             
             # Save the chart to a temporary file
            chart_path2 = "temp_chart2.png"
            fig2.savefig(chart_path2, bbox_inches='tight', dpi=100)
            pdf.image(chart_path2, x=30, w=150)
            os.remove(chart_path2)
            pdf.ln(10)
             
             # Employee Performance Table
            pdf.set_font("Roboto", 'B', 10)
            pdf.cell(60, 7, "Employee", 1, 0)
            pdf.cell(40, 7, "Completed", 1, 0)
            pdf.cell(40, 7, "Total Tasks", 1, 0)
            pdf.cell(40, 7, "Completion Rate", 1, 1)
             
            pdf.set_font("Roboto", size=9)
            for emp_id, stats in employee_stats.items():
                rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                 
                pdf.cell(60, 7, stats['name'][:25], 1, 0)
                pdf.cell(40, 7, str(stats['completed']), 1, 0, 'C')
                pdf.cell(40, 7, str(stats['total']), 1, 0, 'C')
                pdf.cell(40, 7, f"{rate:.1f}%", 1, 1, 'C')
         
         # Save PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Task_Report_{selected_month.replace(' ', '_')}.pdf"
        )
         
        if file_path:
            pdf.output(file_path)
            if messagebox.askyesno("Success", "Report generated successfully! Would you like to open it now?"):
                webbrowser.open(file_path)

    def _get_available_months(self):
        """Get list of months with task data"""
        ref = db.reference('tasks')
        tasks = ref.get() or {}
        
        months = set()
        for task_id, task in tasks.items():
            if 'created_at' in task:
                task_date = datetime.strptime(task['created_at'].split()[0], "%Y-%m-%d")
                month_str = task_date.strftime("%B %Y")
                months.add(month_str)
         
        return sorted(months, key=lambda x: datetime.strptime(x, "%B %Y"), reverse=True)

    def show_voice_bot(self):
        """Show the voice bot interface in the content frame"""
        # Clear the content frame
        self.clear_content()
        
        # Create a frame for the voice bot
        voice_bot_frame = ctk.CTkFrame(self.content_frame)
        voice_bot_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(voice_bot_frame, text="AI Voice Assistant", 
                    font=("Roboto", 24, "bold"), 
                    text_color=self.text_color).pack(pady=20)
        
        # Status label
        status_label = ctk.CTkLabel(voice_bot_frame, text="Ready", text_color="green")
        status_label.pack(pady=10)
        
        # Conversation text area
        conversation_text = ctk.CTkTextbox(voice_bot_frame, wrap="word", height=400)
        conversation_text.pack(fill="both", expand=True, padx=20, pady=10)
        conversation_text.tag_config("user", foreground="#4fc3f7")
        conversation_text.tag_config("assistant", foreground="#81c784")
        conversation_text.configure(state="disabled")
        
        # Button frame
        button_frame = ctk.CTkFrame(voice_bot_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Initialize voice bot variables
        self.is_listening = False
        self.is_processing = False
        self.stop_speaking = False
        self.conversation_history = []
        
        # Configure speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 155)
        self.engine.setProperty('voice', self.engine.getProperty('voices')[1].id)
        
        # Configure Gemini
        GOOGLE_API_KEY = "AIzaSyDed6l66ws5H2fuvy6Hx-PGkH-GxYvWv6g"  # Replace with your actual API key
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        def update_status(text, color):
            status_label.configure(text=text, text_color=color)
        
        def update_conversation(text, speaker):
            conversation_text.configure(state="normal")
            conversation_text.insert("end", f"{speaker}: {text}\n\n", speaker)
            conversation_text.see("end")
            conversation_text.configure(state="disabled")
        
        def natural_speak(text):
            """More human-like speech with pauses"""
            update_conversation(text, "Assistant")
            
            if self.stop_speaking:
                return
            
            # Split into sentences for more natural pacing
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            for sentence in sentences:
                if self.stop_speaking:  # Check if we should stop speaking
                    self.engine.stop()  # Immediately stop any ongoing speech
                    break
                self.engine.say(sentence)
                self.engine.runAndWait()
                time.sleep(0.3)  # Natural pause between sentences
        
        def listen_for_speech(timeout=5, phrase_time_limit=10):
            """Listen with dynamic timeout based on speech detection"""
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                update_status("Listening...", "blue")
                
                try:
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    update_status("Processing...", "orange")
                    
                    try:
                        text = recognizer.recognize_google(audio)
                        update_conversation(text, "You")
                        return text
                    except sr.UnknownValueError:
                        natural_speak("I didn't quite catch that. Could you repeat?")
                        return None
                    except sr.RequestError:
                        natural_speak("There seems to be a problem with the speech service.")
                        return None
                        
                except sr.WaitTimeoutError:
                    return None
        
        def generate_gemini_response(prompt):
            """Generate response using Gemini AI with conversation context"""
            try:
                # Include last 3 exchanges for context
                context = "\n".join(self.conversation_history[-6:]) if self.conversation_history else ""
                full_prompt = f"{context}\nUser: {prompt}\nAssistant:"
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,  # More creative responses
                        "top_p": 0.9,
                        "max_output_tokens": 200
                    }
                )
                return response.text.strip()
            except Exception as e:
                print(f"API Error: {e}")
                return "I'm having trouble processing that right now. Could you try again?"
        
        def stop_conversation():
            # Stop listening and processing
            self.is_listening = False
            self.is_processing = False
            self.stop_speaking = True
            
            # Stop any ongoing speech immediately
            self.engine.stop()
            
            # Update UI
            listen_button.configure(state="normal")
            stop_button.configure(state="disabled")
            update_status("Ready", "green")
            
            # Clear any ongoing processing
            self.conversation_history = []
            
            # Reset the stop flag after a short delay
            threading.Timer(1.0, lambda: setattr(self, 'stop_speaking', False)).start()
        
        def start_conversation():
            if self.is_listening or self.is_processing:
                return
                
            self.is_listening = True
            self.stop_speaking = False  # Reset stop flag when starting new conversation
            listen_button.configure(state="disabled")
            stop_button.configure(state="normal")
            
            # Initial greeting from Gemini
            initial_prompt = "Greet the user warmly and ask how you can help them today."
            greeting = generate_gemini_response(initial_prompt)
            natural_speak(greeting)
            self.conversation_history.append(f"Assistant: {greeting}")
            
            def conversation_thread():
                while self.is_listening:
                    user_input = listen_for_speech()
                    
                    if user_input is None:
                        if not self.is_listening:  # Check if stopped while listening
                            break
                        continue
                        
                    self.is_processing = True
                    
                    # Generate response from Gemini
                    response = generate_gemini_response(user_input)
                    natural_speak(response)
                    
                    # Update conversation history
                    self.conversation_history.append(f"You: {user_input}")
                    self.conversation_history.append(f"Assistant: {response}")
                    
                    self.is_processing = False
                    
                    # Check for natural conversation end points
                    if any(word in response.lower() for word in ["goodbye", "bye", "see you"]):
                        stop_conversation()
            
            # Start conversation in a separate thread
            threading.Thread(target=conversation_thread).start()
        
        # Create buttons
        listen_button = ctk.CTkButton(
            button_frame, 
            text="Start Conversation",
            command=start_conversation
        )
        listen_button.pack(side="left", padx=10)
        
        stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=stop_conversation,
            state="disabled"
        )
        stop_button.pack(side="left", padx=10)

    def show_admin_chat(self):
        """Show the admin chatbot interface in the content frame"""
        # Clear the content frame
        self.clear_content()
        
        # Create a frame for the chatbot
        chat_frame = ctk.CTkFrame(self.content_frame)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(chat_frame, text="Admin Assistant", 
                    font=("Roboto", 24, "bold"), 
                    text_color=self.text_color).pack(pady=20)
        
        # Create chat area with scrollbar
        chat_container = ctk.CTkFrame(chat_frame)
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas with scrollbar
        canvas = ctk.CTkCanvas(chat_container, bg="white", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(chat_container, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Input frame
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Command entry
        command_entry = ctk.CTkEntry(input_frame, placeholder_text="Type your command...",
                                    font=("Roboto", 14))
        command_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Initialize chat variables
        self.chat_history = []
        self.current_form = None
        self.form_data = {}
        self.form_fields = []
        self.current_field_index = 0
        
        def add_message(sender, message):
            message_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            message_frame.pack(fill="x", pady=5, padx=10)
            
            # Style based on sender
            if sender == "Assistant":
                bg_color = self.primary_color
                text_color = "white"
                align = "w"  # Left alignment for bot
            else:
                bg_color = self.accent_color
                text_color = self.text_color
                align = "e"  # Right alignment for user
            
            # Create message container
            container = ctk.CTkFrame(message_frame, fg_color=bg_color, corner_radius=10)
            container.pack(fill="x", pady=2, padx=5, anchor=align)
            
            # Sender label
            sender_label = ctk.CTkLabel(container, text=f"{sender}:",
                                      font=("Roboto", 12, "bold"),
                                      text_color=text_color)
            sender_label.pack(anchor="w", padx=10, pady=(5, 0))
            
            # Message label
            message_label = ctk.CTkLabel(container, text=message,
                                       font=("Roboto", 12),
                                       text_color=text_color,
                                       wraplength=500)
            message_label.pack(anchor="w", padx=10, pady=(0, 5))
            
            # Update canvas scroll region
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(1.0)
            
            # Add to chat history
            self.chat_history.append(f"{sender}: {message}")
        
        def process_command():
            command = command_entry.get().strip()
            if not command:
                return
                
            # Clear the entry
            command_entry.delete(0, "end")
            
            # Add user message to chat
            add_message("You", command)
            
            # Process the command
            command = command.lower()
            
            try:
                # If we're in a form, handle form input
                if self.current_form:
                    handle_form_input(command, add_message)
                    return

                # User Management
                if any(word in command for word in ["user", "users", "customer", "customers"]):
                    if "add" in command or "create" in command or "new" in command:
                        start_form("user", {
                            'username': 'Enter username',
                            'password': 'Enter password',
                            'name': 'Enter full name',
                            'email': 'Enter email',
                            'phone': 'Enter phone number',
                            'address': 'Enter address',
                            'role': 'Enter role (admin/employee/customer)'
                        }, add_message)
                    elif "delete" in command or "remove" in command:
                        add_message("Assistant", "Please enter the username or email of the user to delete:")
                        self.current_form = "delete_user"
                    elif "edit" in command or "update" in command or "modify" in command:
                        add_message("Assistant", "Please enter the username or email of the user to edit:")
                        self.current_form = "edit_user"
                    else:
                        show_user_table(add_message)
                
                # Task Management
                elif any(word in command for word in ["task", "tasks", "todo", "todos"]):
                    if "add" in command or "create" in command or "new" in command:
                        start_form("task", {
                            'title': 'Enter task title',
                            'description': 'Enter task description',
                            'assigned_to': 'Enter username of assignee',
                            'priority': 'Enter priority (High/Medium/Low)',
                            'deadline': 'Enter deadline (YYYY-MM-DD)'
                        }, add_message)
                    elif "delete" in command or "remove" in command:
                        add_message("Assistant", "Please enter the task ID or title to delete:")
                        self.current_form = "delete_task"
                    elif "edit" in command or "update" in command or "modify" in command:
                        add_message("Assistant", "Please enter the task ID or title to edit:")
                        self.current_form = "edit_task"
                    else:
                        show_task_page(add_message)
                
                # Inventory Management
                elif any(word in command for word in ["inventory", "product", "products", "stock"]):
                    if "add" in command or "create" in command or "new" in command:
                        start_form("product", {
                            'name': 'Enter product name',
                            'description': 'Enter product description',
                            'price': 'Enter price',
                            'quantity': 'Enter quantity',
                            'category': 'Enter category'
                        }, add_message)
                    elif "delete" in command or "remove" in command:
                        add_message("Assistant", "Please enter the product ID or name to delete:")
                        self.current_form = "delete_product"
                    elif "edit" in command or "update" in command or "modify" in command:
                        add_message("Assistant", "Please enter the product ID or name to edit:")
                        self.current_form = "edit_product"
                    else:
                        show_inventory_page(add_message)
                
                # Employee Management
                elif any(word in command for word in ["employee", "employees", "staff"]):
                    if "add" in command or "create" in command or "new" in command:
                        start_form("employee", {
                            'username': 'Enter username',
                            'password': 'Enter password',
                            'name': 'Enter full name',
                            'email': 'Enter email',
                            'phone': 'Enter phone number',
                            'address': 'Enter address',
                            'designation': 'Enter designation'
                        }, add_message)
                    elif "delete" in command or "remove" in command:
                        add_message("Assistant", "Please enter the username or email of the employee to delete:")
                        self.current_form = "delete_employee"
                    elif "edit" in command or "update" in command or "modify" in command:
                        add_message("Assistant", "Please enter the username or email of the employee to edit:")
                        self.current_form = "edit_employee"
                    else:
                        show_employee_management(add_message)
                
                # Billing Management
                elif any(word in command for word in ["billing", "invoice", "invoices", "bill", "bills"]):
                    if "create" in command or "new" in command or "generate" in command:
                        start_form("invoice", {
                            'customer': 'Enter customer username/email',
                            'products': 'Enter products (comma-separated)',
                            'quantities': 'Enter quantities (comma-separated)'
                        }, add_message)
                    elif "delete" in command or "remove" in command:
                        add_message("Assistant", "Please enter the invoice ID to delete:")
                        self.current_form = "delete_invoice"
                    else:
                        show_billing_page(add_message)
                
                # Settings
                elif "setting" in command or "settings" in command:
                    show_settings_page(add_message)
                
                # Statistics
                elif any(word in command for word in ["stat", "statistics", "stats", "report", "reports"]):
                    show_statistics(add_message)
                
                # Help
                elif "help" in command:
                    help_text = """I can help you with the following:

1. User Management:
   - Add/Edit/Delete users
   - View all users
   - Manage user roles

2. Task Management:
   - Create/Edit/Delete tasks
   - Assign tasks
   - Track task progress

3. Inventory Management:
   - Add/Edit/Delete products
   - Check stock levels
   - Update quantities

4. Employee Management:
   - Add/Edit/Delete employees
   - Manage roles and permissions
   - View employee details

5. Billing Management:
   - Create/Delete invoices
   - View billing history
   - Generate reports

6. Other Commands:
   - Settings
   - Statistics/Reports
   - Help (shows this message)

You can use natural language to interact with me. For example:
- "Add a new user"
- "Show me all tasks"
- "Create an invoice for John"
- "Update product stock"
- "Delete employee Sarah"

How can I assist you today?"""
                    add_message("Assistant", help_text)
                
                # Natural language processing for other commands
                else:
                    # Use OpenAI for natural language processing
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful admin assistant for a CRM system. " +
                             "You can help with user management, inventory, billing, and other admin tasks. " +
                             "Keep responses concise and professional. If you don't understand a command, ask for clarification."},
                            {"role": "user", "content": command}
                        ],
                        temperature=0.7
                    )
                    
                    ai_response = response.choices[0].message.content
                    add_message("Assistant", ai_response)
                    
            except Exception as e:
                add_message("Assistant", f"Sorry, I encountered an error: {str(e)}")
                add_message("Assistant", "Please try again or type 'help' to see available commands.")
        
        def start_form(form_type, fields, add_message_func):
            self.current_form = form_type
            self.form_data = {}
            self.form_fields = list(fields.keys())
            self.current_field_index = 0
            
            add_message_func("Assistant", f"Let's add a new {form_type}. Please provide the following information:")
            add_message_func("Assistant", fields[self.form_fields[0]])
        
        def handle_form_input(input_text, add_message_func):
            if self.current_form in ["delete_user", "delete_task", "delete_product", "delete_employee", "delete_invoice"]:
                # Handle deletion
                try:
                    ref = db.reference(self.current_form.split('_')[1] + 's')
                    # Find the item by username/email or ID
                    items = ref.get()
                    if items:
                        for key, item in items.items():
                            if (input_text.lower() in item.get('username', '').lower() or 
                                input_text.lower() in item.get('email', '').lower() or 
                                input_text.lower() in str(item.get('id', ''))):
                                ref.child(key).delete()
                                add_message_func("Assistant", f"{self.current_form.split('_')[1].capitalize()} deleted successfully!")
                                self.current_form = None
                                return
                        
                        add_message_func("Assistant", f"No {self.current_form.split('_')[1]} found with that information.")
                except Exception as e:
                    add_message_func("Assistant", f"Error: {str(e)}")
                finally:
                    self.current_form = None
                return

            # Handle form input
            if self.current_field_index < len(self.form_fields):
                field = self.form_fields[self.current_field_index]
                self.form_data[field] = input_text
                self.current_field_index += 1
                
                if self.current_field_index < len(self.form_fields):
                    next_field = self.form_fields[self.current_field_index]
                    add_message_func("Assistant", f"Please enter the {next_field}:")
                else:
                    # Form is complete, submit it
                    handle_form_submission(self.current_form, self.form_data, add_message_func)
                    self.current_form = None
                    self.form_data = {}
        
        def handle_form_submission(form_type, data, add_message_func):
            try:
                if form_type == "user":
                    # Add user to Firebase
                    ref = db.reference('users')
                    user_data = {
                        'username': data['username'],
                        'password': data['password'],
                        'name': data['name'],
                        'email': data['email'],
                        'phone': data['phone'],
                        'address': data['address'],
                        'role': data['role'],
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ref.push(user_data)
                    add_message_func("Assistant", "User added successfully!")
                    
                elif form_type == "employee":
                    # Add employee to Firebase
                    ref = db.reference('users')
                    employee_data = {
                        'username': data['username'],
                        'password': data['password'],
                        'name': data['name'],
                        'email': data['email'],
                        'phone': data['phone'],
                        'address': data['address'],
                        'role': 'employee',
                        'designation': data['designation'],
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ref.push(employee_data)
                    add_message_func("Assistant", "Employee added successfully!")
                    
                elif form_type == "task":
                    # Add task to Firebase
                    ref = db.reference('tasks')
                    task_data = {
                        'title': data['title'],
                        'description': data['description'],
                        'assigned_to': data['assigned_to'],
                        'priority': data['priority'],
                        'deadline': data['deadline'],
                        'status': 'pending',
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ref.push(task_data)
                    add_message_func("Assistant", "Task created successfully!")
                    
                elif form_type == "product":
                    # Add product to Firebase
                    ref = db.reference('products')
                    product_data = {
                        'name': data['name'],
                        'description': data['description'],
                        'price': float(data['price']),
                        'quantity': int(data['quantity']),
                        'category': data['category'],
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ref.push(product_data)
                    add_message_func("Assistant", "Product added successfully!")
                    
                elif form_type == "invoice":
                    # Add invoice to Firebase
                    ref = db.reference('invoices')
                    products = [p.strip() for p in data['products'].split(',')]
                    quantities = [int(q.strip()) for q in data['quantities'].split(',')]
                    
                    # Calculate total
                    total = 0
                    product_ref = db.reference('products')
                    products_data = product_ref.get()
                    
                    for product, quantity in zip(products, quantities):
                        if products_data:
                            for _, product_data in products_data.items():
                                if product_data.get('name', '').lower() == product.lower():
                                    total += float(product_data.get('price', 0)) * quantity
                                    break
                    
                    invoice_data = {
                        'customer': data['customer'],
                        'products': products,
                        'quantities': quantities,
                        'total': total,
                        'status': 'pending',
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    ref.push(invoice_data)
                    add_message_func("Assistant", "Invoice created successfully!")
                    
            except Exception as e:
                add_message_func("Assistant", f"Error: {str(e)}")
                add_message_func("Assistant", "Please try again.")
        
        def show_user_table(add_message_func):
            try:
                ref = db.reference('users')
                users = ref.get()
                
                if not users:
                    add_message_func("Assistant", "No users found in the database.")
                    return
                
                add_message_func("Assistant", "Here are all the users:")
                for _, user in users.items():
                    user_info = f"Username: {user.get('username', 'N/A')}\n"
                    user_info += f"Name: {user.get('name', 'N/A')}\n"
                    user_info += f"Email: {user.get('email', 'N/A')}\n"
                    user_info += f"Role: {user.get('role', 'N/A')}\n"
                    user_info += f"Created: {user.get('created_at', 'N/A')}\n"
                    add_message_func("Assistant", user_info)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving users: {str(e)}")
        
        def show_task_page(add_message_func):
            try:
                ref = db.reference('tasks')
                tasks = ref.get()
                
                if not tasks:
                    add_message_func("Assistant", "No tasks found in the database.")
                    return
                
                add_message_func("Assistant", "Here are all the tasks:")
                for _, task in tasks.items():
                    task_info = f"Title: {task.get('title', 'N/A')}\n"
                    task_info += f"Description: {task.get('description', 'N/A')}\n"
                    task_info += f"Assigned to: {task.get('assigned_to', 'N/A')}\n"
                    task_info += f"Priority: {task.get('priority', 'N/A')}\n"
                    task_info += f"Deadline: {task.get('deadline', 'N/A')}\n"
                    task_info += f"Status: {task.get('status', 'N/A')}\n"
                    add_message_func("Assistant", task_info)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving tasks: {str(e)}")
        
        def show_inventory_page(add_message_func):
            try:
                ref = db.reference('products')
                products = ref.get()
                
                if not products:
                    add_message_func("Assistant", "No products found in the database.")
                    return
                
                add_message_func("Assistant", "Here are all the products:")
                for _, product in products.items():
                    product_info = f"Name: {product.get('name', 'N/A')}\n"
                    product_info += f"Description: {product.get('description', 'N/A')}\n"
                    product_info += f"Price: ${product.get('price', 'N/A')}\n"
                    product_info += f"Quantity: {product.get('quantity', 'N/A')}\n"
                    product_info += f"Category: {product.get('category', 'N/A')}\n"
                    add_message_func("Assistant", product_info)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving products: {str(e)}")
        
        def show_employee_management(add_message_func):
            try:
                ref = db.reference('users')
                users = ref.get()
                
                if not users:
                    add_message_func("Assistant", "No employees found in the database.")
                    return
                
                add_message_func("Assistant", "Here are all the employees:")
                for _, user in users.items():
                    if user.get('role') == 'employee':
                        employee_info = f"Username: {user.get('username', 'N/A')}\n"
                        employee_info += f"Name: {user.get('name', 'N/A')}\n"
                        employee_info += f"Email: {user.get('email', 'N/A')}\n"
                        employee_info += f"Designation: {user.get('designation', 'N/A')}\n"
                        employee_info += f"Created: {user.get('created_at', 'N/A')}\n"
                        add_message_func("Assistant", employee_info)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving employees: {str(e)}")
        
        def show_billing_page(add_message_func):
            try:
                ref = db.reference('invoices')
                invoices = ref.get()
                
                if not invoices:
                    add_message_func("Assistant", "No invoices found in the database.")
                    return
                
                add_message_func("Assistant", "Here are all the invoices:")
                for _, invoice in invoices.items():
                    invoice_info = f"Customer: {invoice.get('customer', 'N/A')}\n"
                    invoice_info += f"Products: {', '.join(invoice.get('products', []))}\n"
                    invoice_info += f"Quantities: {', '.join(map(str, invoice.get('quantities', [])))}\n"
                    invoice_info += f"Total: ${invoice.get('total', 'N/A')}\n"
                    invoice_info += f"Status: {invoice.get('status', 'N/A')}\n"
                    invoice_info += f"Created: {invoice.get('created_at', 'N/A')}\n"
                    add_message_func("Assistant", invoice_info)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving invoices: {str(e)}")
        
        def show_settings_page(add_message_func):
            add_message_func("Assistant", "Settings page is under construction. Please check back later.")
        
        def show_statistics(add_message_func):
            try:
                # Get counts from different collections
                users_ref = db.reference('users')
                tasks_ref = db.reference('tasks')
                products_ref = db.reference('products')
                invoices_ref = db.reference('invoices')
                
                users = users_ref.get() or {}
                tasks = tasks_ref.get() or {}
                products = products_ref.get() or {}
                invoices = invoices_ref.get() or {}
                
                # Calculate statistics
                total_users = len(users)
                total_employees = sum(1 for user in users.values() if user.get('role') == 'employee')
                total_customers = sum(1 for user in users.values() if user.get('role') == 'customer')
                total_tasks = len(tasks)
                total_products = len(products)
                total_invoices = len(invoices)
                
                # Calculate total revenue
                total_revenue = sum(float(invoice.get('total', 0)) for invoice in invoices.values())
                
                # Display statistics
                stats = f"""System Statistics:

1. Users:
   - Total Users: {total_users}
   - Employees: {total_employees}
   - Customers: {total_customers}

2. Tasks:
   - Total Tasks: {total_tasks}

3. Inventory:
   - Total Products: {total_products}

4. Billing:
   - Total Invoices: {total_invoices}
   - Total Revenue: ${total_revenue:.2f}
"""
                add_message_func("Assistant", stats)
            except Exception as e:
                add_message_func("Assistant", f"Error retrieving statistics: {str(e)}")
        
        # Send button
        send_btn = ctk.CTkButton(input_frame, text="Send",
                                 command=process_command,
                                 width=100)
        send_btn.pack(side="right")
        
        # Bind Enter key
        command_entry.bind("<Return>", lambda e: process_command())
        
        # Welcome message
        add_message("Assistant", "Hello! I'm your admin assistant. How can I help you today?")
        add_message("Assistant", "Type 'help' to see all available commands.")
    def show_about_us(self):
        self.clear_content()
        

        # Create a canvas and scrollbar
        canvas = ctk.CTkCanvas(self.content_frame, bg="white", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.content_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header Section
        header_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Company Logo
        if self.company_settings.get('logo'):
            try:
                image_data = bytes.fromhex(self.company_settings['logo'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                logo_label = ctk.CTkLabel(header_frame, image=photo, text="")
                logo_label.image = photo
                logo_label.pack(pady=20)
            except:
                pass
        
        # Title
        ctk.CTkLabel(header_frame, 
                    text=self.company_settings['about_us'].get('header', "Get a Chance to know About Us and Relive Our Journey"),
                    font=("Roboto", 24, "bold"),
                    text_color=self.primary_color).pack(pady=10)
        
        # Subtitle
        ctk.CTkLabel(header_frame, 
                    text=self.company_settings['about_us'].get('subheader', "Meet our dynamic team and discover the meaning to success as we will let you know how we work."),
                    font=("Roboto", 16),
                    wraplength=800,
                    justify="center").pack(pady=10)
        
        # Separator line
        ctk.CTkFrame(header_frame, height=2, fg_color=self.primary_color).pack(fill="x", pady=20)
        
        # Introduction Section
        intro_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        intro_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(intro_frame, 
                    text=self.company_settings['about_us']['introduction'],
                    font=("Roboto", 16),
                    wraplength=800,
                    justify="left").pack(pady=10)
        
        # Mission and Vision Section
        mission_vision_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        mission_vision_frame.pack(fill="x", pady=(0, 30))
        
        # Mission
        mission_frame = ctk.CTkFrame(mission_vision_frame, fg_color=self.accent_color)
        mission_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(mission_frame, text="Our Mission", 
                    font=("Roboto", 18, "bold"),
                    text_color=self.primary_color).pack(pady=(10, 5))
        
        ctk.CTkLabel(mission_frame, 
                    text=self.company_settings['about_us']['mission'],
                    font=("Roboto", 14),
                    wraplength=800,
                    justify="center").pack(pady=(0, 10))
        
        # Vision
        vision_frame = ctk.CTkFrame(mission_vision_frame, fg_color=self.accent_color)
        vision_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(vision_frame, text="Our Vision", 
                    font=("Roboto", 18, "bold"),
                    text_color=self.primary_color).pack(pady=(10, 5))
        
        ctk.CTkLabel(vision_frame, 
                    text=self.company_settings['about_us']['vision'],
                    font=("Roboto", 14),
                    wraplength=800,
                    justify="center").pack(pady=(0, 10))
        
        # Values Section
        values_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        values_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(values_frame, text="Our Values", 
                    font=("Roboto", 20, "bold"),
                    text_color=self.primary_color).pack(pady=(0, 15))
        
        values = self.company_settings['about_us']['values'].split('\n')
        for value in values:
            if value.strip():
                ctk.CTkLabel(values_frame, 
                            text=f"• {value.strip()}",
                            font=("Roboto", 14),
                            wraplength=800,
                            justify="left").pack(pady=2)
        
        # Team Section
        team_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        team_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(team_frame, text="Our Team", 
                    font=("Roboto", 20, "bold"),
                    text_color=self.primary_color).pack(pady=(0, 15))
        
        # Team Photo
        if self.company_settings['about_us']['images'].get('team_photo'):
            try:
                image_data = bytes.fromhex(self.company_settings['about_us']['images']['team_photo'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                team_photo_label = ctk.CTkLabel(team_frame, image=photo, text="")
                team_photo_label.image = photo
                team_photo_label.pack(pady=10)
            except:
                pass
        
        ctk.CTkLabel(team_frame, 
                    text=self.company_settings['about_us']['team'],
                    font=("Roboto", 14),
                    wraplength=800,
                    justify="center").pack(pady=10)
        
        # Stats Section
        stats_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(stats_frame, text="Our Achievements", 
                    font=("Roboto", 20, "bold"),
                    text_color=self.primary_color).pack(pady=(0, 15))
        
        stats = self.company_settings['about_us']['achievements'].split('\n')
        for stat in stats:
            if stat.strip():
                ctk.CTkLabel(stats_frame, 
                            text=f"• {stat.strip()}",
                            font=("Roboto", 14),
                            wraplength=800,
                            justify="left").pack(pady=2)
        
        # Timeline Section
        timeline_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        timeline_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(timeline_frame, text="Our Journey", 
                    font=("Roboto", 20, "bold"),
                    text_color=self.primary_color).pack(pady=(0, 15))
        
        timeline_events = self.company_settings['about_us'].get('timeline', '').split('\n')
        for event in timeline_events:
            if event.strip():
                ctk.CTkLabel(timeline_frame, 
                            text=f"• {event.strip()}",
                            font=("Roboto", 14),
                            wraplength=800,
                            justify="left").pack(pady=2)
        
        # Office Section
        office_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        office_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(office_frame, text="Our Office", 
                    font=("Roboto", 20, "bold"),
                    text_color=self.primary_color).pack(pady=(0, 15))
        
        # Office Photo
        if self.company_settings['about_us']['images'].get('office_photo'):
            try:
                image_data = bytes.fromhex(self.company_settings['about_us']['images']['office_photo'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                office_photo_label = ctk.CTkLabel(office_frame, image=photo, text="")
                office_photo_label.image = photo
                office_photo_label.pack(pady=10)
            except:
                pass
        
        # Contact Information Section
        contact_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.accent_color)
        contact_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(contact_frame, text="Contact Us", 
                    font=("Roboto", 24, "bold"),
                    text_color=self.primary_color).pack(pady=(20, 15))
        
        # Contact details in a grid
        contact_grid = ctk.CTkFrame(contact_frame, fg_color="text_color")
        contact_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        # Address
        address_frame = ctk.CTkFrame(contact_grid, fg_color="text_color")
        address_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(address_frame, text="📍 Address:", 
                    font=("Roboto", 16, "bold"),
                    text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(address_frame, text=self.company_settings['address'], 
                    font=("Roboto", 16),
                    text_color="white").pack(side="left", padx=10)
        
        # Phone
        phone_frame = ctk.CTkFrame(contact_grid, fg_color="text_color")
        phone_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(phone_frame, text="📞 Phone:", 
                    font=("Roboto", 16, "bold"),
                    text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(phone_frame, text=self.company_settings['phone'], 
                    font=("Roboto", 16),
                    text_color="white").pack(side="left", padx=10)
        
        # Email
        email_frame = ctk.CTkFrame(contact_grid, fg_color="text_color")
        email_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(email_frame, text="✉️ Email:", 
                    font=("Roboto", 16, "bold"),
                    text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(email_frame, text=self.company_settings['email'], 
                    font=("Roboto", 16),
                    text_color="white").pack(side="left", padx=10)
        
        # Website
        website_frame = ctk.CTkFrame(contact_grid, fg_color="text_color")
        website_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(website_frame, text="🌐 Website:", 
                    font=("Roboto", 16, "bold"),
                    text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(website_frame, text=self.company_settings['text_color'], 
                    font=("Roboto", 16),
                    text_color="white").pack(side="left", padx=10)
        
        # Call to Action Button
        cta_button = ctk.CTkButton(contact_frame, 
                                 text="Get in Touch",
                                 font=("Roboto", 16, "bold"),
                                 fg_color="white",
                                 text_color=self.primary_color,
                                 hover_color="#F5F5F5",
                                 command=lambda: self.navigate("Help Center"))
        cta_button.pack(pady=(0, 20))


    def show_about_us_admin_page(self):
        self.clear_content()
        
        # Create a canvas and scrollbar
        canvas = ctk.CTkCanvas(self.content_frame, bg="white", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.content_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((500, 600), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main title
        ctk.CTkLabel(scrollable_frame, text="Edit About Us Page", 
                    font=("Roboto", 24, "bold"),
                    text_color=self.text_color).pack(pady=20)
        
        # Create a tabview for different sections
        tabview = ctk.CTkTabview(scrollable_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add tabs for each section
        tabview.add("Main Content")
        tabview.add("Team")
        tabview.add("Stats")
        tabview.add("Values")
        tabview.add("Timeline")
        
        
        # Main Content Tab
        main_content_frame = tabview.tab("Main Content")
        
        # Title
        ctk.CTkLabel(main_content_frame, text="Main Page Content", 
                    font=("Roboto", 18, "bold")).pack(pady=(0, 10), anchor="w")
        
        # Header Text
        ctk.CTkLabel(main_content_frame, text="Header Text:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.about_header_entry = ctk.CTkEntry(main_content_frame)
        self.about_header_entry.pack(fill="x", pady=5)
        self.about_header_entry.insert(0, "Get a Chance to know About Us and Relive Our Journey")
        
        # Subheader Text
        ctk.CTkLabel(main_content_frame, text="Subheader Text:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.about_subheader_entry = ctk.CTkEntry(main_content_frame)
        self.about_subheader_entry.pack(fill="x", pady=5)
        self.about_subheader_entry.insert(0, "Meet our dynamic team and discover the meaning to success as we will let you know how we work.")
        
        # Introduction Text
        ctk.CTkLabel(main_content_frame, text="Introduction Text:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.about_intro_entry = ctk.CTkTextbox(main_content_frame, height=100)
        self.about_intro_entry.pack(fill="x", pady=5)
        self.about_intro_entry.insert("1.0", self.company_settings['about_us']['introduction'])
        
        # Mission Text
        ctk.CTkLabel(main_content_frame, text="Mission Text:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.about_mission_entry = ctk.CTkTextbox(main_content_frame, height=60)
        self.about_mission_entry.pack(fill="x", pady=5)
        self.about_mission_entry.insert("1.0", self.company_settings['about_us']['mission'])
        
        # Vision Text
        ctk.CTkLabel(main_content_frame, text="Vision Text:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.about_vision_entry = ctk.CTkTextbox(main_content_frame, height=60)
        self.about_vision_entry.pack(fill="x", pady=5)
        self.about_vision_entry.insert("1.0", self.company_settings['about_us']['vision'])
        
        # Team Tab
        team_frame = tabview.tab("Team")
        
        # Team Section Title
        ctk.CTkLabel(team_frame, text="Team Section Title:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.team_title_entry = ctk.CTkEntry(team_frame)
        self.team_title_entry.pack(fill="x", pady=5)
        self.team_title_entry.insert(0, "Meet Our Team")
        
        # Team Description
        ctk.CTkLabel(team_frame, text="Team Description:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.team_desc_entry = ctk.CTkTextbox(team_frame, height=100)
        self.team_desc_entry.pack(fill="x", pady=5)
        self.team_desc_entry.insert("1.0", self.company_settings['about_us']['team'])
        
        # Stats Tab
        stats_frame = tabview.tab("Stats")
        
        # Stats Section Title
        ctk.CTkLabel(stats_frame, text="Stats Section Title:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.stats_title_entry = ctk.CTkEntry(stats_frame)
        self.stats_title_entry.pack(fill="x", pady=5)
        self.stats_title_entry.insert(0, "Our Achievements")
        
        # Stats List
        ctk.CTkLabel(stats_frame, text="Stats (one per line):", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.stats_entry = ctk.CTkTextbox(stats_frame, height=150)
        self.stats_entry.pack(fill="x", pady=5)
        self.stats_entry.insert("1.0", self.company_settings['about_us']['achievements'])
        
        # Values Tab
        values_frame = tabview.tab("Values")
        
        # Values Section Title
        ctk.CTkLabel(values_frame, text="Values Section Title:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.values_title_entry = ctk.CTkEntry(values_frame)
        self.values_title_entry.pack(fill="x", pady=5)
        self.values_title_entry.insert(0, "Our Values")
        
        # Values List
        ctk.CTkLabel(values_frame, text="Values (one per line):", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.values_entry = ctk.CTkTextbox(values_frame, height=150)
        self.values_entry.pack(fill="x", pady=5)
        self.values_entry.insert("1.0", self.company_settings['about_us']['values'])
        
        # Timeline Tab
        timeline_frame = tabview.tab("Timeline")
        
        # Timeline Section Title
        ctk.CTkLabel(timeline_frame, text="Timeline Section Title:", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.timeline_title_entry = ctk.CTkEntry(timeline_frame)
        self.timeline_title_entry.pack(fill="x", pady=5)
        self.timeline_title_entry.insert(0, "Our Journey")
        
        # Timeline Events
        ctk.CTkLabel(timeline_frame, text="Timeline Events (one per line, format: Year - Event):", 
                    font=("Roboto", 14)).pack(pady=(10, 5), anchor="w")
        self.timeline_entry = ctk.CTkTextbox(timeline_frame, height=200)
        self.timeline_entry.pack(fill="x", pady=5)
        self.timeline_entry.insert("1.0", self.company_settings['about_us'].get('timeline', ''))
        
        # Images Tab
        images_frame = tabview.tab("Images")
        
        # Team Photo
        ctk.CTkLabel(images_frame, text="Team Photo:", 
                    font=("Roboto", 14)).pack(pady=(20, 5), anchor="w")
        self.team_photo_frame = ctk.CTkFrame(images_frame, fg_color="transparent")
        self.team_photo_frame.pack(fill="x", pady=5)
        
        if self.company_settings['about_us']['images'].get('team_photo'):
            try:
                image_data = bytes.fromhex(self.company_settings['about_us']['images']['team_photo'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.team_photo_label = ctk.CTkLabel(self.team_photo_frame, image=photo, text="")
                self.team_photo_label.image = photo
                self.team_photo_label.pack(side="left", padx=10)
            except:
                pass
        
        upload_team_btn = ctk.CTkButton(images_frame, text="Upload Team Photo", command=lambda: self.upload_image('team_photo'))
        upload_team_btn.pack(pady=5)
        
        # Office Photo
        ctk.CTkLabel(images_frame, text="Office Photo:", 
                    font=("Roboto", 14)).pack(pady=(20, 5), anchor="w")
        self.office_photo_frame = ctk.CTkFrame(images_frame, fg_color="transparent")
        self.office_photo_frame.pack(fill="x", pady=5)
        
        if self.company_settings['about_us']['images'].get('office_photo'):
            try:
                image_data = bytes.fromhex(self.company_settings['about_us']['images']['office_photo'])
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.office_photo_label = ctk.CTkLabel(self.office_photo_frame, image=photo, text="")
                self.office_photo_label.image = photo
                self.office_photo_label.pack(side="left", padx=10)
            except:
                pass
        
        upload_office_btn = ctk.CTkButton(images_frame, text="Upload Office Photo", command=lambda: self.upload_image('office_photo'))
        upload_office_btn.pack(pady=5)
        
        # Save Button
        save_button = ctk.CTkButton(scrollable_frame, 
                                  text="Save About Us Page",
                                  font=("Roboto", 16, "bold"),
                                  fg_color=self.primary_color,
                                  command=self.save_about_us_settings)
        save_button.pack(pady=20)


    def save_about_us_settings(self):
        try:
            # Update company settings with new about us content
            self.company_settings['about_us'] = {
                'introduction': self.about_intro_entry.get("1.0", "end-1c"),
                'mission': self.about_mission_entry.get("1.0", "end-1c"),
                'vision': self.about_vision_entry.get("1.0", "end-1c"),
                'values': self.values_entry.get("1.0", "end-1c"),
                'team': self.team_desc_entry.get("1.0", "end-1c"),
                'achievements': self.stats_entry.get("1.0", "end-1c"),
                'locations': self.timeline_entry.get("1.0", "end-1c"),
                'images': {
                    'team_photo': self.team_photo_frame.cget("image"),
                    'office_photo': self.office_photo_frame.cget("image")
                }
            }
            
            # Save to Firebase
            ref = db.reference('company_settings')
            ref.update(self.company_settings)
            
            messagebox.showinfo("Success", "About Us page settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    
if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()