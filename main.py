import chess_functions as cf
import moves as mv
from time import time

# Starting fen
FEN_start = ('rnbqkbnr/pppppppp/8/4Q3/8/8/PPPPPPPP/RNB1KBNR w KQkq h6 0 0')


#board_info[0], board_info[1], board_info[2], board_info[3], half_moves, full_moves 
Piece_bitboard_list, player, castle_rights_bitboard, enpassant_bitboard, half_moves, full_moves=cf.get_bitboards_and_other_stuff(FEN_start)
# print(Piece_bitboard_list)
move_list:list = []
board_info = [Piece_bitboard_list, player, castle_rights_bitboard, enpassant_bitboard, half_moves, full_moves, move_list] #pawn_push,pawn_capture,king,knight,bishop,rook,queen

t=[]

cf.make_grid(board_info)
t_1= time()
board_info = mv.update_board_info(board_info)

# board_info=cf.move(move, board_info)
# board_info[1]=not board_info[1]
t_2 = time()
cf.make_grid(board_info)
print(cf.eval(board_info))


print(t_2-t_1,board_info[1])
