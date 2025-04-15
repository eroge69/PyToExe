import tkinter as tk
from tkinter import messagebox
import threading
from math import sqrt

# Function to generate prime numbers
Prim = []
def prime_generator(start, end, stop_event):
    for num in range(start, end):
        if stop_event.is_set():
            break

        if num > 1:
            is_prime = True
            for i in range(2, int(sqrt(num)) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                print(num)
                Prim.append(num)

# GUI part to show message boxes
def show_messages(stop_event):
    root = tk.Tk()
    root.withdraw()

    for _ in range(20):
        messagebox.showwarning(
            "Security Warning",
            "You have been hacked! Don't open files from people you don't know!"
        )

    root.destroy()
    stop_event.set()

# Main execution
if __name__ == '__main__':
    start = int(7415000000)
    end = int(999999999999999999999999999999999999999999)

    stop_event = threading.Event()

    prime_thread = threading.Thread(target=prime_generator, args=(start, end, stop_event))
    prime_thread.start()

    show_messages(stop_event)

    prime_thread.join()