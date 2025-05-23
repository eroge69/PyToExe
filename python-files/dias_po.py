
import pyodbc
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime, timedelta

# Database connection
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.1.15;'  # Your server's IP address
        'DATABASE=easyway;'  # Your database name
        'UID=sa;'  # SQL Server login
        'PWD=tstc123;'  # Your password

    )

# Fetch sales summary and stock info
def fetch_sales_and_stock():
    conn = get_connection()
    fixed_today = datetime(2025, 2, 16)
    from_date = fixed_today - timedelta(days=90)

    # Sales data last 3 months
    sales_query = """
    SELECT 
        i.ItemCode, 
        i.ItemDescrip, 
        i.TrDate, 
        i.Qty, 
        s.Supp_Code
    FROM 
        tb_InvDet i
    LEFT JOIN 
        tb_Item s ON i.ItemCode = s.Item_Code
    WHERE 
        i.TrDate >= ?
    """
    sales_df = pd.read_sql(sales_query, conn, params=[from_date])
    sales_df['TrDate'] = pd.to_datetime(sales_df['TrDate'])
    sales_df['Supp_Code'] = sales_df['Supp_Code'].fillna("N/A")

    # Calculate total qty sold per item
    total_sales = (
        sales_df.groupby('ItemCode', as_index=False)
        .agg({
            'Qty': 'sum',
            'ItemDescrip': 'first',
            'Supp_Code': 'first'
        })
    )
    # Monthly average and monthly requirement (1.5x average)
    total_sales['MonthlyAvg'] = total_sales['Qty'] // 3
    total_sales['MonthlyReq'] = (total_sales['MonthlyAvg'] * 1.5).round().astype(int)

    # Get current stock per item summed across all locations from your stock view
    stock_query = """
    SELECT ItemCode, SUM(Stock) AS CurrentStock
    FROM dbo.Vw_Stock
    GROUP BY ItemCode
    """
    stock_df = pd.read_sql(stock_query, conn)

    conn.close()

    # Merge sales + stock data on ItemCode
    merged = pd.merge(total_sales, stock_df, on='ItemCode', how='left')
    merged['CurrentStock'] = merged['CurrentStock'].fillna(0).astype(int)

    # Calculate reorder quantity = MonthlyReq - CurrentStock, but minimum 0
    merged['ReorderQty'] = (merged['MonthlyReq'] - merged['CurrentStock']).clip(lower=0)

    return merged

# Update treeview UI with dataframe and update row count label
def update_ui(filtered_df):
    for row in tree.get_children():
        tree.delete(row)
    if filtered_df.empty:
        supplier_combo.config(state="disabled")
        export_button.config(state="disabled")
        rows_label.config(text="Rows: 0")
    else:
        supplier_combo.config(state="readonly")
        export_button.config(state="normal")
        for row in filtered_df.itertuples():
            tree.insert(
                "", "end",
                values=(
                    str(row.ItemCode),
                    row.ItemDescrip,
                    row.Supp_Code,
                    int(row.Qty),
                    int(row.MonthlyAvg),
                    int(row.MonthlyReq),
                    int(row.CurrentStock),
                    int(row.ReorderQty)
                )
            )
        rows_label.config(text=f"Rows: {len(filtered_df)}")

# Background thread processing
def process_data():
    start_button.config(state=tk.DISABLED)
    progress_bar.start()
    try:
        global full_df
        full_df = fetch_sales_and_stock()

        suppliers = sorted(full_df['Supp_Code'].unique().tolist())
        supplier_combo['values'] = ["All Suppliers"] + suppliers
        supplier_combo.current(0)

        update_ui(full_df)
    finally:
        progress_bar.stop()
        start_button.config(state=tk.NORMAL)

# Filter by selected supplier
def filter_by_supplier(event=None):
    selected = supplier_var.get()
    if selected == "All Suppliers":
        update_ui(full_df)
    else:
        filtered = full_df[full_df['Supp_Code'] == selected]
        update_ui(filtered)

# Export filtered data to Excel
def export_to_excel():
    selected = supplier_var.get()
    if selected == "All Suppliers":
        filtered = full_df[full_df['ReorderQty'] > 0]
    else:
        filtered = full_df[(full_df['Supp_Code'] == selected) & (full_df['ReorderQty'] > 0)]

    if filtered.empty:
        messagebox.showinfo("Export", "No items with reorder quantity for the selected supplier.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    try:
        filtered.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

# Scroll functions
def scroll_to_top():
    tree.yview_moveto(0)

def scroll_to_bottom():
    tree.yview_moveto(1)

# Setup UI
root = tk.Tk()
root.title("Supplier-Based Sales Report with Stock and Reorder Qty")
root.geometry("1100x650")

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(
    frame,
    text="Sales Summary (Last 3 Months) with Stock and Reorder Qty",
    font=("Helvetica", 16)
)
title_label.pack(pady=10)

controls_frame = ttk.Frame(frame)
controls_frame.pack(pady=5)

start_button = ttk.Button(
    controls_frame,
    text="Fetch Data",
    command=lambda: threading.Thread(target=process_data, daemon=True).start()
)
start_button.pack(side=tk.LEFT, padx=10)

supplier_var = tk.StringVar()
supplier_combo = ttk.Combobox(
    controls_frame,
    textvariable=supplier_var,
    state="readonly",
    width=30
)
supplier_combo.bind("<<ComboboxSelected>>", filter_by_supplier)
supplier_combo.pack(side=tk.LEFT, padx=10)

export_button = ttk.Button(
    controls_frame,
    text="Export to Excel",
    command=export_to_excel
)
export_button.pack(side=tk.LEFT, padx=10)

scroll_top_button = ttk.Button(controls_frame, text="Scroll to Top", command=scroll_to_top)
scroll_top_button.pack(side=tk.LEFT, padx=5)

scroll_bottom_button = ttk.Button(controls_frame, text="Scroll to Bottom", command=scroll_to_bottom)
scroll_bottom_button.pack(side=tk.LEFT, padx=5)

progress_bar = ttk.Progressbar(frame, mode="indeterminate")
progress_bar.pack(pady=10, fill=tk.X)

# Treeview + scrollbar container frame
tree_frame = ttk.Frame(frame)
tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

columns = ("ItemCode", "ItemDescrip", "Supp_Code", "Total Qty", "Monthly Avg", "Monthly Req", "Current Stock", "Reorder Qty")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=tree.yview)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")

rows_label = ttk.Label(frame, text="Rows: 0")
rows_label.pack(anchor='w', padx=10)

full_df = pd.DataFrame()

root.mainloop()
