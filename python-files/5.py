import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

def validate_input():
    """Проверка всех входных данных перед генерацией XML"""
    errors = []
    
    # Проверка места деятельности (МД)
    subject_id = subject_id_entry.get().strip()
    if len(subject_id) != 14 or not subject_id.isdigit():
        errors.append("Место деятельности (МД) должно содержать 14 цифр")
    
    # Проверка стоимости и НДС
    try:
        float(cost_entry.get().strip())
    except ValueError:
        errors.append("Цена должна быть числом. Недопустимо использование знака запятой, только - точка.")
    
    try:
        float(vat_entry.get().strip())
    except ValueError:
        errors.append("НДС должен быть числом. Недопустимо использование знака запятой, только - точка.")
    
    # Проверка даты документа
    doc_date = doc_date_entry.get().strip()
    try:
        datetime.strptime(doc_date, "%d.%m.%Y")
    except ValueError:
        errors.append("Неверный формат даты! Используйте ДД.ММ.ГГГГ.")
    
    # Проверка списка SGTIN
    sgtin_list = sgtin_text.get("1.0", tk.END).strip().split("\n")
    if not any(sgtin.strip() for sgtin in sgtin_list):
        errors.append("Добавьте хотя бы один SGTIN.")
    
    # Проверка номера документа
    if not doc_number_entry.get().strip():
        errors.append("Введите номер документа")
    
    return errors

def generate_xml():
    """Генерация XML файла"""
    # Валидация входных данных
    errors = validate_input()
    if errors:
        messagebox.showerror("Ошибки ввода", "\n".join(errors))
        return

    # Получаем данные из полей ввода
    sgtin_list = [sgtin.strip() for sgtin in sgtin_text.get("1.0", tk.END).strip().split("\n") if sgtin.strip()]
    cost = cost_entry.get().strip()
    vat_value = vat_entry.get().strip()
    subject_id = subject_id_entry.get().strip()
    doc_number = doc_number_entry.get().strip()
    doc_date = doc_date_entry.get().strip()

    # Создаем XML-структуру
    root = ET.Element("documents", version="1.38", xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance")
    retail_sale = ET.SubElement(root, "retail_sale", action_id="511")
    
    ET.SubElement(retail_sale, "subject_id").text = subject_id
    ET.SubElement(retail_sale, "operation_date").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+03:00")
    
    sales = ET.SubElement(retail_sale, "sales")
    union = ET.SubElement(sales, "union")

    # Добавляем все SGTIN
    for sgtin in sgtin_list:
        detail = ET.SubElement(union, "detail")
        ET.SubElement(detail, "sgtin").text = sgtin
        ET.SubElement(detail, "cost").text = cost
        ET.SubElement(detail, "vat_value").text = vat_value

    # Добавляем данные о документе
    sale_docs = ET.SubElement(union, "sale_docs")
    ET.SubElement(sale_docs, "doc_type").text = "3"
    ET.SubElement(sale_docs, "doc_number").text = doc_number
    ET.SubElement(sale_docs, "doc_date").text = doc_date

    # Форматируем XML
    xml_str = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="UTF-8")

    # Сохраняем файл
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")],
        initialfile="511.xml"
    )
    if file_path:
        try:
            with open(file_path, "wb") as f:
                f.write(xml_pretty)
            messagebox.showinfo("Успешно", f"Файл успешно сохранён:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

# Создание графического интерфейса
app = tk.Tk()
app.title("Генератор XML для схемы 511 (тип 3 - договор)")
app.resizable(False, False)

# Настройка сетки
app.grid_columnconfigure(1, weight=1)

# Поле для места деятельности
tk.Label(app, text="Место деятельности (МД):*", anchor="w").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
subject_id_entry = tk.Entry(app, width=20)
subject_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
subject_id_entry.insert(0, "00000000002030")
tk.Label(app, text="(14 цифр)", fg="gray").grid(row=0, column=2, sticky="w", padx=5)

# Поле для списка SGTIN
tk.Label(app, text="Список SGTIN:*", anchor="w").grid(row=1, column=0, sticky="nw", padx=5, pady=2)
sgtin_text = tk.Text(app, height=15, width=50)
sgtin_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)
tk.Label(app, text="(каждый код с новой строки)", fg="gray").grid(row=3, column=0, columnspan=3, sticky="w", padx=5)

# Поля для стоимости и НДС
tk.Label(app, text="Цена:*", anchor="w").grid(row=4, column=0, sticky="w", padx=5, pady=2)
cost_entry = tk.Entry(app, width=20)
cost_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
cost_entry.insert(0, "7010.34")

tk.Label(app, text="НДС:*", anchor="w").grid(row=5, column=0, sticky="w", padx=5, pady=2)
vat_entry = tk.Entry(app, width=20)
vat_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)
vat_entry.insert(0, "637.30")

# Поля для документа
tk.Label(app, text="Номер документа:*", anchor="w").grid(row=6, column=0, sticky="w", padx=5, pady=2)
doc_number_entry = tk.Entry(app)
doc_number_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
doc_number_entry.insert(0, "0000001")

tk.Label(app, text="Дата документа:*", anchor="w").grid(row=7, column=0, sticky="w", padx=5, pady=2)
doc_date_entry = tk.Entry(app)
doc_date_entry.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
doc_date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
tk.Label(app, text="(формат ДД.ММ.ГГГГ)", fg="gray").grid(row=7, column=2, sticky="w", padx=5)

# Кнопка генерации
generate_btn = tk.Button(app, text="Сгенерировать XML", command=generate_xml)
generate_btn.grid(row=8, column=0, columnspan=3, pady=10, sticky="ew")

# Подпись обязательных полей
tk.Label(app, text="* - обязательные поля", fg="gray").grid(row=9, column=0, columnspan=3, sticky="w", padx=5)

app.mainloop()