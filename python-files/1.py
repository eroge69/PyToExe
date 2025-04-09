import json

class Notebook:
    def __init__(self, filename='notes.json'):
        self.filename = filename
        self.load_notes()

    def load_notes(self):
        try:
            with open(self.filename, 'r') as f:
                self.notes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.notes = []

    def save_notes(self):
        with open(self.filename, 'w') as f:
            json.dump(self.notes, f)

    def add_note(self, note):
        self.notes.append(note)
        self.save_notes()
        print("Заметка добавлена!")

    def edit_note(self, index, new_note):
        if 0 <= index < len(self.notes):
            self.notes[index] = new_note
            self.save_notes()
            print("Заметка отредактирована!")
        else:
            print("Заметка с таким индексом не найдена.")

    def search_notes(self, search_term):
        found_notes = [note for note in self.notes if search_term in note]
        return found_notes

    def display_notes(self):
        if not self.notes:
            print("Записная книжка пуста.")
        else:
            for index, note in enumerate(self.notes):
                print(f"{index}: {note}")


def main():
    notebook = Notebook()

    while True:
        print("\nМеню:")
        print("1. Добавить заметку")
        print("2. Редактировать заметку")
        print("3. Искать заметку")
        print("4. Показать все заметки")
        print("5. Выход")

        choice = input("Выберите действие (1-5): ")

        if choice == '1':
            note = input("Введите заметку: ")
            notebook.add_note(note)
        elif choice == '2':
            notebook.display_notes()
            index = int(input("Введите индекс заметки для редактирования: "))
            new_note = input("Введите новую заметку: ")
            notebook.edit_note(index, new_note)
        elif choice == '3':
            search_term = input("Введите поисковый термин: ")
            found_notes = notebook.search_notes(search_term)
            if found_notes:
                print("Найденные заметки:")
                for note in found_notes:
                    print(note)
            else:
                print("Заметки не найдены.")
        elif choice == '4':
            notebook.display_notes()
        elif choice == '5':
            print("Выход из программы.")
            break
        else:
            print("Некорректный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
