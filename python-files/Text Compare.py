import difflib
import tkinter as tk
from tkinter import ttk

def compare_sentences():
    text1 = entry1.get("1.0", tk.END).rstrip()
    text2 = entry2.get("1.0", tk.END).rstrip()

    result1.tag_delete("insert", "delete", "replace")
    result2.tag_delete("insert", "delete", "replace")

    result1.tag_configure("insert", background="lightgreen")
    result1.tag_configure("delete", background="salmon")
    result1.tag_configure("replace", background="lightblue")

    result2.tag_configure("insert", background="lightgreen")
    result2.tag_configure("delete", background="salmon")
    result2.tag_configure("replace", background="lightblue")

    words1 = text1.split()
    words2 = text2.split()

    matcher = difflib.SequenceMatcher(None, words1, words2)
    opcodes = matcher.get_opcodes()

    def highlight_words(widget, original_text, words, indices, tag):
        start_word_idx, end_word_idx = indices
        count = 0
        for i, word in enumerate(original_text.split()):
            word_start = original_text.find(word, count)
            word_end = word_start + len(word)
            if start_word_idx <= i < end_word_idx:
                start = f"1.0+{word_start}c"
                end = f"1.0+{word_end}c"
                widget.tag_add(tag, start, end)
            count = word_end

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "replace":
            highlight_words(result1, text1, words1, (i1, i2), "replace")
            highlight_words(result2, text2, words2, (j1, j2), "replace")
        elif tag == "delete":
            highlight_words(result1, text1, words1, (i1, i2), "delete")
        elif tag == "insert":
            highlight_words(result2, text2, words2, (j1, j2), "insert")

def clear_all():
    entry1.config(state="normal")
    entry2.config(state="normal")
    entry1.delete("1.0", tk.END)
    entry2.delete("1.0", tk.END)
    entry1.tag_delete("insert", "delete", "replace")
    entry2.tag_delete("insert", "delete", "replace")

# GUI Setup
root = tk.Tk()
root.title("Sentence Comparator")
root.state("zoomed")  # Fullscreen

# Configure layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Text boxes
entry1 = tk.Text(root, wrap="word", font=("Arial", 14))
entry1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

entry2 = tk.Text(root, wrap="word", font=("Arial", 14))
entry2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

# Result references
result1 = entry1
result2 = entry2

# Button frame
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

compare_btn = ttk.Button(button_frame, text="Compare", command=compare_sentences)
compare_btn.pack(side="left", padx=20)

clear_btn = ttk.Button(button_frame, text="Clear", command=clear_all)
clear_btn.pack(side="left", padx=20)

root.mainloop()
