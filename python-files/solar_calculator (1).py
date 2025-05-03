def solar_system_calculator():
    print("برنامج حساب منظومة الطاقة الشمسية - باسم جليل")
    try:
        current_amp = float(input("أدخل التيار المطلوب بالأمبير (A): "))
        voltage = float(input("أدخل الفولتية التي تعمل بها (مثل 12 أو 24): "))
        hours_per_day = float(input("أدخل عدد ساعات الاستخدام يومياً: "))

        # حساب استهلاك الطاقة اليومي بالوات ساعة
        daily_consumption_wh = current_amp * voltage * hours_per_day
        print(f"\nاستهلاكك اليومي من الطاقة: {daily_consumption_wh:.2f} واط-ساعة")

        # افتراضات
        panel_power_watt = 300  # قدرة اللوح الواحد بالواط
        panel_daily_output_wh = panel_power_watt * 5  # متوسط إنتاج اللوح في اليوم (5 ساعات شمس فعالة)
        battery_voltage = 12
        battery_capacity_ah = 100
        battery_dod = 0.5  # عمق تفريغ البطارية (50%)
        inverter_safety_factor = 1.2  # زيادة 20% على الحمل الأقصى

        # حساب عدد الألواح الشمسية المطلوبة
        num_panels = daily_consumption_wh / panel_daily_output_wh
        num_panels = int(num_panels) + 1  # تقريب للأعلى

        # حساب عدد البطاريات المطلوبة
        total_battery_capacity_wh = daily_consumption_wh / battery_dod
        battery_capacity_wh = battery_voltage * battery_capacity_ah
        num_batteries = total_battery_capacity_wh / battery_capacity_wh
        num_batteries = int(num_batteries) + 1  # تقريب للأعلى

        # حساب حجم الإنفرتر المطلوب
        max_power_watt = current_amp * voltage
        inverter_power_watt = max_power_watt * inverter_safety_factor
        inverter_power_watt = int(inverter_power_watt) + 1  # تقريب للأعلى

        # عرض النتائج
        print("\n--- نتائج الحساب ---")
        print(f"عدد الألواح الشمسية المطلوبة (300 واط لكل لوح): {num_panels} لوح")
        print(f"عدد البطاريات المطلوبة (12 فولت 100 أمبير): {num_batteries} بطارية")
        print(f"حجم الإنفرتر المطلوب: {inverter_power_watt} واط")

    except ValueError:
        print("يرجى إدخال أرقام صحيحة.")

if __name__ == "__main__":
    solar_system_calculator()
