import tkinter as tk

class EisenhowerMatrixSimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eisenhower Matrix")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        self.matrix_frame = tk.Frame(root)
        self.matrix_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid weights for matrix frame
        self.matrix_frame.columnconfigure(0, weight=1)
        self.matrix_frame.columnconfigure(1, weight=1)
        self.matrix_frame.rowconfigure(0, weight=1)
        self.matrix_frame.rowconfigure(1, weight=1)

        self.quadrants = {
            "Urgent & Important": self.create_quadrant("Urgent & Important", 0, 0, "#f28b82"),
            "Not Urgent & Important": self.create_quadrant("Not Urgent & Important", 0, 1, "#fbbc04"),
            "Urgent & Not Important": self.create_quadrant("Urgent & Not Important", 1, 0, "#fdd663"),
            "Not Urgent & Not Important": self.create_quadrant("Not Urgent & Not Important", 1, 1, "#81c995"),
        }

        tk.Button(root, text="Clear All", command=self.clear_all).pack(pady=10)

    def create_quadrant(self, title, row, col, color):
        frame = tk.LabelFrame(self.matrix_frame, text=title, bg=color)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        frame.grid_propagate(False)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_frame = tk.Frame(frame, bg=color)
        text_frame.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, bg="white")
        text_widget.pack(fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)

        return text_widget

    def clear_all(self):
        for quadrant in self.quadrants.values():
            quadrant.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = EisenhowerMatrixSimpleApp(root)
    root.mainloop()
