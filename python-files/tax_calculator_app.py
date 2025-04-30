
# نسخة غير تفاعلية تصلح للبيئات المحمية بدون مدخلات

# اختبار تلقائي للدالة

def calculate_tax(amount, tax_rate):
    try:
        amount = float(amount)
        tax_rate = float(tax_rate)
        tax_value = amount * (tax_rate / 100)
        total = amount + tax_value
        return f"الضريبة: {tax_value:.2f}\nالمجموع الكلي: {total:.2f}"
    except ValueError:
        return "يرجى إدخال قيم رقمية صحيحة."


# حالات اختبار
print("\n--- اختبار 1 ---")
print(calculate_tax(100, 14))  # متوقع: الضريبة 14 والمجموع 114

print("\n--- اختبار 2 ---")
print(calculate_tax(250.5, 10))  # متوقع: الضريبة 25.05 والمجموع 275.55

print("\n--- اختبار 3 (خطأ) ---")
print(calculate_tax("abc", 14))  # متوقع: رسالة خطأ

print("\n--- اختبار 4 ---")
print(calculate_tax(0, 15))  # متوقع: الضريبة 0 والمجموع 0
