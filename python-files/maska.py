import tkinter as tk

class DraggableMask:
    def __init__(self, width, height):
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Убираем заголовок и рамку окна
        self.root.attributes("-topmost", True)  # Окно всегда поверх других
        self.root.configure(bg="black")  # Задаем черный фон

        # Устанавливаем размеры окна
        self.width = width
        self.height = height
        self.root.geometry(f"{self.width}x{self.height}")

        # Переменные для отслеживания состояния перетаскивания
        self.is_dragging = False
        self.start_x = 0
        self.start_y = 0

        # Привязываем события мыши
        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag)
        self.root.bind("<ButtonRelease-1>", self.stop_drag)

    def start_drag(self, event):
        """Начало перетаскивания"""
        self.is_dragging = True
        self.start_x = event.x
        self.start_y = event.y

    def drag(self, event):
        """Перетаскивание окна"""
        if self.is_dragging:
            x = self.root.winfo_x() + (event.x - self.start_x)
            y = self.root.winfo_y() + (event.y - self.start_y)
            self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        """Окончание перетаскивания"""
        self.is_dragging = False

    def run(self):
        """Запуск главного цикла"""
        self.root.mainloop()

if __name__ == "__main__":
    # Задайте ширину и высоту маски в пикселях
    mask_width = 1800
    mask_height = 270

    app = DraggableMask(mask_width, mask_height)
    app.run()
