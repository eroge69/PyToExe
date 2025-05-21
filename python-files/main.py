import openai

# Установите ваш API ключ от OpenAI
openai.api_key = 'sk-abcdef1234567890abcdef1234567890abcdef12'

def chat_with_gpt(prompt):
    """
    Функция для отправки запроса к ChatGPT и получения ответа
    """
    try:
        # Отправляем запрос к API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Можно использовать "gpt-4" если у вас есть доступ
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Возвращаем ответ от ChatGPT
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Основной цикл программы
print("Введите ваше сообщение...")
while True:
    user_input = input("Ты: ")
    
    if user_input.lower() in ['выход', 'exit', 'quit']:
        print("пока, пидор!")
        break
    
    response = chat_with_gpt(user_input)
    print("ChatGPT:", response)