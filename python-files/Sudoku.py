import pygame
import numpy as np
import easyocr
import cv2
from tkinter import Tk, filedialog

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
FONT_SMALL = pygame.font.SysFont("comicsans", 20)

# Sudoku board
board = np.zeros((9, 9), dtype=int)

# Sudoku solver using backtracking
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
        if board[row - row % 3 + i // 3][col - col % 3 + i % 3] == num:
            return False
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def solve_row(board, row):
    for col in range(9):
        if board[row][col] == 0:
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    if solve_sudoku(board):
                        return True
                    board[row][col] = 0
            return False
    return True

def solve_column(board, col):
    for row in range(9):
        if board[row][col] == 0:
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    if solve_sudoku(board):
                        return True
                    board[row][col] = 0
            return False
    return True

def solve_box(board, box_start_row, box_start_col):
    for i in range(3):
        for j in range(3):
            row, col = box_start_row + i, box_start_col + j
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def draw_grid():
    for i in range(10):
        if i % 3 == 0:
            thickness = 4
        else:
            thickness = 1
        pygame.draw.line(WINDOW, BLACK, (i * WIDTH / 9, 0), (i * WIDTH / 9, HEIGHT), thickness)
        pygame.draw.line(WINDOW, BLACK, (0, i * HEIGHT / 9), (WIDTH, i * HEIGHT / 9), thickness)

def draw_numbers(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                text = FONT.render(str(board[i][j]), True, BLACK)
                WINDOW.blit(text, (j * WIDTH / 9 + 20, i * HEIGHT / 9 + 10))

def draw_buttons():
    solve_all_button = pygame.Rect(420, 10, 160, 40)
    pygame.draw.rect(WINDOW, GRAY, solve_all_button)
    text = FONT_SMALL.render("Solve All", True, BLACK)
    WINDOW.blit(text, (450, 20))

    solve_row_button = pygame.Rect(420, 60, 160, 40)
    pygame.draw.rect(WINDOW, GRAY, solve_row_button)
    text = FONT_SMALL.render("Solve Row", True, BLACK)
    WINDOW.blit(text, (450, 70))

    solve_column_button = pygame.Rect(420, 110, 160, 40)
    pygame.draw.rect(WINDOW, GRAY, solve_column_button)
    text = FONT_SMALL.render("Solve Column", True, BLACK)
    WINDOW.blit(text, (450, 120))

    solve_box_button = pygame.Rect(420, 160, 160, 40)
    pygame.draw.rect(WINDOW, GRAY, solve_box_button)
    text = FONT_SMALL.render("Solve Box", True, BLACK)
    WINDOW.blit(text, (450, 170))

    load_image_button = pygame.Rect(420, 210, 160, 40)
    pygame.draw.rect(WINDOW, GRAY, load_image_button)
    text = FONT_SMALL.render("Load Image", True, BLACK)
    WINDOW.blit(text, (450, 220))

    return solve_all_button, solve_row_button, solve_column_button, solve_box_button, load_image_button

def draw_window():
    WINDOW.fill(WHITE)
    draw_grid()
    draw_numbers(board)
    buttons = draw_buttons()
    pygame.display.update()
    return buttons

def extract_sudoku(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    grid = np.zeros((9, 9), dtype=int)

    for (bbox, text, prob) in result:
        if prob > 0.4:
            x, y = bbox[0]
            row, col = int(y // (image.shape[0] / 9)), int(x // (image.shape[1] / 9))
            try:
                num = int(text)
                grid[row][col] = num
            except ValueError:
                continue

    return grid

def load_image():
    Tk().withdraw()  # Prevent Tk window from appearing
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (540, 540))
        return extract_sudoku(image)
    return None

def main():
    global board  # Declare the global variable at the start of the function
    selected = None
    running = True

    while running:
        buttons = draw_window()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if buttons[0].collidepoint(pos):
                    solve_sudoku(board)
                elif buttons[1].collidepoint(pos):
                    if selected:
                        solve_row(board, selected[0])
                elif buttons[2].collidepoint(pos):
                    if selected:
                        solve_column(board, selected[1])
                elif buttons[3].collidepoint(pos):
                    if selected:
                        solve_box(board, selected[0] - selected[0] % 3, selected[1] - selected[1] % 3)
                elif buttons[4].collidepoint(pos):
                    new_board = load_image()
                    if new_board is not None:
                        board = new_board  # Update the global variable
                else:
                    x, y = pos[1] // (HEIGHT // 9), pos[0] // (WIDTH // 9)
                    selected = (x, y)
            if event.type == pygame.KEYDOWN:
                if selected:
                    if event.key == pygame.K_1: board[selected[0]][selected[1]] = 1
                    if event.key == pygame.K_2: board[selected[0]][selected[1]] = 2
                    if event.key == pygame.K_3: board[selected[0]][selected[1]] = 3
                    if event.key == pygame.K_4: board[selected[0]][selected[1]] = 4
                    if event.key == pygame.K_5: board[selected[0]][selected[1]] = 5
                    if event.key == pygame.K_6: board[selected[0]][selected[1]] = 6
                    if event.key == pygame.K_7: board[selected[0]][selected[1]] = 7
                    if event.key == pygame.K_8: board[selected[0]][selected[1]] = 8
                    if event.key == pygame.K_9: board[selected[0]][selected[1]] = 9
                    if event.key == pygame.K_BACKSPACE: board[selected[0]][selected[1]] = 0

    pygame.quit()

if __name__ == "__main__":
    main()
