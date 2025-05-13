import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import time
import threading
import json
import os
import pickle

class VisualNovelTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Novel Display - NVL Mode")
        
        # Set the initial window size to 800x600
        self.width = 800
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Text display settings
        self.typewriter_speed = 0.05  # seconds per character
        self.sentences = []
        self.current_sentence_index = 0
        self.displayed_text = ""
        self.displayed_paragraphs = []
        self.sentences_per_page = 4  # Auto-clear after this many sentences
        self.sentence_counter = 0    # To track when to clear the screen
        
        # File handling variables
        self.current_file_path = None
        self.save_file_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        
        # Create save directory if it doesn't exist
        if not os.path.exists(self.save_file_directory):
            os.makedirs(self.save_file_directory)
        
        # State flags
        self.is_typing = False
        self.is_waiting = False
        self.typing_thread = None
        self.stop_typing = False  # Flag to stop typing thread
        self.animation_completed = False  # Track if current animation is completed
        self.all_text_displayed = False  # Track if all text has been displayed
        
        # Colors
        self.background_color = "#000000"  # Black
        self.text_color = "#FFFFFF"  # White
        self.border_color = "#CCCCCC"  # Light gray
        self.button_bg = "#333333"  # Dark gray
        self.button_fg = "#FFFFFF"  # White
        
        # Main frame
        self.main_frame = tk.Frame(root, bg=self.background_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create the text display frame with border (NVL area)
        self.frame = tk.Frame(self.main_frame, bg=self.border_color, padx=2, pady=2)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the text widget for NVL display
        self.text_display = tk.Text(self.frame, bg=self.background_color, fg=self.text_color,
                                   wrap=tk.WORD, padx=15, pady=15, relief=tk.FLAT,
                                   highlightthickness=0, font=("DejaVu Sans Mono", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_display.config(state=tk.DISABLED)  # Make it read-only
        
        # Add click-to-advance binding
        self.text_display.bind("<Button-1>", self.handle_next)
        
        # Create control buttons frame
        self.control_frame = tk.Frame(self.main_frame, bg=self.background_color)
        self.control_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Add history button
        self.history_button = tk.Button(self.control_frame, text="History", 
                                       command=self.show_history, bg=self.button_bg, 
                                       fg=self.button_fg, padx=10)
        self.history_button.pack(side=tk.LEFT, padx=5)
        
        # Add save/load buttons
        self.save_button = tk.Button(self.control_frame, text="Save", 
                                    command=self.save_progress, bg=self.button_bg,
                                    fg=self.button_fg, padx=10)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.load_button = tk.Button(self.control_frame, text="Load", 
                                    command=self.load_progress, bg=self.button_bg,
                                    fg=self.button_fg, padx=10)
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Create a status bar for instructions
        self.status_bar = tk.Label(root, text="SPACE/ENTER/X/CLICK: Next | C: Clear | UP/DOWN: Speed",
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set up key bindings
        self.root.bind("<space>", self.handle_next)
        self.root.bind("<Return>", self.handle_next)
        self.root.bind("x", self.handle_next)
        self.root.bind("X", self.handle_next)
        self.root.bind("c", self.clear_screen)
        self.root.bind("C", self.clear_screen)
        self.root.bind("<Up>", self.increase_speed)
        self.root.bind("<Down>", self.decrease_speed)
        
        # History of all displayed text
        self.text_history = []
        
        # Show file selection dialog or welcome message
        self.prompt_for_file()
    
    def create_menu_bar(self):
        """Create a menu bar with File options"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Open Text File", command=self.load_text_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save Progress", command=self.save_progress)
        file_menu.add_command(label="Load Progress", command=self.load_progress)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def prompt_for_file(self):
        """Show welcome message and prompt user to select a file"""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)
        welcome_message = (
            "Welcome to the Enhanced Visual Novel Display!\n\n"
            "Please use the 'File > Open Text File' menu to load your story text, "
            "or click the button below to select a file.\n\n"
            "New features:\n"
            "• Click screen to advance text\n"
            "• History button to review past text\n"
            "• Save/Load your reading progress\n"
            "• Load text from files\n\n"
        )
        self.text_display.insert(tk.END, welcome_message)
        
        # Add a button directly in the text display
        open_button_frame = tk.Frame(self.text_display, bg=self.background_color)
        open_button = tk.Button(open_button_frame, text="Select Text File", 
                               command=self.load_text_file, bg=self.button_bg,
                               fg=self.button_fg, padx=10, pady=5)
        open_button.pack(pady=10)
        
        self.text_display.window_create(tk.END, window=open_button_frame)
        
        # Or add a sample text option
        self.text_display.insert(tk.END, "\n\nOr load a sample story:")
        
        sample_button_frame = tk.Frame(self.text_display, bg=self.background_color)
        sample_button = tk.Button(sample_button_frame, text="Load Sample Text", 
                                 command=self.load_sample_text, bg=self.button_bg,
                                 fg=self.button_fg, padx=10, pady=5)
        sample_button.pack(pady=10)
        
        self.text_display.window_create(tk.END, window=sample_button_frame)
        self.text_display.config(state=tk.DISABLED)
    
    def load_text_file(self):
        """Open a file dialog to select a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        
        if file_path:
            self.current_file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    self.set_text(text)
                    # Update window title with filename
                    filename = os.path.basename(file_path)
                    self.root.title(f"Visual Novel - {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")
    
    def load_sample_text(self):
        """Load a sample text for demonstration"""
        sample_text = (
            "Welcome to the Enhanced Visual Novel Display program with NVL mode! "
            "This displays text in a novel-like format across the full screen. "
            "Each sentence appears with a typewriter effect. "
            "You can press SPACE, ENTER, X, or simply CLICK the screen to continue. "
            "Press C to clear the screen when it gets too full. "
            "Use UP and DOWN arrows to adjust the typing speed. "
            "Click the History button to review previously read text. "
            "You can now save your progress and continue later! "
            "This mode is perfect for descriptive passages and narration. "
            "The screen will automatically refresh every four sentences. "
            "Try clicking anywhere on this screen to advance to the next sentence. "
            "You can save your progress at any time with the Save button. "
            "Enjoy using this enhanced visual novel system!"
        )
        self.current_file_path = "sample_text"  # Fake path for sample
        self.set_text(sample_text)
        self.root.title("Visual Novel - Sample Text")
    
    def set_text(self, text):
        """Set the text to be displayed and split into sentences."""
        # Split text into sentences (simple split on ., ! and ?)
        text = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').replace('."', '."|').replace('?"', '?"|').replace('!"', '!"|')
        self.sentences = [s.strip() for s in text.split('|') if s.strip()]
        self.current_sentence_index = 0
        self.displayed_paragraphs = []
        self.text_history = []  # Reset history
        self.sentence_counter = 0  # Reset counter when new text is set
        self.all_text_displayed = False
        self.display_next_sentence()
    
    def show_history(self):
        """Show a window with all previously displayed text"""
        if not self.text_history:
            messagebox.showinfo("History", "No text history available yet.")
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("Reading History")
        history_window.geometry("600x400")
        
        # Create a scrolled text widget to display history
        history_text = scrolledtext.ScrolledText(
            history_window, 
            wrap=tk.WORD, 
            bg=self.background_color,
            fg=self.text_color,
            font=("DejaVu Sans Mono", 12),
            padx=15,
            pady=15
        )
        history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert all history text
        for sentence in self.text_history:
            history_text.insert(tk.END, sentence + "\n\n")
        
        # Scroll to the end
        history_text.see(tk.END)
        
        # Close button
        close_button = tk.Button(
            history_window, 
            text="Close", 
            command=history_window.destroy,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=10
        )
        close_button.pack(pady=10)
        
        # Center the window
        history_window.update_idletasks()
        width = history_window.winfo_width()
        height = history_window.winfo_height()
        x = (history_window.winfo_screenwidth() // 2) - (width // 2)
        y = (history_window.winfo_screenheight() // 2) - (height // 2)
        history_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make window modal
        history_window.transient(self.root)
        history_window.grab_set()
        self.root.wait_window(history_window)
    
    def save_progress(self):
        """Save the current reading progress"""
        if not self.current_file_path or not self.sentences:
            messagebox.showinfo("Save", "No text loaded to save progress for.")
            return
            
        # Generate a save file name based on the current text file
        base_name = os.path.basename(self.current_file_path)
        if base_name == "sample_text":  # Handle sample text
            base_name = "sample_text.txt"
            
        file_name = os.path.splitext(base_name)[0]
        save_name = filedialog.asksaveasfilename(
            initialdir=self.save_file_directory,
            title="Save Your Progress",
            initialfile=f"{file_name}_save",
            defaultextension=".vnsave",
            filetypes=(("Visual Novel Save", "*.vnsave"), ("All files", "*.*"))
        )
        
        if not save_name:
            return  # User cancelled
            
        save_data = {
            'current_sentence_index': self.current_sentence_index,
            'text_history': self.text_history,
            'source_file': self.current_file_path
        }
        
        try:
            # Use pickle to save the data
            with open(save_name, 'wb') as f:
                pickle.dump(save_data, f)
            messagebox.showinfo("Save", "Progress saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save progress: {e}")
    
    def load_progress(self):
        """Load a previously saved reading progress"""
        load_name = filedialog.askopenfilename(
            initialdir=self.save_file_directory,
            title="Load Your Progress",
            filetypes=(("Visual Novel Save", "*.vnsave"), ("All files", "*.*"))
        )
        
        if not load_name:
            return  # User cancelled
            
        try:
            # Load the saved data
            with open(load_name, 'rb') as f:
                save_data = pickle.load(f)
                
            source_file = save_data.get('source_file')
            
            # Check if we need to load the source file first
            if source_file != self.current_file_path:
                if source_file == "sample_text":
                    # Handle sample text
                    self.load_sample_text()
                elif os.path.exists(source_file):
                    # Load the original text file
                    with open(source_file, 'r', encoding='utf-8') as file:
                        text = file.read()
                        # Set text but don't start displaying
                        text = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|')
                        self.sentences = [s.strip() for s in text.split('|') if s.strip()]
                        self.root.title(f"Visual Novel - {os.path.basename(source_file)}")
                        self.current_file_path = source_file
                else:
                    # Source file not found
                    messagebox.showerror("Error", f"Source file not found: {source_file}")
                    return
            
            # Restore the saved state
            self.text_history = save_data.get('text_history', [])
            self.current_sentence_index = save_data.get('current_sentence_index', 0)
            
            # Reset display state
            self.displayed_paragraphs = []
            self.sentence_counter = 0
            self.all_text_displayed = False
            
            # Show last few sentences from history to provide context
            last_sentences = self.text_history[-4:] if len(self.text_history) > 4 else self.text_history
            self.displayed_paragraphs = last_sentences
            
            # Update the display
            self.update_display()
            self.is_waiting = True
            self.animation_completed = True
            self.show_continue_indicator()
            
            messagebox.showinfo("Load", f"Progress loaded! Continuing from sentence {self.current_sentence_index}.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load progress: {e}")
    
    def display_next_sentence(self):
        """Display the next sentence in the sequence."""
        if self.current_sentence_index < len(self.sentences):
            # Check if we need to clear the screen (every 4 sentences)
            if self.sentence_counter >= self.sentences_per_page:
                self.clear_screen()
                self.sentence_counter = 0
            
            self.is_typing = True
            self.is_waiting = False
            self.animation_completed = False
            self.displayed_text = ""
            
            # Start the typing animation in a separate thread
            self.stop_typing = False
            if self.typing_thread and self.typing_thread.is_alive():
                self.stop_typing = True
                self.typing_thread.join()
                
            self.typing_thread = threading.Thread(target=self.animate_typing)
            self.typing_thread.daemon = True
            self.typing_thread.start()
            
            self.current_sentence_index += 1
            self.sentence_counter += 1
        else:
            # We've reached the end of all sentences
            self.is_typing = False
            self.is_waiting = False
            self.all_text_displayed = True
            self.show_completion_message()
    
    def animate_typing(self):
        """Typewriter animation effect in a separate thread"""
        current_sentence = self.sentences[self.current_sentence_index - 1]
        
        for i in range(len(current_sentence) + 1):
            if self.stop_typing:
                break
                
            self.displayed_text = current_sentence[:i]
            
            # Update the UI from the main thread
            self.root.after(0, self.update_display)
            time.sleep(self.typewriter_speed)
            
        # Ensure the full sentence is displayed even if typing was stopped
        self.displayed_text = current_sentence
        
        # Add to text history
        if current_sentence not in self.text_history:
            self.text_history.append(current_sentence)
        
        # Set the waiting state once typing is done
        self.is_typing = False
        self.animation_completed = True
        
        # Add the completed sentence to displayed paragraphs
        if self.displayed_text and (not self.displayed_paragraphs or self.displayed_text != self.displayed_paragraphs[-1]):
            # If we already have the maximum sentences, replace the oldest one
            if len(self.displayed_paragraphs) >= self.sentences_per_page:
                self.displayed_paragraphs = self.displayed_paragraphs[-(self.sentences_per_page-1):]
            
            self.displayed_paragraphs.append(self.displayed_text)
        
        # Update the display and show continue indicator
        self.root.after(0, self.update_display)
        self.is_waiting = True
        self.root.after(0, self.show_continue_indicator)
        
    def update_display(self):
        """Update the text on screen with the current displayed text"""
        # If we're still typing, just update the current text
        current_display = []
        
        # Add all completed paragraphs
        current_display.extend(self.displayed_paragraphs)
        
        # If we're still typing, add the current text being typed
        if self.is_typing:
            current_display.append(self.displayed_text)
            
        # Update the text display
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)
        
        # Display all paragraphs with spacing
        for i, paragraph in enumerate(current_display):
            self.text_display.insert(tk.END, paragraph + "\n\n")
            
        self.text_display.config(state=tk.DISABLED)
    
    def show_continue_indicator(self):
        """Show a continue indicator when waiting for input"""
        if self.is_waiting:
            self.text_display.config(state=tk.NORMAL)
            self.text_display.insert(tk.END, "\n▼")  # Down arrow as continue indicator
            self.text_display.config(state=tk.DISABLED)
            
    def show_completion_message(self):
        """Show a message when all text has been displayed"""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.insert(tk.END, "\n\n--- End of Visual Novel ---\n")
        self.text_display.insert(tk.END, "All text has been displayed.")
        self.text_display.config(state=tk.DISABLED)
        
        # Update status bar
        self.status_bar.config(text="Visual Novel Complete | C: Clear | Press ESC to exit")
        
        # Add ESC key binding to exit
        self.root.bind("<Escape>", lambda e: self.root.quit())
    
    def handle_next(self, event=None):
        """Handle space/enter/X key to advance text"""
        if self.is_typing:
            # If we're currently typing, complete the animation immediately
            self.stop_typing = True
        elif self.is_waiting and self.animation_completed:
            # If we've completed a sentence animation and are waiting for input,
            # move to the next sentence
            self.animation_completed = False  # Reset for next sentence
            self.display_next_sentence()
            
    def clear_screen(self, event=None):
        """Clear the screen (NVL-specific function)"""
        self.displayed_paragraphs = []
        self.update_display()
            
    def increase_speed(self, event=None):
        """Make typing faster"""
        self.typewriter_speed = max(0.01, self.typewriter_speed - 0.01)
        self.update_status()
        
    def decrease_speed(self, event=None):
        """Make typing slower"""
        self.typewriter_speed = min(0.2, self.typewriter_speed + 0.01)
        self.update_status()
    
    def update_status(self):
        """Update the status bar with current speed"""
        speed_info = f"Typing Speed: {self.typewriter_speed:.2f}s | "
        self.status_bar.config(text=f"{speed_info}SPACE/ENTER/X/CLICK: Next | C: Clear | UP/DOWN: Speed")

def main():
    root = tk.Tk()
    app = VisualNovelTkinter(root)
    root.mainloop()

if __name__ == "__main__":
    main()