def calculate_nds(amount):
    # Расчет НДС 20% (если сумма с НДС)
    nds_20 = amount / 6
    amount_after_nds_20 = amount - nds_20
    
    # Расчет НДС 10% (если сумма также с НДС)
    nds_10 = amount / 11
    amount_after_nds_10 = amount - nds_10
    
    return (nds_20, amount_after_nds_20, nds_10, amount_after_nds_10)

def main():
    print("Программа ООО Сураспецхим")
    print("Расчет НДС 20% и 10% от введенной суммы (с учетом НДС).")
    
    while True:
        try:
            # Ввод суммы от пользователя
            amount = float(input("Введите сумму (с учетом НДС): "))
            
            # Вызов функции для расчета НДС
            nds_20, amount_after_nds_20, nds_10, amount_after_nds_10 = calculate_nds(amount)
            
            # Вывод результатов для НДС 20%
            print(f"\nРезультаты для ставки НДС 20%:")
            print(f"Сумма НДС: {nds_20:.4f}")
            print(f"Сумма без НДС: {amount_after_nds_20:.4f}")
            
            # Вывод результатов для НДС 10%
            print(f"\nРезультаты для ставки НДС 10%:")
            print(f"Сумма НДС: {nds_10:.4f}")
            print(f"Сумма без НДС: {amount_after_nds_10:.4f}")
        
            # Предложение пользователю продолжить или завершить
            continue_choice = input("\nХотите выполнить новый расчет? (да/нет): ").strip().lower()
            if continue_choice != 'да':
                print("Спасибо за использование программы. До свидания!")
                break

        except ValueError:
            print("Пожалуйста, введите корректную числовую сумму.")

if __name__ == "__main__":
    main()
