import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkinter import filedialog
import os

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('claims_management.db')
        self.create_tables()
        self.create_default_data()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                         UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Login TEXT UNIQUE NOT NULL,
                         Password TEXT NOT NULL,
                         FullName TEXT NOT NULL,
                         RoleID INTEGER NOT NULL,
                         DepartmentID INTEGER,
                         PositionID INTEGER,
                         FOREIGN KEY(RoleID) REFERENCES Roles(RoleID),
                         FOREIGN KEY(DepartmentID) REFERENCES Departments(DepartmentID),
                         FOREIGN KEY(PositionID) REFERENCES Positions(PositionID))''')
        
        # Roles table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Roles (
                         RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Name TEXT UNIQUE NOT NULL,
                         CanCreate BOOLEAN DEFAULT 0,
                         CanApprove BOOLEAN DEFAULT 0,
                         CanExecute BOOLEAN DEFAULT 0)''')
        
        # Departments table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Departments (
                         DepartmentID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Name TEXT UNIQUE NOT NULL)''')
        
        # Positions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Positions (
                         PositionID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Name TEXT UNIQUE NOT NULL)''')
        
        # Countries table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Countries (
                         CountryID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Name TEXT UNIQUE NOT NULL)''')
        
        # Clients table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Clients (
                         ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Name TEXT NOT NULL,
                         Address TEXT,
                         Phone TEXT,
                         Email TEXT,
                         ContactPerson TEXT,
                         CountryID INTEGER,
                         FOREIGN KEY(CountryID) REFERENCES Countries(CountryID))''')
        
        # Claims table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Claims (
                         ClaimID INTEGER PRIMARY KEY AUTOINCREMENT,
                         Title TEXT NOT NULL,
                         Description TEXT,
                         ClientID INTEGER,
                         CreatedBy INTEGER NOT NULL,
                         ApprovedBy INTEGER,
                         ExecutedBy INTEGER,
                         CreationDate DATETIME NOT NULL,
                         ApprovalDate DATETIME,
                         ExecutionDate DATETIME,
                         Status TEXT DEFAULT 'New',
                         FOREIGN KEY(ClientID) REFERENCES Clients(ClientID),
                         FOREIGN KEY(CreatedBy) REFERENCES Users(UserID),
                         FOREIGN KEY(ApprovedBy) REFERENCES Users(UserID),
                         FOREIGN KEY(ExecutedBy) REFERENCES Users(UserID))''')
        
        self.conn.commit()
    
    def create_default_data(self):
        cursor = self.conn.cursor()
        
        # Check if admin role exists
        cursor.execute("SELECT COUNT(*) FROM Roles WHERE Name='Administrator'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Roles (Name, CanCreate, CanApprove, CanExecute) VALUES (?, ?, ?, ?)",
                          ('Administrator', 1, 1, 1))
            cursor.execute("INSERT INTO Roles (Name, CanCreate, CanApprove, CanExecute) VALUES (?, ?, ?, ?)",
                          ('Manager', 1, 1, 0))
            cursor.execute("INSERT INTO Roles (Name, CanCreate, CanApprove, CanExecute) VALUES (?, ?, ?, ?)",
                          ('User', 1, 0, 0))
            cursor.execute("INSERT INTO Roles (Name, CanCreate, CanApprove, CanExecute) VALUES (?, ?, ?, ?)",
                          ('Executor', 0, 0, 1))
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Login='Admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT RoleID FROM Roles WHERE Name='Administrator'")
            role_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO Users (Login, Password, FullName, RoleID) VALUES (?, ?, ?, ?)",
                          ('Admin', '111', 'System Administrator', role_id))
        
        # Add some sample departments
        departments = ['IT', 'Finance', 'HR', 'Operations', 'Sales']
        for dept in departments:
            cursor.execute("SELECT COUNT(*) FROM Departments WHERE Name=?", (dept,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Departments (Name) VALUES (?)", (dept,))
        
        # Add some sample positions
        positions = ['Director', 'Manager', 'Specialist', 'Assistant', 'Engineer']
        for pos in positions:
            cursor.execute("SELECT COUNT(*) FROM Positions WHERE Name=?", (pos,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Positions (Name) VALUES (?)", (pos,))
        
        # Add some sample countries
        countries = ['USA', 'UK', 'Germany', 'France', 'Japan']
        for country in countries:
            cursor.execute("SELECT COUNT(*) FROM Countries WHERE Name=?", (country,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Countries (Name) VALUES (?)", (country,))
        
        self.conn.commit()
    
    def get_user_by_credentials(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT u.*, r.Name as RoleName, r.CanCreate, r.CanApprove, r.CanExecute 
                          FROM Users u JOIN Roles r ON u.RoleID = r.RoleID 
                          WHERE u.Login=? AND u.Password=?''', (username, password))
        return cursor.fetchone()
    
    def close(self):
        self.conn.close()

class LoginForm:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        master.title("Claims Management System - Login")
        master.geometry("400x300")
        master.resizable(False, False)
        
        # Center the window
        window_width = master.winfo_reqwidth()
        window_height = master.winfo_reqheight()
        position_right = int(master.winfo_screenwidth()/2 - window_width/2)
        position_down = int(master.winfo_screenheight()/2 - window_height/2)
        master.geometry(f"+{position_right}+{position_down}")
        
        # Logo or header image would go here
        self.header_label = ttk.Label(master, text="Claims Management System", font=('Arial', 16, 'bold'))
        self.header_label.pack(pady=20)
        
        # Login frame
        login_frame = ttk.Frame(master, padding="20")
        login_frame.pack(pady=10)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)
        self.username_entry.focus()
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        # Login button
        self.login_button = ttk.Button(login_frame, text="Login", command=self.authenticate)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Bind Enter key to login
        master.bind('<Return>', lambda event: self.authenticate())
    
    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        user = self.db.get_user_by_credentials(username, password)
        
        if user:
            self.master.withdraw()
            main_root = tk.Toplevel()
            MainApplication(main_root, self.db, user)
            main_root.protocol("WM_DELETE_WINDOW", lambda: self.on_main_close(main_root))
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def on_main_close(self, window):
        window.destroy()
        self.master.deiconify()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

class MainApplication:
    def __init__(self, master, db, user):
        self.master = master
        self.db = db
        self.user = user
        self.current_user_id = user[0]
        self.current_user_name = user[3]
        self.user_role = user[8]
        self.can_create = bool(user[9])
        self.can_approve = bool(user[10])
        self.can_execute = bool(user[11])
        
        master.title(f"Claims Management System - {self.user_role}: {self.current_user_name}")
        master.geometry("1000x700")
        
        # Menu Bar
        self.create_menu_bar()
        
        # Status Bar
        self.statusbar = ttk.Label(master, text=f"User: {self.current_user_name} | Role: {self.user_role} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Notebook (Tab control)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_claims_tab()
        self.create_approval_tab()
        self.create_execution_tab()
        self.create_reports_tab()
        
        # Update clock
        self.update_clock()
    
    def create_menu_bar(self):
        menubar = tk.Menu(self.master)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Change User", command=self.change_user)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Administration menu (only for admins)
        if self.user_role == 'Administrator':
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(label="User Management", command=self.open_user_management)
            admin_menu.add_command(label="Role Management", command=self.open_role_management)
            menubar.add_cascade(label="Administration", menu=admin_menu)
        
        # References menu
        ref_menu = tk.Menu(menubar, tearoff=0)
        ref_menu.add_command(label="Clients", command=self.open_client_management)
        ref_menu.add_command(label="Countries", command=self.open_country_management)
        ref_menu.add_command(label="Departments", command=self.open_department_management)
        ref_menu.add_command(label="Positions", command=self.open_position_management)
        menubar.add_cascade(label="References", menu=ref_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)
    
    def create_claims_tab(self):
        self.claims_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.claims_tab, text="My Claims")
        
        # Treeview for claims
        columns = ("ID", "Title", "Client", "Created", "Status")
        self.claims_tree = ttk.Treeview(self.claims_tab, columns=columns, show="headings", selectmode='browse')
        
        for col in columns:
            self.claims_tree.heading(col, text=col)
            self.claims_tree.column(col, width=100, anchor=tk.W)
        
        self.claims_tree.column("ID", width=50)
        self.claims_tree.column("Title", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.claims_tab, orient=tk.VERTICAL, command=self.claims_tree.yview)
        self.claims_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.claims_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.claims_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_new_claim = ttk.Button(btn_frame, text="New Claim", command=self.new_claim, 
                                      state=tk.NORMAL if self.can_create else tk.DISABLED)
        self.btn_new_claim.pack(side=tk.LEFT, padx=5)
        
        self.btn_edit_claim = ttk.Button(btn_frame, text="Edit", command=self.edit_claim)
        self.btn_edit_claim.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete_claim = ttk.Button(btn_frame, text="Delete", command=self.delete_claim)
        self.btn_delete_claim.pack(side=tk.LEFT, padx=5)
        
        self.btn_view_claim = ttk.Button(btn_frame, text="View Details", command=self.view_claim)
        self.btn_view_claim.pack(side=tk.LEFT, padx=5)
        
        self.btn_refresh = ttk.Button(btn_frame, text="Refresh", command=self.load_claims)
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.load_claims()
    
    def create_approval_tab(self):
        self.approval_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.approval_tab, text="For Approval")
        
        # Treeview for approval queue
        columns = ("ID", "Title", "Client", "Created By", "Created", "Status")
        self.approval_tree = ttk.Treeview(self.approval_tab, columns=columns, show="headings", selectmode='browse')
        
        for col in columns:
            self.approval_tree.heading(col, text=col)
            self.approval_tree.column(col, width=100, anchor=tk.W)
        
        self.approval_tree.column("ID", width=50)
        self.approval_tree.column("Title", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.approval_tab, orient=tk.VERTICAL, command=self.approval_tree.yview)
        self.approval_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.approval_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.approval_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_approve = ttk.Button(btn_frame, text="Approve", command=self.approve_claim,
                                     state=tk.NORMAL if self.can_approve else tk.DISABLED)
        self.btn_approve.pack(side=tk.LEFT, padx=5)
        
        self.btn_reject = ttk.Button(btn_frame, text="Reject", command=self.reject_claim,
                                    state=tk.NORMAL if self.can_approve else tk.DISABLED)
        self.btn_reject.pack(side=tk.LEFT, padx=5)
        
        self.btn_view_for_approval = ttk.Button(btn_frame, text="View Details", command=self.view_claim_for_approval)
        self.btn_view_for_approval.pack(side=tk.LEFT, padx=5)
        
        self.btn_refresh_approval = ttk.Button(btn_frame, text="Refresh", command=self.load_approval_queue)
        self.btn_refresh_approval.pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.load_approval_queue()
    
    def create_execution_tab(self):
        self.execution_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.execution_tab, text="For Execution")
        
        # Treeview for execution queue
        columns = ("ID", "Title", "Client", "Approved By", "Approved", "Status")
        self.execution_tree = ttk.Treeview(self.execution_tab, columns=columns, show="headings", selectmode='browse')
        
        for col in columns:
            self.execution_tree.heading(col, text=col)
            self.execution_tree.column(col, width=100, anchor=tk.W)
        
        self.execution_tree.column("ID", width=50)
        self.execution_tree.column("Title", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.execution_tab, orient=tk.VERTICAL, command=self.execution_tree.yview)
        self.execution_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.execution_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.execution_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_execute = ttk.Button(btn_frame, text="Mark as Executed", command=self.execute_claim,
                                    state=tk.NORMAL if self.can_execute else tk.DISABLED)
        self.btn_execute.pack(side=tk.LEFT, padx=5)
        
        self.btn_view_for_execution = ttk.Button(btn_frame, text="View Details", command=self.view_claim_for_execution)
        self.btn_view_for_execution.pack(side=tk.LEFT, padx=5)
        
        self.btn_refresh_execution = ttk.Button(btn_frame, text="Refresh", command=self.load_execution_queue)
        self.btn_refresh_execution.pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.load_execution_queue()
    
    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Add report controls here
        ttk.Label(self.reports_tab, text="Reports will be available in future versions", 
                 font=('Arial', 12)).pack(pady=50)
    
    def load_claims(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''SELECT c.ClaimID, c.Title, cl.Name as ClientName, 
                         c.CreationDate, c.Status
                         FROM Claims c
                         LEFT JOIN Clients cl ON c.ClientID = cl.ClientID
                         WHERE c.CreatedBy = ?
                         ORDER BY c.CreationDate DESC''', (self.current_user_id,))
        
        # Clear existing data
        for row in self.claims_tree.get_children():
            self.claims_tree.delete(row)
            
        # Add new data
        for row in cursor.fetchall():
            self.claims_tree.insert("", tk.END, values=row)
    
    def load_approval_queue(self):
        if not self.can_approve:
            return
            
        cursor = self.db.conn.cursor()
        cursor.execute('''SELECT c.ClaimID, c.Title, cl.Name as ClientName, 
                         u.FullName as Creator, c.CreationDate, c.Status
                         FROM Claims c
                         LEFT JOIN Clients cl ON c.ClientID = cl.ClientID
                         JOIN Users u ON c.CreatedBy = u.UserID
                         WHERE c.ApprovedBy IS NULL AND c.Status != 'Rejected'
                         ORDER BY c.CreationDate''')
        
        # Clear existing data
        for row in self.approval_tree.get_children():
            self.approval_tree.delete(row)
            
        # Add new data
        for row in cursor.fetchall():
            self.approval_tree.insert("", tk.END, values=row)
    
    def load_execution_queue(self):
        if not self.can_execute:
            return
            
        cursor = self.db.conn.cursor()
        cursor.execute('''SELECT c.ClaimID, c.Title, cl.Name as ClientName, 
                         u.FullName as Approver, c.ApprovalDate, c.Status
                         FROM Claims c
                         LEFT JOIN Clients cl ON c.ClientID = cl.ClientID
                         JOIN Users u ON c.ApprovedBy = u.UserID
                         WHERE c.ExecutedBy IS NULL AND c.Status = 'Approved'
                         ORDER BY c.ApprovalDate''')
        
        # Clear existing data
        for row in self.execution_tree.get_children():
            self.execution_tree.delete(row)
            
        # Add new data
        for row in cursor.fetchall():
            self.execution_tree.insert("", tk.END, values=row)
    
    def new_claim(self):
        form = ClaimForm(self.master, self.db, self.current_user_id, mode='new')
        form.show()
        self.load_claims()
    
    def edit_claim(self):
        selected = self.claims_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to edit")
            return
        
        claim_id = self.claims_tree.item(selected)['values'][0]
        form = ClaimForm(self.master, self.db, self.current_user_id, mode='edit', claim_id=claim_id)
        form.show()
        self.load_claims()
    
    def view_claim(self):
        selected = self.claims_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to view")
            return
        
        claim_id = self.claims_tree.item(selected)['values'][0]
        form = ClaimForm(self.master, self.db, self.current_user_id, mode='view', claim_id=claim_id)
        form.show()
    
    def delete_claim(self):
        selected = self.claims_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to delete")
            return
        
        claim_id = self.claims_tree.item(selected)['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this claim?"):
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM Claims WHERE ClaimID=?", (claim_id,))
            self.db.conn.commit()
            self.load_claims()
    
    def approve_claim(self):
        selected = self.approval_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to approve")
            return
        
        claim_id = self.approval_tree.item(selected)['values'][0]
        
        cursor = self.db.conn.cursor()
        cursor.execute('''UPDATE Claims 
                         SET ApprovedBy=?, ApprovalDate=?, Status='Approved'
                         WHERE ClaimID=?''', 
                      (self.current_user_id, datetime.now(), claim_id))
        self.db.conn.commit()
        
        messagebox.showinfo("Success", "Claim approved successfully")
        self.load_approval_queue()
        self.load_execution_queue()
    
    def reject_claim(self):
        selected = self.approval_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to reject")
            return
        
        claim_id = self.approval_tree.item(selected)['values'][0]
        
        cursor = self.db.conn.cursor()
        cursor.execute('''UPDATE Claims 
                         SET Status='Rejected'
                         WHERE ClaimID=?''', 
                      (claim_id,))
        self.db.conn.commit()
        
        messagebox.showinfo("Success", "Claim rejected")
        self.load_approval_queue()
    
    def execute_claim(self):
        selected = self.execution_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to mark as executed")
            return
        
        claim_id = self.execution_tree.item(selected)['values'][0]
        
        cursor = self.db.conn.cursor()
        cursor.execute('''UPDATE Claims 
                         SET ExecutedBy=?, ExecutionDate=?, Status='Executed'
                         WHERE ClaimID=?''', 
                      (self.current_user_id, datetime.now(), claim_id))
        self.db.conn.commit()
        
        messagebox.showinfo("Success", "Claim marked as executed")
        self.load_execution_queue()
    
    def view_claim_for_approval(self):
        selected = self.approval_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to view")
            return
        
        claim_id = self.approval_tree.item(selected)['values'][0]
        form = ClaimForm(self.master, self.db, self.current_user_id, mode='view', claim_id=claim_id)
        form.show()
    
    def view_claim_for_execution(self):
        selected = self.execution_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a claim to view")
            return
        
        claim_id = self.execution_tree.item(selected)['values'][0]
        form = ClaimForm(self.master, self.db, self.current_user_id, mode='view', claim_id=claim_id)
        form.show()
    
    def change_user(self):
        self.master.destroy()
        root = tk.Tk()
        LoginForm(root, self.db)
        root.mainloop()
    
    def open_user_management(self):
        form = UserManagementForm(self.master, self.db)
        form.show()
    
    def open_role_management(self):
        form = RoleManagementForm(self.master, self.db)
        form.show()
    
    def open_client_management(self):
        form = ClientManagementForm(self.master, self.db)
        form.show()
    
    def open_country_management(self):
        form = CountryManagementForm(self.master, self.db)
        form.show()
    
    def open_department_management(self):
        form = DepartmentManagementForm(self.master, self.db)
        form.show()
    
    def open_position_management(self):
        form = PositionManagementForm(self.master, self.db)
        form.show()
    
    def show_about(self):
        about_text = """Claims Management System
Version 1.0
Developed for Company XYZ
        
© 2023 All Rights Reserved"""
        messagebox.showinfo("About", about_text)
    
    def update_clock(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.statusbar.config(text=f"User: {self.current_user_name} | Role: {self.user_role} | Date: {now}")
        self.master.after(1000, self.update_clock)

# All the management forms would be defined here (UserManagementForm, RoleManagementForm, etc.)
# As well as the ClaimForm for creating/editing/viewing claims

if __name__ == "__main__":
    # Initialize database
    db = Database()
    
    # Create and run login form
    root = tk.Tk()
    login_form = LoginForm(root, db)
    root.mainloop()
    
    # Close database connection when done
    db.close()