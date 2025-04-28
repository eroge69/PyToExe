import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def fetch_payout_data():
    from_date = payout_from_date.get()
    to_date = payout_to_date.get()
    print(f"[Payout Summary] Fetching data from {from_date} to {to_date}")

def fetch_order_data():
    from_date = order_from_date.get()
    to_date = order_to_date.get()
    print(f"[Order Level Summary] Fetching data from {from_date} to {to_date}")

# Create main window
root = tk.Tk()
root.title("Meesho Business Dashboard")
root.geometry("1000x750")

# Create notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Create Frames for each tab
payout_frame = ttk.Frame(notebook)
order_frame = ttk.Frame(notebook)

notebook.add(payout_frame, text='Payout Summary')
notebook.add(order_frame, text='Order Level Summary')

# ... [all previous code remains same]

# ========================
# Payout Summary Layout
# ========================

# Date Range Section
payout_date_frame = ttk.Frame(payout_frame)
payout_date_frame.pack(pady=10)

ttk.Label(payout_date_frame, text="From Date:").grid(row=0, column=0, padx=5)
payout_from_date = DateEntry(payout_date_frame, date_pattern='dd-mm-yyyy')
payout_from_date.grid(row=0, column=1, padx=5)

ttk.Label(payout_date_frame, text="To Date:").grid(row=0, column=2, padx=5)
payout_to_date = DateEntry(payout_date_frame, date_pattern='dd-mm-yyyy')
payout_to_date.grid(row=0, column=3, padx=5)

ttk.Button(payout_date_frame, text="Fetch Data", command=fetch_payout_data).grid(row=0, column=4, padx=5)

# Summary Labels
summary_frame = ttk.Frame(payout_frame)
summary_frame.pack(pady=20)

ttk.Label(summary_frame, text="Total Payout: ₹71,615", font=('Arial', 14)).grid(row=0, column=0, padx=20)
ttk.Label(summary_frame, text="Payout Settled: ₹70,440", font=('Arial', 14)).grid(row=0, column=1, padx=20)
ttk.Label(summary_frame, text="Payout Pending: ₹1,175", font=('Arial', 14)).grid(row=0, column=2, padx=20)

# 👉 Create a separate frame just for chart
chart_frame = ttk.Frame(payout_frame)
chart_frame.pack(pady=20)

# Bar Chart
fig, ax = plt.subplots(figsize=(5, 3))
months = ['Dec-24', 'Jan-25', 'Feb-25', 'Mar-25']
payouts = [5000, 15000, 60000, 70000]

ax.bar(months, payouts, color='skyblue')
ax.set_title('Monthly Payouts')
ax.set_ylabel('Amount (₹)')

canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.draw()
canvas.get_tk_widget().pack()

# ... [rest order tab layout remains same]

# ========================
# Order Level Summary Layout
# ========================

# Date Range Section
order_date_frame = ttk.Frame(order_frame)
order_date_frame.pack(pady=10)

ttk.Label(order_date_frame, text="From Date:").grid(row=0, column=0, padx=5)
order_from_date = DateEntry(order_date_frame, date_pattern='dd-mm-yyyy')
order_from_date.grid(row=0, column=1, padx=5)

ttk.Label(order_date_frame, text="To Date:").grid(row=0, column=2, padx=5)
order_to_date = DateEntry(order_date_frame, date_pattern='dd-mm-yyyy')
order_to_date.grid(row=0, column=3, padx=5)

ttk.Button(order_date_frame, text="Fetch Data", command=fetch_order_data).grid(row=0, column=4, padx=5)

# Order Overview Labels
order_summary_frame = ttk.Frame(order_frame)
order_summary_frame.pack(pady=20)

ttk.Label(order_summary_frame, text="Total Orders: 590", font=('Arial', 14)).grid(row=0, column=0, padx=20)
ttk.Label(order_summary_frame, text="Delivered: 392", font=('Arial', 14)).grid(row=0, column=1, padx=20)
ttk.Label(order_summary_frame, text="Returned: 36", font=('Arial', 14)).grid(row=0, column=2, padx=20)

# Order Table
columns = ('Order ID', 'Order Status', 'Order Value', 'Payout Status')
tree = ttk.Treeview(order_frame, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)

# Example Data
sample_orders = [
    ('1382670527549289152', 'Delivered', '₹216', 'Settled'),
    ('1383336204002754240', 'RTO', '₹0', 'NA'),
    ('13841092027928064', 'Returned', '₹0', 'NA')
]

for order in sample_orders:
    tree.insert('', tk.END, values=order)

tree.pack(expand=True, fill='both', pady=20)

# Run the app
root.mainloop()
