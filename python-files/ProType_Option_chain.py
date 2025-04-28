!pip install RangeSlider

'''import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import pandas as pd
import threading
import time
# Global variables
auto_refresh = False
refresh_interval = 3  # Default 3 seconds
optionchain = pd.DataFrame()
# NSE URL Setup
url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'accept-encoding': 'gzip, deflate, br, zstd'
}
session = requests.Session()
request = session.get(url, headers=headers)
cookies = dict(request.cookies)
# Data Fetch
def dataframe():
    response = session.get(url, headers=headers, cookies=cookies).json()
    rawdata = pd.DataFrame(response)
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    data = []
    for i in range(len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
        expiry = None
        call_iv = None
        if rawop['CE'][i] != 0:
            call_iv = rawop['CE'][i].get('IV', None)
            expiry = rawop['CE'][i].get('expiryDate', None)
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
        put_iv = None
        if rawop['PE'][i] != 0:
            if expiry is None:
                expiry = rawop['PE'][i].get('expiryDate', None)
            put_iv = rawop['PE'][i].get('IV', None)
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
        opdata = {
            'EXPIRY DATE': expiry,
            'CALL CHNG OI': callcoi,
            'CALL LTP': cltp,
            'Call IV': call_iv,
            'Call OI': calloi,
            'STRIKE PRICE': stp,
            'Put OI': putoi,
            'Put IV': put_iv,
            'Put LTP': pltp,
            'PUT CHNG OI': putcoi
        }
        data.append(opdata)
    optionchain = pd.DataFrame(data)
    return optionchain
# Refresh Data
def refresh_data():
    global optionchain
    try:
        optionchain = dataframe()
        update_table()
        update_summary()
    except Exception as e:
        print(f"Error refreshing data: {e}")
# Auto Refresh Logic
def auto_refresh_loop():
    global auto_refresh
    while auto_refresh:
        refresh_data()
        time.sleep(refresh_interval)
def start_auto_refresh():
    global auto_refresh
    auto_refresh = True
    threading.Thread(target=auto_refresh_loop, daemon=True).start()
def stop_auto_refresh():
    global auto_refresh
    auto_refresh = False
# Strike slider change
def update_summary(event=None):
    if optionchain.empty:
        return
    strike_min = strike_slider.get()
    strike_max = strike_slider2.get()
    selected = optionchain[
        (optionchain['STRIKE PRICE'] >= strike_min) & (optionchain['STRIKE PRICE'] <= strike_max)
    ]
    call_oi_sum = selected['Call OI'].sum()
    put_oi_sum = selected['Put OI'].sum()
    oi_difference = call_oi_sum - put_oi_sum
    if oi_difference < 0:
        result = f'Put Writers of {abs(oi_difference):.2f}'
    else:
        result = f'Call Writers of {oi_difference:.2f}'
    result_label.config(text=result)
    summary_label.config(text=f"CALL OI SUM: {call_oi_sum} | PUT OI SUM: {put_oi_sum}")
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    
    for _, row in optionchain.iterrows():
        tree.insert('', 'end', values=(
            row['EXPIRY DATE'], row['STRIKE PRICE'], row['Call OI'], row['Put OI'],
            row['CALL LTP'], row['Put LTP']
        ))
# Close App
def close_app():
    stop_auto_refresh()
    root.destroy()
# GUI Setup
root = tk.Tk()
root.title("NIFTY Option Chain App")
root.geometry('1000x600')
frame = tk.Frame(root)
frame.pack(pady=10)
refresh_button = tk.Button(frame, text="Refresh Now 🔄", command=refresh_data)
refresh_button.grid(row=0, column=0, padx=10)
start_button = tk.Button(frame, text="Start Auto Refresh ▶️", command=start_auto_refresh)
start_button.grid(row=0, column=1, padx=10)
stop_button = tk.Button(frame, text="Stop Auto Refresh ⏹️", command=stop_auto_refresh)
stop_button.grid(row=0, column=2, padx=10)
close_button = tk.Button(frame, text="Close ❌", command=close_app)
close_button.grid(row=0, column=3, padx=10)
interval_label = tk.Label(frame, text="Timer (sec):")
interval_label.grid(row=1, column=0, pady=10)
timer_box = ttk.Combobox(frame, values=[1, 2, 3, 4, 5], width=5)
timer_box.set(3)
timer_box.grid(row=1, column=1)
def change_timer(event):
    global refresh_interval
    refresh_interval = int(timer_box.get())
timer_box.bind("<<ComboboxSelected>>", change_timer)
# Strike range
strike_slider = tk.Scale(frame, from_=18000, to=21000, orient=tk.HORIZONTAL, label="Strike Min")
strike_slider.grid(row=2, column=0, columnspan=2, pady=10)
strike_slider2 = tk.Scale(frame, from_=18000, to=21000, orient=tk.HORIZONTAL, label="Strike Max")
strike_slider2.grid(row=2, column=2, columnspan=2, pady=10)
strike_slider.bind("<ButtonRelease-1>", update_summary)
strike_slider2.bind("<ButtonRelease-1>", update_summary)
result_label = tk.Label(root, text="Result", font=('Arial', 14))
result_label.pack(pady=10)
summary_label = tk.Label(root, text="", font=('Arial', 12))
summary_label.pack()
# Table view
tree = ttk.Treeview(root, columns=("Expiry", "Strike", "Call OI", "Put OI", "Call LTP", "Put LTP"), show="headings")
tree.heading("Expiry", text="Expiry Date")
tree.heading("Strike", text="Strike Price")
tree.heading("Call OI", text="Call OI")
tree.heading("Put OI", text="Put OI")
tree.heading("Call LTP", text="Call LTP")
tree.heading("Put LTP", text="Put LTP")
tree.pack(expand=True, fill='both')
# Start
refresh_data()
root.mainloop()
'''

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import pandas as pd
import threading
import time
# Global variables
auto_refresh = False
refresh_interval = 3  # Default 3 seconds
optionchain = pd.DataFrame()
# NSE URL Setup
url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'accept-encoding': 'gzip, deflate, br, zstd','accept-language':'en-US,en;q=0.8',
    #'cookie':'nseQuoteSymbols=[{"symbol":"NIFTY","identifier":"OPTIDXNIFTY30-04-2025PE24000.00","type":"equity"}]; nsit=bSmioYODz_Ut6kH3Lqz0VOJS; AKA_A2=A; _abck=389FA9A26BE13493EC2E7CD284C3F3C0~0~YAAQHIgsMZjUwluWAQAAukyAfA045sBkHcs8HVj9T7krSbiC5HjWJE1T8pPfT8iuRPTXIaDyww4yo7d4rS5ugMHmUt82OMhLtcrP+NRYd+shjApVfC6vt1UUV0PGweNV91/lPNkkXqqBCLAMzSmX6jpx4bB5CcNsf21xVSe/YYHILkY9AAHte7TdUXj7BmeGrym1pPyl+JSD5rcRdxFP3B5UefGxeOAP56XiHZ8fCKw8KKU4YBAY3eh2mjpMnc1l4m47h8tK4jNfyUeeClK+C2+Uf/IBOOHediVApwmjEkoupu0wb/rH8mQueDq0WLZkExnGa0blU2Im/HixrYz1es81YAALzlGAoBHR2kAvQXDDvayzPRFbJLtZhwBEwLQuppAzk1nekhYKd0gYBRSPXI4vgcDQ1rv/XMokCcEsQY0XACyJ0ZXLlMXNfwcUSe5Gb2EoVEFbn/6hbNvQFudhrAG2ZicKa2DYStj7+O+sFOJHK3XhBnTc4kf6erjRb98tNUpJvgUn2pDbFmedxG/A6QOn/p8vetLM+eW7Cq0W~-1~-1~-1; bm_mi=64E2B8C45276AC8A44E6E4AE8E91C7AD~YAAQnccsMeVloVqWAQAALlCAfBsQsDMNPFah05BMxYAbh8g158tA8QCoNFqjvfwucIt57F5Cr7V5IsPiScz9A457o/1o40S0aHTNTfAE798+nuJBKgD5VOyUWT8fVX8zaSYRG3VFPPV+pqf03agmsr2wk/CKNOnc2upfhfKfU5athTE1CRO2U46KX65qwMNNtZSYSVF/4op/vOf1ISm7W0t26Mzx+OpKJbj4KkmUjs3i5sAuXLC5m5EG1sviAv1NL4uSNBLGY6xueqarIb5raRjBouq22FZ1paITtPeumv5ihkRplgCNUElLaEOc31rQjNJIzUqFcplXeqjL~1; ak_bmsc=406C38E055F4359132B5F5A996DA7B3A~000000000000000000000000000000~YAAQHIgsMUjVwluWAQAAAmOAfBsn3FaigD9aL5Woj4r6CZ8fKt0ZEBJcIPUHh4/yEzY9eVWnV39C8yoerTZcmwb/nML4j8o0otVwLe+tH6av29CvD5XENAef8ieKDYLE2fKoGEDYiQP1Vm0xaBVfMrrMUQyE9aWdJZFoPZIWTUkbaXL4ruONE90n52wxV+lL4CmsRQu+p9IYZA2oQ42q9Iu0jijdb6qoy3A0pGwd+0nTsiZCN1Dnx0SkOWLPyGznTfVcxAo3aJiTtRQc4pnu/Qui0qfhBkyZfWXe1cQ5+WpRBXtfy1iM5Wisse9WAPUtOoX1AucJEPaCxaKnZYY0nYI+xx6crbxmysDkSXPEW1/z4D07LwhN9uLxiv3HNBbnprd/4CFtSM0rTrTkzETGNFlWNMc9S7lsms41; bm_sz=76374D6F807607B363E456973CBB4E4C~YAAQHIgsMbzVwluWAQAADnOAfBuRw7aoCPKekr15EmUMGHuX1XsU6P/X9HIJK/2dQz7sdQrB9GjZB9TqFMoVaXioTrNw2Rqb5E3DRrEwr7D08xJSLe+Zja6cuc8kKQnuGIwYG4lTESqfpAuKyECPa5/O0jSLfyA9We/bBA2MZ8FukupHE5jtu8O9snf8+V2uygGJqGVf6lQ9vTv28ca8CHhq86BlOfOUC4lx8dD1SCPSa64CLjD6E7ephBgxKoO/neFQi9oRpFBtBNDIYQeSoVK6YPOEOAW6cERSNktVTvM+N19vUBOoec9tueP0Yx7zCV4IZmIdyhC0SI7qVlsDE1uTBkgl7UfOjXD2lnTH5XROKnvScvSCijv3PhiOQhb60rJo4O+9p4YHF8mEId9r+Bme~4474161~3487300; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTc0NTg0NTUxNiwiZXhwIjoxNzQ1ODUyNzE2fQ.vqYf-wSdsN7QAvsV9KGZo3BRMw1Uea7hnduUhGuIgVc; bm_sv=3E07AB22BEF700DE064F506DDB3CD8C5~YAAQHIgsMfDVwluWAQAAdHiAfBucCs38aQmNWemhNFYmgw2IRNuHsM18X8Bpis+rIACVIuqL5r2T2XJkA9Y+PiZVG5WgzKWdzbLrDvV4ESG5KCUD4tfanZv4yTmCHLXg7lB118NCayajQ+PgcCciJQLtRrvJQPJKn/4+Nb6UumH3JA/PfEZ2g2GvhilsYA38MwC6kiJ8/pCiJfnmMwwIeOUYVVmBb2GZ35tmGDxRcyudU3ca2eT0qLZxSM5jA1VpDv82~1'
}
session = requests.Session()
request = session.get(url, headers=headers)
cookies = dict(request.cookies)
# Data Fetch
def dataframe():
    global session, headers, url
    # Refresh the cookies every time
    session = requests.Session()
    request = session.get('https://www.nseindia.com', headers=headers)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from NSE")
    response_json = response.json()
    rawdata = pd.DataFrame(response_json)
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    data = []
    for i in range(len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
        expiry = None
        call_iv = None
        if rawop['CE'][i] != 0:
            call_iv = rawop['CE'][i].get('IV', None)
            expiry = rawop['CE'][i].get('expiryDate', None)
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
        put_iv = None
        if rawop['PE'][i] != 0:
            if expiry is None:
                expiry = rawop['PE'][i].get('expiryDate', None)
            put_iv = rawop['PE'][i].get('IV', None)
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
        opdata = {
            'EXPIRY DATE': expiry,
            'CALL CHNG OI': callcoi,
            'CALL LTP': cltp,
            'Call IV': call_iv,
            'Call OI': calloi,
            'STRIKE PRICE': stp,
            'Put OI': putoi,
            'Put IV': put_iv,
            'Put LTP': pltp,
            'PUT CHNG OI': putcoi
        }
        data.append(opdata)
    optionchain = pd.DataFrame(data)
    return optionchain
# Refresh Data
def refresh_data():
    global optionchain
    try:
        optionchain = dataframe()
        build_strike_sliders()
        update_table()
        update_summary()
    except Exception as e:
        print(f"Error refreshing data: {e}")
# Build the Strike Range Sliders based on available data
def build_strike_sliders():
    global strike_slider, strike_slider2
    try:
        strike_slider.destroy()
        strike_slider2.destroy()
    except:
        pass
    if optionchain.empty:
        return
    min_strike = int(optionchain['STRIKE PRICE'].min())
    max_strike = int(optionchain['STRIKE PRICE'].max())
    strike_slider = tk.Scale(frame, from_=min_strike, to=max_strike, orient=tk.HORIZONTAL, label="Strike Min", resolution=50)
    strike_slider.grid(row=2, column=0, columnspan=2, pady=10)
    strike_slider2 = tk.Scale(frame, from_=min_strike, to=max_strike, orient=tk.HORIZONTAL, label="Strike Max", resolution=50)
    strike_slider2.grid(row=2, column=2, columnspan=2, pady=10)
    strike_slider.set(min_strike)
    strike_slider2.set(max_strike)
    strike_slider.bind("<ButtonRelease-1>", update_summary)
    strike_slider2.bind("<ButtonRelease-1>", update_summary)
# Auto Refresh Logic
def auto_refresh_loop():
    global auto_refresh
    while auto_refresh:
        refresh_data()
        time.sleep(refresh_interval)
def start_auto_refresh():
    global auto_refresh
    auto_refresh = True
    threading.Thread(target=auto_refresh_loop, daemon=True).start()
def stop_auto_refresh():
    global auto_refresh
    auto_refresh = False
# Strike slider change
def update_summary(event=None):
    if optionchain.empty:
        return
    try:
        strike_min = strike_slider.get()
        strike_max = strike_slider2.get()
    except:
        return
    selected = optionchain[
        (optionchain['STRIKE PRICE'] >= strike_min) & (optionchain['STRIKE PRICE'] <= strike_max)
    ]
    call_oi_sum = selected['Call OI'].sum()
    put_oi_sum = selected['Put OI'].sum()
    oi_difference = call_oi_sum - put_oi_sum
    if oi_difference < 0:
        result = f'Put Writers of {abs(oi_difference):.2f}'
    else:
        result = f'Call Writers of {oi_difference:.2f}'
    result_label.config(text=result)
    summary_label.config(text=f"CALL OI SUM: {call_oi_sum} | PUT OI SUM: {put_oi_sum}")
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    
    for _, row in optionchain.iterrows():
        tree.insert('', 'end', values=(
            row['EXPIRY DATE'], row['STRIKE PRICE'], row['Call OI'], row['Put OI'],
            row['Call IV'], row['Put IV']
        ))
# Close App
def close_app():
    stop_auto_refresh()
    root.destroy()
# GUI Setup
root = tk.Tk()
root.title("NIFTY Option Chain App")
root.geometry('1000x600')
frame = tk.Frame(root)
frame.pack(pady=10)
refresh_button = tk.Button(frame, text="Refresh Now 🔄", command=refresh_data)
refresh_button.grid(row=0, column=0, padx=10)
start_button = tk.Button(frame, text="Start Auto Refresh ▶️", command=start_auto_refresh)
start_button.grid(row=0, column=1, padx=10)
stop_button = tk.Button(frame, text="Stop Auto Refresh ⏹️", command=stop_auto_refresh)
stop_button.grid(row=0, column=2, padx=10)
close_button = tk.Button(frame, text="Close ❌", command=close_app)
close_button.grid(row=0, column=3, padx=10)
interval_label = tk.Label(frame, text="Timer (sec):")
interval_label.grid(row=1, column=0, pady=10)
timer_box = ttk.Combobox(frame, values=[1, 2, 3, 4, 5], width=5)
timer_box.set(3)
timer_box.grid(row=1, column=1)
def change_timer(event):
    global refresh_interval
    refresh_interval = int(timer_box.get())
timer_box.bind("<<ComboboxSelected>>", change_timer)
# Dummy place holders for sliders
strike_slider = tk.Scale(frame, from_=18000, to=21000, orient=tk.HORIZONTAL, label="Strike Min")
strike_slider.grid(row=2, column=0, columnspan=2, pady=10)
strike_slider2 = tk.Scale(frame, from_=18000, to=21000, orient=tk.HORIZONTAL, label="Strike Max")
strike_slider2.grid(row=2, column=2, columnspan=2, pady=10)
strike_slider.bind("<ButtonRelease-1>", update_summary)
strike_slider2.bind("<ButtonRelease-1>", update_summary)
result_label = tk.Label(root, text="Result", font=('Arial', 14))
result_label.pack(pady=10)
summary_label = tk.Label(root, text="", font=('Arial', 12))
summary_label.pack()
# Table view
tree = ttk.Treeview(root, columns=("Expiry", "Strike", "Call OI", "Put OI", "Call IV", "Put IV"), show="headings")
tree.heading("Expiry", text="Expiry Date")
tree.heading("Call OI", text="Call OI")
tree.heading("Call IV", text="Call IV")
tree.heading("Strike", text="Strike Price")
tree.heading("Put OI", text="Put OI")
tree.heading("Put IV", text="Put IV")
tree.pack(expand=True, fill='both')
# Start
refresh_data()
root.mainloop()





