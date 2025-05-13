
import os
import re
import tkinter as tk
from tkinter import filedialog

def extract_links(file_path):
    links = []
    ext = os.path.splitext(file_path)[1].lower()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

        if ext == '.xspf':
            links = re.findall(r'<location>(.*?)</location>', content)
        elif ext in ['.m3u', '.m3u8']:
            lines = content.splitlines()
            links = [line for line in lines if line and not line.startswith('#')]
        elif ext == '.html':
            links = re.findall(r'href=["\'](http[s]?://[^"\']+)["\']', content)
        else:
            print("Unsupported file type!")

    return links

def main():
    root = tk.Tk()
    root.withdraw()

    print("Select a playlist file (.xspf, .m3u, .m3u8, .html)")
    file_path = filedialog.askopenfilename(filetypes=[("Playlist files", "*.xspf *.m3u *.m3u8 *.html")])

    if not file_path:
        print("No file selected.")
        return

    links = extract_links(file_path)

    if not links:
        print("No links found in the file.")
        return

    # Generate output file path with same name, different extension
    base_name = os.path.splitext(file_path)[0]
    output_file = base_name + ".txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')

    print(f"{len(links)} links saved to {output_file}")

if __name__ == '__main__':
    main()
