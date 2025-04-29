import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import messagebox

def add_contact():
    first_name = entry_first.get()
    last_name = entry_last.get()
    phone_number = entry_phone.get()
    department = entry_department.get()

    if not first_name or not last_name or not phone_number or not department:
        messagebox.showerror("Помилка", "Заповніть усі поля!")
        return

    try:
        tree = ET.parse("phonebook.xml")
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        root = ET.Element("AddressBook")
        tree = ET.ElementTree(root)
    
    new_id = max([int(contact.find("id").text) for contact in root.findall("Contact")] + [199]) + 1
    
    contact = ET.SubElement(root, "Contact")
    ET.SubElement(contact, "id").text = str(new_id)
    ET.SubElement(contact, "FirstName").text = first_name
    ET.SubElement(contact, "LastName").text = last_name
    ET.SubElement(contact, "Frequent").text = "0"
    
    phone = ET.SubElement(contact, "Phone", type="Work")
    ET.SubElement(phone, "phonenumber").text = phone_number
    ET.SubElement(phone, "accountindex").text = "0"
    
    ET.SubElement(contact, "Primary").text = "0"
    ET.SubElement(contact, "Department").text = department
    
    tree.write("phonebook.xml", encoding="UTF-8", xml_declaration=True)
    messagebox.showinfo("Готово", "Контакт додано!")
    entry_first.delete(0, tk.END)
    entry_last.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_department.delete(0, tk.END)

# GUI
root = tk.Tk()
root.title("Редактор телефонної книги Grandstream")
root.geometry("400x300")

tk.Label(root, text="Ім'я:").pack()
entry_first = tk.Entry(root)
entry_first.pack()

tk.Label(root, text="Прізвище:").pack()
entry_last = tk.Entry(root)
entry_last.pack()

tk.Label(root, text="Номер телефону:").pack()
entry_phone = tk.Entry(root)
entry_phone.pack()

tk.Label(root, text="Відділ:").pack()
entry_department = tk.Entry(root)
entry_department.pack()

tk.Button(root, text="Додати контакт", command=add_contact).pack()

root.mainloop()
