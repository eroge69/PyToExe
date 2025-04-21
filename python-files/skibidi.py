import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import re
import json

class TriggerFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phantom TriggerFinder")
        self.root.configure(bg='black')
        self.triggers = []
        self.selected_folder = ""

        # Load and resize the custom "FLK" icon
        icon_image = Image.open('my_icon.png')  # Ensure this path points to your icon file
        icon_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
        self.my_icon = ImageTk.PhotoImage(icon_image)

        # Create header frame for icon, title, and buttons
        header_frame = tk.Frame(self.root, bg='black')
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Add the custom icon to the header
        icon_label = tk.Label(header_frame, image=self.my_icon, bg='black')
        icon_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Add the title next to the icon
        title_label = tk.Label(header_frame, text="Phantom TriggerFinder", font=("Arial", 16), fg='white', bg='black')
        title_label.pack(side=tk.LEFT, pady=5)

        # Add Save and Edit buttons to the right of the header
        save_button = tk.Button(header_frame, text="Save", command=self.save_triggers, bg='gray', fg='white')
        save_button.pack(side=tk.RIGHT, padx=10)
        edit_button = tk.Button(header_frame, text="Edit", command=self.edit_trigger, bg='gray', fg='white')
        edit_button.pack(side=tk.RIGHT, padx=10)

        # Configure style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('T.PanedWindow', background='black')
        style.configure('Treeview', background='black', foreground='white', fieldbackground='black')
        style.map('Treeview', background=[('selected', 'red')], foreground=[('selected', 'white')])
        style.configure('TButton', background='black', foreground='white')

        # Main layout using PanedWindow
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Folder Tree)
        left_frame = tk.Frame(self.paned, bg='black')
        self.paned.add(left_frame, weight=1)
        
        self.folder_search_var = tk.StringVar()
        folder_search_entry = tk.Entry(left_frame, textvariable=self.folder_search_var, bg='black', fg='white', insertbackground='white')
        folder_search_entry.pack(fill=tk.X, padx=5, pady=5)
        folder_search_entry.bind('<KeyRelease>', self.filter_tree)
        
        self.folder_tree = ttk.Treeview(left_frame, show='tree')
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_file_select)

        # Central Code Area
        center_frame = tk.Frame(self.paned, bg='black')
        self.paned.add(center_frame, weight=3)
        
        self.code_text = scrolledtext.ScrolledText(center_frame, bg='black', fg='white', insertbackground='white', wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.configure(state='disabled')
        
        # Define tags for syntax highlighting
        self.code_text.tag_configure('keyword', foreground='red')
        self.code_text.tag_configure('string', foreground='green')
        self.code_text.tag_configure('comment', foreground='gray')
        self.code_text.tag_configure('highlight', background='#333333', foreground='white')

        # Right Sidebar (Triggers)
        right_frame = tk.Frame(self.paned, bg='black')
        self.paned.add(right_frame, weight=1)
        
        # Trigger search bar
        self.trigger_search_var = tk.StringVar()
        trigger_search_entry = tk.Entry(right_frame, textvariable=self.trigger_search_var, bg='black', fg='white', insertbackground='white')
        trigger_search_entry.pack(fill=tk.X, padx=5, pady=2)
        trigger_search_entry.bind('<KeyRelease>', self.filter_triggers)
        
        tk.Label(right_frame, text="Triggers", bg='black', fg='white').pack(pady=2)
        self.trigger_list = tk.Listbox(right_frame, bg='black', fg='white', selectbackground='red', selectforeground='white', width=50)
        self.trigger_list.pack(fill=tk.BOTH, expand=True)
        self.trigger_list.bind('<<ListboxSelect>>', self.on_trigger_select)
        
        # Action Buttons
        btn_frame = tk.Frame(right_frame, bg='black')
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Save Selected", command=self.save_selected, bg='black', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected, bg='black', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Open File", command=self.open_file, bg='black', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Add New Event", command=self.add_new_event, bg='black', fg='white').pack(side=tk.LEFT, padx=2)

        # Menu Bar
        menubar = tk.Menu(root, bg='black', fg='white', activebackground='red', activeforeground='white')
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, bg='black', fg='white', activebackground='red')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Browse Folder", command=self.browse_folder)
        file_menu.add_command(label="Search Events", command=self.search_events)
        file_menu.add_command(label="Load Saved Triggers", command=self.load_triggers)
        file_menu.add_command(label="Save Triggers", command=self.save_triggers)
        file_menu.add_command(label="Export to HTML", command=self.export_to_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_tree.delete(*self.folder_tree.get_children())
            self.load_folder_tree(folder)

    def load_folder_tree(self, folder):
        for item in os.listdir(folder):
            path = os.path.join(folder, item)
            if os.path.isdir(path):
                folder_id = self.folder_tree.insert('', 'end', text=item, open=False)
                self.load_folder_tree_recursive(path, folder_id)
            elif item.endswith('.lua'):
                self.folder_tree.insert('', 'end', text=item)

    def load_folder_tree_recursive(self, folder, parent):
        for item in os.listdir(folder):
            path = os.path.join(folder, item)
            if os.path.isdir(path):
                folder_id = self.folder_tree.insert(parent, 'end', text=item, open=False)
                self.load_folder_tree_recursive(path, folder_id)
            elif item.endswith('.lua'):
                self.folder_tree.insert(parent, 'end', text=item)

    def on_file_select(self, event):
        selected = self.folder_tree.selection()
        if selected:
            item = self.folder_tree.item(selected)
            file_name = item['text']
            if file_name.endswith('.lua'):
                file_path = os.path.join(self.selected_folder, file_name)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.code_text.configure(state='normal')
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(tk.END, content)
                self.code_text.configure(state='disabled')
                self.apply_syntax_highlighting(content)

    def apply_syntax_highlighting(self, content):
        self.code_text.configure(state='normal')
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, content)
        keywords = ['TriggerEvent', 'TriggerServerEvent', 'TriggerClientEvent', 'AddEventHandler', 'RegisterNetEvent']
        for keyword in keywords:
            start = '1.0'
            while True:
                pos = self.code_text.search(keyword, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.code_text.tag_add('keyword', pos, end)
                start = end
        self.code_text.configure(state='disabled')

    def search_events(self):
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        self.triggers = []
        patterns = [
            r'TriggerEvent\s*\(\s*["\']([^"\']+)["\'](?:,\s*([^)]+))?\)',
            r'TriggerServerEvent\s*\(\s*["\']([^"\']+)["\'](?:,\s*([^)]+))?\)',
            r'TriggerClientEvent\s*\(\s*["\']([^"\']+)["\'](?:,\s*([^)]+))?\)',
            r'AddEventHandler\s*\(\s*["\']([^"\']+)["\'](?:,\s*([^)]+))?\)',
            r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\'](?:,\s*([^)]+))?\)'
        ]
        for root, _, files in os.walk(self.selected_folder):
            for file in files:
                if file.endswith('.lua'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            for pattern in patterns:
                                matches = re.finditer(pattern, line)
                                for match in matches:
                                    event_name = match.group(1)
                                    args = match.group(2) if match.group(2) else ''
                                    func = pattern.split('\\')[0]
                                    event_type = {
                                        'TriggerEvent': 'Local',
                                        'TriggerServerEvent': 'Client-to-Server',
                                        'TriggerClientEvent': 'Server-to-Client',
                                        'AddEventHandler': 'Handler',
                                        'RegisterNetEvent': 'Net Register'
                                    }.get(func, 'Unknown')
                                    full_trigger = f"{func}('{event_name}'"
                                    if args:
                                        full_trigger += f", {args.strip()}"
                                    full_trigger += ")"
                                    self.triggers.append({
                                        'full_trigger': full_trigger,
                                        'event': event_name,
                                        'file': file_path,
                                        'line': i,
                                        'type': event_type,
                                        'code_line': line.strip()
                                    })
        self.update_trigger_list()

    def update_trigger_list(self):
        self.trigger_list.delete(0, tk.END)
        for trigger in self.triggers:
            self.trigger_list.insert(tk.END, trigger['full_trigger'])

    def on_trigger_select(self, event):
        selection = self.trigger_list.curselection()
        if selection:
            index = selection[0]
            trigger = self.triggers[index]
            file_path = trigger['file']
            line_num = trigger['line']
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.code_text.configure(state='normal')
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(tk.END, content)
            self.code_text.see(f"{line_num}.0")
            self.code_text.tag_remove('highlight', '1.0', tk.END)
            self.code_text.tag_add('highlight', f"{line_num}.0", f"{line_num}.end")
            self.code_text.configure(state='disabled')
            self.apply_syntax_highlighting(content)

    def filter_triggers(self, event):
        search_term = self.trigger_search_var.get().lower()
        self.trigger_list.delete(0, tk.END)
        for trigger in self.triggers:
            if search_term in trigger['full_trigger'].lower():
                self.trigger_list.insert(tk.END, trigger['full_trigger'])

    def filter_tree(self, event):
        pass

    def save_triggers(self):
        messagebox.showinfo("Info", "Save functionality not implemented yet.")

    def edit_trigger(self):
        messagebox.showinfo("Info", "Edit functionality not implemented yet.")

    def save_selected(self):
        messagebox.showinfo("Info", "Save Selected not implemented yet.")

    def delete_selected(self):
        messagebox.showinfo("Info", "Delete Selected not implemented yet.")

    def open_file(self):
        selection = self.trigger_list.curselection()
        if selection:
            index = selection[0]
            trigger = self.triggers[index]
            os.startfile(trigger['file'])

    def add_new_event(self):
        messagebox.showinfo("Info", "Add New Event not implemented yet.")

    def load_triggers(self):
        messagebox.showinfo("Info", "Load Triggers not implemented yet.")

    def export_to_html(self):
        if not self.triggers:
            messagebox.showwarning("Warning", "No triggers to export.")
            return

        # Define important keywords
        important_keywords = ["Item", "Money", "reward", "finish", "giveReward", "giveItemToPlayer", "giveItem", "AddMoney", "GiveChestItem"]
        
        # Categorize triggers
        important_triggers = []
        obfuscated_triggers = []
        other_triggers = []
        
        for trigger in self.triggers:
            event_name = trigger['event']
            
            # Check for obfuscation: long strings (>20 chars with mixed letters/numbers/symbols) or base64-like patterns
            is_obfuscated = False
            if len(event_name) > 20 and re.search(r'[a-zA-Z0-9+/=]{20,}', event_name):
                is_obfuscated = True
            elif re.search(r'^[A-Za-z0-9+/=]+$', event_name) and event_name.endswith('='):
                is_obfuscated = True
            
            if is_obfuscated:
                obfuscated_triggers.append(trigger)
                continue
                
            # Check for important triggers (after the colon)
            if ':' in event_name:
                event_suffix = event_name.split(':', 1)[1]
                is_important = any(keyword.lower() in event_suffix.lower() for keyword in important_keywords)
            else:
                is_important = False
                
            if is_important:
                important_triggers.append(trigger)
            else:
                other_triggers.append(trigger)

        # Convert trigger data to JSON
        trigger_data = {
            "important": important_triggers,
            "obfuscated": obfuscated_triggers,
            "others": other_triggers
        }
        trigger_json = json.dumps(trigger_data)

        # HTML content with side-by-side sections and toggle functionality
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Phantom TriggerFinder</title>
    <style>
        body {{ background-color: black; color: white; font-family: Arial, sans-serif; }}
        header {{ display: flex; align-items: center; padding: 10px; }}
        header img {{ width: 50px; height: 50px; margin-right: 10px; }}
        header h1 {{ margin: 0; }}
        .main {{ display: flex; flex-direction: column; }}
        .trigger-container {{ display: flex; justify-content: space-between; width: 100%; }}
        .trigger-section {{ width: 32%; padding: 10px; }}
        .code-viewer {{ width: 100%; padding: 10px; }}
        ul {{ list-style: none; padding: 0; display: none; }}
        li {{ cursor: pointer; padding: 5px; margin: 2px 0; }}
        li:hover {{ background-color: #333; }}
        pre {{ background-color: #111; padding: 10px; border-radius: 5px; }}
        .important {{ background-color: #2a2a2a; border-left: 3px solid red; }}
        .obfuscated {{ background-color: #2a2a2a; border-left: 3px solid purple; }}
        h2 {{ cursor: pointer; margin: 0; padding: 5px; background-color: #222; border-radius: 3px; }}
        h2:hover {{ background-color: #333; }}
    </style>
</head>
<body>
    <header>
        <img src="my_icon.png" alt="FLK Icon">
        <h1>Phantom TriggerFinder</h1>
    </header>
    <div class="main">
        <div class="trigger-container">
            <div class="trigger-section">
                <h2 onclick="toggleSection('important-triggers')">Fontos</h2>
                <ul id="important-triggers"></ul>
            </div>
            <div class="trigger-section">
                <h2 onclick="toggleSection('obfuscated-triggers')">Obfuscated</h2>
                <ul id="obfuscated-triggers"></ul>
            </div>
            <div class="trigger-section">
                <h2 onclick="toggleSection('other-triggers')">Egyéb Triggerek</h2>
                <ul id="other-triggers"></ul>
            </div>
        </div>
        <div class="code-viewer">
            <h2>Code</h2>
            <pre id="code"></pre>
            <p><strong>File:</strong> <span id="file-path"></span></p>
            <p><strong>Line:</strong> <span id="line-number"></span></p>
            <p><strong>Type:</strong> <span id="event-type"></span></p>
        </div>
    </div>
    <script>
        const triggerData = {trigger_json};

        const importantTriggerList = document.getElementById('important-triggers');
        const obfuscatedTriggerList = document.getElementById('obfuscated-triggers');
        const otherTriggerList = document.getElementById('other-triggers');
        const codePre = document.getElementById('code');
        const filePathSpan = document.getElementById('file-path');
        const lineNumberSpan = document.getElementById('line-number');
        const eventTypeSpan = document.getElementById('event-type');

        function toggleSection(sectionId) {{
            const ul = document.getElementById(sectionId);
            ul.style.display = ul.style.display === 'block' ? 'none' : 'block';
        }}

        function populateList(ul, triggers, className) {{
            triggers.forEach(trigger => {{
                const li = document.createElement('li');
                li.textContent = trigger.full_trigger;
                li.className = className;
                li.onclick = () => {{
                    codePre.textContent = trigger.code_line;
                    filePathSpan.textContent = trigger.file;
                    lineNumberSpan.textContent = trigger.line;
                    eventTypeSpan.textContent = trigger.type;
                }};
                ul.appendChild(li);
            }});
        }}

        populateList(importantTriggerList, triggerData.important, 'important');
        populateList(obfuscatedTriggerList, triggerData.obfuscated, 'obfuscated');
        populateList(otherTriggerList, triggerData.others, '');

    </script>
</body>
</html>
"""
        # Save the HTML content to a file
        with open("triggers_export.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        messagebox.showinfo("Success", "Triggers exported to triggers_export.html")

if __name__ == "__main__":
    root = tk.Tk()
    app = TriggerFinderGUI(root)
    root.mainloop()