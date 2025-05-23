import random

def play_guess_the_number():
    """الدالة الرئيسية لتشغيل لعبة تخمين الرقم."""
    print("مرحبًا بك في لعبة تخمين الرقم!")
    print("لقد اخترت رقمًا بين 1 و 100. حاول أن تخمنه.")

    # يختار الكمبيوتر رقمًا عشوائيًا بين 1 و 100
    secret_number = random.randint(1, 100)
    attempts = 0
    guessed_correctly = False

    while not guessed_correctly:
        try:
            # يطلب من اللاعب إدخال تخمينه
            guess_str = input("أدخل تخمينك (رقم بين 1 و 100): ")
            guess = int(guess_str) # تحويل الإدخال إلى رقم صحيح

            attempts += 1 # زيادة عدد المحاولات

            if guess < 1 or guess > 100:
                print("الرجاء إدخال رقم بين 1 و 100 فقط.")
            elif guess < secret_number:
                print("أعلى من ذلك! حاول مرة أخرى.")
            elif guess > secret_number:
                print("أقل من ذلك! حاول مرة أخرى.")
            else:
                guessed_correctly = True
                print(f"تهانينا! لقد خمنت الرقم {secret_number} بشكل صحيح!")
                print(f"لقد استغرقت {attempts} محاولات.")

        except ValueError:
            # هذا الجزء للتعامل مع إدخال المستخدم إذا لم يكن رقمًا
            print("خطأ! الرجاء إدخال رقم صحيح.")
        except Exception as e:
            print(f"حدث خطأ غير متوقع: {e}")

    # السؤال إذا كان اللاعب يريد اللعب مرة أخرى
    play_again = input("هل تريد اللعب مرة أخرى؟ (نعم/لا): ").lower()
    if play_again == "نعم":
        play_guess_the_number() # إعادة تشغيل اللعبة
    else:
        print("شكرًا للعب! إلى اللقاء.")

# لبدء اللعبة عند تشغيل الملف
if __name__ == "__main__":
    play_guess_the_number()