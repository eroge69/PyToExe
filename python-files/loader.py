import os
import subprocess

def print_banner():
    banner = """
    ██╗   ██╗███████╗██╗  ██╗ ██████╗      ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
    ██║   ██║██╔════╝╚██╗██╔╝██╔═══██╗    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
    ██║   ██║█████╗   ╚███╔╝ ██║   ██║    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   
    ╚██╗ ██╔╝██╔══╝   ██╔██╗ ██║   ██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   
     ╚████╔╝ ███████╗██╔╝ ██╗╚██████╔╝    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   
      ╚═══╝  ╚══════╝╚═╝  ╚═╝ ╚═════╝      ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
    """
    print(banner)

def check_java():
    """ Проверяет, установлена ли Java 17 """
    try:
        result = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr  # Объединяем stdout и stderr
        if "17." in output:
            return True
        else:
            print("Установите Java 17!")
            return False
    except FileNotFoundError:
        print("Установите Java 17!")
        return False

def start_loft(ram):
    """ Запускает Vexo Client с указанным количеством ОЗУ """
    if not check_java():
        return
    try:
        subprocess.Popen(["java", f"-Xmx{ram}G", "-jar", "Loft client.jar"])
        print(f"Vexo Client запущен с {ram} ГБ ОЗУ.")
    except Exception as e:
        print(f"Ошибка при запуске: {e}")

def main():
    print_banner()
    while True:
        print("\n1. Запустить чит")
        print("2. Выбрать ОЗУ (от 4 до 32 ГБ)")
        print("3. Проверить, установлена ли Java 17")
        print("4. Закрыть Minecraft")
        print("5. Выход")
        
        choice = input("\nVexo выберите действие: ")
        
        if choice == "1":
            start_loft(4)  # По умолчанию 4 ГБ
        elif choice == "2":
            try:
                ram = int(input("Введите количество ОЗУ (4-32 ГБ): "))
                if 4 <= ram <= 32:
                    start_loft(ram)
                else:
                    print("Ошибка: укажите значение от 4 до 32.")
            except ValueError:
                print("Ошибка: введите число от 4 до 32.")
        elif choice == "3":
            if check_java():
                print("Java 17 установлена.")
            else:
                print("Java 17 не найдена.")
        elif choice == "4":
            os.system("taskkill /F /IM javaw.exe")
            print("Minecraft закрыт.")
        elif choice == "5":
            print("Выход...")
            break
        else:
            print("Неверный ввод. Повторите попытку.")

if __name__ == "__main__":
    main()
