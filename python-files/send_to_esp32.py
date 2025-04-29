import http.client
import urllib.parse
import time

# IP-адрес и порт ESP32
ESP32_IP = "192.168.4.1"  # Замените на IP-адрес вашего ESP32
ESP32_PORT = 80
ENDPOINT = "/set_project"

def send_project_name():
    try:
        # Читаем название проекта из файла
        with open("D:/ReaperSend/project_name.txt", "r") as file:
            project_name = file.read().strip()

        # Формируем данные для POST-запроса
        params = urllib.parse.urlencode({"project": project_name})
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Устанавливаем соединение с ESP32
        conn = http.client.HTTPConnection(ESP32_IP, ESP32_PORT, timeout=5)
        
        # Отправляем POST-запрос
        conn.request("POST", ENDPOINT, params, headers)
        
        # Получаем ответ
        response = conn.getresponse()
        if response.status == 200:
            print(f"Successfully sent project name: {project_name}")
        else:
            print(f"Failed to send project name. Status code: {response.status}")
        
        # Закрываем соединение
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        send_project_name()
        time.sleep(10)  # Отправляем каждые 10 секунд