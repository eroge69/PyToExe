

import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from datetime import datetime

# Database Connection Function
def connect_db():
    try:
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=DESKTOP-AR9A3PR\\SQLEXPRESS;"
            "Database=i_score_db;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to connect to database:\n{str(e)}")
        return None

# ========== Helper Functions ==========
def setup_tab_with_treeview(tab, columns, column_settings):
    frame = ttk.Frame(tab)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tree_scroll_y = ttk.Scrollbar(frame)
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree_scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree = ttk.Treeview(frame, columns=columns, show='headings', 
                       yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    for col, settings in column_settings.items():
        tree.heading(col, text=col)
        tree.column(col, **settings)
    
    tab.treeview = tree
    return tree

def get_treeview(tab):
    return tab.treeview

def clear_form():
    entries["CustomerID"].delete(0, tk.END)
    entries["CustomerID"].insert(0, str(get_next_customer_id()))
    for label, widget in entries.items():
        if label != "CustomerID":
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)

def on_customer_select(event):
    selected = tree_customers.selection()
    if not selected:
        return
    item = tree_customers.item(selected[0])
    values = item["values"]
    for i, label in enumerate(labels):
        if label in entries:
            widget = entries[label]
            if isinstance(widget, ttk.Combobox):
                widget.set(values[i] if i < len(values) else "")
            else:
                widget.delete(0, tk.END)
                widget.insert(0, values[i] if i < len(values) else "")

def get_next_customer_id():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(CustomerID) FROM dbo.Customers")
        max_id = cursor.fetchone()[0]
        conn.close()
        return (max_id or 0) + 1
    return 1

def get_next_loan_id():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(ApplicationID) FROM dbo.LoanApplications")
        max_id = cursor.fetchone()[0]
        conn.close()
        return (max_id or 0) + 1
    return 1

def get_next_payment_id():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(PaymentID) FROM dbo.Payments")
        max_id = cursor.fetchone()[0]
        conn.close()
        return (max_id or 0) + 1
    return 1

def validate_customer_data(values):
    try:
        # Validate CustomerID
        if not values[0].isdigit():
            return False, "CustomerID must be a number"
            
        # Validate Name
        if len(values[1].strip()) < 2:
            return False, "Full name must be at least 2 characters"
            
        # Validate Gender
        if values[2] not in ['Male', 'Female']:
            return False, "Gender must be either Male or Female"
            
        # Validate Age
        age = int(values[3])
        if not (18 <= age <= 100):
            return False, "Age must be between 18 and 100"
            
        # Validate Marital Status
        if values[4] not in ['Single', 'Married', 'Divorced', 'Widowed']:
            return False, "Invalid marital status"
            
        # Validate Income
        income = float(values[5])
        if income <= 0:
            return False, "Annual income must be positive"
            
        # Validate Loan Amount
        loan_amount = float(values[7])
        if loan_amount < 0:
            return False, "Loan amount cannot be negative"
            
        return True, ""
    except ValueError as e:
        return False, f"Invalid number format: {str(e)}"

# ========== Loan Applications Functions ==========
def validate_loan_data(values):
    try:
        # Validate ApplicationID
        if not values[0].isdigit():
            return False, "ApplicationID must be a number"
            
        # Validate CustomerID
        if not values[1].isdigit():
            return False, "CustomerID must be a number"
            
        # Validate LoanAmount
        loan_amount = float(values[2])
        if loan_amount <= 0:
            return False, "Loan amount must be positive"
            
        # Validate ApplicationDate
        try:
            datetime.strptime(values[3], '%Y-%m-%d')
        except ValueError:
            return False, "Application date must be in YYYY-MM-DD format"
            
        # Validate LoanPurpose
        if len(values[4].strip()) < 3:
            return False, "Loan purpose must be at least 3 characters"
            
        return True, ""
    except ValueError as e:
        return False, f"Invalid number format: {str(e)}"

def add_loan_application():
    values = [
        loan_entries["ApplicationID"].get(),
        loan_entries["CustomerID"].get(),
        loan_entries["LoanAmount"].get(),
        loan_entries["ApplicationDate"].get(),
        loan_entries["LoanPurpose"].get(),
        loan_entries["ApplicationStatus"].get()
    ]
    
    is_valid, error_msg = validate_loan_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO dbo.LoanApplications 
                (ApplicationID, CustomerID, LoanAmount, ApplicationDate, LoanPurpose, ApplicationStatus)
                VALUES (?, ?, ?, ?, ?, ?)
            """, values)
            conn.commit()
            load_loans()
            clear_loan_form()
            messagebox.showinfo("Success", "Loan application added successfully!")
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))
        finally:
            conn.close()

def delete_loan_application():
    selected = loan_tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a loan application first!")
        return
        
    loan_id = loan_tree.item(selected[0])["values"][0]
    
    if not messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete loan application {loan_id}?"
    ):
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dbo.LoanApplications WHERE ApplicationID = ?", loan_id)
            conn.commit()
            load_loans()
            messagebox.showinfo("Success", "Loan application deleted successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Delete Error", str(e))
        finally:
            conn.close()

def edit_loan_application():
    selected = loan_tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a loan application first!")
        return
        
    original_loan_id = loan_tree.item(selected[0])["values"][0]
    values = [
        loan_entries["ApplicationID"].get(),
        loan_entries["CustomerID"].get(),
        loan_entries["LoanAmount"].get(),
        loan_entries["ApplicationDate"].get(),
        loan_entries["LoanPurpose"].get(),
        loan_entries["ApplicationStatus"].get()
    ]
    
    is_valid, error_msg = validate_loan_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Check if ID is being changed to an existing one
            if values[0] != original_loan_id:
                cursor.execute("SELECT COUNT(*) FROM dbo.LoanApplications WHERE ApplicationID = ?", values[0])
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "ApplicationID already exists!")
                    return
            
            cursor.execute("""
                UPDATE dbo.LoanApplications SET
                ApplicationID = ?, CustomerID = ?, LoanAmount = ?, ApplicationDate = ?, 
                LoanPurpose = ?, ApplicationStatus = ?
                WHERE ApplicationID = ?
            """, values + [original_loan_id])
            
            conn.commit()
            load_loans()
            messagebox.showinfo("Success", "Loan application updated successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Update Error", str(e))
        finally:
            conn.close()

def clear_loan_form():
    loan_entries["ApplicationID"].delete(0, tk.END)
    loan_entries["ApplicationID"].insert(0, str(get_next_loan_id()))
    for widget in loan_entries.values():
        if widget != loan_entries["ApplicationID"]:
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
    loan_entries["ApplicationDate"].insert(0, datetime.now().strftime('%Y-%m-%d'))

def on_loan_select(event):
    selected = loan_tree.selection()
    if not selected:
        return
    item = loan_tree.item(selected[0])
    values = item["values"]
    loan_entries["ApplicationID"].delete(0, tk.END)
    loan_entries["ApplicationID"].insert(0, values[0])
    loan_entries["CustomerID"].delete(0, tk.END)
    loan_entries["CustomerID"].insert(0, values[1])
    loan_entries["LoanAmount"].delete(0, tk.END)
    loan_entries["LoanAmount"].insert(0, values[3])
    loan_entries["ApplicationDate"].delete(0, tk.END)
    loan_entries["ApplicationDate"].insert(0, values[2])
    loan_entries["LoanPurpose"].delete(0, tk.END)
    loan_entries["LoanPurpose"].insert(0, values[4])
    loan_entries["ApplicationStatus"].set(values[5])

# ========== Payment Functions ==========
def validate_payment_data(values):
    try:
        # Validate PaymentID
        if not values[0].isdigit():
            return False, "PaymentID must be a number"
            
        # Validate CustomerID
        if not values[1].isdigit():
            return False, "CustomerID must be a number"
            
        # Validate AmountPaid
        amount = float(values[2])
        if amount <= 0:
            return False, "Payment amount must be positive"
            
        # Validate PaymentDate
        try:
            datetime.strptime(values[3], '%Y-%m-%d')
        except ValueError:
            return False, "Payment date must be in YYYY-MM-DD format"
            
        return True, ""
    except ValueError as e:
        return False, f"Invalid number format: {str(e)}"

def add_payment():
    values = [
        payment_entries["PaymentID"].get(),
        payment_entries["CustomerID"].get(),
        payment_entries["AmountPaid"].get(),
        payment_entries["PaymentDate"].get(),
        payment_entries["PaymentStatus"].get()
    ]
    
    is_valid, error_msg = validate_payment_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO dbo.Payments 
                (PaymentID, CustomerID, AmountPaid, PaymentDate, PaymentStatus)
                VALUES (?, ?, ?, ?, ?)
            """, values)
            conn.commit()
            load_payments()
            clear_payment_form()
            messagebox.showinfo("Success", "Payment added successfully!")
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))
        finally:
            conn.close()

def delete_payment():
    selected = payment_tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a payment first!")
        return
        
    payment_id = payment_tree.item(selected[0])["values"][0]
    
    if not messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete payment {payment_id}?"
    ):
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dbo.Payments WHERE PaymentID = ?", payment_id)
            conn.commit()
            load_payments()
            calculate_iscores()
            messagebox.showinfo("Success", "Payment deleted successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Delete Error", str(e))
        finally:
            conn.close()

def edit_payment():
    selected = payment_tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a payment first!")
        return
        
    original_payment_id = payment_tree.item(selected[0])["values"][0]
    values = [
        payment_entries["PaymentID"].get(),
        payment_entries["CustomerID"].get(),
        payment_entries["AmountPaid"].get(),
        payment_entries["PaymentDate"].get(),
        payment_entries["PaymentStatus"].get()
    ]
    
    is_valid, error_msg = validate_payment_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Check if ID is being changed to an existing one
            if values[0] != original_payment_id:
                cursor.execute("SELECT COUNT(*) FROM dbo.Payments WHERE PaymentID = ?", values[0])
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "PaymentID already exists!")
                    return
            
            cursor.execute("""
                UPDATE dbo.Payments SET
                PaymentID = ?, CustomerID = ?, AmountPaid = ?, PaymentDate = ?, PaymentStatus = ?
                WHERE PaymentID = ?
            """, values + [original_payment_id])
            
            conn.commit()
            load_payments()
            calculate_iscores()
            messagebox.showinfo("Success", "Payment updated successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Update Error", str(e))
        finally:
            conn.close()

def clear_payment_form():
    payment_entries["PaymentID"].delete(0, tk.END)
    payment_entries["PaymentID"].insert(0, str(get_next_payment_id()))
    for widget in payment_entries.values():
        if widget != payment_entries["PaymentID"]:
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
    payment_entries["PaymentDate"].insert(0, datetime.now().strftime('%Y-%m-%d'))

def on_payment_select(event):
    selected = payment_tree.selection()
    if not selected:
        return
    item = payment_tree.item(selected[0])
    values = item["values"]
    payment_entries["PaymentID"].delete(0, tk.END)
    payment_entries["PaymentID"].insert(0, values[0])
    payment_entries["CustomerID"].delete(0, tk.END)
    payment_entries["CustomerID"].insert(0, values[1])
    payment_entries["AmountPaid"].delete(0, tk.END)
    payment_entries["AmountPaid"].insert(0, values[3])
    payment_entries["PaymentDate"].delete(0, tk.END)
    payment_entries["PaymentDate"].insert(0, values[2])
    payment_entries["PaymentStatus"].set(values[4])

# ========== Database Functions ==========
def load_customers():
    tree_customers.delete(*tree_customers.get_children())
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Customers ORDER BY CustomerID")
        for row in cursor.fetchall():
            tree_customers.insert("", "end", values=row)
        conn.close()

def load_loans():
    loan_tree.delete(*loan_tree.get_children())
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.LoanApplications ORDER BY ApplicationID")
        for row in cursor.fetchall():
            loan_tree.insert("", "end", values=row)
        conn.close()

def load_payments():
    payment_tree.delete(*payment_tree.get_children())
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Payments ORDER BY PaymentID")
        for row in cursor.fetchall():
            payment_tree.insert("", "end", values=row)
        conn.close()

def calculate_iscores():
    tree = get_treeview(tab_scores)
    tree.delete(*tree.get_children())
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    # Get all customers
    cursor.execute("SELECT * FROM dbo.Customers ORDER BY CustomerID")
    customers = cursor.fetchall()

    for cust in customers:
        cust_id = cust.CustomerID
        full_name = cust.FullName
        credit_history = cust.Credit_History
        annual_income = cust.Annual_Income or 0
        loan_amount = cust.Loan_Amount or 0
        defaulted = cust.Defaulted

        # Base score
        base_score = 350

        # Credit score
        credit_score = 100 if credit_history else 0

        # Income score
        if annual_income > 100000:
            income_score = 100
        elif annual_income > 50000:
            income_score = 70
        elif annual_income > 20000:
            income_score = 40
        else:
            income_score = 20

        # Loan score
        if loan_amount < 30000:
            loan_score = 70
        elif loan_amount < 80000:
            loan_score = 40
        else:
            loan_score = 20

        # Default score
        default_score = 70 if not defaulted else -50

        # Payment score
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dbo.Payments 
            WHERE CustomerID = ? AND PaymentStatus = 'On Time'
        """, cust_id)
        on_time_payments = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM dbo.Payments 
            WHERE CustomerID = ?
        """, cust_id)
        total_payments = cursor.fetchone()[0]

        payment_ratio = on_time_payments / total_payments if total_payments > 0 else 1

        if payment_ratio >= 0.95:
            payment_score = 80
        elif payment_ratio >= 0.80:
            payment_score = 50
        elif payment_ratio >= 0.60:
            payment_score = 30
        else:
            payment_score = 0

        # Application score
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dbo.LoanApplications 
            WHERE CustomerID = ? AND ApplicationStatus = 'Approved'
        """, cust_id)
        approved_apps = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM dbo.LoanApplications 
            WHERE CustomerID = ?
        """, cust_id)
        total_apps = cursor.fetchone()[0]

        app_ratio = approved_apps / total_apps if total_apps > 0 else 1

        if app_ratio >= 0.9:
            application_score = 50
        elif app_ratio >= 0.7:
            application_score = 30
        elif app_ratio >= 0.5:
            application_score = 10
        else:
            application_score = 0

        # Final score calculation
        final_score = (base_score + credit_score + income_score + 
                       loan_score + default_score + payment_score + 
                       application_score)

        # Ensure score is between 350 and 800
        final_score = max(350, min(800, final_score))

        tree.insert("", "end", values=(cust_id, full_name, round(final_score, 2)))
    
    conn.close()

# ========== CRUD Operations for Customers ==========
def add_customer():
    values = [entries[lbl].get() if not isinstance(entries[lbl], ttk.Combobox) 
              else entries[lbl].get() for lbl in labels]
    
    is_valid, error_msg = validate_customer_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO dbo.Customers 
                (CustomerID, FullName, Gender, Age, Marital_Status, 
                 Annual_Income, Credit_History, Loan_Amount, Defaulted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            conn.commit()
            load_customers()
            calculate_iscores()
            clear_form()
            messagebox.showinfo("Success", "Customer added successfully!")
        except pyodbc.IntegrityError as e:
            if 'PRIMARY KEY constraint' in str(e):
                messagebox.showerror("Insert Error", 
                    "CustomerID already exists. Please use a unique ID.")
            else:
                messagebox.showerror("Insert Error", str(e))
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))
        finally:
            conn.close()

def delete_customer():
    selected = tree_customers.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a customer first!")
        return
        
    customer_id = tree_customers.item(selected[0])["values"][0]
    customer_name = tree_customers.item(selected[0])["values"][1]
    
    if not messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete customer {customer_id}: {customer_name}?\n"
        "This will also delete all related loan applications and payments!"
    ):
        return
        
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Delete related records
            cursor.execute("DELETE FROM dbo.Payments WHERE CustomerID = ?", customer_id)
            cursor.execute("DELETE FROM dbo.LoanApplications WHERE CustomerID = ?", customer_id)
            
            # Delete customer
            cursor.execute("DELETE FROM dbo.Customers WHERE CustomerID = ?", customer_id)
            
            conn.commit()
            load_customers()
            load_loans()
            load_payments()
            calculate_iscores()
            clear_form()
            messagebox.showinfo("Success", "Customer deleted successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Delete Error", str(e))
        finally:
            conn.close()

def edit_customer():
    selected = tree_customers.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a customer first!")
        return
        
    original_customer_id = tree_customers.item(selected[0])["values"][0]
    values = [entries[lbl].get() if not isinstance(entries[lbl], ttk.Combobox) 
              else entries[lbl].get() for lbl in labels]
    new_customer_id = values[0]

    is_valid, error_msg = validate_customer_data(values)
    if not is_valid:
        messagebox.showerror("Validation Error", error_msg)
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            if original_customer_id != new_customer_id:
                cursor.execute("SELECT COUNT(*) FROM dbo.Customers WHERE CustomerID = ?", new_customer_id)
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "CustomerID already exists!")
                    conn.rollback()
                    return

            cursor.execute("""
                UPDATE dbo.Customers SET
                CustomerID = ?, FullName = ?, Gender = ?, Age = ?, Marital_Status = ?,
                Annual_Income = ?, Credit_History = ?, Loan_Amount = ?, Defaulted = ?
                WHERE CustomerID = ?
            """, values + [original_customer_id])
            
            if original_customer_id != new_customer_id:
                cursor.execute("""
                    UPDATE dbo.Payments 
                    SET CustomerID = ? 
                    WHERE CustomerID = ?
                """, (new_customer_id, original_customer_id))
                
                cursor.execute("""
                    UPDATE dbo.LoanApplications 
                    SET CustomerID = ? 
                    WHERE CustomerID = ?
                """, (new_customer_id, original_customer_id))
            
            conn.commit()
            load_customers()
            load_loans()
            load_payments()
            calculate_iscores()
            messagebox.showinfo("Success", "Customer updated successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Update Error", str(e))
        finally:
            conn.close()

# ========== GUI Setup ==========
root = tk.Tk()
root.title("i-Score Management System")
root.geometry("1200x700")
root.configure(bg='#f0f0f0')

# Set custom font styles
title_font = Font(family="Segoe UI", size=12, weight="bold")
label_font = Font(family="Segoe UI", size=10)
button_font = Font(family="Segoe UI", size=10, weight="bold")
tree_font = Font(family="Consolas", size=9)

# Configure ttk Style
style = ttk.Style()
style.theme_use('clam')

# Custom colors
primary_color = '#2c3e50'
secondary_color = '#3498db'
success_color = '#27ae60'
danger_color = '#e74c3c'
light_bg = '#ecf0f1'
dark_bg = '#2c3e50'

# Configure style elements
style.configure('TNotebook', background=light_bg)
style.configure('TNotebook.Tab', font=title_font, padding=[15,5], background=light_bg)
style.map('TNotebook.Tab', 
          background=[('selected', primary_color)], 
          foreground=[('selected', 'white')])

style.configure('TFrame', background=light_bg)
style.configure('TLabel', background=light_bg, font=label_font)
style.configure('TButton', font=button_font, padding=5)
style.configure('Treeview', font=tree_font, rowheight=25)
style.configure('Treeview.Heading', font=button_font, background=primary_color, foreground='white')
style.map('Treeview', background=[('selected', secondary_color)])

# Create Notebook (Tabs)
tabControl = ttk.Notebook(root)
tab_customers = ttk.Frame(tabControl)
tab_loans = ttk.Frame(tabControl)
tab_payments = ttk.Frame(tabControl)
tab_scores = ttk.Frame(tabControl)

tabControl.add(tab_customers, text=' Customers Management ')
tabControl.add(tab_loans, text=' Loan Applications ')
tabControl.add(tab_payments, text=' Payment Records ')
tabControl.add(tab_scores, text=' i-Score Analysis ')

tabControl.pack(expand=1, fill="both", padx=10, pady=10)

# ========== Customers Tab ==========
customer_panes = ttk.PanedWindow(tab_customers, orient=tk.HORIZONTAL)
customer_panes.pack(fill=tk.BOTH, expand=1)

# Left Panel - Customer List
list_frame = ttk.Frame(customer_panes, padding=10)
customer_panes.add(list_frame, weight=3)

# Search Frame
search_frame = ttk.Frame(list_frame)
search_frame.pack(fill=tk.X, pady=(0,10))

ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0,5))
search_entry = ttk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
search_btn = ttk.Button(search_frame, text="🔍", width=3)
search_btn.pack(side=tk.LEFT)

# Treeview with Scrollbars
tree_frame = ttk.Frame(list_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree_scroll_y = ttk.Scrollbar(tree_frame)
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree_customers = ttk.Treeview(tree_frame, columns=(
    "CustomerID", "FullName", "Gender", "Age", "Marital_Status",
    "Annual_Income", "Credit_History", "Loan_Amount", "Defaulted"
), show='headings', yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

tree_scroll_y.config(command=tree_customers.yview)
tree_scroll_x.config(command=tree_customers.xview)

# Configure columns
columns = {
    "CustomerID": {"width": 80, "anchor": tk.CENTER},
    "FullName": {"width": 150, "anchor": tk.W},
    "Gender": {"width": 70, "anchor": tk.CENTER},
    "Age": {"width": 50, "anchor": tk.CENTER},
    "Marital_Status": {"width": 100, "anchor": tk.W},
    "Annual_Income": {"width": 100, "anchor": tk.E},
    "Credit_History": {"width": 100, "anchor": tk.CENTER},
    "Loan_Amount": {"width": 100, "anchor": tk.E},
    "Defaulted": {"width": 80, "anchor": tk.CENTER}
}

for col, settings in columns.items():
    tree_customers.heading(col, text=col)
    tree_customers.column(col, **settings)

tree_customers.pack(fill=tk.BOTH, expand=True)

# Right Panel - Customer Details
detail_frame = ttk.Frame(customer_panes, padding=10)
customer_panes.add(detail_frame, weight=1)

# Customer Form
form_frame = ttk.LabelFrame(detail_frame, text="Customer Details", padding=10)
form_frame.pack(fill=tk.BOTH, expand=True)

labels = [
    "CustomerID", "FullName", "Gender", "Age", "Marital_Status",
    "Annual_Income", "Credit_History", "Loan_Amount", "Defaulted"
]

entries = {}
for i, label in enumerate(labels):
    frame = ttk.Frame(form_frame)
    frame.pack(fill=tk.X, pady=2)
    
    ttk.Label(frame, text=label+":", width=15).pack(side=tk.LEFT)
    
    if label == "Gender":
        entry = ttk.Combobox(frame, values=["Male", "Female"], state="readonly")
    elif label == "Marital_Status":
        entry = ttk.Combobox(frame, values=["Single", "Married", "Divorced", "Widowed"], state="readonly")
    elif label == "Credit_History" or label == "Defaulted":
        entry = ttk.Combobox(frame, values=["True", "False"], state="readonly")
    else:
        entry = ttk.Entry(frame)
    
    entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
    entries[label] = entry

# Button Frame
button_frame = ttk.Frame(detail_frame)
button_frame.pack(fill=tk.X, pady=(10,0))

# Configure custom button styles
style.configure('primary.TButton', background=secondary_color, foreground='white')
style.configure('success.TButton', background=success_color, foreground='white')
style.configure('danger.TButton', background=danger_color, foreground='white')

ttk.Button(button_frame, text="Add New", command=add_customer, 
           style='success.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(button_frame, text="Update", command=edit_customer, 
           style='primary.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(button_frame, text="Delete", command=delete_customer, 
           style='danger.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

# Clear Button
ttk.Button(button_frame, text="Clear Form", command=clear_form).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

# ========== Loan Applications Tab ==========
loan_panes = ttk.PanedWindow(tab_loans, orient=tk.HORIZONTAL)
loan_panes.pack(fill=tk.BOTH, expand=1)

# Left Panel - Loan List
loan_list_frame = ttk.Frame(loan_panes, padding=10)
loan_panes.add(loan_list_frame, weight=3)

# Loan Treeview
loan_tree_frame = ttk.Frame(loan_list_frame)
loan_tree_frame.pack(fill=tk.BOTH, expand=True)

loan_scroll_y = ttk.Scrollbar(loan_tree_frame)
loan_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

loan_scroll_x = ttk.Scrollbar(loan_tree_frame, orient=tk.HORIZONTAL)
loan_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

loan_tree = ttk.Treeview(loan_tree_frame, columns=(
    "ApplicationID", "CustomerID", "ApplicationDate", "LoanAmount", "LoanPurpose", "ApplicationStatus"
), show='headings', yscrollcommand=loan_scroll_y.set, xscrollcommand=loan_scroll_x.set)

loan_scroll_y.config(command=loan_tree.yview)
loan_scroll_x.config(command=loan_tree.xview)

# Configure Loan columns
loan_columns = {
    "ApplicationID": {"width": 80, "anchor": tk.CENTER},
    "CustomerID": {"width": 80, "anchor": tk.CENTER},
    "ApplicationDate": {"width": 100, "anchor": tk.CENTER},
    "LoanAmount": {"width": 100, "anchor": tk.E},
    "LoanPurpose": {"width": 150, "anchor": tk.W},
    "ApplicationStatus": {"width": 120, "anchor": tk.CENTER}
}

for col, settings in loan_columns.items():
    loan_tree.heading(col, text=col)
    loan_tree.column(col, **settings)

loan_tree.pack(fill=tk.BOTH, expand=True)

# Right Panel - Loan Details
loan_detail_frame = ttk.Frame(loan_panes, padding=10)
loan_panes.add(loan_detail_frame, weight=1)

# Loan Form
loan_form_frame = ttk.LabelFrame(loan_detail_frame, text="Loan Application Details", padding=10)
loan_form_frame.pack(fill=tk.BOTH, expand=True)

loan_labels = ["ApplicationID", "CustomerID", "LoanAmount", "ApplicationDate", "LoanPurpose", "ApplicationStatus"]

loan_entries = {}
for i, label in enumerate(loan_labels):
    frame = ttk.Frame(loan_form_frame)
    frame.pack(fill=tk.X, pady=2)
    
    ttk.Label(frame, text=label+":", width=15).pack(side=tk.LEFT)
    
    if label == "ApplicationStatus":
        entry = ttk.Combobox(frame, values=["Pending", "Approved", "Rejected"], state="readonly")
    else:
        entry = ttk.Entry(frame)
    
    entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
    loan_entries[label] = entry

# Loan Button Frame
loan_button_frame = ttk.Frame(loan_detail_frame)
loan_button_frame.pack(fill=tk.X, pady=(10,0))

ttk.Button(loan_button_frame, text="Add Loan", command=add_loan_application, 
           style='success.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(loan_button_frame, text="Update Loan", command=edit_loan_application, 
           style='primary.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(loan_button_frame, text="Delete Loan", command=delete_loan_application, 
           style='danger.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(loan_button_frame, text="Clear Form", command=clear_loan_form).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

# ========== Payments Tab ==========
payment_panes = ttk.PanedWindow(tab_payments, orient=tk.HORIZONTAL)
payment_panes.pack(fill=tk.BOTH, expand=1)

# Left Panel - Payments List
payment_list_frame = ttk.Frame(payment_panes, padding=10)
payment_panes.add(payment_list_frame, weight=3)

# Payments Treeview
payment_tree_frame = ttk.Frame(payment_list_frame)
payment_tree_frame.pack(fill=tk.BOTH, expand=True)

payment_scroll_y = ttk.Scrollbar(payment_tree_frame)
payment_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

payment_scroll_x = ttk.Scrollbar(payment_tree_frame, orient=tk.HORIZONTAL)
payment_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

payment_tree = ttk.Treeview(payment_tree_frame, columns=(
    "PaymentID", "CustomerID", "PaymentDate", "AmountPaid", "PaymentStatus"
), show='headings', yscrollcommand=payment_scroll_y.set, xscrollcommand=payment_scroll_x.set)

payment_scroll_y.config(command=payment_tree.yview)
payment_scroll_x.config(command=payment_tree.xview)

# Configure Payment columns
payment_columns = {
    "PaymentID": {"width": 80, "anchor": tk.CENTER},
    "CustomerID": {"width": 80, "anchor": tk.CENTER},
    "PaymentDate": {"width": 100, "anchor": tk.CENTER},
    "AmountPaid": {"width": 100, "anchor": tk.E},
    "PaymentStatus": {"width": 120, "anchor": tk.CENTER}
}

for col, settings in payment_columns.items():
    payment_tree.heading(col, text=col)
    payment_tree.column(col, **settings)

payment_tree.pack(fill=tk.BOTH, expand=True)

# Right Panel - Payment Details
payment_detail_frame = ttk.Frame(payment_panes, padding=10)
payment_panes.add(payment_detail_frame, weight=1)

# Payment Form
payment_form_frame = ttk.LabelFrame(payment_detail_frame, text="Payment Details", padding=10)
payment_form_frame.pack(fill=tk.BOTH, expand=True)

payment_labels = ["PaymentID", "CustomerID", "AmountPaid", "PaymentDate", "PaymentStatus"]

payment_entries = {}
for i, label in enumerate(payment_labels):
    frame = ttk.Frame(payment_form_frame)
    frame.pack(fill=tk.X, pady=2)
    
    ttk.Label(frame, text=label+":", width=15).pack(side=tk.LEFT)
    
    if label == "PaymentStatus":
        entry = ttk.Combobox(frame, values=["On Time", "Late", "Missed"], state="readonly")
    else:
        entry = ttk.Entry(frame)
    
    entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
    payment_entries[label] = entry

# Payment Button Frame
payment_button_frame = ttk.Frame(payment_detail_frame)
payment_button_frame.pack(fill=tk.X, pady=(10,0))

ttk.Button(payment_button_frame, text="Add Payment", command=add_payment, 
           style='success.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(payment_button_frame, text="Update Payment", command=edit_payment, 
           style='primary.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(payment_button_frame, text="Delete Payment", command=delete_payment, 
           style='danger.TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
ttk.Button(payment_button_frame, text="Clear Form", command=clear_payment_form).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

# ========== Scores Tab ==========
score_frame = ttk.Frame(tab_scores, padding=10)
score_frame.pack(fill=tk.BOTH, expand=True)

# iScore Header with Refresh Button
score_header_frame = ttk.Frame(score_frame)
score_header_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Label(score_header_frame, text="i-Score Analysis", font=title_font).pack(side=tk.LEFT)
ttk.Button(score_header_frame, text="Refresh Scores", command=calculate_iscores).pack(side=tk.RIGHT)

# Scores Treeview
score_tree_frame = ttk.Frame(score_frame)
score_tree_frame.pack(fill=tk.BOTH, expand=True)

score_columns = ["CustomerID", "FullName", "iScore"]
score_column_settings = {
    "CustomerID": {"width": 100, "anchor": tk.CENTER},
    "FullName": {"width": 200, "anchor": tk.W},
    "iScore": {"width": 100, "anchor": tk.CENTER}
}

score_tree = setup_tab_with_treeview(tab_scores, score_columns, score_column_settings)

# ========== Event Bindings ==========
tree_customers.bind('<<TreeviewSelect>>', on_customer_select)
loan_tree.bind('<<TreeviewSelect>>', on_loan_select)
payment_tree.bind('<<TreeviewSelect>>', on_payment_select)

# ========== Application Startup ==========
def on_startup():
    # Initialize default values
    entries["CustomerID"].insert(0, str(get_next_customer_id()))
    loan_entries["ApplicationID"].insert(0, str(get_next_loan_id()))
    loan_entries["ApplicationDate"].insert(0, datetime.now().strftime('%Y-%m-%d'))
    payment_entries["PaymentID"].insert(0, str(get_next_payment_id()))
    payment_entries["PaymentDate"].insert(0, datetime.now().strftime('%Y-%m-%d'))
    
    # Load data
    load_customers()
    load_loans()
    load_payments()
    calculate_iscores()

# Call startup function
on_startup()

# Start the application
root.mainloop()
