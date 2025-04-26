import subprocess

def run_program():
    print("Доступные программы для запуска:")
    print("1. Запустить кряк")

    while True:
        choice = input("Введите номер для запуска (или 'выход' для завершения): ")

        if choice == '1':
            subprocess.run(["CrackKerach"])
        elif choice == '2':
            subprocess.run([""])
        elif choice == '3':
            subprocess.run([""])
        elif choice.lower() == 'выход':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    run_program()
