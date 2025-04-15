from numba.cpython.randomimpl import double

import moves as mv
import chess_functions as cf
import evaluation as ev
from random import randint
from time import time

from moves import knight_moves, rook_moves


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
            self.__setattr__("en_passants", 0b1 << self.board_sqrs_dict[en_passant_fen])

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

    def find_moves(self):
        self.pawn_moves()
        self.king_moves()
        self.knight_moves()
        self.bishop_moves()
        self.rook_moves()
        self.queen_moves()
        pass

    def pawn_moves(self):
        not_hfile = 0b1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110
        not_afile = 0b0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111

        move_list=self.move_list

        if self.white_turn:
            pawns = self.piece_bitboards.w_pawn
            for _ in range(pawns.bit_count()):
                pointer = 0b1<<(pawns.bit_length()-1)

                # pawn pushes incl double pawn push
                if (pawn_push:= pointer<<8) & self.piece_bitboards.total_bitboard ==0:
                    if ((double_push:= pawn_push<<8) & self.piece_bitboards.total_bitboard ==0) and pointer.bit_length()<=16:
                        move_list.append(double_push|pointer)
                    elif pointer.bit_length()>48:
                        for i in range(4):
                            move_list.append(pawn_push|pointer|0x10000<<(i))
                    move_list.append(pawn_push|pointer)

                #pawn captures right
                if (pawn_cap_right:= pointer<<7) & (self.piece_bitboards.b_bitboard|self.en_passants) != 0 and pointer&not_hfile!=0:
                    if pointer.bit_length()>49:
                        for i in range(4):
                            move_list.append(pawn_cap_right|pointer|0x10000<<(i))
                    move_list.append(pawn_cap_right|pointer)

                #pawn captures left
                if (pawn_cap_left:= pointer<<9) & (self.piece_bitboards.b_bitboard|self.en_passants) != 0 and pointer&not_afile!=0:
                    if pointer.bit_length()>48:
                        for i in range(4):
                            move_list.append(pawn_cap_left|pointer|0x10000<<(i))
                    move_list.append(pawn_cap_left|pointer)
                pawns^=pointer

        else:
            pawns = self.piece_bitboards.b_pawn
            for _ in range(pawns.bit_count()):
                pointer = 0b1 << (pawns.bit_length() - 1)
                # pawn pushes incl double pawn push
                if (pawn_push := pointer >> 8) & self.piece_bitboards.total_bitboard == 0:
                    if (( double_push := pawn_push >> 8) & self.piece_bitboards.total_bitboard == 0) and pointer.bit_length() > 48:
                        move_list.append(double_push|pointer)
                    elif pointer.bit_length()<=16:
                        for i in range(4):
                            move_list.append(pawn_push | pointer | 0x10000 << (i))
                    move_list.append(pawn_push|pointer)

                # pawn captures right
                if (pawn_cap_right := pointer >> 9) & (
                        self.piece_bitboards.w_bitboard | self.en_passants) != 0 and pointer & not_hfile != 0:
                    if pointer.bit_length()<=16:
                        for i in range(4):
                            move_list.append(pawn_cap_right | pointer | 0x10000 << (i))
                    move_list.append(pawn_cap_right | pointer)

                # pawn captures left
                if (pawn_cap_left := pointer >> 7) & (self.piece_bitboards.w_bitboard | self.en_passants) != 0 and pointer & not_afile != 0:
                    if pointer.bit_length()<=16:
                        for i in range(4):
                            move_list.append(pawn_cap_left | pointer | 0x10000 << (i))
                    move_list.append(pawn_cap_left | pointer)
                pawns ^= pointer

    def king_moves(self):
        not_hfile = 0b1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110
        not_afile = 0b0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111
        not_8th_rank = (0b1<<56)-1
        not_1st_rank = (0b1<<8)-1

        king_castle = 0b110
        queen_castle = 0b1110000

        move_list = self.move_list


        if self.white_turn:
            kr = self.piece_bitboards.w_king & not_hfile
            kl = self.piece_bitboards.w_king & not_afile
            kup = self.piece_bitboards.w_king & not_8th_rank
            kd = self.piece_bitboards.w_king & not_1st_rank

            moves = []
            moves.append(kup&kl | (kup&kl)<<9 & ~self.piece_bitboards.w_bitboard)
            moves.append(kup | kup<<8 &~self.piece_bitboards.w_bitboard)
            moves.append(kup&kr | (kup&kr)<<7 &~self.piece_bitboards.w_bitboard)
            moves.append(kl | kl<<1 &~self.piece_bitboards.w_bitboard)
            moves.append(kr | kr>>1 &~self.piece_bitboards.w_bitboard)
            moves.append(kd & kl | (kd & kl) >>7 & ~self.piece_bitboards.w_bitboard)
            moves.append(kd | kd >> 8 & ~self.piece_bitboards.w_bitboard)
            moves.append(kd & kr | (kd & kr) >>9 & ~self.piece_bitboards.w_bitboard)

            for move in moves:
                if move.bit_count()==2:
                    move_list.append(move)

            if 0b1000&self.castle_rights!=0 and king_castle&self.piece_bitboards.total_bitboard==0:
                move_list.append(0b1000)
            if 0b100&self.castle_rights!=0 and queen_castle&self.piece_bitboards.total_bitboard==0:
                move_list.append(0b100)

        else:
            kr = self.piece_bitboards.b_king & not_hfile
            kl = self.piece_bitboards.b_king & not_afile
            kup = self.piece_bitboards.b_king & not_8th_rank
            kd = self.piece_bitboards.b_king & not_1st_rank

            moves = []
            moves.append(kup & kl | (kup & kl) << 9 & ~self.piece_bitboards.b_bitboard)
            moves.append(kup | kup << 8 & ~self.piece_bitboards.b_bitboard)
            moves.append(kup & kr | (kup & kr) << 7 & ~self.piece_bitboards.b_bitboard)
            moves.append(kl | kl << 1 & ~self.piece_bitboards.b_bitboard)
            moves.append(kr | kr >> 1 & ~self.piece_bitboards.b_bitboard)
            moves.append(kd & kl | (kd & kl) >> 7 & ~self.piece_bitboards.b_bitboard)
            moves.append(kd | kd >> 8 & ~self.piece_bitboards.b_bitboard)
            moves.append(kd & kr | (kd & kr) >> 9 & ~self.piece_bitboards.b_bitboard)

            for move in moves:
                if move.bit_count() == 2:
                    move_list.append(move)

            if 0b10 & self.castle_rights != 0 and king_castle<<56 & self.piece_bitboards.total_bitboard == 0:
                move_list.append(0b10)
            if 0b1 & self.castle_rights != 0 and queen_castle<<56 & self.piece_bitboards.total_bitboard == 0:
                move_list.append(0b1)

    def knight_moves(self):
        not_hfile = 0b1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110
        not_afile = 0b0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111
        not_ghfile = 0b1111_1100_1111_1100_1111_1100_1111_1100_1111_1100_1111_1100_1111_1100_1111_1100
        not_abfile = 0b0011_1111_0011_1111_0011_1111_0011_1111_0011_1111_0011_1111_0011_1111_0011_1111
        not_8th_rank = (0b1 << 56) - 1
        not_78_rank = (0b1 << 48) - 1

        move_list = self.move_list

        if self.white_turn:
            piece = self.piece_bitboards.w_knight
        else:
            piece = self.piece_bitboards.b_knight

        for _ in range(piece.bit_count()):
            i = (piece.bit_length() - 1)
            pointer = 0b1 << (i)

            move1 = (pointer & not_hfile) | (((pointer) >> 17) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                    else self.piece_bitboards.b_bitboard))
            move2 = (pointer & not_afile) | (((pointer) >> 15) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                    else self.piece_bitboards.b_bitboard))
            move3 = (pointer & not_abfile) | (((pointer) >> 6) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                    else self.piece_bitboards.b_bitboard))
            move4 = (pointer & not_abfile & not_8th_rank) | ((pointer << 10) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                    else self.piece_bitboards.b_bitboard))
            move5 = (pointer & not_afile & not_78_rank) | ((pointer << 17) & ~(self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard))
            move6 = (pointer & not_hfile & not_78_rank) | ((pointer<< 15) & ~(self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard))
            move7 = (pointer & not_ghfile & not_8th_rank) | ((pointer << 6) & ~(self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard))
            move8 = (pointer & not_ghfile) | (((pointer ) >> 10) & ~(self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard))

            if move1.bit_count() == 2:
                move_list.append(move1)
            if move2.bit_count() == 2:
                move_list.append(move2)
            if move3.bit_count() == 2:
                move_list.append(move3)
            if move4.bit_count() == 2:
                move_list.append(move4)
            if move5.bit_count() == 2:
                move_list.append(move5)
            if move6.bit_count() == 2:
                move_list.append(move6)
            if move7.bit_count() == 2:
                move_list.append(move7)
            if move8.bit_count() == 2:
                move_list.append(move8)
            piece ^= pointer

    def bishop_moves(self, piece_type="bishop"):
        not_hfile = 0b1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110
        not_afile = 0b0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111
        not_8th_rank = (0b1 << 56) - 1
        not_1st_rank = ~(0b1 << 8) - 1

        move_list = self.move_list

        if self.white_turn:
            piece = self.piece_bitboards.__getattribute__("w_"+piece_type)
        else: piece = self.piece_bitboards.__getattribute__("b_"+piece_type)

        for _ in range(piece.bit_count()):
            i = (piece.bit_length() - 1)
            pointer = 0b1<<(i)


            counter_1 = min(i % 8, i // 8)
            counter_2 = min(i % 8, 7 - i // 8)
            counter_3 = min(7 - i % 8, i // 8)
            counter_4 = min(7 - i % 8, 7 - i // 8)

            tr = pointer
            tl = pointer
            br = pointer
            bl = pointer

            for j in range(max(counter_1, counter_2, counter_3, counter_4)):
                tr = ((tr & not_hfile & not_8th_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                                        else self.piece_bitboards.w_bitboard)) << 7) & ~(
                    self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard)

                tl = ((tl & not_afile & not_8th_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                                        else self.piece_bitboards.w_bitboard)) << 9) & ~(
                    self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard)

                br = ((br & not_hfile & not_1st_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                                        else self.piece_bitboards.w_bitboard)) >> 9) & ~(
                    self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard)

                bl = ((bl & not_afile & not_1st_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                                        else self.piece_bitboards.w_bitboard)) >> 7) & ~(
                    self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard)

                move_tr = pointer | tr
                move_tl = pointer | tl
                move_br = pointer | br
                move_bl = pointer | bl

                if move_tr.bit_count() == 2:
                    move_list.append(move_tr)
                if move_tl.bit_count() == 2:
                    move_list.append(move_tl)
                if move_br.bit_count() == 2:
                    move_list.append(move_br)
                if move_bl.bit_count() == 2:
                    move_list.append(move_bl)

            piece ^= pointer

    def rook_moves(self, piece_type="rook"):
        not_hfile = 0b1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110_1111_1110
        not_afile = 0b0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111_0111_1111
        not_8th_rank = (0b1 << 56) - 1
        not_1st_rank = ~(0b1 << 8) - 1

        move_list = self.move_list

        if self.white_turn:
            piece = self.piece_bitboards.__getattribute__("w_" + piece_type)
        else:
            piece = self.piece_bitboards.__getattribute__("b_" + piece_type)

        for _ in range(piece.bit_count()):
            i = (piece.bit_length() - 1)
            pointer = 0b1<<(i)

            tp = pointer
            bt = pointer
            rt = pointer
            lt = pointer
            counter_1 = max(i % 8, i // 8)
            counter_2 = max(i % 8, 7 - i // 8)
            counter_3 = max(7 - i % 8, i // 8)
            counter_4 = max(7 - i % 8, 7 - i // 8)


            for j in range(max(counter_1,counter_2,counter_3,counter_4)):
                tp = ((tp & not_8th_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                            else self.piece_bitboards.w_bitboard)) << 8) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                                    else self.piece_bitboards.b_bitboard)
                top = pointer | tp

                bt = ((bt & not_1st_rank & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                            else self.piece_bitboards.w_bitboard)) >> 8) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                                    else self.piece_bitboards.b_bitboard)
                bot = pointer | bt

                rt = ((rt & not_hfile  & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                            else self.piece_bitboards.w_bitboard)) >> 1) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                                    else self.piece_bitboards.b_bitboard)
                right = pointer | rt

                lt = ((lt & not_afile & ~(self.piece_bitboards.b_bitboard if self.white_turn
                                            else self.piece_bitboards.w_bitboard)) <<1) & ~(self.piece_bitboards.w_bitboard if self.white_turn
                                                                                    else self.piece_bitboards.b_bitboard)
                left = pointer | lt

                if top.bit_count()==2:
                    move_list.append(top)
                if bot.bit_count()==2:
                    move_list.append(bot)
                if right.bit_count()==2:
                    move_list.append(right)
                if left.bit_count()==2:
                    move_list.append(left)
            piece ^= pointer

    def queen_moves(self):
        self.bishop_moves(piece_type="queen")
        self.rook_moves(piece_type="queen")

    def _make_move(self, move: int):
        pass

    def make_move(self, **kwargs):
        try:
            move = kwargs["move"]

            if type(move) == int:
                move_bit_board = move
            elif move == "0-0":
                move_bit_board = 0b1000 if self.white_turn else 0b10
                if move_bit_board not in self.move_list:
                    print("Error: not a valid move")
                    return False
            elif move == "0-0-0":
                move_bit_board = 0b100 if self.white_turn else 0b1
                if move_bit_board not in self.move_list:
                    print("Error: not a valid move")
                    return False

            #regular moves
            elif move.__len__()==4:
                move_bit_board = 0b1 << self.board_sqrs_dict[move[:2]] | 0b1 << self.board_sqrs_dict[move[2:]]
                if move_bit_board not in self.move_list:
                    print("Error: not a valid move")
                    return False

            #promotions
            elif move.__len__() == 5:
                move_bit_board = 0b1 << self.board_sqrs_dict[move[:2]] | 0b1 << self.board_sqrs_dict[move[2:4]]
                if move[-1] == "Q":
                    move_bit_board |= 0x10000
                elif move[-1] == "R":
                    move_bit_board |= 0x10000<<(1)
                elif move[-1] == "N":
                    move_bit_board |= 0x10000<<(2)
                elif move[-1] == "B":
                    move_bit_board |= 0x10000<<(3)
                else:
                    print("Error: not a valid move")
                    return False
        except:
            return False

        self._make_move(move_bit_board)
        return True

    def rev_bits(self, bit):  ## dont ask me how this works, but it reverses the bits
        bit = (bit * 0x0202020202 & 0x010884422010) % 1023
        return bit

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
new_game.set_game_state_from_fen(fen=fen)
new_game.grid_renderer.render_grid(new_game.piece_bitboards)
t1 = time()
new_game.find_moves()
t2 = time()

print("###!!3")
for move in new_game.move_list:
    print(bin(move))


print(new_game.move_list.__len__())
print(t2-t1)


