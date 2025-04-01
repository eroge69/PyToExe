import webbrowser
import time

def rickroll():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    webbrowser.open(url)
    print("You've been rickrolled!")
    time.sleep(5)  # Увеличил задержку для .exe версии

def main():
    print(">>> rickroll()")
    rickroll()

if __name__ == "__main__":
    main()