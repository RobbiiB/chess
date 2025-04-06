import moves as mv
import chess_functions as cf
import evaluation as ev
from random import randint
from time import time

from moves import knight_moves


class Game():
    def __init__(self):
        self.white_turn: bool = True ##True for white, false for black
        self.half_moves: int = 0
        self.full_moves: int = 0
        self.castle_rights: int = 0 ##Castle possibiities
        self.en_passants: int = 0 ##en passant squares
        self.move_list: list(int) = [] ##valid moves
        self.piece_bitboards: Piece_Bitboards = Piece_Bitboards()
        self.board_sqrs_dict: dict = {
            "a8": 63, "b8": 62, "c8": 61, "d8": 60, "e8": 59, "f8": 58, "g8": 57, "h8": 56,
            "a7": 55, "b7": 54, "c7": 53, "d7": 52, "e7": 51, "f7": 50, "g7": 49, "h7": 48,
            "a6": 47, "b6": 46, "c6": 45, "d6": 44, "e6": 43, "f6": 42, "g6": 41, "h6": 40,
            "a5": 39, "b5": 38, "c5": 37, "d5": 36, "e5": 35, "f5": 34, "g5": 33, "h5": 32,
            "a4": 31, "b4": 30, "c4": 29, "d4": 28, "e4": 27, "f4": 26, "g4": 25, "h4": 24,
            "a3": 23, "b3": 22, "c3": 21, "d3": 20, "e3": 19, "f3": 18, "g3": 17, "h3": 16,
            "a2": 15, "b2": 14, "c2": 13, "d2": 12, "e2": 11, "f2": 10, "g2": 9, "h2": 8,
            "a1": 7, "b1": 6, "c1": 5, "d1": 4, "e1": 3, "f1": 2, "g1": 1, "h1": 0
        }
        self.inv_board_sqrs_dict: dict = dict(zip(self.board_sqrs_dict.values(), self.board_sqrs_dict.keys()))

        self.castle_dict: dict = {
                                "K": 0b1000,
                                "Q": 0b0100,
                                "k": 0b0010,
                                "q": 0b0001,
                                0b1000: "O-O",
                                0b0100: "O-O-O",
                                0b0010: "O-O",
                                0b0001: "O-O-O"
                            }
        self.grid_renderer: Grid_Renderer = Grid_Renderer()

    def _set_en_passants_from_fen(self, en_passant_fen: str):
        if en_passant_fen != "-":
            self.__setattr__("en_passants", 0b1 >> self.board_sqrs_dict[en_passant_fen])

    def _set_half_moves_from_fen(self, half_move_fen: str):
        try:
            self.__setattr__("half_moves",int(half_move_fen))
        except:
            print("Something went wrong")

    def _set_full_moves_from_fen(self, full_move_fen: str):
        try:
            self.__setattr__("full_moves", int(full_move_fen))
        except:
            print("Something went wrong")

    def _set_castle_rights_from_fen(self, castle_right_fen: str):
        for element in castle_right_fen:
            self.__setattr__("castle_rights", self.__getattribute__("castle_rights") | self.castle_dict[element])

    def _set_player_from_fen(self, player_fen: str):
        self.__setattr__("white_turn", player_fen == "w")

    def _set_bitboards_from_fen(self, board_fen: str):
        inv_piece_bitboard_dict_list = {
            'p': "b_pawn",
            'r': "b_rook",
            'n': "b_knight",
            'b': "b_bishop",
            'q': "b_queen",
            'k': "b_king",
            'P': "w_pawn",
            'R': "w_rook",
            'N': "w_knight",
            'B': "w_bishop",
            'Q': "w_queen",
            'K': "w_king"
        }
        bit_adder = 0b1<<63
        for element in board_fen:
            if element == "/":
                pass
            else:
                try:
                    i = int(element)
                    bit_adder = bit_adder >> i
                except:
                    self.piece_bitboards.__setattr__(
                        inv_piece_bitboard_dict_list[element],
                        self.piece_bitboards.__getattribute__(inv_piece_bitboard_dict_list[element])| bit_adder
                        )
                    bit_adder = bit_adder >> 1

    def set_game_state_from_fen(self, fen: str):
        board_fen, player_fen, castle_rights_fen, en_passant_fen, half_move_fen, full_move_fen = fen.split(" ")

        self._set_en_passants_from_fen(en_passant_fen=en_passant_fen)
        self._set_half_moves_from_fen(half_move_fen=half_move_fen)
        self._set_full_moves_from_fen(full_move_fen=full_move_fen)
        self._set_castle_rights_from_fen(castle_right_fen=castle_rights_fen)
        self._set_player_from_fen(player_fen=player_fen)
        self._set_bitboards_from_fen(board_fen=board_fen)
        self.piece_bitboards.update_bitboards()



    def num_to_move(self, move_idx)->str:
        move_num = self.move_list[move_idx]

        if move_num.bit_count()==1:
            move = "0-0" if self.castle_dict[move_num]==("K" or "k") else "0-0-0"

        elif move_num.bit_count()==2:
            firstpart = (self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard) & move_num
            move = self.inv_board_sqrs_dict[firstpart]
            move += self.inv_board_sqrs_dict[firstpart^move_num]

        elif move_num.bit_count()==3:
            piece_list = ["R", "N", "B", "Q"]

            """
            Since the last part can only be perfect powers of two the bit_length, is equal to the exponent +17 of last 
            part. Neat little trick. The rest of the number is then matched with the color bitboards to find the 
            starting square.
            """
            promotion_part = (move_num>>16 & 0b1111)
            last_part = promotion_part.bit_length()-1


            move_num = move_num & ~(promotion_part<<16)
            first_part = (self.piece_bitboards.w_pawn if self.white_turn else self.piece_bitboards.b_pawn) & move_num


            second_part = move_num & ~first_part
            move = self.inv_board_sqrs_dict[first_part] + self.inv_board_sqrs_dict[second_part] + piece_list[last_part]
        return move

    def move_to_num(self, move: str):
        if move == "0-0":
            move_num = self.castle_dict["K" if self.white_turn else "k"]
        elif move == "0-0-0":
            move_num = self.castle_dict["Q" if self.white_turn else "q"]
        elif move.__len__()==4:
            move_num = self.board_sqrs_dict[move[:2]] | self.board_sqrs_dict[move[2:]]
        elif move.__len__()==5:
            piece_list = ["R", "N", "B", "Q"]
            move_num = (self.board_sqrs_dict[move[:2]] |
                        self.board_sqrs_dict[move[2:4]] |
                        (0b10000000000000000 << piece_list.index(move[-1])))
        else:
            print("something went wrong")
        return move_num

class Piece_Bitboards():
    def __init__(self):
        self.w_pawn: int = 0
        self.b_pawn: int = 0
        self.w_rook: int = 0
        self.b_rook: int = 0
        self.w_knight: int = 0
        self.b_knight: int = 0
        self.w_bishop: int = 0
        self.b_bishop: int = 0
        self.w_queen: int = 0
        self.b_queen: int = 0
        self.w_king: int = 0
        self.b_king: int = 0
        self.w_bitboard: int = self.w_pawn | self.w_rook | self.w_knight | self.w_bishop | self.w_queen | self.w_king
        self.b_bitboard: int = self.b_pawn | self.b_rook | self.b_knight | self.b_bishop | self.b_queen | self.b_king
        self.total_bitboard: int = self.w_bitboard | self.b_bitboard
        self.piece_names: list(str) = ["w_pawn", "b_pawn", "w_rook", "b_rook", "w_knight", "b_knight", "w_bishop",
                                    "b_bishop", "w_queen", "b_queen", "w_king", "b_king"]

    def update_bitboards(self):
        self.__setattr__("w_bitboard", self.w_pawn | self.w_rook | self.w_knight | self.w_bishop | self.w_queen | self.w_king)
        self.__setattr__("b_bitboard", self.b_pawn | self.b_rook | self.b_knight | self.b_bishop | self.b_queen | self.b_king)
        self.__setattr__("total_bitboard", self.w_bitboard | self.b_bitboard)

class Grid_Renderer():
    def __init__(self):
        self.grid: list(list)|None = None

    def create_grid(self, piece_bitboards: Piece_Bitboards):
        grid = [
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
            ["|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |", "|   |"],
        ]

        piece_bitboard_dict_list = {
            "b_pawn": 'p',
            "b_rook": 'r',
            "b_knight": 'n',
            "b_bishop": 'b',
            "b_queen": 'q',
            "b_king": 'k',
            "w_pawn": 'P',
            "w_rook": 'R',
            "w_knight": 'N',
            "w_bishop": 'B',
            "w_queen": 'Q',
            "w_king": 'K'
        }



        bit_adder = 0b1000000000000000000000000000000000000000000000000000000000000000

        for i in range(64):
            if piece_bitboards.total_bitboard & bit_adder != 0:
                for name in piece_bitboards.piece_names:
                    if bit_adder & piece_bitboards.__getattribute__(name)!=0:
                        new_piece = "| " + piece_bitboard_dict_list[name] + " |"
                        grid[i // 8][i % 8] = new_piece
                        break
            bit_adder = bit_adder >> 1

        self.grid = grid

    def render_grid(self, piece_bitboards: Piece_Bitboards):
        self.create_grid(piece_bitboards)
        # making the chessboard, might add the numbers and letters idk yet
        print("+---++---++---++---++---++---++---++---+")
        print("\n+---++---++---++---++---++---++---++---+\n".join(["".join(row) for row in self.grid]))
        print("+---++---++---++---++---++---++---++---+")
        self.grid = None

new_game = Game()

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0'
t1 = time()
new_game.set_game_state_from_fen(fen=fen)
new_game.grid_renderer.render_grid(new_game.piece_bitboards)
t2 = time()

print(t2-t1)

