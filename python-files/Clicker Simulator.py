import tkinter as tk

class ClickerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Clicker Game")
        self.root.geometry("400x400")

        self.score = 0
        self.multiplier = 1

        self.label = tk.Label(root, text="Score: 0", font=("Arial", 16))
        self.label.pack(pady=10)

        self.button = tk.Button(root, text="Click Me!", font=("Arial", 14), command=self.increment_score)
        self.button.pack(pady=10)

        self.multiplier_label = tk.Label(root, text="Multiplier: x1", font=("Arial", 14))
        self.multiplier_label.pack(pady=10)

        self.upgrades = [
            {"cost": 10, "multiplier": 2},
            {"cost": 50, "multiplier": 5},
            {"cost": 200, "multiplier": 10},
            {"cost": 1000, "multiplier": 20},
            {"cost": 5000, "multiplier": 50}
        ]

        self.upgrade_buttons = []
        for i, upgrade in enumerate(self.upgrades):
            btn = tk.Button(root, text=f"Upgrade {i+1}: Cost {upgrade['cost']} (x{upgrade['multiplier']})",
                            font=("Arial", 12), command=lambda u=upgrade: self.buy_upgrade(u))
            btn.pack(pady=5)
            self.upgrade_buttons.append(btn)

    def increment_score(self):
        self.score += self.multiplier
        self.label.config(text=f"Score: {self.score}")

    def buy_upgrade(self, upgrade):
        if self.score >= upgrade["cost"]:
            self.score -= upgrade["cost"]
            self.multiplier = upgrade["multiplier"]
            self.label.config(text=f"Score: {self.score}")
            self.multiplier_label.config(text=f"Multiplier: x{self.multiplier}")

if __name__ == "__main__":
    root = tk.Tk()
    game = ClickerGame(root)
    root.mainloop()
