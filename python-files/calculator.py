import time
import math


def gam(x, y):
    return x + y

def tafriq(x, y):
    return x - y


def zarb(x, y):
    return x * y


def taghsim(x, y):
    if y == 0:
        return "تقسیم بر صفر غیر مجاز است."
    return x / y


def tvan(x, y):
    return x ** y


def radikal(x):
    if x <= 0:
        return "عدد مثبت وارد کنید"
    return math.sqrt(x)

def ghadr(x):
    return abs(x)

def dalay():
    time.sleep(1.3)

restart = "\nدر حال محاسبه...\n"

def end2():
    print("حمايت فراموش نشه\nCreated By OMID\nTelegram : @iran5090\nدر حال خروج...")
    dalay()
    print("شما خارج شديد👋")
    exit()

def end():
    while True:
        agine = input("\nمیخوای دوباره استفاده کنی؟ (y/n)").strip().lower()
        if agine == "y":
            start()
        elif agine == "n":
            print("حمايت فراموش نشه\nCreated By OMID\nTelegram : @iran5090\nدر حال خروج...")
            dalay()
            print("شما خارج شديد👋")
            exit()
        else:
            print("\nفقط y یا n وارد کنید\n")


def start():
    print("===========🩵🩵(❁´◡`❁)💖💖=============")
    print("1- جمع")
    print("2- تفریق")
    print("3- ضرب")
    print("4- تقسیم")
    print("5- توان")
    print("6- رادیکال")
    print("7- قدر مطلق")
    print("8- خروج")
    print("===========💚💚(^///^)💜💜=============")

# دریافت ورودی
    while True:
        choose = input("لطفاً عدد مورد نظر را وارد کنید (بین 1 تا 8):\n>>> ")
        if not choose.strip():
            print("\nورودی نمی‌تونه خالی باشه.\n")
            continue
        try:
            choose2 = int(choose)
            if choose2 not in [1, 2, 3, 4, 5, 6, 7, 8]:
                print("\nعدد مناسب وارد کنيد (بین 1 تا 8)\n")
                continue
        except ValueError:
            print("\nفقط عدد وارد کنید.\n")
            continue
        else:
            break
#محاسبه راديکال
    if choose2 == 6:
        while True:
            number1 = input("عدد خود را برای رایدیکال وارد کنيد.\n>>> ")
            if not number1.strip():
                print("\nورودی نمی‌تونه خالی باشه.\n")
                continue
            try:
                num1 = float(number1)
                if num1 < 1:
                    print("\nبرای محاسبه رادیکال عدد وارد شده باید مثبت باشد\n")
            except ValueError:
                print("\nفقط عدد وارد کن.\n")
                continue
            break
        print(restart)
        print("\nresult = ", radikal(num1))
        dalay()
        end()

    if choose2 == 7:
        while True:
            number1 = input("عدد خود را برای قدر مطلق وارد کنيد.\n>>> ")
            if not number1.strip():
                print("\nورودی نمی‌تونه خالی باشه.\n")
                continue
            try:
                num1 = float(number1)
            except ValueError:
                print("\nفقط عدد وارد کن.\n")
                continue
            break
        print("\nresult = ", ghadr(num1))
        print(restart)
        dalay()
        end()

    if choose2 == 8:
        end2()

# دريافت عدد اول
    while True:
        number1 = input("عدد اول رو وارد کن \n>>> ")
        if not number1.strip():
            print("\nورودی نمی‌تونه خالی باشه.\n")
            continue
        try:
            num1 = float(number1)

        except ValueError:
            print("\nفقط عدد وارد کن.\n")
            continue
        break

# دريافت عدد دوم
    while True:
        number2 = input("عدد دوم رو وارد کن \n>>> ")
        if not number2.strip():
            print("\nورودی نمی‌تونه خالی باشه.\n")
            continue
        try:
            num2 = float(number2)
        except ValueError:
            print("\nفقط عدد وارد کن.\n")
            continue
        break

# انجام محاسبات
    print(restart)
    dalay()
    match choose2:
        case 1:
            print("\nresult = ", gam(num1, num2))
        case 2:
            print("\nresult = ", tafriq(num1, num2))
        case 3:
            print("\nresult = ", zarb(num1, num2))
        case 4:
            print("\nresult = ", taghsim(num1, num2))
        case 5:
            print("\nresult = ", tvan(num1, num2))
    end()


start()

