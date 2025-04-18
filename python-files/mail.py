import smtplib
import random
import os

# Gmail hesab məlumatları
gmail_user = "muradofff2008@gmail.com"
gmail_app_password = "rxkz nkng zqsy ehad"  # Tətbiq şifrəni buraya daxil edin

# Doğrulama kodu
dogrulama_kodu = str(random.randint(100000, 999999))

# E-poçt göndərmə funksiyası
def send_email(to_email, subject, message_text):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # TLS şifrələməsini aktivləşdirir
        server.login(gmail_user, gmail_app_password)  # Gmail hesabı ilə daxil olmaq

        message = f"Subject: {subject}\n\n{message_text}"
        server.sendmail(gmail_user, to_email, message.encode("utf-8"))
        server.quit()

        print(f"E-poçt {to_email} ünvanına göndərildi.")  # Bu sətri tərcümə edirik
        return True
    except Exception as e:
        print(f"E-poçt göndərmə xətası: {e}")
        return False

# Gmail adresini fayldan tapmaq
def get_email_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                if "gmail.com" in line:
                    return line.strip().split(":")[-1].strip()  # Gmail ünvanını tapırıq
    return None

# Lang.txt faylını yoxlayaraq dil tərcüməsini almaq
def get_language(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lang = file.read().strip().lower()
            if lang == "en":
                return "en"
            elif lang == "az":
                return "az"
    return "az"  # Default dil az (Azərbaycan dili)

# Doğrulama yoxlaması
def dogrulama_kontrol():
    kod = input(get_input_translation(lang))  # Dilə görə giriş sorğusunu göstəririk
    if kod == dogrulama_kodu:
        create_file("verify.shadowvault")  # Doğrulama uğurlu olduqda
    else:
        create_file("unverify.shadowvault")  # Yanlış kod daxil edildikdə

# Fayl yaratma funksiyası
def create_file(file_path):
    try:
        with open(file_path, "w") as f:
            f.write("Bu fayl doğrulama məqsədilə yaradılıb.")
    except Exception as e:
        print(f"Fayl yaratma xətası: {e}")

# Mesajın tərcüməsi
def get_message_translation(lang):
    if lang == "en":
        return f"ShadowVault verification code: {dogrulama_kodu}"
    elif lang == "az":
        return f"ShadowVault doğrulama kodunuz: {dogrulama_kodu}"
    else:
        return f"ShadowVault doğrulama kodunuz: {dogrulama_kodu}"  # Default az (Azərbaycan dili)

# Başlığın tərcüməsi
def get_subject_translation(lang):
    if lang == "en":
        return "Verification Code"
    elif lang == "az":
        return "Doğrulama Kodu"
    else:
        return "Doğrulama Kodu"  # Default az (Azərbaycan dili)

# Giriş sorğusunun tərcüməsi
def get_input_translation(lang):
    if lang == "en":
        return "Enter the verification code sent: "
    elif lang == "az":
        return "Göndərilən doğrulama kodunu daxil edin: "
    else:
        return "Göndərilən doğrulama kodunu daxil edin: "  # Default az (Azərbaycan dili)

# Gmail adresini fayldan oxu və doğrulama prosesini başlat
file_path = os.path.join(os.getcwd(), "login.txt")  # Hal-hazırki qovluqda "login.txt" faylı
email = get_email_from_file(file_path)

# Lang.txt faylını oxu və dil tərcüməsini seç
lang_file_path = os.path.join(os.getcwd(), "lang.txt")  # Hal-hazırki qovluqda "lang.txt" faylı
lang = get_language(lang_file_path)

if email:
    subject = get_subject_translation(lang)  # Başlıq tərcüməsi
    message_text = get_message_translation(lang)  # Mesajın tərcüməsi
    
    if send_email(email, subject, message_text):
        print(get_email_sent_translation(lang))  # E-poçt göndərildikdən sonra tərcüməni göstəririk
        dogrulama_kontrol()
else:
    print("Gmail tapılmadı!")

# E-poçt göndərilməsi mesajının tərcüməsi
def get_email_sent_translation(lang):
    if lang == "en":
        return f"Email sent to {email}."
    elif lang == "az":
        return f"E-poçt {email} ünvanına göndərildi."
    else:
        return f"E-poçt {email} ünvanına göndərildi."  # Default az (Azərbaycan dili)
