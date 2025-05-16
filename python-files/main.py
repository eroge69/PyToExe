import subprocess

def get_dhcp_clients(scope, filename="dhcp_clients.txt"):
    """
    Выполняет команду netsh dhcp server scope <scope> show client
    и записывает вывод в текстовый файл.

    Args:
        scope (str): IP-адрес scope DHCP-сервера.
        filename (str): Имя файла для записи вывода.
    """

    try:
        command = ["netsh", "dhcp", "server", "scope", scope, "show", "client"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate()

        # Обработка вывода:
        # - Декодируем байты в строку, используя кодировку cp866, если она не UTF-8
        #   (актуально для Windows)
        # - Заменяем символы возврата каретки (\r) на символы новой строки (\n)
        try:
            output = stdout.decode("utf-8").replace('\r', '')
        except UnicodeDecodeError:
            output = stdout.decode("cp866").replace('\r', '')  # Попробуем cp866

        if stderr:
            error_output = stderr.decode("utf-8").replace('\r', '')
            print(f"Ошибка при выполнении команды: {error_output}")
            return False # Сигнализируем об ошибке

        with open(filename, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"Вывод команды успешно записан в файл: {filename}")
        return True # Сигнализируем об успехе

    except FileNotFoundError:
        print("Ошибка: Команда netsh не найдена. Убедитесь, что она доступна в PATH.")
        return False # Сигнализируем об ошибке

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False # Сигнализируем об ошибке


if __name__ == "__main__":
    scope_ip = "10.25.13.0"  # Замените на нужный IP-адрес scope
    output_file = "dhcp_clients.txt"
    success = get_dhcp_clients(scope_ip, output_file)
    if not success:
        print("Не удалось получить список DHCP клиентов.")
