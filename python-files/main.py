import numpy as np
import time
from sys import exit
from chess import *
from LCE import *

def find_positions(board, depth):
    if depth <= 0:
        return 1
    moves = movegen(board)
    count = 0
    for move in moves:
        if move[0] == 0 and move[1] == 0 and move[2] == 0 and move[3] == 0: break
        make_move(board, move)
        if not check_for_check(board, ~board[8][1] & 0b00000001):
            count += find_positions(board, depth - 1)
        unmake_move(board, move)
    return count

if __name__ == "__main__":
    # This spaghetti code abomination of a ui is just temporary

    board = starting_board()
    move_history = []
    play = input("Play?: ")
    if play == "y":
        print_board(board)
        while True:
            if len(move_history) > 0:
                u = input("Make move, undo, or let the AI play? (m, u, or a): ")
                if u == "u":
                    unmake_move(board, move_history[-1])
                    move_history.pop()
                    print()
                    print_board(board)
                    continue
                if u == "a":
                    move = find_move(board)
                    make_move(board, move)
                    move_history.append(move)
                    print()
                    print_board(board)
                    continue
            else:
                u = input("Make move, or let the AI play? (m, or a): ")
                if u == "a":
                    move = find_move(board)
                    make_move(board, move)
                    move_history.append(move)
                    print()
                    print_board(board)
                    continue

            try:
                x = int(input("x: "))
                y = int(input("y: "))
                nx = int(input("nx: "))
                ny = int(input("ny: "))
            except:
                print("Invalid")
                continue

            moves = movegen(board)

            legal = False
            count = 0
            index = 0
            move_index = 0
            for move in moves:
                if (move[0] == x and
                    move[1] == y and
                    move[2] == nx and
                    move[3] == ny):
                    move_index = index
                    count += 1
                    legal = True
                index += 1

            if legal:
                if count > 1:
                    promotion_piece = int(input("Promote pawn to what piece?: "))
                    legal = False
                    for move in moves:
                        if (move[0] == x and
                            move[1] == y and
                            move[2] == nx and
                            move[3] == ny and
                            move[12] == promotion_piece):
                            make_move(board, move)
                            if check_for_check(board, ~board[8][1] & 0b00000001): unmake_move(board, move)
                            else: legal = True
                            break
                    if legal:
                        move_history.append(move)
                    else:
                        print()
                        print("Not legal")
                else:
                    legal = False
                    make_move(board, moves[move_index])
                    if check_for_check(board, ~board[8][1] & 0b00000001): unmake_move(board, moves[move_index])
                    else: legal = True
                    if legal:
                        move_history.append(moves[move_index])
                    else:
                        print()
                        print("Not legal")
            else:
                print()
                print("Not legal")

            print()
            print_board(board)
    else:
        print(find_positions(board, 1))
        print(find_positions(board, 2))
        start = time.time()
        print(find_positions(board, 3))
        end = time.time()
        print(end - start)
        print_board(board)