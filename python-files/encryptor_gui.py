import numpy as np
from tkinter import Tk, filedialog, messagebox
import os

# Алфавит Z32 (русские буквы, ё = е)
alphabet = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
    'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э',
    'Ю', 'Я'
]


def clean_text(text):
    text = text.upper().replace('Ё', 'Е')
    return [char for char in text if char in alphabet]


def prepare_text(text):
    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("Текст не содержит символов из алфавита!")
    pad_len = (4 - len(cleaned)) % 4
    return cleaned + ['А'] * pad_len


def text_to_numbers(text):
    return [alphabet.index(char) for char in text]


def numbers_to_text(numbers):
    return ''.join([alphabet[num] for num in numbers])


def generate_key_const():
    return np.array([
        [3, 1, 1, 1],
        [1, 3, 1, 1],
        [1, 1, 3, 1],
        [1, 1, 1, 3]
    ])


def encrypt_hill(plaintext, key):
    nums = text_to_numbers(plaintext)
    encrypted = []
    for i in range(0, len(nums), 4):
        block = np.array(nums[i:i + 4])
        encrypted_block = np.dot(key, block) % 32
        encrypted.extend(encrypted_block)
    return numbers_to_text(encrypted)


def main():
    try:
        root = Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Выберите файл для шифрования",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if not file_path:
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        prepared = prepare_text(text)
        key = generate_key_const()
        ciphertext = encrypt_hill(prepared, key)

        # Формируем путь для сохранения
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        encrypted_name = f"зашифрованный_{base_name}"
        output_path = os.path.join(dir_name, encrypted_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ciphertext)

        messagebox.showinfo(
            "Готово",
            f"Файл успешно зашифрован:\n{output_path}"
        )

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")


if __name__ == "__main__":
    main()