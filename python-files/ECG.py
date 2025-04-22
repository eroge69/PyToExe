import os
import re
from tkinter import Tk, filedialog, messagebox
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF файла"""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def find_value_after(text, phrase):
    """Ищет текст после указанной фразы"""
    pattern = re.escape(phrase) + r'\s*[:–-]?\s*([^\n]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "НЕ НАЙДЕНО"


def process_rhythm_line(text):
    """Обрабатывает строку с типами ритмов"""
    rhythm_text = find_value_after(text, "За время обследования наблюдались следующие типы ритмов:")
    if rhythm_text != "НЕ НАЙДЕНО":
        # Удаляем точку в конце, если есть, и добавляем нужное окончание
        rhythm_text = rhythm_text.rstrip('.') + " уд./мин. в течение всего наблюдения."
    return rhythm_text


def process_hr_line(text, phrase):
    """Обрабатывает строку с ЧСС и форматирует согласно требованиям"""
    pattern = re.escape(phrase) + r'.*?(\d+).*?(\d+).*?(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        first, second, third = match.groups()
        if "днем" in phrase.lower():
            return f"Во время бодрствования средняя ЧСС: {first} (от {second} до {third})"
        else:
            return f"Во время сна средняя ЧСС: {first} (от {second} до {third})"
    return "НЕ НАЙДЕНО"


def process_pdf_file(pdf_path):
    """Обрабатывает PDF файл и извлекает нужные данные"""
    text = extract_text_from_pdf(pdf_path)

    # Извлекаем основные данные
    duration = find_value_after(text, "Длительность наблюдения")
    suitable = find_value_after(text, "Пригодно для анализа")
    rhythm_types = process_rhythm_line(text)

    # Обрабатываем данные ЧСС
    hr_day = process_hr_line(text, "ЧСС днем (бодрствование)")
    hr_night = process_hr_line(text, "ЧСС ночью (во время сна)")

    # Формируем заключение
    conclusion = f"""Длительность наблюдения – {duration}
Пригодно для анализа – {suitable}

{rhythm_types}

{hr_day}
{hr_night}"""

    return conclusion


def save_as_docx(content, original_path):
    """Сохраняет текст в DOCX файл"""
    folder = os.path.dirname(original_path)
    filename = os.path.basename(original_path).replace('.pdf', '') + '_Заключение.docx'
    save_path = os.path.join(folder, filename)

    doc = Document()
    doc.add_paragraph(content)
    doc.save(save_path)
    return save_path


def main():
    """Основная функция программы"""
    root = Tk()
    root.withdraw()

    # Выбираем PDF файл
    pdf_path = filedialog.askopenfilename(
        title="Выберите PDF файл",
        filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
    )

    if not pdf_path:
        messagebox.showwarning("Отменено", "Файл не выбран")
        return

    try:
        # Обрабатываем файл
        conclusion = process_pdf_file(pdf_path)
        docx_path = save_as_docx(conclusion, pdf_path)

        # Показываем сообщение об успехе
        messagebox.showinfo(
            "Успешно",
            f"Файл успешно обработан и сохранен как:\n{docx_path}"
        )
    except Exception as e:
        # Показываем сообщение об ошибке
        messagebox.showerror(
            "Ошибка",
            f"Произошла ошибка при обработке файла:\n{str(e)}"
        )


if __name__ == "__main__":
    main()