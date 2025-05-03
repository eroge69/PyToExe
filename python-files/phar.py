import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from available_medications import available_medications

try:
    import pandas as pd  # Add this import for exporting to Excel
except ModuleNotFoundError:
    messagebox.showerror("خطأ", "المكتبة 'pandas' غير مثبتة. يرجى تثبيتها باستخدام الأمر: pip install pandas")
    exit()

# إنشاء قاعدة البيانات والجداول
conn = sqlite3.connect("patients.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    file_number INTEGER PRIMARY KEY,
    national_id TEXT UNIQUE NOT NULL CHECK(LENGTH(national_id) = 12),
    birth_year INTEGER CHECK(birth_year BETWEEN 1900 AND 9999),
    file_year INTEGER CHECK(file_year BETWEEN 1900 AND 9999),
    patient_name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_number INTEGER,
    medication_name TEXT NOT NULL,
    FOREIGN KEY (file_number) REFERENCES patients(file_number) ON DELETE CASCADE
)
''')

conn.commit()

# التحقق من صحة السنة
def is_valid_year(year):
    try:
        year = int(year)
        return 1900 <= year <= 9999
    except ValueError:
        return False

# دالة إضافة مريض جديد
def add_patient():
    file_number = file_entry.get().strip()
    name = name_entry.get().strip()
    national_id = national_id_entry.get().strip()
    birth_year = birth_year_entry.get().strip()
    file_year = file_year_entry.get().strip()

    if not all([file_number, name, national_id, birth_year, file_year]):
        messagebox.showerror("خطأ", "جميع الحقول مطلوبة.")
        return

    try:
        file_number = int(file_number)
        birth_year = int(birth_year)
        file_year = int(file_year)

        if not is_valid_year(birth_year) or not is_valid_year(file_year):
            messagebox.showerror("خطأ", "سنة الميلاد أو سنة فتح الملف غير صالحة.")
            return

        if not national_id.isdigit() or len(national_id) != 12:
            messagebox.showerror("خطأ", "الرقم الوطني يجب أن يكون 12 رقمًا.")
            return

        cursor.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?)",
                       (file_number, national_id, birth_year, file_year, name))
        conn.commit()
        messagebox.showinfo("نجاح", "تمت إضافة المريض بنجاح.")
        clear_fields()
        refresh_table()
        open_medication_window(file_number)

    except sqlite3.IntegrityError:
        messagebox.showerror("خطأ", "رقم الملف أو الرقم الوطني موجود بالفعل.")
    except ValueError:
        messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة في الحقول.")

# دالة فتح نافذة إضافة الأدوية
def open_medication_window(file_number):
    medication_window = tk.Toplevel(root)
    medication_window.title(f"إضافة أدوية للمريض رقم {file_number}")
    medication_window.geometry("400x300")

    # تكبير الخط في النافذة
    font_style = ("Arial", 14)

    tk.Label(medication_window, text="رقم الملف:", font=font_style).pack(pady=5)
    file_number_label = tk.Label(medication_window, text=file_number, font=font_style)
    file_number_label.pack(pady=5)

    tk.Label(medication_window, text="اختر الدواء:", font=font_style).pack(pady=5)
    medication_combobox = ttk.Combobox(medication_window, values=available_medications, state="readonly", font=font_style)
    medication_combobox.pack(pady=5)

    def add_medication():
        medication_name = medication_combobox.get().strip()

        if not medication_name:
            messagebox.showerror("خطأ", "يرجى اختيار دواء من القائمة.")
            return

        # التحقق من وجود الدواء بالفعل لنفس المريض
        cursor.execute("SELECT * FROM medications WHERE file_number = ? AND medication_name = ?", (file_number, medication_name))
        if cursor.fetchone():
            messagebox.showwarning("تحذير", "الدواء موجود بالفعل للمريض.")
            return

        try:
            cursor.execute("INSERT INTO medications (file_number, medication_name) VALUES (?, ?)",
                           (file_number, medication_name))
            conn.commit()
            # مسح حقل اختيار الدواء فقط دون تغيير حجم النافذة
            medication_combobox.set("")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة الدواء: {str(e)}")

    add_button = tk.Button(medication_window, text="إضافة دواء", font=font_style, command=add_medication, bg="#4CAF50", fg="white")
    add_button.pack(pady=10)

    close_button = tk.Button(medication_window, text="إغلاق", font=font_style, command=medication_window.destroy, bg="#f44336", fg="white")
    close_button.pack(pady=10)

# دالة مسح الحقول
def clear_fields():
    file_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    national_id_entry.delete(0, tk.END)
    birth_year_entry.delete(0, tk.END)
    file_year_entry.delete(0, tk.END)

# دالة تحديث جدول المرضى
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT file_number, patient_name, national_id, birth_year, file_year FROM patients")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# دالة البحث عن المرضى
def search_patients():
    search_term = search_entry.get().strip()

    if not search_term:
        messagebox.showerror("خطأ", "يرجى إدخال مصطلح للبحث.")
        return

    # استعلام قاعدة البيانات
    cursor.execute('''
        SELECT file_number, patient_name, national_id, birth_year, file_year
        FROM patients
        WHERE file_number LIKE ? OR patient_name LIKE ? OR national_id LIKE ?
    ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))

    results = cursor.fetchall()

    # تحديث الجدول
    for row in tree.get_children():
        tree.delete(row)

    for row in results:
        tree.insert("", "end", values=row)

# دالة فتح نافذة تعديل الأدوية والرقم الوطني
def open_edit_medications_window(file_number):
    edit_medications_window = tk.Toplevel(root)
    edit_medications_window.title(f"تعديل أدوية والرقم الوطني للمريض رقم {file_number}")
    edit_medications_window.geometry("500x500")

    # تكبير الخط في النافذة
    font_style = ("Arial", 14)

    # استعلام قاعدة البيانات للحصول على بيانات المريض
    cursor.execute("SELECT national_id FROM patients WHERE file_number = ?", (file_number,))
    patient_data = cursor.fetchone()
    national_id = patient_data[0] if patient_data else ""

    # إضافة حقل لتعديل الرقم الوطني
    tk.Label(edit_medications_window, text="الرقم الوطني:", font=font_style).pack(pady=10)
    national_id_entry = tk.Entry(edit_medications_window, font=font_style, width=20)
    national_id_entry.insert(0, national_id)
    national_id_entry.pack(pady=10)

    # دالة لتحديث الرقم الوطني
    def update_national_id():
        new_national_id = national_id_entry.get().strip()

        if not new_national_id.isdigit() or len(new_national_id) != 12:
            messagebox.showerror("خطأ", "الرقم الوطني يجب أن يكون 12 رقمًا.")
            return

        try:
            cursor.execute("UPDATE patients SET national_id = ? WHERE file_number = ?", (new_national_id, file_number))
            conn.commit()
            messagebox.showinfo("نجاح", "تم تحديث الرقم الوطني بنجاح.")
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "الرقم الوطني موجود بالفعل.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التحديث: {str(e)}")

    # زر تحديث الرقم الوطني
    update_id_button = tk.Button(edit_medications_window, text="تحديث الرقم الوطني", font=font_style, command=update_national_id, bg="#4CAF50", fg="white")
    update_id_button.pack(pady=10)

    # استعلام قاعدة البيانات للحصول على الأدوية
    cursor.execute("SELECT medication_name FROM medications WHERE file_number = ?", (file_number,))
    medications = cursor.fetchall()

    # عرض الأدوية في قائمة
    tk.Label(edit_medications_window, text="الأدوية:", font=font_style).pack(pady=10)
    medications_frame = tk.Frame(edit_medications_window, bg="#ffffff", bd=2, relief="groove")
    medications_frame.pack(pady=10, padx=10, fill="both", expand=True)

    for med in medications:
        medication_frame = tk.Frame(medications_frame, bg="#ffffff", bd=1, relief="solid")
        medication_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(medication_frame, text=med[0], font=font_style, bg="#ffffff").pack(side="left", padx=10)

        # زر حذف الدواء
        def delete_medication(med_name):
            confirm = messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف الدواء {med_name}؟")

            if confirm:
                cursor.execute("DELETE FROM medications WHERE file_number = ? AND medication_name = ?", (file_number, med_name))
                conn.commit()
                messagebox.showinfo("نجاح", f"تم حذف الدواء {med_name} بنجاح.")
                edit_medications_window.destroy()
                open_edit_medications_window(file_number)  # إعادة تحميل النافذة بعد الحذف

        delete_button = tk.Button(medication_frame, text="حذف", font=font_style, command=lambda m=med[0]: delete_medication(m), bg="#f44336", fg="white")
        delete_button.pack(side="right", padx=10)

    # إضافة دواء جديد
    tk.Label(edit_medications_window, text="إضافة دواء جديد:", font=font_style).pack(pady=10)
    medication_combobox = ttk.Combobox(edit_medications_window, values=available_medications, state="readonly", font=font_style)
    medication_combobox.pack(pady=10)

    def add_medication():
        medication_name = medication_combobox.get().strip()

        if not medication_name:
            messagebox.showerror("خطأ", "يرجى اختيار دواء من القائمة.")
            return

        # التحقق من وجود الدواء بالفعل لنفس المريض
        cursor.execute("SELECT * FROM medications WHERE file_number = ? AND medication_name = ?", (file_number, medication_name))
        if cursor.fetchone():
            messagebox.showwarning("تحذير", "الدواء موجود بالفعل للمريض.")
            return

        try:
            cursor.execute("INSERT INTO medications (file_number, medication_name) VALUES (?, ?)", (file_number, medication_name))
            conn.commit()
            messagebox.showinfo("نجاح", "تمت إضافة الدواء بنجاح.")
            edit_medications_window.destroy()
            open_edit_medications_window(file_number)  # إعادة تحميل النافذة بعد الإضافة
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة الدواء: {str(e)}")

    add_button = tk.Button(edit_medications_window, text="إضافة دواء", font=font_style, command=add_medication, bg="#4CAF50", fg="white")
    add_button.pack(pady=10)

    # زر حذف المريض بالكامل
    def delete_patient():
        confirm = messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف المريض بالكامل؟")

        if confirm:
            cursor.execute("DELETE FROM patients WHERE file_number = ?", (file_number,))
            conn.commit()
            messagebox.showinfo("نجاح", "تم حذف المريض بالكامل بنجاح.")
            edit_medications_window.destroy()
            refresh_table()

    delete_patient_button = tk.Button(edit_medications_window, text="حذف المريض بالكامل", font=font_style, command=delete_patient, bg="#f44336", fg="white")
    delete_patient_button.pack(pady=10)

# دالة فتح نافذة حذف أو تعديل المريض
def open_delete_or_edit_window():
    delete_edit_window = tk.Toplevel(root)
    delete_edit_window.title("حذف أو تعديل مريض")
    delete_edit_window.geometry("500x400")

    # تكبير الخط في النافذة
    font_style = ("Arial", 14)

    tk.Label(delete_edit_window, text="رقم الملف:", font=font_style).pack(pady=10)
    file_number_entry = tk.Entry(delete_edit_window, font=font_style, width=20)
    file_number_entry.pack(pady=10)

    def load_patient_data():
        file_number = file_number_entry.get().strip()

        if not file_number:
            messagebox.showerror("خطأ", "يرجى إدخال رقم الملف.")
            return

        try:
            file_number = int(file_number)
        except ValueError:
            messagebox.showerror("خطأ", "رقم الملف يجب أن يكون رقمًا صحيحًا.")
            return

        # استعلام قاعدة البيانات للحصول على بيانات المريض
        cursor.execute("SELECT * FROM patients WHERE file_number = ?", (file_number,))
        patient_data = cursor.fetchone()

        if not patient_data:
            messagebox.showerror("خطأ", "لم يتم العثور على المريض.")
            return

        # فتح نافذة تعديل الأدوية
        open_edit_medications_window(file_number)
        delete_edit_window.destroy()

    # زر تحميل بيانات المريض
    load_button = tk.Button(delete_edit_window, text="تحميل البيانات", font=font_style, command=load_patient_data, bg="#008CBA", fg="white")
    load_button.pack(pady=10)

# دالة للانتقال إلى الحقل التالي عند الضغط على Enter
def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"

# دالة لعرض الأدوية الخاصة بالمريض
def show_medications(event):
    selected_item = tree.selection()[0]  # الحصول على العنصر المحدد
    file_number = tree.item(selected_item, "values")[0]  # الحصول على رقم الملف

    # استعلام قاعدة البيانات للحصول على الأدوية
    cursor.execute("SELECT medication_name FROM medications WHERE file_number = ?", (file_number,))
    medications = cursor.fetchall()

    # إنشاء نافذة جديدة لعرض الأدوية
    medication_list_window = tk.Toplevel(root)
    medication_list_window.title(f"الأدوية الخاصة بالمريض رقم {file_number}")
    medication_list_window.geometry("400x300")

    # تكبير الخط في النافذة
    font_style = ("Arial", 14)

    tk.Label(medication_list_window, text="الأدوية:", font=font_style).pack(pady=10)

    # عرض الأدوية في قائمة
    for med in medications:
        tk.Label(medication_list_window, text=med[0], font=font_style).pack()

# دالة لفتح نافذة الاستعلام عن المرضى بالدواء
def open_medication_query_window():
    medication_query_window = tk.Toplevel(root)
    medication_query_window.title("الاستعلام عن المرضى بالدواء")
    medication_query_window.geometry("500x400")

    # تكبير الخط في النافذة
    font_style = ("Arial", 14)

    tk.Label(medication_query_window, text="اختر الدواء:", font=font_style).pack(pady=10)
    medication_combobox = ttk.Combobox(medication_query_window, values=available_medications, state="readonly", font=font_style)
    medication_combobox.pack(pady=10)

    # جدول لعرض النتائج
    results_tree = ttk.Treeview(medication_query_window, columns=("رقم الملف", "اسم المريض", "الرقم الوطني", "سنة الميلاد", "سنة فتح الملف"), show="headings")

    results_tree.heading("رقم الملف", text="رقم الملف")
    results_tree.heading("اسم المريض", text="اسم المريض")
    results_tree.heading("الرقم الوطني", text="الرقم الوطني")
    results_tree.heading("سنة الميلاد", text="سنة الميلاد")
    results_tree.heading("سنة فتح الملف", text="سنة فتح الملف")

    for col in results_tree["columns"]:
        results_tree.column(col, width=100)

    results_tree.pack(pady=10, fill="both", expand=True)

    def search_by_medication():
        medication_name = medication_combobox.get().strip()

        if not medication_name:
            messagebox.showerror("خطأ", "يرجى اختيار دواء من القائمة.")
            return

        # استعلام قاعدة البيانات
        cursor.execute('''
            SELECT p.file_number, p.patient_name, p.national_id, p.birth_year, p.file_year
            FROM patients p
            INNER JOIN medications m ON p.file_number = m.file_number
            WHERE m.medication_name = ?
        ''', (medication_name,))

        results = cursor.fetchall()

        # تحديث الجدول
        for row in results_tree.get_children():
            results_tree.delete(row)

        for row in results:
            results_tree.insert("", "end", values=row)

    search_button = tk.Button(medication_query_window, text="بحث", font=font_style, command=search_by_medication, bg="#008CBA", fg="white")
    search_button.pack(pady=10)

    def export_to_excel():
        medication_name = medication_combobox.get().strip()

        if not medication_name:
            messagebox.showerror("خطأ", "يرجى اختيار دواء من القائمة.")
            return

        # استعلام قاعدة البيانات
        cursor.execute('''
            SELECT p.file_number, p.patient_name, p.national_id, p.birth_year, p.file_year
            FROM patients p
            INNER JOIN medications m ON p.file_number = m.file_number
            WHERE m.medication_name = ?
        ''', (medication_name,))

        results = cursor.fetchall()

        if not results:
            messagebox.showinfo("معلومات", "لا توجد بيانات لتصديرها.")
            return

        # تحويل النتائج إلى DataFrame
        df = pd.DataFrame(results, columns=["رقم الملف", "اسم المريض", "الرقم الوطني", "سنة الميلاد", "سنة فتح الملف"])

        # تصدير إلى ملف Excel
        try:
            file_path = f"{medication_name}_patients.xlsx"
            df.to_excel(file_path, index=False)
            messagebox.showinfo("نجاح", f"تم تصدير البيانات إلى {file_path} بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {str(e)}")

    export_button = tk.Button(medication_query_window, text="تصدير إلى Excel", font=font_style, command=export_to_excel, bg="#4CAF50", fg="white")
    export_button.pack(pady=10)

# دالة عرض معلومات حول المبرمج
def show_about():
    messagebox.showinfo("حول", "تم تطوير هذا البرنامج بواسطة الصيدلي عبدالجليل الشلوي.")

# تعديل واجهة المستخدم لإضافة زر "حول"
def create_gui():
    global file_entry, name_entry, national_id_entry, birth_year_entry, file_year_entry, tree, root, search_entry

    root = tk.Tk()
    root.title("صيدلية الأمراض النفسية والعصبية")  # Updated title
    root.geometry("1000x700")

    # Define font_style to avoid NameError
    font_style = ("Arial", 14)

    # إضافة قائمة في شريط العنوان
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # إضافة قائمة "حول"
    about_menu = tk.Menu(menu_bar, tearoff=0)
    about_menu.add_command(label="حول", command=show_about)
    menu_bar.add_cascade(label="حول", menu=about_menu)

    # تعديل عنوان النافذة ليكون في المنتصف
    title_label = tk.Label(root, text="ادارة الخدمات الصحية درنه", font=("Arial", 16, "bold"), bg="#ffffff")
    title_label.pack(pady=10)

    # إطار البحث
    search_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    search_frame.pack(pady=10, padx=20, fill="x")

    tk.Label(search_frame, text="بحث (بالاسم، رقم الملف، أو الرقم الوطني):", font=font_style, bg="#ffffff").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    search_entry = tk.Entry(search_frame, font=font_style, width=30)
    search_entry.grid(row=0, column=1, padx=10, pady=5)
    search_entry.bind("<Return>", lambda event: search_patients())  # تفعيل Enter للبحث

    search_button = tk.Button(search_frame, text="بحث", font=font_style, command=search_patients, bg="#008CBA", fg="white")
    search_button.grid(row=0, column=2, padx=10, pady=5)

    # زر حذف أو تعديل
    delete_edit_button = tk.Button(search_frame, text="حذف أو تعديل", font=font_style, command=open_delete_or_edit_window, bg="#FF9800", fg="white")
    delete_edit_button.grid(row=0, column=3, padx=10, pady=5)

    # زر الاستعلام عن المرضى بالدواء
    medication_query_button = tk.Button(search_frame, text="الاستعلام عن المرضى بالدواء", font=font_style, command=open_medication_query_window, bg="#9C27B0", fg="white")
    medication_query_button.grid(row=0, column=4, padx=10, pady=5)

    # إطار إدخال بيانات المريض
    input_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    input_frame.pack(pady=20, padx=20, fill="x")

    tk.Label(input_frame, text="رقم الملف:", font=font_style, bg="#ffffff").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    file_entry = tk.Entry(input_frame, font=font_style, width=20)
    file_entry.grid(row=0, column=1, padx=10, pady=5)
    file_entry.bind("<Return>", focus_next_widget)  # تفعيل Enter للانتقال

    tk.Label(input_frame, text="اسم المريض:", font=font_style, bg="#ffffff").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    name_entry = tk.Entry(input_frame, font=font_style, width=20)
    name_entry.grid(row=1, column=1, padx=10, pady=5)
    name_entry.bind("<Return>", focus_next_widget)

    tk.Label(input_frame, text="الرقم الوطني:", font=font_style, bg="#ffffff").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    national_id_entry = tk.Entry(input_frame, font=font_style, width=20)
    national_id_entry.grid(row=2, column=1, padx=10, pady=5)
    national_id_entry.bind("<Return>", focus_next_widget)

    tk.Label(input_frame, text="سنة الميلاد:", font=font_style, bg="#ffffff").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    birth_year_entry = tk.Entry(input_frame, font=font_style, width=20)
    birth_year_entry.grid(row=3, column=1, padx=10, pady=5)
    birth_year_entry.bind("<Return>", focus_next_widget)

    tk.Label(input_frame, text="سنة فتح الملف:", font=font_style, bg="#ffffff").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    file_year_entry = tk.Entry(input_frame, font=font_style, width=20)
    file_year_entry.grid(row=4, column=1, padx=10, pady=5)
    file_year_entry.bind("<Return>", lambda event: add_patient())  # تفعيل Enter للإضافة

    add_button = tk.Button(input_frame, text="إضافة مريض", font=font_style, command=add_patient, bg="#4CAF50", fg="white")
    add_button.grid(row=5, column=0, columnspan=2, pady=10)

    # إطار عرض جدول المرضى
    table_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    table_frame.pack(pady=20, padx=20, fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=("رقم الملف", "اسم المريض", "الرقم الوطني", "سنة الميلاد", "سنة فتح الملف"), show="headings", height=10)

    tree.heading("رقم الملف", text="رقم الملف")
    tree.heading("اسم المريض", text="اسم المريض")
    tree.heading("الرقم الوطني", text="الرقم الوطني")
    tree.heading("سنة الميلاد", text="سنة الميلاد")
    tree.heading("سنة فتح الملف", text="سنة فتح الملف")

    for col in tree["columns"]:
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True)

    # ربط حدث النقر المزدوج لعرض الأدوية
    tree.bind("<Double-Button-1>", show_medications)

    # تمرير أفقي إذا كان الجدول كبيرا
    x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    x_scrollbar.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=x_scrollbar.set)

    # تهيئة الجدول بالبيانات الموجودة
    refresh_table()

    root.mainloop()

# تشغيل الواجهة الرسومية
if __name__ == "__main__":
    create_gui()
