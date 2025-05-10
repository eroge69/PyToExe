# ملف: martingale_trading_bot.py

import time
from datetime import datetime
from iqoptionapi.stable_api import IQOptionAPI
from random import choice

# إعدادات التداول
START_AMOUNT = 1.0
MULTIPLIER = 2.2
MIN_PAYOUT = 80
DEMO_SESSIONS = 3

# بيانات الدخول
EMAIL = "fidawoxrulleb@gmail.com"
PASSWORD = "mahdirhallab"

# تسجيل الدخول
I_want_money = IQOptionAPI("iqoption.com", EMAIL, PASSWORD)
I_want_money.connect()

if not I_want_money.check_connect():
    print("فشل الاتصال بحساب IQ Option.")
    exit()
else:
    print("تم تسجيل الدخول بنجاح.")

# محاكاة تحقق الشمعة الصاعدة (استبدل بتحليل فعلي لاحقاً)
def is_bullish_candle():
    return choice([True, False])

# تنفيذ جلسة واحدة
def run_session(session_number):
    is_demo = session_number <= DEMO_SESSIONS
    account_type = "practice" if is_demo else "REAL"
    I_want_money.change_balance(account_type)
    amount = START_AMOUNT

    print(f"\nبدء الجلسة {session_number} - {'تجريبي' if is_demo else 'حقيقي'}")

    while True:
        if is_bullish_candle():
            print(f"[{'DEMO' if is_demo else 'REAL'}] وضع صفقة بقيمة {amount}$")
            _, id = I_want_money.buy(amount, "EURUSD", "call", 1)
            if id:
                while not I_want_money.check_win_v3(id):
                    time.sleep(1)
                result = I_want_money.check_win_v3(id)
                if result > 0:
                    print(f"ربح! العودة إلى {START_AMOUNT}$")
                    break
                else:
                    amount = round(amount * MULTIPLIER, 2)
                    print(f"خسارة... المحاولة القادمة ستكون بـ {amount}$")
            else:
                print("فشل فتح الصفقة. إعادة المحاولة لاحقًا.")
        else:
            print("انتظار شمعة صاعدة...")
        time.sleep(1)

# الحلقة الرئيسية
if __name__ == "__main__":
    session = 1
    while True:
        run_session(session)
        session += 1
