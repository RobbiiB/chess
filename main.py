import chess_functions as cf
import moves as mv
import evaluation as ev
import engine as eg
from time import time

if __name__ == '__main__':
    # Starting fen
    FEN_start = ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0')


    #board_info[0], board_info[1], board_info[2], board_info[3], half_moves, full_moves
    Piece_bitboard_list, player, castle_rights_bitboard, enpassant_bitboard, half_moves, full_moves=cf.get_bitboards_and_other_stuff(FEN_start)
    # print(Piece_bitboard_list)
    move_list:list = []
    promotion_moves = []
    board_info = [Piece_bitboard_list, player, castle_rights_bitboard, enpassant_bitboard, half_moves, full_moves, move_list, promotion_moves] #pawn_push,pawn_capture,king,knight,bishop,rook,queen

    t=[]

    #%%
    cf.make_grid(board_info)
    for q in range(2):
        t_1= time()
        board_info = mv.update_board_info(board_info)

        move = eg.select_move(board_info)
        board_info = mv.make_move(board_info, move=move)
        # board_info[1]=not board_info[1]
        t_2 = time()
        cf.make_grid(board_info)
        print(f"eval: {ev.eval(board_info)}")

        print(f"turn: {q+1}")
        t.append(t_2-t_1)
        # print(t[-1])

    #%%
    print(t)

    print(max(t))
    print(min(t))
    print(sum(t)/t.__len__())

    #0b10000000000000001000000000000000
    #0b10000000000000001000000000000000