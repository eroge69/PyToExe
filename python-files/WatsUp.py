import re
from datetime import datetime
import csv

def parse_whatsapp_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pattern = re.compile(r'^(\d{1,2}\.\d{1,2}\.\d{2,4}, \d{1,2}:\d{2}) - (.*?): (.*)$')
    data = []
    for line in lines:
        match = pattern.match(line)
        if match:
            date_time_str, author, message = match.groups()
            date_time = datetime.strptime(date_time_str, '%d.%m.%Y, %H:%M')
            data.append([date_time.date(), date_time.time(), author, message.strip()])

    return data

def save_to_csv(data, output_file):
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Дата', 'Время', 'Автор', 'Сообщение'])
        writer.writerows(data)

if __name__ == "__main__":
    input_file = 'chat.txt'
    output_file = 'whatsapp_report.csv'
    data = parse_whatsapp_chat(input_file)
    save_to_csv(data, output_file)
    print(f'Отчет сохранен в {output_file}')