def solution_mixer():
    print("=== Калькулятор смешивания растворов ===")
    print("Расчет пропорций для получения нужного объема и концентрации\n")
    
    while True:
        try:
            # Ввод целевых параметров
            target_volume = float(input("Введите нужный объем конечного раствора : "))
            target_concentration = float(input("Введите нужную концентрацию (%): "))
            
            # Ввод параметров первого раствора
            c1 = float(input("\nВведите концентрацию первого раствора (%): "))
            
            # Ввод параметров второго раствора
            c2 = float(input("Введите концентрацию второго раствора (%): "))
            
            # Проверка на возможность смешивания
            if not (min(c1, c2) <= target_concentration <= max(c1, c2)):
                print(f"Ошибка: Невозможно получить {target_concentration}% раствор "
                      f"из {c1}% и {c2}% растворов!")
                continue
            
            # Расчет по правилу креста (метод алгебраических пропорций)
            if c1 == c2:
                volume1 = target_volume / 2
                volume2 = target_volume / 2
            else:
                part1 = abs(target_concentration - c2)
                part2 = abs(c1 - target_concentration)
                total_parts = part1 + part2
                
                volume1 = (part1 / total_parts) * target_volume
                volume2 = (part2 / total_parts) * target_volume
            
            # Вывод результатов
            print("\n=== Результаты расчета ===")
            print(f"Для получения {target_volume:.1f}  {target_concentration}% раствора:")
            print(f"- {c1}% раствора нужно: {volume1:.1f} ")
            print(f"- {c2}% раствора нужно: {volume2:.1f} ")
            
            # Проверка точности
            final_concentration = (volume1 * c1 + volume2 * c2) / (volume1 + volume2)
            print(f"\nПроверка: полученная концентрация = {final_concentration:.2f}%")
            
            # Запрос на повтор
            repeat = input("\nСделать еще один расчет? (y/n): ").lower()
            if repeat != 'y':
                print("Работа программы завершена.")
                break
                
        except ValueError:
            print("Ошибка: введите числовые значения!")
            continue

# Запуск программы
solution_mixer()
