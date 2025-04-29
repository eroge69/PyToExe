Python 3.8.2 (tags/v3.8.2:7b3ab59, Feb 25 2020, 23:03:10) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import csv

# مسیری که مبلغ شهریه در آن ذخیره می‌شود
TUITION_FEE_FILE = 'tuition_fee.txt'

# تابع برای تنظیم مبلغ شهریه
def set_tuition_fee():
    try:
        new_fee = int(input("مبلغ شهریه جدید (به ریال): "))
        with open(TUITION_FEE_FILE, 'w') as file:
            file.write(str(new_fee))
        print("مبلغ شهریه با موفقیت تنظیم شد.")
    except ValueError:
        print("لطفا مبلغی عددی وارد کنید.")

# تابع برای خواندن مبلغ شهریه
def get_tuition_fee():
    try:
        with open(TUITION_FEE_FILE, 'r') as file:
            fee = int(file.read().strip())
            return fee
    except FileNotFoundError:
        print("مبلغ شهریه تنظیم نشده است. لطفاً ابتدا مبلغ شهریه را تنظیم کنید.")
        return None
    except ValueError:
        print("مقدار موجود در فایل نامعتبر است.")
        return None

# تابع برای ثبت نام دانش آموز
def register_student():
    tuition_fee = get_tuition_fee()
    if tuition_fee is None:
        return  # اگر شهریه معتبر نیست، از تابع خارج می‌شود

    name = input("نام دانش آموز: ")
    age = input("سن دانش آموز: ")
    current_grade = input("پایه تحصیلی دانش آموز (1 تا 6): ")
    parent_contact = input("شماره تماس والدین: ")
    registration_year = input("سال ثبت نام (1404 تا 1420): ")
    national_code = input("کد ملی دانش آموز: ")

    # اعتبارسنجی سال
    if not (1404 <= int(registration_year) <= 1420):
        print("سال ثبت نام نامعتبر است! لطفاً سالی بین 1404 تا 1420 وارد کنید.")
        return

    # اعتبارسنجی کد ملی
    if not (national_code.isdigit() and len(national_code) == 10):
        print("کد ملی نامعتبر است! لطفاً کدی 10 رقمی وارد کنید.")
        return

    # انتخاب جنسیت
    gender = input("جنسیت (مرد/زن): ").lower()
    if gender not in ["مرد", "زن"]:
        print("جنسیت نامعتبر است! لطفاً 'مرد' یا 'زن' وارد کنید.")
        return

    # انتخاب ترم
    semester = input("ترم (بهار/تابستان/پاییز/زمستان): ").lower()
    if semester not in ["بهار", "تابستان", "پاییز", "زمستان"]:
        print("ترم نامعتبر است! لطفاً ترمی از گزینه‌های موجود وارد کنید.")
        return
    
    # دریافت شهریه
    tuition_fee_paid = int(input(f"مبلغ شهریه پرداخت شده (ریال): "))
    
    # محاسبه بدهکاری یا بستانکاری
    if tuition_fee_paid < tuition_fee:
        debt = tuition_fee - tuition_fee_paid
        financial_status = f"دانش آموز بدهکار است به مبلغ {debt} ریال."
    elif tuition_fee_paid > tuition_fee:
        credit = tuition_fee_paid - tuition_fee
        financial_status = f"دانش آموز بستانکار است به مبلغ {credit} ریال."
    else:
        financial_status = "دانش آموز شهریه را به طور کامل پرداخت کرده است."

    # ذخیره اطلاعات در یک فایل CSV
    with open('students.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, age, current_grade, parent_contact, registration_year, national_code, gender, semester, tuition_fee_paid, financial_status])
    
    print("ثبت نام با موفقیت انجام شد!")
    print(financial_status)

# تابع برای ثبت نمره دانش آموز
def record_grade():
    name = input("نام دانش آموز برای ثبت نمره: ")
    subject = input("موضوع نمره (مثلا ریاضی): ")
    grade = float(input("نمره: "))  # تبدیل ورودی به نوع عددی

    # انتخاب ترم
    semester = input("ترم (بهار/تابستان/پاییز/زمستان): ").lower()
    if semester not in ["بهار", "تابستان", "پاییز", "زمستان"]:
        print("ترم نامعتبر است! لطفاً ترمی از گزینه‌های موجود وارد کنید.")
        return

    # تعیین وضعیت و پایه بعدی
    if grade >= 50:
        status = "قبول"
    else:
        status = "مردود"

    # به‌روزرسانی فایل نمرات و وضعیت
    with open('grades.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, subject, grade, status, semester])

    print(f"نمره با موفقیت ثبت شد! وضعیت: {status}")

    # اگر دانش آموز قبول شد، ثبت نام در پایه بعدی
    if status == "قبول":
        update_student_grade(name)

# تابع برای به روز رسانی پایه دانش آموز
def update_student_grade(name):
    students = []
    # خواندن اطلاعات از فایل students.csv
    with open('students.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == name:  # اگر نام دانش آموز برابر با نام ورودی باشد
                current_grade = int(row[2])  # پایه فعلی
                if current_grade < 6:  # اگر دانش آموز در پایه 6 نیست
                    new_grade = current_grade + 1
                    row[2] = str(new_grade)  # به روز رسانی پایه
                print(f"دانش آموز {name} به پایه {row[2]} منتقل شد.")
            students.append(row)

    # نوشتن اطلاعات به‌روز شده به فایل
    with open('students.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(students)

# برنامه اصلی
if __name__ == "__main__":
    while True:
        admin_action = input("آیا ادمین هستید و می‌خواهید (1) مبلغ شهریه را تنظیم کنید یا (2) ثبت نام دانش آموز یا (3) ثبت نمره انجام دهید؟ (1/2/3): ")
        if admin_action == '1':
            set_tuition_fee()
        elif admin_action == '2':
            register_student()
        elif admin_action == '3':
            record_grade()
        else:
            print("عملیات نامعتبر است!")
        
        cont = input("آیا می‌خواهید عملیات دیگری انجام دهید؟ (بله/خیر): ")
        if cont.lower() != 'بله':
            break
KeyboardInterrupt
>>> 