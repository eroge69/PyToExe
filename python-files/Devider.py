def calculate_voltage_divider():
    print("Voltage Divider Calculator")
    print("What do you want to calculate?")
    print("1. Voltage across R1 (upper resistor)")
    print("2. Voltage across R2 (lower resistor, Vout)")
    print("3. R1 (upper resistor)")
    print("4. R2 (lower resistor)")
    
    choice = input("Enter your choice (1-4): ")

    # Ввод входного напряжения
    try:
        Vin = float(input("Enter input voltage Vin (V): "))
        if Vin <= 0:
            print("Error: Input voltage must be positive!")
            return
    except ValueError:
        print("Error: Invalid input for voltage!")
        return

    if choice == "1" or choice == "2":
        # Считаем напряжения на резисторах
        try:
            R1 = float(input("Enter R1 (upper resistor, ohms): "))
            R2 = float(input("Enter R2 (lower resistor, ohms): "))
            if R1 <= 0 or R2 <= 0:
                print("Error: Resistors must be positive!")
                return
            if R1 + R2 == 0:
                print("Error: Total resistance cannot be zero!")
                return

            # Расчёты
            Vout = Vin * R2 / (R1 + R2)  # Напряжение на R2
            VR1 = Vin - Vout              # Напряжение на R1

            if choice == "1":
                print(f"\nVoltage across R1: {VR1:.2f} V")
            else:
                print(f"\nVoltage across R2 (Vout): {Vout:.2f} V")
            print(f"Current through the divider: {(Vin / (R1 + R2) * 1000):.2f} mA")

        except ValueError:
            print("Error: Invalid input for resistors!")
            return

    elif choice == "3":
        # Считаем R1, зная R2 и желаемое напряжение на R2 (Vout)
        try:
            R2 = float(input("Enter R2 (lower resistor, ohms): "))
            Vout = float(input("Enter desired Vout (voltage across R2, V): "))
            if R2 <= 0:
                print("Error: R2 must be positive!")
                return
            if Vout <= 0 or Vout >= Vin:
                print("Error: Vout must be positive and less than Vin!")
                return

            # Расчёт R1
            R1 = R2 * (Vin - Vout) / Vout
            print(f"\nRequired R1: {R1:.2f} ohms")
            print(f"Voltage across R1: {(Vin - Vout):.2f} V")
            print(f"Current through the divider: {(Vin / (R1 + R2) * 1000):.2f} mA")

        except ValueError:
            print("Error: Invalid input for R2 or Vout!")
            return

    elif choice == "4":
        # Считаем R2, зная R1 и желаемое напряжение на R2 (Vout)
        try:
            R1 = float(input("Enter R1 (upper resistor, ohms): "))
            Vout = float(input("Enter desired Vout (voltage across R2, V): "))
            if R1 <= 0:
                print("Error: R1 must be positive!")
                return
            if Vout <= 0 or Vout >= Vin:
                print("Error: Vout must be positive and less than Vin!")
                return

            # Расчёт R2
            R2 = R1 * Vout / (Vin - Vout)
            print(f"\nRequired R2: {R2:.2f} ohms")
            print(f"Voltage across R1: {(Vin - Vout):.2f} V")
            print(f"Current through the divider: {(Vin / (R1 + R2) * 1000):.2f} mA")

        except ValueError:
            print("Error: Invalid input for R1 or Vout!")
            return

    else:
        print("Error: Invalid choice! Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    calculate_voltage_divider()