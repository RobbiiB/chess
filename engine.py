import moves as mv
import chess_functions as cf
import evaluation as ev
from random import randint


def move_choice_NegaMax(board_info:list)->int:
    max = -float("inf")
    move_idx=0
    for i in range(2):
        boardstate = board_info[:]
        boardstate = mv.make_move(boardstate, move=boardstate[6][i])
        boardstate[1] = not boardstate[1]
        cf.make_grid(boardstate)
        score = ev.eval(boardstate)
        print(score)
        del boardstate
        if score > max:
            max = score
            move_idx = i

    return move_idx



def random_move(board_info):
    move_idx = randint(0, len(board_info[6])-1)
    return move_idx

def select_move(board_info:list):
    move_idx = random_move(board_info)
    # move_idx = move_choice_NegaMax(board_info)
    return move_idx