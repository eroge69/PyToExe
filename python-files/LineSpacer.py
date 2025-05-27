{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "c9ca9d7d-0cfc-4753-8951-61f98cd9c898",
   "metadata": {},
   "outputs": [],
   "source": [
    "import tkinter as tk\n",
    "from tkinter import scrolledtext, filedialog\n",
    "\n",
    "def add_line_spaces():\n",
    "    input_text = input_box.get(\"1.0\", tk.END).strip()\n",
    "    lines = input_text.splitlines()\n",
    "    spaced_text = \"\\n\\n\".join(lines)\n",
    "    output_box.delete(\"1.0\", tk.END)\n",
    "    output_box.insert(tk.END, spaced_text)\n",
    "\n",
    "def save_to_file():\n",
    "    content = output_box.get(\"1.0\", tk.END).strip()\n",
    "    if not content:\n",
    "        return\n",
    "\n",
    "    file_path = filedialog.asksaveasfilename(\n",
    "        defaultextension=\".txt\",\n",
    "        filetypes=[(\"Text Files\", \"*.txt\"), (\"All Files\", \"*.*\")],\n",
    "        title=\"Save Output As\"\n",
    "    )\n",
    "\n",
    "    if file_path:\n",
    "        with open(file_path, 'w', encoding='utf-8') as file:\n",
    "            file.write(content)\n",
    "\n",
    "root = tk.Tk()\n",
    "root.title(\"Line Spacer App\")\n",
    "\n",
    "tk.Label(root, text=\"Enter your text:\").pack()\n",
    "input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=10)\n",
    "input_box.pack(padx=10, pady=5)\n",
    "\n",
    "tk.Button(root, text=\"Add Line Spaces\", command=add_line_spaces).pack(pady=5)\n",
    "\n",
    "tk.Label(root, text=\"Formatted text:\").pack()\n",
    "output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=10)\n",
    "output_box.pack(padx=10, pady=5)\n",
    "\n",
    "tk.Button(root, text=\"Save to File\", command=save_to_file).pack(pady=10)\n",
    "\n",
    "root.mainloop()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.18"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
