import webbrowser
import time

def rickroll():
    url = "https://www.pornhub.com"  # Измененная ссылка на главную страницу Pornhub
    webbrowser.open(url)
    print("Surprise!")
    time.sleep(5)

def main():
    print(">>> rickroll()")
    rickroll()

if __name__ == "__main__":
    main()