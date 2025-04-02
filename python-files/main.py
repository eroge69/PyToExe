def main():
    print("Программа расчёта робастного среднего по ГОСТ 13528")
    print("=" * 50)
    print("\nВведите данные от 3 до 7 лабораторий.")
    print("Для каждой лаборатории введите 5 результатов измерений.\n")

    # Шаг 1. Ввод данных (соответствует разделу 5 ГОСТ 13528)
    labs = []
    num_labs = 0
    
    # Запрашиваем количество лабораторий (3-7)
    while True:
        try:
            num_labs = int(input("Введите количество лабораторий (3-7): "))
            if 3 <= num_labs <= 7:
                break
            print("Ошибка! Допустимо от 3 до 7 лабораторий.")
        except ValueError:
            print("Ошибка! Введите целое число.")

    # Ввод данных для каждой лаборатории (пункт 5.2 ГОСТ)
    for i in range(num_labs):
        while True:
            try:
                data = input(f"Лаборатория {i+1}. Введите 5 результатов через пробел: ").split()
                if len(data) != 5:
                    print("Ошибка! Нужно ровно 5 значений.")
                    continue
                
                # Преобразуем в числа и проверяем корректность
                values = [float(x) for x in data]
                labs.append(values)
                break
            except ValueError:
                print("Ошибка! Вводите только числа, разделённые пробелами.")

    # Шаг 2. Вычисляем средние для каждой лаборатории (формула (1) ГОСТ)
    lab_means = [sum(values)/len(values) for values in labs]
    
    print("\nСредние значения по лабораториям:")
    for i, mean in enumerate(lab_means, 1):
        print(f"Лаборатория {i}: {mean:.4f}")

    # Шаг 3. Вычисляем начальную медиану (алгоритм A, пункт С.2 ГОСТ)
    sorted_means = sorted(lab_means)
    n = len(sorted_means)
    
    # Формула для медианы (С.2.1)
    if n % 2 == 1:
        median = sorted_means[n//2]
    else:
        median = (sorted_means[n//2 - 1] + sorted_means[n//2]) / 2

    # Шаг 4. Вычисляем MAD (медианное абсолютное отклонение) (С.2.2)
    deviations = [abs(x - median) for x in lab_means]
    sorted_deviations = sorted(deviations)
    
    # Медиана отклонений (С.2.2)
    if n % 2 == 1:
        mad = sorted_deviations[n//2]
    else:
        mad = (sorted_deviations[n//2 - 1] + sorted_deviations[n//2]) / 2
    
    # Приводим к нормальному распределению (С.2.2)
    s_star = 1.483 * mad

    # Шаг 5. Итеративное вычисление весов (С.2.3)
    print("\nИтеративный процесс вычисления робастного среднего:")
    for iteration in range(1, 6):  # 5 итераций обычно достаточно
        # Вычисляем веса по Хуберу (С.2.3)
        weights = []
        for x in lab_means:
            deviation = abs(x - median)
            if deviation <= 1.5 * s_star:
                weights.append(1.0)
            else:
                weights.append((1.5 * s_star) / deviation)
        
        # Новое робастное среднее (С.2.4)
        new_median = sum(x*w for x,w in zip(lab_means, weights)) / sum(weights)
        
        print(f"Итерация {iteration}: {new_median:.6f}")
        
        # Проверка сходимости (С.2.5)
        if abs(new_median - median) < 0.0001 * median:
            break
            
        median = new_median

    # Шаг 6. Расчёт стандартной неопределённости (формула (8) ГОСТ)
    u = 1.25 * s_star / (n ** 0.5)

    # Шаг 7. Вывод результатов
    print("\n" + "=" * 50)
    print("ОТЧЁТ О РЕЗУЛЬТАТАХ")
    print("=" * 50)
    print(f"Количество лабораторий: {num_labs}")
    print("\nСредние значения по лабораториям:")
    for i, mean in enumerate(lab_means, 1):
        print(f"Лаборатория {i}: {mean:.6f}")
    
    print("\nРобастные характеристики:")
    print(f"- Медиана (начальная): {sorted_means[n//2]:.6f}")
    print(f"- MAD: {mad:.6f}")
    print(f"- s* (робастное стандартное отклонение): {s_star:.6f}")
    print(f"- Робастное среднее (X*): {median:.6f}")
    print(f"- Стандартная неопределённость u(X): {u:.6f}")
    
    # Ожидание перед закрытием
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()