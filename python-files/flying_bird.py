import tkinter as tk
import random

# Constants
WIDTH = 300
HEIGHT = 500
PIPE_WIDTH = 50
PIPE_GAP = 140
BIRD_WIDTH = 30
BIRD_HEIGHT = 30
GRAVITY = 1
FLAP_STRENGTH = -10
PIPE_SPEED = 4
PIPE_DISTANCE = 200

class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='skyblue')
        self.canvas.pack()

        # Score
        self.score = 0
        self.score_text = self.canvas.create_text(WIDTH // 2, 30, text="Score: 0", font=("Arial", 20), fill="white")

        # Buttons
        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, font=("Arial", 12), bg="green")
        self.start_button.pack(pady=5)

        self.flap_button = tk.Button(root, text="Flap!", command=self.flap, font=("Arial", 12), bg="orange", state=tk.DISABLED)
        self.flap_button.pack(pady=5)

        # Bird
        self.bird = self.canvas.create_oval(80, HEIGHT//2, 80 + BIRD_WIDTH, HEIGHT//2 + BIRD_HEIGHT, fill="yellow")
        self.bird_velocity = 0

        # Pipes and IDs
        self.pipes = []
        self.pipe_id_counter = 0
        self.passed_pipe_ids = set()

        # Game state
        self.is_game_over = False
        self.is_running = False

        # Track Game Over text so we can remove it later
        self.game_over_text_id = None  # <-- FIX HERE

        self.game_loop()

    def start_game(self):
        self.is_running = True
        self.is_game_over = False
        self.score = 0
        self.update_score()
        self.flap_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.canvas.coords(self.bird, 80, HEIGHT // 2, 80 + BIRD_WIDTH, HEIGHT // 2 + BIRD_HEIGHT)
        self.bird_velocity = 0

        # Remove pipes
        for top, bottom, _ in self.pipes:
            self.canvas.delete(top)
            self.canvas.delete(bottom)
        self.pipes.clear()
        self.passed_pipe_ids.clear()
        self.pipe_id_counter = 0

        # Remove "Game Over" text if it exists
        if self.game_over_text_id is not None:  # <-- FIX HERE
            self.canvas.delete(self.game_over_text_id)
            self.game_over_text_id = None  # <-- FIX HERE

    def flap(self):
        if self.is_running and not self.is_game_over:
            self.bird_velocity = FLAP_STRENGTH

    def create_pipe(self):
        pipe_height = random.randint(80, HEIGHT - PIPE_GAP - 80)
        x1 = WIDTH
        x2 = WIDTH + PIPE_WIDTH

        top = self.canvas.create_rectangle(x1, 0, x2, pipe_height, fill="green")
        bottom = self.canvas.create_rectangle(x1, pipe_height + PIPE_GAP, x2, HEIGHT, fill="green")

        pipe_id = self.pipe_id_counter
        self.pipe_id_counter += 1

        self.pipes.append((top, bottom, pipe_id))

    def move_pipes(self):
        for top, bottom, pipe_id in self.pipes:
            self.canvas.move(top, -PIPE_SPEED, 0)
            self.canvas.move(bottom, -PIPE_SPEED, 0)

        while self.pipes and self.canvas.coords(self.pipes[0][0])[2] < 0:
            self.canvas.delete(self.pipes[0][0])
            self.canvas.delete(self.pipes[0][1])
            self.pipes.pop(0)

        if not self.pipes or (WIDTH - self.canvas.coords(self.pipes[-1][0])[2]) > PIPE_DISTANCE:
            self.create_pipe()

        bird_x = self.canvas.coords(self.bird)[0]
        for top, _, pipe_id in self.pipes:
            pipe_right_edge = self.canvas.coords(top)[2]
            if pipe_right_edge < bird_x and pipe_id not in self.passed_pipe_ids:
                self.score += 1
                self.passed_pipe_ids.add(pipe_id)
                self.update_score()

    def check_collision(self):
        bird_coords = self.canvas.coords(self.bird)

        if bird_coords[1] <= 0 or bird_coords[3] >= HEIGHT:
            self.game_over()

        for top, bottom, _ in self.pipes:
            if self._overlaps(bird_coords, self.canvas.coords(top)) or self._overlaps(bird_coords, self.canvas.coords(bottom)):
                self.game_over()

    def _overlaps(self, a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def game_over(self):
        self.is_game_over = True
        self.is_running = False
        self.flap_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        # Create and store Game Over text ID
        self.game_over_text_id = self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER", font=('Arial', 22, 'bold'), fill="red")  # <-- FIX HERE

    def update_bird(self):
        self.bird_velocity += GRAVITY
        self.canvas.move(self.bird, 0, self.bird_velocity)

    def update_score(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def game_loop(self):
        if self.is_running and not self.is_game_over:
            self.update_bird()
            self.move_pipes()
            self.check_collision()
        self.root.after(20, self.game_loop)

# Run game
if __name__ == "__main__":
    root = tk.Tk()
    game = FlappyBirdGame(root)
    root.mainloop()
