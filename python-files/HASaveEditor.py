import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

class SaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hollywood Animal Save Editor")
        self.current_file = None
        self.original_content = []
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_currencies_tab()
        self.create_gifts_tab()
        
        # Create menu buttons (outside notebook)
        self.create_menu_buttons()
        
    def create_menu_buttons(self):
        # Buttons frame at bottom
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.load_btn = tk.Button(button_frame, text="Load Save", command=self.load_file)
        self.save_btn = tk.Button(button_frame, text="Save Changes", command=self.save_file)
        self.exit_btn = tk.Button(button_frame, text="Exit", command=self.root.quit)
        
        self.load_btn.pack(side='left', padx=5)
        self.save_btn.pack(side='left', padx=5)
        self.exit_btn.pack(side='right', padx=5)

    def create_currencies_tab(self):
        # Currencies Tab
        currencies_frame = ttk.Frame(self.notebook)
        self.notebook.add(currencies_frame, text="Currencies")
        
        # Labels and entries for currencies
        tk.Label(currencies_frame, text="Budget:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Label(currencies_frame, text="Cash:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Label(currencies_frame, text="Reputation:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Label(currencies_frame, text="Influence:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        
        self.budget_entry = tk.Entry(currencies_frame, width=20)
        self.cash_entry = tk.Entry(currencies_frame, width=20)
        self.reputation_entry = tk.Entry(currencies_frame, width=20)
        self.influence_entry = tk.Entry(currencies_frame, width=20)
        
        self.budget_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cash_entry.grid(row=1, column=1, padx=5, pady=5)
        self.reputation_entry.grid(row=2, column=1, padx=5, pady=5)
        self.influence_entry.grid(row=3, column=1, padx=5, pady=5)

    def create_gifts_tab(self):
        # Gifts Tab
        gifts_frame = ttk.Frame(self.notebook)
        self.notebook.add(gifts_frame, text="Gifts")
        
        # Gift types and their display names
        self.gift_types = {
            "WATCH": "Silvermoon Kronos Watch",
            "SIGARS": "Alexandre Dumas Siglo VI Cigars",
            "ALCOHOL": "Whiskey Glennafola 50 Cask Strength",
            "WARDROBE_COUTURE": "Wardrobe by Christo Duvalier",
            "EUROPEAN_SPORTCAR": "Lussuria Atlantic Sports Car"
        }
        
        # Create entry fields for gifts
        for row, (gift_id, display_name) in enumerate(self.gift_types.items()):
            tk.Label(gifts_frame, text=f"{display_name}:").grid(row=row, column=0, padx=5, pady=2, sticky="e")
            entry = tk.Entry(gifts_frame, width=15)
            entry.grid(row=row, column=1, padx=5, pady=2)
            setattr(self, f"{gift_id}_entry", entry)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.original_content = f.readlines()
                self.current_file = file_path
                
                # Load currencies
                currency_patterns = {
                    'budget': r'"budget":\s*(\d+)',
                    'cash': r'"cash":\s*(\d+)',
                    'reputation': r'"reputation":"(\d+\.\d{3})"',
                    'influence': r'"influence":\s*(\d+)'
                }
                
                # Load gifts
                gift_line = None
                for i, line in enumerate(self.original_content):
                    if '"otherCountableResources"' in line:
                        gift_line = self.original_content[i]
                        break
                
                # Process currencies
                found_currencies = {key: False for key in currency_patterns}
                for line in self.original_content:
                    for key, pattern in currency_patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            value = match.group(1)
                            entry = getattr(self, f"{key}_entry")
                            entry.delete(0, tk.END)
                            entry.insert(0, value)
                            found_currencies[key] = True
                
                # Process gifts
                if gift_line:
                    for gift_id in self.gift_types:
                        match = re.search(fr'"{gift_id}":(\d+)', gift_line)
                        entry = getattr(self, f"{gift_id}_entry")
                        entry.delete(0, tk.END)
                        entry.insert(0, match.group(1) if match else '0')
                else:
                    for gift_id in self.gift_types:
                        entry = getattr(self, f"{gift_id}_entry")
                        entry.delete(0, tk.END)
                        entry.insert(0, '0')
                
                # Check for missing currencies
                missing_currencies = [key for key, found in found_currencies.items() if not found]
                if missing_currencies:
                    messagebox.showerror("Error", f"Missing currency values: {', '.join(missing_currencies)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def save_file(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded!")
            return
            
        try:
            # Validate and collect new values
            new_values = {}
            
            # Process currencies
            currency_entries = {
                'budget': (self.budget_entry, r'(?<="budget":)\s*\d+', int),
                'cash': (self.cash_entry, r'(?<="cash":)\s*\d+', int),
                'reputation': (self.reputation_entry, r'(?<="reputation":")\d+\.\d{3}', lambda x: f"{float(x):.3f}"),
                'influence': (self.influence_entry, r'(?<="influence":)\s*\d+', int)
            }
            
            for key, (entry, pattern, validator) in currency_entries.items():
                value = entry.get()
                new_values[key] = (pattern, str(validator(value)))
            
            # Process gifts
            gift_values = {}
            for gift_id in self.gift_types:
                entry = getattr(self, f"{gift_id}_entry")
                value = entry.get()
                if not value.isdigit():
                    raise ValueError(f"Invalid value for {self.gift_types[gift_id]} - must be whole number")
                gift_values[gift_id] = value
            
            # Update file content
            updated_content = []
            gift_line_index = -1
            
            for i, line in enumerate(self.original_content):
                updated_line = line
                
                # Process currencies
                for key, (pattern, replacement) in new_values.items():
                    updated_line = re.sub(pattern, f' {replacement}', updated_line)
                
                # Find gift line
                if '"otherCountableResources"' in updated_line:
                    gift_line_index = i
                    # Process existing gifts
                    for gift_id in self.gift_types:
                        pattern = fr'(?<="{gift_id}":)\d+'
                        updated_line = re.sub(pattern, gift_values[gift_id], updated_line)
                    
                    # Add missing gifts
                    for gift_id in self.gift_types:
                        if f'"{gift_id}":' not in updated_line:
                            # Check if we're at the end of the object
                            if '"$type"' in updated_line and '}}' in updated_line:
                                updated_line = updated_line.replace('}}', f', "{gift_id}":{gift_values[gift_id]}}}')
                            elif '}}' in updated_line:
                                updated_line = updated_line.replace('}}', f', "{gift_id}":{gift_values[gift_id]}}}')
                            else:
                                updated_line = updated_line.replace('}', f', "{gift_id}":{gift_values[gift_id]}}}')
                
                updated_content.append(updated_line)
            
            # Write back to file
            with open(self.current_file, 'w') as f:
                f.writelines(updated_content)
            
            messagebox.showinfo("Success", "Save file updated successfully!")
            
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()
