import os
import hashlib
import hmac
from ecdsa.curves import SECP256k1

def generate_valid_private_key():
    """تولید کلید خصوصی معتبر با استفاده از منبع امن رمزنگاری"""
    while True:
        # تولید 32 بایت تصادفی ایمن
        entropy = os.urandom(32) + os.urandom(32)  # ترکیب دو منبع آنتروپی
        
        # استفاده از HMAC-SHA512 برای افزایش امنیت
        key = hmac.new(
            key=b"bitcoin-privkey-generation",
            msg=entropy,
            digestmod=hashlib.sha512
        ).digest()
        
        # تبدیل به کلید خصوصی معتبر
        private_key = int.from_bytes(key[:32], byteorder='big')
        curve_order = SECP256k1.order
        
        # بررسی اعتبار کلید
        if 1 <= private_key < curve_order:
            return format(private_key, '064x')  # خروجی به صورت هگزادسیمال

# تولید و نمایش کلید
valid_key = generate_valid_private_key()
print(f"کلید خصوصی معتبر:\n{valid_key}")
print(f"اعتبار سنجی: {1 <= int(valid_key, 16) < SECP256k1.order}")