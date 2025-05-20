import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu, filedialog
import subprocess
import os
import shutil
import sys

clipboard = None
current_dir = os.getcwd()

def load_icons():
    global icons
    icons = {}
    try:
        icons['folder'] = tk.PhotoImage(file="folder_icon.png")
        icons['file'] = tk.PhotoImage(file="file_icon.png")
    except:
        icons['folder'] = tk.PhotoImage(width=16, height=16)
        icons['file'] = tk.PhotoImage(width=16, height=16)

def insert_node(parent, path):
    try:
        for name in os.listdir(path):
            abspath = os.path.join(path, name)
            is_dir = os.path.isdir(abspath)
            node = tree.insert(parent, 'end', text=name, open=False, values=[abspath])
            if is_dir:
                tree.insert(node, 'end')  # dummy for expansion
    except:
        pass

def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    root_path = "C:\\" if sys.platform.startswith("win") else "/"
    root_node = tree.insert('', 'end', text=root_path, open=False, values=[root_path])
    insert_node(root_node, root_path)

def on_tree_expand(event):
    node = tree.focus()
    path = tree.item(node)['values'][0]
    children = tree.get_children(node)
    if len(children) == 1 and not tree.item(children[0], 'values'):
        tree.delete(children[0])
        insert_node(node, path)

def on_tree_select(event):
    global current_dir
    node = tree.focus()
    path = tree.item(node)['values'][0]
    current_dir = os.path.dirname(path) if os.path.isfile(path) else path
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(5000)
                preview.delete(1.0, tk.END)
                preview.insert(tk.END, content)
        except:
            preview.delete(1.0, tk.END)
            preview.insert(tk.END, "[Cannot preview this file]")

def rename_item(path):
    new_name = filedialog.asksaveasfilename(initialdir=os.path.dirname(path), title="Rename file/folder", initialfile=os.path.basename(path))
    if new_name and os.path.basename(new_name) != os.path.basename(path):
        try:
            os.rename(path, new_name)
            update_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename: {e}")

def delete_item(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        update_treeview()
    except Exception as e:
        terminal.insert(tk.END, f"Delete error: {e}\n")

def open_file(path):
    try:
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        terminal.insert(tk.END, f"Failed to open: {e}\n")

def copy_item(path):
    global clipboard
    clipboard = path

def cut_item(path):
    global clipboard
    clipboard = ("cut", path)

def paste_item():
    global clipboard
    if clipboard is None:
        return
    src = clipboard[1] if isinstance(clipboard, tuple) else clipboard
    try:
        dst = os.path.join(current_dir, os.path.basename(src))
        if isinstance(clipboard, tuple) and clipboard[0] == "cut":
            shutil.move(src, dst)
        else:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        update_treeview()
    except Exception as e:
        terminal.insert(tk.END, f"Paste error: {e}\n")

def on_right_click(event):
    try:
        row_id = tree.identify_row(event.y)
        if not row_id:
            return
        tree.selection_set(row_id)
        path = tree.item(row_id)['values'][0]
        menu = Menu(root, tearoff=0)
        if os.path.isdir(path):
            menu.add_command(label="Open Folder", command=lambda: open_file(path))
        else:
            menu.add_command(label="Open File", command=lambda: open_file(path))
        menu.add_command(label="Rename", command=lambda: rename_item(path))
        menu.add_command(label="Delete", command=lambda: delete_item(path))
        menu.add_command(label="Copy", command=lambda: copy_item(path))
        menu.add_command(label="Cut", command=lambda: cut_item(path))
        menu.add_command(label="Paste", command=paste_item)
        menu.post(event.x_root, event.y_root)
    except:
        pass

def run_command(event=None):
    global current_dir
    cmd = entry.get()
    terminal.insert(tk.END, f"> {cmd}\n")
    if cmd == "exit":
        root.destroy()
        return
    if cmd.startswith('print("') and cmd.endswith('")'):
        terminal.insert(tk.END, cmd[7:-2] + "\n")
    elif cmd.startswith("cd "):
        try:
            os.chdir(os.path.join(current_dir, cmd[3:].strip()))
            current_dir = os.getcwd()
            update_treeview()
        except Exception as e:
            terminal.insert(tk.END, f"cd error: {e}\n")
    elif cmd == "pwd":
        terminal.insert(tk.END, current_dir + "\n")
    elif cmd in ["ls", "dir"]:
        try:
            terminal.insert(tk.END, "\n".join(os.listdir(current_dir)) + "\n")
        except Exception as e:
            terminal.insert(tk.END, f"ls error: {e}\n")
    else:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=current_dir)
            terminal.insert(tk.END, result.stdout + result.stderr)
        except Exception as e:
            terminal.insert(tk.END, f"Error: {e}\n")
    entry.delete(0, tk.END)

def create_folder():
    name = filedialog.asksaveasfilename(initialdir=current_dir, title="New folder")
    if name:
        os.makedirs(name, exist_ok=True)
        update_treeview()

# GUI setup
root = tk.Tk()
root.title("🌍 File Explorer + Terminal")

load_icons()

# Toolbar
toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X)
tk.Button(toolbar, text="🔄 Refresh", command=update_treeview).pack(side=tk.LEFT)
tk.Button(toolbar, text="📁 New Folder", command=create_folder).pack(side=tk.LEFT)

# Main layout
main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=True)

# File browser (treeview)
file_frame = tk.Frame(main)
file_frame.pack(side=tk.LEFT, fill=tk.Y)

tree = ttk.Treeview(file_frame)
tree.pack(side=tk.LEFT, fill=tk.Y)
tree.bind("<<TreeviewOpen>>", on_tree_expand)
tree.bind("<<TreeviewSelect>>", on_tree_select)
tree.bind("<Button-3>", on_right_click)

# Content (preview + terminal)
content_frame = tk.Frame(main)
content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

preview = tk.Text(content_frame, height=10, bg="#f0f0f0")
preview.pack(fill=tk.X, padx=5, pady=5)

terminal = scrolledtext.ScrolledText(content_frame, height=20, bg="black", fg="white")
terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Command entry
entry = tk.Entry(root, bg="black", fg="white")
entry.pack(fill=tk.X, padx=5, pady=5)
entry.bind("<Return>", run_command)

# Load filesystem
update_treeview()
entry.focus()
root.mainloop()
