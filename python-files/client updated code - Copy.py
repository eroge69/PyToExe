import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk, messagebox

root = tk.Tk()
root.withdraw()

name = simpledialog.askstring("Name", "Enter your name:")
HOST = simpledialog.askstring("Server IP", "Enter server IP:")
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(name.encode('utf-8'))

root = tk.Tk()
root.title(f"Chat - {name}")
root.geometry("700x500")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=4)
root.grid_columnconfigure(1, weight=1)

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
chat_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

user_frame = tk.Frame(root)
user_frame.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=5)

tk.Label(user_frame, text="Users Online", font=("Arial", 10, "bold")).pack(pady=(0, 5))
user_listbox = tk.Listbox(user_frame, selectmode=tk.MULTIPLE)
user_listbox.pack(fill=tk.BOTH, expand=True)

def open_group_popup():
    popup = tk.Toplevel(root)
    popup.title("Create Group")
    popup.geometry("300x300")

    tk.Label(popup, text="Group Name:").pack()
    group_name_entry = tk.Entry(popup)
    group_name_entry.pack(pady=5)

    tk.Label(popup, text="Select members:").pack()
    member_listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE)
    for user in user_selector['values']:
        if user != 'Broadcast' and not user.startswith('[Group]'):
            member_listbox.insert(tk.END, user)
    member_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_group():
        group_name = group_name_entry.get().strip()
        selected_indices = member_listbox.curselection()
        selected_members = [member_listbox.get(i) for i in selected_indices]
        if not group_name or not selected_members:
            messagebox.showerror("Error", "Please enter a group name and select members.")
            return
        members_str = ",".join(selected_members)
        client.send(f"/create_group {group_name} {members_str}".encode('utf-8'))
        update_recipient_options(f"[Group] {group_name}")
        popup.destroy()

    tk.Button(popup, text="Create", command=create_group).pack(pady=10)

tk.Button(user_frame, text="New Group", command=open_group_popup).pack(pady=2)

entry_frame = tk.Frame(root)
entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
entry_frame.grid_columnconfigure(0, weight=4)
entry_frame.grid_columnconfigure(1, weight=1)

entry = tk.Entry(entry_frame)
entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

user_selector = ttk.Combobox(entry_frame, state="readonly")
user_selector.grid(row=0, column=1, sticky="ew")
user_selector['values'] = ['Broadcast']
user_selector.set('Broadcast')

def update_recipient_options(option):
    current_values = list(user_selector['values'])
    if option not in current_values:
        user_selector['values'] = current_values + [option]

def receive_messages():
    while True:
        try:
            msg = client.recv(2048).decode('utf-8')
            if msg.startswith("/users "):
                users = msg.replace("/users ", "").split(",")
                if name in users:
                    users.remove(name)
                user_selector['values'] = ['Broadcast'] + users + [v for v in user_selector['values'] if v.startswith('[Group]')]
                if user_selector.get() not in user_selector['values']:
                    user_selector.set('Broadcast')

                user_listbox.delete(0, tk.END)
                for user in users:
                    user_listbox.insert(tk.END, user)
            else:
                chat_area.config(state='normal')
                chat_area.insert(tk.END, msg + "\n")
                chat_area.yview(tk.END)
                chat_area.config(state='disabled')
        except:
            break

def send_message(event=None):
    msg = entry.get().strip()
    recipient = user_selector.get()
    if msg:
        if recipient == 'Broadcast':
            chat_area.config(state='normal')
            chat_area.insert(tk.END, f"{name}: {msg}\n")
            chat_area.config(state='disabled')
            client.send(msg.encode('utf-8'))
        elif recipient.startswith("[Group] "):
            group_name = recipient.replace("[Group] ", "")
            chat_area.config(state='normal')
            chat_area.insert(tk.END, f"To group {group_name}: {msg}\n")
            chat_area.config(state='disabled')
            client.send(f"/group_msg {group_name} {msg}".encode('utf-8'))
        else:
            chat_area.config(state='normal')
            chat_area.insert(tk.END, f"To {recipient} (private): {msg}\n")
            chat_area.config(state='disabled')
            client.send(f"/msg {recipient} {msg}".encode('utf-8'))
        entry.delete(0, tk.END)

entry.bind("<Return>", send_message)

threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()