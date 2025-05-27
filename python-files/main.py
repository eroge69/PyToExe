import tkinter as tk

def create_window(i):
    window = tk.Tk()
    window.title(f"zxczxczxczxczxczxczxczxczxczxc {i}")
    window.geometry("200x100+{}+{}".format(100 + i*30, 100 + i*30))
    label = tk.Label(window, text=f"zxczxczxczxczxczxczxczxczxczxc {i}")
    label.pack(expand=True)
    # Чтобы окно не закрывалось сразу
    window.mainloop()

if __name__ == "__main__":
    # Создаём много окон — но просто так, они будут блокировать друг друга,
    # поэтому используем несколько процессов или потоков.
    import threading
    num_windows = 199
    threads = []
    for i in range(num_windows):
        t = threading.Thread(target=create_window, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
