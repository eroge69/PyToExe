import tkinter as tk
from tkinter import scrolledtext, ttk
from mistralai import Mistral

class DesktopHelper:
    def __init__(self, main_):
        self.root = main_
        self.root.title("Desktop Helper - Arlo")

        # Use a style for ttk widgets
        style = ttk.Style(self.root)
        style.theme_use("clam")  # Use a modern theme

        # Set window size and disable resizing
        self.root.geometry("450x600")
        self.root.resizable(False, False)

        # Set background color
        bg_color = "#e3f3ff"  # Baby blue background
        text_color = "#333333"  # Dark text color
        button_bg = "#3f3fd9"  # Blue buttons
        button_fg = "white"  # White text on buttons
        font = ("Helvetica", 12)

        # Apply background color to the main window
        self.root.configure(bg=bg_color)

        # Configure button style
        style.configure("TButton", background=button_bg, foreground=button_fg, font=font)

        # Create a frame for the entry and buttons
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Create a text entry field
        self.entry = ttk.Entry(input_frame, width=50, font=font)
        self.entry.pack(pady=5, padx=5, fill="x", expand=True)

        # Bind the Enter key to process the command
        self.entry.bind('<Return>', self.on_enter_pressed)

        # Create a button to submit the command
        self.submit_button = ttk.Button(input_frame, text="Submit", command=self.process_command)
        self.submit_button.pack(side="left", fill="x", expand=True, padx=5)

        # Create a clear button
        self.clear_button = ttk.Button(input_frame, text="Clear", command=self.clear_display)
        self.clear_button.pack(side="left", fill="x", expand=True, padx=5)

        # Create a close button
        self.close_button = ttk.Button(input_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side="left", fill="x", expand=True, padx=5)

        # Create a text display area
        self.display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=20, font=font, bg="white", fg=text_color)
        self.display.pack(pady=10, padx=10, fill="both", expand=True)

        # Connect to the Mistral client
        self.api_key = "ySCnKUIRLsNjp2ZVx1JCajSivQBP9Znb"
        if not self.api_key:
            raise ValueError("API key not found. Please set the MISTRAL_API_KEY environment variable.")
        self.client = Mistral(api_key=self.api_key)

        # Initialize to store the context as a list of messages
        self.context = []

    def on_enter_pressed(self, event=None):
        self.process_command()

    def process_command(self, event=None):
        command = self.entry.get()
        if command.strip():  # Check if the command is not empty or only whitespace
            response = self.get_response_from_api(command)
            self.display.insert(tk.END, f"You: {command}\n")
            self.display.insert(tk.END, f"Arlo: {response}\n\n")
            self.entry.delete(0, tk.END)

    def get_response_from_api(self, query):
        # Add the query to the context
        self.context.append({"role": "user", "content": query})

        model = "mistral-large-latest"
        chat_response = self.client.chat.complete(
            model=model,
            messages=self.context
        )
        # Store the response in the context
        assistant_response = chat_response.choices[0].message.content
        self.context.append({"role": "assistant", "content": assistant_response})

        return assistant_response

    def clear_display(self):
        # Clear all text in the display box
        self.display.delete(1.0, tk.END)
        # Clear the context
        self.context.clear()

    def copy_text(self, event=None):
        # Copy selected text to the clipboard
        try:
            selected_text = self.display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            # If no text is selected, do nothing or show a message
            print("No text selected to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopHelper(root)
    root.mainloop()
