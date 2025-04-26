
import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import csv

def scrape_temu(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "Failed to fetch the page."
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text.strip() if soup.find("title") else "No title"
        images = list({
            img.get("src") for img in soup.find_all("img")
            if img.get("src") and "media" in img.get("src")
        })
        images = images[:5]

        price_text = ""
        for text in soup.stripped_strings:
            if "$" in text and len(text) < 15:
                price_text = text
                break

        return {
            "title": title,
            "price": price_text,
            "images": images
        }, None
    except Exception as e:
        return None, str(e)

def run_scraper():
    url = url_entry.get()
    result, error = scrape_temu(url)
    if error:
        messagebox.showerror("Error", error)
        return

    title_var.set(result["title"])
    price_var.set(result["price"])
    image_text.delete(1.0, tk.END)
    for img in result["images"]:
        image_text.insert(tk.END, img + "\n")

    app.current_result = result

def export_to_csv():
    if not hasattr(app, "current_result"):
        messagebox.showerror("Error", "No product data to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    with open(file_path, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Price", "Images"])
        writer.writerow([
            app.current_result["title"],
            app.current_result["price"],
            ", ".join(app.current_result["images"])
        ])

    messagebox.showinfo("Saved", "Product data saved successfully!")

app = tk.Tk()
app.title("Temu Product Scraper")
app.geometry("600x400")

tk.Label(app, text="Temu Product URL:").pack(pady=5)
url_entry = tk.Entry(app, width=80)
url_entry.pack()

tk.Button(app, text="Scrape Product", command=run_scraper).pack(pady=10)

tk.Label(app, text="Title:").pack()
title_var = tk.StringVar()
tk.Entry(app, textvariable=title_var, width=80).pack()

tk.Label(app, text="Price:").pack()
price_var = tk.StringVar()
tk.Entry(app, textvariable=price_var, width=80).pack()

tk.Label(app, text="Images:").pack()
image_text = tk.Text(app, height=5, width=80)
image_text.pack()

tk.Button(app, text="Export to CSV", command=export_to_csv).pack(pady=10)

app.mainloop()
