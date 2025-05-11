import tkinter as tk

# Создаем главное окно
root = tk.Tk()
root.overrideredirect(True)  # Убираем рамку и заголовок окна
root.geometry("1x1+0+0")     # Размер 1x1 пиксель, позиция (0,0)
root.attributes("-topmost", True)  # Поверх всех окон
root.wm_attributes("-transparentcolor", "white")  # Делаем белый цвет прозрачным (если нужно)

# Устанавливаем цвет фона (если не нужна прозрачность)
root.config(bg="red")  # Можно заменить на любой цвет

# Запускаем главный цикл
root.mainloop()