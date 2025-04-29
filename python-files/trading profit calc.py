Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk

# Function to calculate profit and revenue
def calculate_profit():
    try:
        buy_price = float(buy_price_entry.get())
        sell_price = float(sell_price_entry.get())
        amount_bought = float(amount_bought_entry.get())
        fees = float(fees_entry.get())

        # Calculate Total Cost, Total Revenue, Profit/Loss, and Profit Percentage
        total_cost = buy_price * amount_bought + fees
        total_revenue = sell_price * amount_bought
        profit_loss = total_revenue - total_cost
        profit_percentage = (profit_loss / total_cost) * 100 if total_cost != 0 else 0

        # Display results
        total_cost_label.config(text=f"Total Cost: ${total_cost:.2f}")
        total_revenue_label.config(text=f"Total Revenue: ${total_revenue:.2f}")
        profit_loss_label.config(text=f"Profit/Loss: ${profit_loss:.2f}")
        profit_percentage_label.config(text=f"Profit %: {profit_percentage:.2f}%")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

# Set up the main window
... root = tk.Tk()
... root.title("Crypto Profit Calculator")
... 
... # Create the input fields
... tk.Label(root, text="Buy Price per Unit ($):").grid(row=0, column=0)
... buy_price_entry = tk.Entry(root)
... buy_price_entry.grid(row=0, column=1)
... 
... tk.Label(root, text="Sell Price per Unit ($):").grid(row=1, column=0)
... sell_price_entry = tk.Entry(root)
... sell_price_entry.grid(row=1, column=1)
... 
... tk.Label(root, text="Amount Bought (Units):").grid(row=2, column=0)
... amount_bought_entry = tk.Entry(root)
... amount_bought_entry.grid(row=2, column=1)
... 
... tk.Label(root, text="Total Fees ($):").grid(row=3, column=0)
... fees_entry = tk.Entry(root)
... fees_entry.grid(row=3, column=1)
... 
... # Calculate Button
... calculate_button = tk.Button(root, text="Calculate", command=calculate_profit)
... calculate_button.grid(row=4, columnspan=2)
... 
... # Results Labels
... total_cost_label = tk.Label(root, text="Total Cost: $0.00")
... total_cost_label.grid(row=5, columnspan=2)
... 
... total_revenue_label = tk.Label(root, text="Total Revenue: $0.00")
... total_revenue_label.grid(row=6, columnspan=2)
... 
... profit_loss_label = tk.Label(root, text="Profit/Loss: $0.00")
... profit_loss_label.grid(row=7, columnspan=2)
... 
... profit_percentage_label = tk.Label(root, text="Profit %: 0.00%")
... profit_percentage_label.grid(row=8, columnspan=2)
... 
... # Start the GUI loop
... root.mainloop()
