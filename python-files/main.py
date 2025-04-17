# Функция для расчета времени работы досветки за месяц
def calculate_lighting_time():
    total_minutes = 0  # Общее количество минут работы досветки за месяц

    # Цикл для ввода данных за каждые сутки
    for day in range(1, 31):  # Предполагаем, что в месяце 30 дней
        print(f"День {day}:")

        # Ввод времени включения и выключения
        start_time = input("Введите время включения (в формате ЧЧ:ММ): ")
        end_time = input("Введите время выключения (в формате ЧЧ:ММ): ")

        # Разделяем часы и минуты для времени включения
        start_hour, start_minute = map(int, start_time.split(":"))
        # Разделяем часы и минуты для времени выключения
        end_hour, end_minute = map(int, end_time.split(":"))

        # Переводим все в минуты для удобства расчета
        start_total_minutes = start_hour * 60 + start_minute
        end_total_minutes = end_hour * 60 + end_minute

        # Если время выключения больше времени включения
        if end_total_minutes > start_total_minutes:
            daily_minutes = end_total_minutes - start_total_minutes
        else:
            # Если досветка работала после полуночи
            daily_minutes = (24 * 60 - start_total_minutes) + end_total_minutes

        # Округляем до ближайшего кратного 30 минутам
        daily_minutes = (daily_minutes + 15) // 30 * 30

        # Добавляем к общему времени
        total_minutes += daily_minutes

    # Переводим общее время обратно в часы и минуты
    total_hours = total_minutes // 60
    total_remainder_minutes = total_minutes % 60

    # Выводим результат
    print(f"Общее время работы досветки за месяц: {total_hours} часов {total_remainder_minutes} минут")

# Вызываем функцию
calculate_lighting_time()

