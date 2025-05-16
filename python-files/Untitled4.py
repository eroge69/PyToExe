import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
import os

class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامه فروشگاه")

        self.kalaha = []  # لیست کالاها
        self.factor_items = []  # لیست اقلام فاکتور
        self.logo_path = None  # مسیر لوگو

        # بخش تعریف کالا
        frame_kala = tk.LabelFrame(root, text="تعریف کالا")
        frame_kala.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_kala, text="نام کالا:").grid(row=0, column=0)
        self.entry_name = tk.Entry(frame_kala)
        self.entry_name.grid(row=0, column=1)

        tk.Label(frame_kala, text="قیمت کالا:").grid(row=1, column=0)
        self.entry_price = tk.Entry(frame_kala)
        self.entry_price.grid(row=1, column=1)

        tk.Button(frame_kala, text="افزودن کالا", command=self.add_kala).grid(row=2, column=0, columnspan=2, pady=5)

        # بخش اطلاعات خریدار
        frame_buyer = tk.LabelFrame(root, text="اطلاعات خریدار")
        frame_buyer.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_buyer, text="نام خریدار:").grid(row=0, column=0)
        self.entry_buyer = tk.Entry(frame_buyer)
        self.entry_buyer.grid(row=0, column=1)

        tk.Label(frame_buyer, text="تلفن خریدار:").grid(row=1, column=0)
        self.entry_phone = tk.Entry(frame_buyer)
        self.entry_phone.grid(row=1, column=1)

        # بخش انتخاب کالا برای فاکتور
        frame_factor = tk.LabelFrame(root, text="فاکتور فروش")
        frame_factor.pack(padx=10, pady=5, fill="both", expand=True)

        tk.Label(frame_factor, text="کالا:").grid(row=0, column=0)
        self.kala_var = tk.StringVar()
        self.combo_kala = tk.OptionMenu(frame_factor, self.kala_var, ())
        self.combo_kala.grid(row=0, column=1)

        tk.Label(frame_factor, text="تعداد:").grid(row=1, column=0)
        self.entry_count = tk.Entry(frame_factor)
        self.entry_count.grid(row=1, column=1)

        tk.Button(frame_factor, text="افزودن به فاکتور", command=self.add_to_factor).grid(row=2, column=0, columnspan=2, pady=5)

        # لیست اقلام فاکتور
        self.list_factor = tk.Listbox(frame_factor, width=50)
        self.list_factor.grid(row=3, column=0, columnspan=2, pady=5)

        # دکمه نمایش فاکتور
        tk.Button(frame_factor, text="نمایش فاکتور", command=self.show_factor).grid(row=4, column=0, columnspan=2, pady=5)

        # دکمه ذخیره PDF
        tk.Button(frame_factor, text="ذخیره فاکتور به PDF", command=self.save_pdf).grid(row=5, column=0, columnspan=2, pady=5)

        # دکمه انتخاب لوگو
        btn_select_logo = tk.Button(frame_factor, text="انتخاب لوگو", command=self.select_logo)
        btn_select_logo.grid(row=6, column=0, columnspan=2, pady=5)

    def add_kala(self):
        name = self.entry_name.get().strip()
        try:
            price = float(self.entry_price.get())
        except ValueError:
            messagebox.showerror("خطا", "قیمت نامعتبر است!")
            return
        if not name:
            messagebox.showerror("خطا", "نام کالا نمی‌تواند خالی باشد!")
            return

        self.kalaha.append({"نام": name, "قیمت": price})
        self.update_kala_options()
        messagebox.showinfo("موفقیت", f"کالای '{name}' افزوده شد.")
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)

    def update_kala_options(self):
        menu = self.combo_kala["menu"]
        menu.delete(0, "end")
        for kala in self.kalaha:
            menu.add_command(label=kala["نام"], command=lambda value=kala["نام"]: self.kala_var.set(value))
        if self.kalaha:
            self.kala_var.set(self.kalaha[0]["نام"])
        else:
            self.kala_var.set("")

    def add_to_factor(self):
        kala_name = self.kala_var.get()
        if not kala_name:
            messagebox.showerror("خطا", "لطفاً یک کالا انتخاب کنید.")
            return
        try:
            count = int(self.entry_count.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطا", "تعداد باید عدد صحیح بزرگتر از صفر باشد.")
            return

        # پیدا کردن قیمت کالا
        price = None
        for kala in self.kalaha:
            if kala["نام"] == kala_name:
                price = kala["قیمت"]
                break
        if price is None:
            messagebox.showerror("خطا", "کالا یافت نشد.")
            return

        total_price = price * count
        item = {"نام": kala_name, "تعداد": count, "قیمت واحد": price, "جمع": total_price}
        self.factor_items.append(item)
        self.list_factor.insert(tk.END, f"{kala_name} - تعداد: {count} - قیمت واحد: {price} - جمع: {total_price}")
        self.entry_count.delete(0, tk.END)

    def show_factor(self):
        if not self.factor_items:
            messagebox.showinfo("فاکتور", "هیچ کالایی به فاکتور اضافه نشده است.")
            return

        buyer = self.entry_buyer.get()
        phone = self.entry_phone.get()
        date_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        text = f"نام خریدار: {buyer}\nتلفن خریدار: {phone}\nتاریخ: {date_str}\n\n"
        text += "اقلام فاکتور:\n"
        total = 0
        for item in self.factor_items:
            text += f"- {item['نام']} | تعداد: {item['تعداد']} | قیمت واحد: {item['قیمت واحد']} | جمع: {item['جمع']}\n"
            total += item["جمع"]
        text += f"\nجمع کل: {total} تومان"

        messagebox.showinfo("فاکتور فروش", text)

    def save_pdf(self):
        if not self.factor_items:
            messagebox.showwarning("خطا", "فاکتوری برای ذخیره وجود ندارد.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("فایل PDF", "*.pdf")],
            title="ذخیره فاکتور به فایل PDF"
        )
        if not filepath:
            return

        try:
            self.create_pdf(filepath)
            messagebox.showinfo("موفقیت", f"فاکتور با موفقیت در {filepath} ذخیره شد.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل PDF:\n{e}")

    def create_pdf(self, filepath):
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        font_path = "XB Niloofar.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("Niloofar", font_path))
            c.setFont("Niloofar", 14)
        else:
            c.setFont("Helvetica", 14)

        margin = 50
        y = height - margin

        # اضافه کردن لوگو اگر انتخاب شده
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = ImageReader(self.logo_path)
                logo_width = 100  # عرض لوگو به پوینت
                logo_height = 50  # ارتفاع لوگو به پوینت
                c.drawImage(logo, margin, y - logo_height, width=logo_width, height=logo_height)
                y -= (logo_height + 10)
            except Exception as e:
                messagebox.showwarning("خطا در لوگو", f"لوگو بارگذاری نشد: {e}")

        c.drawRightString(width - margin, y, f"نام خریدار: {self.entry_buyer.get()}")
        y -= 25
        c.drawRightString(width - margin, y, f"تلفن خریدار: {self.entry_phone.get()}")
        y -= 25
        c.drawRightString(width - margin, y, f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
        y -= 40
        c.line(margin, y, width - margin, y)
        y -= 30

        c.drawRightString(width - margin, y, "نام کالا")
        c.drawRightString(width - 300, y, "تعداد")
        c.drawRightString(width - 400, y, "قیمت واحد (تومان)")
        c.drawRightString(width - 550, y, "جمع (تومان)")
        y -= 20
        c.line(margin, y, width - margin, y)
        y -= 20

        total = 0
        for item in self.factor_items:
            c.drawRightString(width - margin, y, item["نام"])
            c.drawRightString(width - 300, y, str(item["تعداد"]))
            c.drawRightString(width - 400, y, f"{item['قیمت واحد']:.2f}")
            c.drawRightString(width - 550, y, f"{item['جمع']:.2f}")
            y -= 25
            total += item["جمع"]

            if y < 100:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 14)

        c.line(margin, y, width - margin, y)
        y -= 30
        c.drawRightString(width - margin, y, f"جمع کل: {total:.2f} تومان")

        c.save()

    def select_logo(self):
        path = filedialog.askopenfilename(
            title="انتخاب فایل لوگو",
            filetypes=[("تصاویر", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            self.logo_path = path
            messagebox.showinfo("لوگو انتخاب شد", f"لوگو در مسیر زیر انتخاب شد:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    root.mainloop()
