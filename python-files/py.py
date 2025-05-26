import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Контрольные точки (отсортированы по длине суффикса в обратном порядке)
BREAKPOINTS = [
    ("_tablet_extra", 1024),
    ("_mobile_extra", 480),
    ("_laptop", 1366),
    ("_tablet", 640),
    ("_mobile", 370),
    ("", 1920),
]

# Базовые размеры шрифта для em
EM_SIZES = {
    "": 16,
    "_laptop": 16,
    "_tablet_extra": 14,
    "_tablet": 14,
    "_mobile_extra": 12,
    "_mobile": 12,
}

def convert_value(value, unit, suffix):
    """Конвертирует значение в vw с учетом единиц измерения и контрольной точки"""
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    
    # Находим параметры для текущего суффикса
    bp = next((bp for s, bp in BREAKPOINTS if suffix.endswith(s)), None)
    em_size = EM_SIZES.get(suffix.split('_')[-1], 16)  # Берем последнюю часть суффикса
    
    if unit == "px":
        return round((value / bp) * 100, 2) if bp else value
    elif unit == "em":
        return round((value * em_size / bp) * 100, 2) if bp else value
    return value

def process_data(data, current_suffix=""):
    """Рекурсивная обработка данных"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Определяем суффикс для текущего ключа
            suffix = next((s for s, _ in BREAKPOINTS if key.endswith(s)), "")
            
            if isinstance(value, dict) and "unit" in value:
                unit = value["unit"]
                if unit in ("px", "em"):
                    converted = {"unit": "vw"}
                    for k, v in value.items():
                        if k == "unit": 
                            continue
                        if isinstance(v, (int, float, str)) and k not in ("isLinked", "sizes"):
                            converted[k] = convert_value(v, unit, suffix or current_suffix)
                        else:
                            converted[k] = process_data(v, suffix or current_suffix)
                    result[key] = converted
                    continue
                    
            result[key] = process_data(value, suffix or current_suffix)
        return result
    
    if isinstance(data, list):
        return [process_data(item, current_suffix) for item in data]
    
    return data

def convert_file(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        converted = process_data(data)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(converted, f, indent=2, ensure_ascii=False)
            
        messagebox.showinfo("Успех", f"Файл сохранен: {output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конвертер единиц Elementor")
        self.geometry("600x250")
        
        self.input_entry = tk.Entry(width=60)
        self.output_entry = tk.Entry(width=60)
        
        tk.Label(text="Входной файл:").pack(pady=5)
        self.input_entry.pack(padx=10)
        tk.Button(text="Выбрать файл", command=self.select_input).pack(pady=5)
        
        tk.Label(text="Выходной файл:").pack(pady=5)
        self.output_entry.pack(padx=10)
        tk.Button(text="Выбрать файл", command=self.select_output).pack(pady=5)
        
        tk.Button(text="Конвертировать", command=self.run_conversion).pack(pady=20)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("JSON/Text", "*.json;*.txt")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, path)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, path)

    def run_conversion(self):
        convert_file(self.input_entry.get(), self.output_entry.get())

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()