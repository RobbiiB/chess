import numpy as np

import moves as mv
import chess_functions as cf
import evaluation as ev
from random import random
from copy import deepcopy
from time import time
import subprocess

from moves import knight_moves, rook_moves


class Game_state():
    def __init__(self):
        self.white_turn: bool = True ##True for white, false for black
        self.half_moves: int = 0
        self.full_moves: int = 0
        self.castle_rights: int = 0 ##Castle possibiities
        self.en_passants: int = 0 ##en passant squares
        self.move_list: list[int] = [] ##valid moves
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

    def copy(self, memodict=None):
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

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
        if castle_right_fen != "-":
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

    def num_to_move(self, move)->str:
        move_num = move

        if move_num.bit_count()==1:
            move = "O-O" if self.castle_dict[move_num]==("K" or "k") else "O-O-O"

        elif move_num.bit_count()==2:
            firstpart = (self.piece_bitboards.w_bitboard if self.white_turn else self.piece_bitboards.b_bitboard) & move_num

            move = self.inv_board_sqrs_dict[firstpart.bit_length()-1]
            move += self.inv_board_sqrs_dict[(firstpart^move_num).bit_length()-1]

        elif move_num.bit_count()==3:
            print(bin(move_num))
            piece_list = ["Q", "R", "N", "B"]

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
            move = self.inv_board_sqrs_dict[first_part.bit_length()-1] + self.inv_board_sqrs_dict[second_part.bit_length()-1] + piece_list[last_part]
        return move

    def move_to_num(self, move: str):
        if move == "O-O":
            move_num = self.castle_dict["K" if self.white_turn else "k"]
        elif move == "O-O-O":
            move_num = self.castle_dict["Q" if self.white_turn else "q"]
        elif move.__len__()==4:
            move_num = (0b1<<self.board_sqrs_dict[move[:2]]) | (0b1<<self.board_sqrs_dict[move[2:]])
        elif move.__len__()==5:
            piece_list = [ "Q", "R", "N", "B"]
            move_num = ((0b1<<self.board_sqrs_dict[move[:2]]) |
                        (0b1<<self.board_sqrs_dict[move[2:4]]) |
                        (0b1_00000000_00000000 << piece_list.index(move[-1])))
        else:
            print("something went wrong")
        return move_num

    def num_to_alg(self, move:int):
        if move.bit_count()==1:
            alg = self.castle_dict[move]
        elif move.bit_count()==2:
            for i in range(6):
                name = self.piece_bitboards.piece_names[2*i+ (0 if self.white_turn else 1)]
                if move&self.piece_bitboards.__getattribute__(name)!=0:
                    if "pawn" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = coordinate_move[:1]+"x"+coordinate_move[2:]
                        else:
                            alg = self.num_to_move(move)[2:]
                    elif "king" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = "Kx"+coordinate_move[2:]
                        else:
                            coordinate_move = self.num_to_move(move)
                            alg = "K" + coordinate_move[2:]
                    elif "queen" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = "Q"+coordinate_move[:2]+"x"+coordinate_move[2:]
                        else:
                            coordinate_move = self.num_to_move(move)
                            alg = "Q"+coordinate_move[:2]+coordinate_move[2:]
                    elif "rook" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = "R"+coordinate_move[:2]+"x"+coordinate_move[2:]
                        else:
                            coordinate_move = self.num_to_move(move)
                            alg = "R"+coordinate_move[:2]+coordinate_move[2:]
                    elif "knight" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = "N"+coordinate_move[:2]+"x"+coordinate_move[2:]
                        else:
                            coordinate_move = self.num_to_move(move)
                            alg = "N"+coordinate_move[:2]+coordinate_move[2:]
                    elif "bishop" in name:
                        if move&self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard")!=0:
                            coordinate_move = self.num_to_move(move)
                            alg = "B"+coordinate_move[:2]+"x"+coordinate_move[2:]
                        else:
                            coordinate_move = self.num_to_move(move)
                            alg = "B"+coordinate_move[:2]+coordinate_move[2:]
        elif move.bit_count()==3:
            piece_list = ["Q", "R", "N", "B"]
            promotion_part = (move >> 16 & 0b1111)
            last_part = promotion_part.bit_length() - 1
            piece = piece_list[last_part]
            if move & self.piece_bitboards.__getattribute__("b_bitboard" if self.white_turn else "w_bitboard") != 0:
                coordinate_move = self.num_to_move(move)
                alg = coordinate_move[:1] + "x" + coordinate_move[2:4] +"=" + piece
            else:
                alg = self.num_to_move(move)[2:4] +"=" + piece
        else: alg = ""
        return alg





    def find_moves(self):
        self.move_list = []
        self.pawn_moves()
        self.king_moves()
        self.knight_moves()
        self.bishop_moves()
        self.rook_moves()
        self.queen_moves()

        order=[]
        for move in self.move_list:
            if move&self.piece_bitboards.b_bitboard:
                order.append(1)
            elif move&self.piece_bitboards.w_bitboard:
                order.append(-1)
            else:
                order.append(0)

        zip_moves = sorted(zip(order,self.move_list))
        sorted_moves = [move for order,move in zip_moves]
        self.__setattr__("move_list", sorted_moves)


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
        not_1st_rank = ~(0b1<<8)-1

        king_castle = 0b110
        queen_castle = 0b1110000

        move_list = self.move_list


        if self.white_turn:
            kr = self.piece_bitboards.w_king & not_hfile
            kl = self.piece_bitboards.w_king & not_afile
            kup = self.piece_bitboards.w_king & not_8th_rank
            kd = self.piece_bitboards.w_king & not_1st_rank

            moves = []
            moves.append((kup&kl) | ((kup&kl)<<9 & ~self.piece_bitboards.w_bitboard))
            moves.append(kup | (kup<<8 &~self.piece_bitboards.w_bitboard))
            moves.append((kup&kr) | ((kup&kr)<<7 &~self.piece_bitboards.w_bitboard))
            moves.append(kl | (kl<<1 &~self.piece_bitboards.w_bitboard))
            moves.append(kr | (kr>>1 &~self.piece_bitboards.w_bitboard))
            moves.append((kd & kl) | ((kd & kl) >>7 & ~self.piece_bitboards.w_bitboard))
            moves.append(kd | (kd >> 8 & ~self.piece_bitboards.w_bitboard))
            moves.append((kd & kr) | ((kd & kr) >>9 & ~self.piece_bitboards.w_bitboard))

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
            moves.append((kup & kl) | ((kup & kl) << 9 & ~self.piece_bitboards.b_bitboard))
            moves.append(kup | (kup << 8 & ~self.piece_bitboards.b_bitboard))
            moves.append((kup & kr) | ((kup & kr) << 7 & ~self.piece_bitboards.b_bitboard))
            moves.append(kl | (kl << 1 & ~self.piece_bitboards.b_bitboard))
            moves.append(kr | (kr >> 1 & ~self.piece_bitboards.b_bitboard))
            moves.append((kd & kl) | ((kd & kl) >> 7 & ~self.piece_bitboards.b_bitboard))
            moves.append(kd | (kd >> 8 & ~self.piece_bitboards.b_bitboard))
            moves.append((kd & kr) | ((kd & kr) >> 9 & ~self.piece_bitboards.b_bitboard))

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
        if move.bit_count()==1:

            if move==0b1000:
                king = 0b10
                rook = 0b100 | (self.piece_bitboards.w_rook & ~0b1)

                self.piece_bitboards.__setattr__("w_king", king)
                self.piece_bitboards.__setattr__("w_rook", rook)

                self.__setattr__("en_passants", 0)
                self.__setattr__("castle_rights", self.castle_rights&~(0b1100))
            elif move == 0b100:
                king = 0b100000
                rook = (self.piece_bitboards.w_rook & ~0b10000000) | 0b10000

                self.piece_bitboards.__setattr__("w_king", king)
                self.piece_bitboards.__setattr__("w_rook", rook)

                self.__setattr__("en_passants", 0)
                self.__setattr__("castle_rights", self.castle_rights & ~(0b1100))
            elif move == 0b10:
                king = 0b10<<56
                rook = (0b100<<56) | (self.piece_bitboards.w_rook & ~(0b1<<56))

                self.piece_bitboards.__setattr__("b_king", king)
                self.piece_bitboards.__setattr__("b_rook", rook)

                self.__setattr__("en_passants", 0)
                self.__setattr__("castle_rights", self.castle_rights & ~(0b11))
            elif move == 0b1:
                king = 0b100000<<56
                rook = (self.piece_bitboards.w_rook & ~(0b10000000<<56)) | (0b10000<<56)

                self.piece_bitboards.__setattr__("b_king", king)
                self.piece_bitboards.__setattr__("b_rook", rook)

                self.__setattr__("en_passants", 0)
                self.__setattr__("castle_rights", self.castle_rights & ~(0b11))
        elif move.bit_count()==3:
            promo = (move&0xF0000)
            actual_move= move & ~promo
            for name in self.piece_bitboards.piece_names:
                piece = self.piece_bitboards.__getattribute__(name)
                self.piece_bitboards.__setattr__(name, piece&~actual_move)
            if promo==0x10000:
                queen = self.piece_bitboards.w_queen if self.white_turn else self.piece_bitboards.b_queen
                self.piece_bitboards.__setattr__("w_queen" if self.white_turn else "b_queen",
                                                queen|(actual_move&0xFF00_0000_0000_00FF))
            elif promo==0x20000:
                rook = self.piece_bitboards.w_rook if self.white_turn else self.piece_bitboards.b_rook
                self.piece_bitboards.__setattr__("w_rook" if self.white_turn else "b_rook",
                                                rook | (actual_move & 0xFF00_0000_0000_00FF))
            elif promo==0x40000:
                knight = self.piece_bitboards.w_knight if self.white_turn else self.piece_bitboards.b_knight
                self.piece_bitboards.__setattr__("w_knight" if self.white_turn else "b_knight",
                                                knight|(actual_move&0xFF00_0000_0000_00FF))
            else:
                bishop = self.piece_bitboards.w_bishop if self.white_turn else self.piece_bitboards.b_bishop
                self.piece_bitboards.__setattr__("w_bishop" if self.white_turn else "b_bishop",
                                                bishop | (actual_move & 0xFF00_0000_0000_00FF))
        else:
            for i in range(6):
                piece_opp = self.piece_bitboards.__getattribute__(self.piece_bitboards.piece_names[2*i +(1 if self.white_turn else 0)])
                piece_opp = piece_opp & ~move
                self.piece_bitboards.__setattr__(self.piece_bitboards.piece_names[2*i +(1 if self.white_turn else 0)], piece_opp)

            for i in range(6):
                name = self.piece_bitboards.piece_names[2*i +(0 if self.white_turn else 1)]
                if (piece:=
                self.piece_bitboards.__getattribute__(name))&move!=0:
                    piece ^= move
                    self.piece_bitboards.__setattr__(name, piece)
                    break

            if move&self.en_passants!=0:
                name = "b_pawn" if self.white_turn else "w_pawn"
                en_passant = (self.en_passants>>8) if self.white_turn else (self.en_passants<<8)
                self.piece_bitboards.__setattr__(name, self.piece_bitboards.__getattribute__(name)&~en_passant)

            self.__setattr__("en_passants", 0b0)


            if name == "w_pawn" or name == "b_pawn":
                if move&0xFF00FF00==move or move&0xFF00_FF00_0000_00==move:
                    en_passant_sqr = 0b1<<(move.bit_length()-9)
                    self.__setattr__("en_passants", en_passant_sqr)
            elif name == "w_king":
                self.__setattr__("castle_rights", self.castle_rights & ~(0b1100))
            elif name == ("b_king"):
                self.__setattr__("castle_rights", self.castle_rights & ~(0b11))
            elif name == "w_rook":
                if self.piece_bitboards.w_rook&0b1==0:
                    self.__setattr__("castle_rights", self.castle_rights & ~(0b1000))
                if self.piece_bitboards.w_rook&0b1000_0000==0:
                    self.__setattr__("castle_rights", self.castle_rights & ~(0b100))
            elif name == "b_rook":
                if self.piece_bitboards.b_rook&(0b1<<56)==0:
                    self.__setattr__("castle_rights", self.castle_rights & ~(0b10))
                if self.piece_bitboards.b_rook&(0b1000_0000<<56)==0:
                    self.__setattr__("castle_rights", self.castle_rights & ~(0b1))

    def make_move(self, **kwargs)->bool:
        try:
            move = kwargs["move"]

            if type(move) == int:
                move_bit_board = move
            elif move == "O-O":
                move_bit_board = 0b1000 if self.white_turn else 0b10
                if move_bit_board not in self.move_list:
                    print("Error: not a valid move")
                    return False
            elif move == "O-O-O":
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
        self.white_turn = not self.white_turn
        self.__setattr__("half_moves", self.half_moves +1)
        if self.white_turn:
            self.__setattr__("full_moves", self.full_moves +1)

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
        piece_bitboards.update_bitboards()
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

class Engine():
    def __init__(self):
        self.grid_renderer: Grid_Renderer = Grid_Renderer()

    def static_eval(self, piece_bitboards: Piece_Bitboards):
        eval = self.material_count(piece_bitboards)
        eval+= self.king_safety(piece_bitboards)
        eval+= self.home_sqr_penalty(piece_bitboards)
        eval+= 0.2*random() - 0.1
        return eval

    def king_safety(self, piece_bitboards: Piece_Bitboards):
        king_safety_param = 0.2
        eval = king_safety_param*(piece_bitboards.w_king&0b11000011!=0)
        eval -=king_safety_param*(piece_bitboards.b_king&(0b11000011<<56)!=0)
        return eval

    def home_sqr_penalty(self, piece_bitboards: Piece_Bitboards):
        hsp = 0.5
        eval = 0
        eval -= hsp * ((piece_bitboards.w_knight&0b1000010).bit_count()-(piece_bitboards.b_knight&(0b1000010<<56)).bit_count())
        eval -= hsp * ((piece_bitboards.w_bishop & 0b100100).bit_count() - (piece_bitboards.b_bishop & (0b100100 << 56)).bit_count())
        eval -= hsp * ((piece_bitboards.w_queen & 0b10000).bit_count() - (piece_bitboards.b_queen & (0b10000 << 56)).bit_count())
        return eval

    def material_count(self, piece_bitboards: Piece_Bitboards) -> float:
        eval = 0.0

        worth = [1., 5., 2.9, 3.1, 9., 300.]

        for i in range(6):
            name_w = piece_bitboards.piece_names[2*i]
            name_b = piece_bitboards.piece_names[2 * i + 1]
            eval += worth[i]*(piece_bitboards.__getattribute__(name_w).bit_count()-piece_bitboards.__getattribute__(name_b).bit_count())
        return eval

    def negamax(self,game_state: Game_state, depth: int):
        best = -float("inf") if game_state.white_turn else float("inf")
        if depth == 0:
            return self.static_eval(game_state.piece_bitboards), 0b0
        else:
            game_state.piece_bitboards.update_bitboards()
            game_state.find_moves()
            best_move = game_state.move_list[0]

            # print(game_state.move_list)
            for move in game_state.move_list:
                new_game = game_state.copy()
                new_game.make_move(move=move)

                eval, next_move= self.negamax(new_game, depth-1)

                if game_state.white_turn:
                    if eval > best:
                        best_move = move
                        best=eval
                else:
                    if eval < best:
                        best_move = move
                        best=eval
            return best, best_move

    def alpha_beta(self, game_state: Game_state, depth, alpha, beta):
        game_state.piece_bitboards.update_bitboards()
        game_state.find_moves()
        move_eval = []
        if depth == 0:
            return self.static_eval(game_state.piece_bitboards), 0b0, []
        elif game_state.piece_bitboards.w_king==0:
            return -300, 0b0, []
        elif game_state.piece_bitboards.b_king==0:
            return 300, 0b0, []
        elif game_state.move_list==[]:
            return 0,0, []

        if game_state.white_turn:
            value = -float("inf")
            move = 0b0
            for move in game_state.move_list:
                new_game_state = game_state.copy()
                new_game_state.make_move(move=move)
                eval = self.alpha_beta(new_game_state, depth-1, alpha, beta)
                move_eval.append(eval[0])
                del new_game_state
                if eval[0] > 200:
                    value = eval[0]
                    best_move = move
                    if value >= beta:

                        break
                elif eval[0]>value:
                    value = eval[0]
                    best_move = move
                    if value >= beta:

                        break
                alpha = max(value, alpha)
            move_eval += [0]*(game_state.move_list.__len__() - move_eval.__len__())
            return value, best_move, move_eval

        else:
            value = float("inf")
            move = 0b0
            for move in game_state.move_list[::-1]:
                new_game_state = game_state.copy()
                new_game_state.make_move(move=move)
                eval = self.alpha_beta(new_game_state, depth - 1, alpha, beta)
                move_eval.append(eval[0])
                del new_game_state
                if eval[0] < -200:
                    value = eval[0]
                    best_move = move
                    if value <= alpha:
                        break
                elif eval[0] < value:
                    value = eval[0]
                    best_move = move
                    if value <= alpha:
                        break
                beta = min(value, beta)

            move_eval += [0]*(game_state.move_list.__len__() - move_eval.__len__())
            return value, best_move, move_eval


    def engine(self,game_state: Game_state):
        # eval = self.negamax(game_state, depth)
        t0 = time()
        depth=1
        while True:
            eval = self.alpha_beta(game_state, depth, -float("inf"), float("inf"))
            t1 = time()
            if depth>3:
                # print(depth)
                break
            elif t1-t0>1:
                # print(t1-t0)
                # print(depth)
                break
            else:
                game_state.__setattr__("move_list",[move for y,move in sorted(zip(eval[-1], game_state.move_list))])
            depth+=1
        return eval
    def matrix_board(self, piece_bitboards: Piece_Bitboards)-> np.ndarray:
        pawns = np.pad(np.array(list(str(bin(piece_bitboards.w_pawn))[2:]), dtype=int),(64-piece_bitboards.w_pawn.bit_length() ,0), mode = "constant", constant_values=0) - np.pad(np.array(list(str(bin(piece_bitboards.b_pawn))[2:]), dtype=int),(64-piece_bitboards.b_pawn.bit_length() ,0), mode = "constant", constant_values=0)
        pawns = pawns.reshape([8,8])
        rooks = np.pad(np.array(list(str(bin(piece_bitboards.w_rook))[2:]), dtype=int),
                       (64 - piece_bitboards.w_rook.bit_length(), 0), mode="constant", constant_values=0) - np.pad(
            np.array(list(str(bin(piece_bitboards.b_rook))[2:]), dtype=int),
            (64 - piece_bitboards.b_rook.bit_length(), 0), mode="constant", constant_values=0)
        rooks = rooks.reshape([8, 8])
        knights = np.pad(np.array(list(str(bin(piece_bitboards.w_knight))[2:]), dtype=int),
                       (64 - piece_bitboards.w_knight.bit_length(), 0), mode="constant", constant_values=0) - np.pad(
            np.array(list(str(bin(piece_bitboards.b_knight))[2:]), dtype=int),
            (64 - piece_bitboards.b_knight.bit_length(), 0), mode="constant", constant_values=0)
        knights = knights.reshape([8, 8])
        bishops = np.pad(np.array(list(str(bin(piece_bitboards.w_bishop))[2:]), dtype=int),
                       (64 - piece_bitboards.w_bishop.bit_length(), 0), mode="constant", constant_values=0) - np.pad(
            np.array(list(str(bin(piece_bitboards.b_bishop))[2:]), dtype=int),
            (64 - piece_bitboards.b_bishop.bit_length(), 0), mode="constant", constant_values=0)
        bishops = bishops.reshape([8, 8])
        queens = np.pad(np.array(list(str(bin(piece_bitboards.w_queen))[2:]), dtype=int),
                         (64 - piece_bitboards.w_queen.bit_length(), 0), mode="constant", constant_values=0) - np.pad(
            np.array(list(str(bin(piece_bitboards.b_queen))[2:]), dtype=int),
            (64 - piece_bitboards.b_queen.bit_length(), 0), mode="constant", constant_values=0)
        queens = queens.reshape([8, 8])
        kings = np.pad(np.array(list(str(bin(piece_bitboards.w_king))[2:]), dtype=int),
                        (64 - piece_bitboards.w_king.bit_length(), 0), mode="constant", constant_values=0) - np.pad(
            np.array(list(str(bin(piece_bitboards.b_king))[2:]), dtype=int),
            (64 - piece_bitboards.b_king.bit_length(), 0), mode="constant", constant_values=0)
        kings = kings.reshape([8, 8])

        matrix = np.array([pawns, rooks, knights, bishops, queens, kings])

        return matrix

class Game():
    def __init__(self):
        self.engine: Engine = Engine()
        self.game_state: Game_state = Game_state()
        self.grid_renderer: Grid_Renderer = Grid_Renderer()

    def read_move_out(self, move: str):
        move_name = ""
        if "K" in move[:-1]:
            move_name += "King "
        elif "Q" in move[:-1]:
            move_name += "Queen "
        elif "R" in move[:-1]:
            move_name += "Rook "
        elif "B" in move[:-1]:
            move_name += "Bishop "
        elif "N" in move[:-1]:
            move_name += "Knight "
        else:
            move_name += "Pawn "
        if "x" in move:
            move_name += "takes "
        else:
            move_name += "to "
        if "=" in move:
            move_name += f"{move[-4]} {move[-3]}"
            if "K" in move[-1]:
                move_name += "King "
            elif "Q" in move[-1]:
                move_name += "Queen "
            elif "R" in move[-1]:
                move_name += "Rook "
            elif "B" in move[-1]:
                move_name += "Bishop "
            elif "N" in move[-1]:
                move_name += "Knight "
        else:
            move_name += f"{move[-2]} {move[-1]}"

        subprocess.call(["say", move_name])

    def make_pgn(self, move:int|str, pgn:str):
        if type(move) is str:
            move_num = self.game_state.move_to_num(move)
            print(move)
        else:
            move_num = move

        if self.game_state.half_moves % 2 == 0:
            pgn += " " + f"{self.game_state.full_moves}." + f" {self.game_state.num_to_alg(move_num)}"
        else:
            pgn += " " + f"{self.game_state.num_to_alg(move_num)}"

        return pgn

    def game_loop_pvp(self):
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0'
        self.game_state.set_game_state_from_fen(fen=fen)
        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
        game_going = True
        while game_going:
            if self.game_state.piece_bitboards.w_king == 0:
                print("Black wins")
                game_going = False
            elif self.game_state.piece_bitboards.b_king == 0:
                print("White wins")
                game_going = False
            else:
                self.game_state.find_moves()
                if self.game_state.move_list.__len__() == 0:
                    print("Black wins") if self.game_state.white_turn else print("White wins")
                    game_going = False
                else:
                    move = input()
                    if move == "Stop":
                        # game_going = False
                        break
                    made_move = self.game_state.make_move(move=move)
                    if made_move:
                        # self.game_state.white_turn = not self.game_state.white_turn
                        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
                        t1 = time()
                        eval = self.engine.engine(game_state=self.game_state, depth=2)
                        t2 = time()
                        print(f"eval: {eval[0]}, move:{bin(eval[1])}")

                        print(t2 - t1)
            # game_going=False

        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
    def game_loop_pve(self, player_is_white=None):
        pgn = ""
        t = []
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq g6 0 0'
        self.game_state.set_game_state_from_fen(fen=fen)
        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
        if player_is_white==None:
            player_is_white = random()>0.5
        game_going = True
        while game_going:
            if self.game_state.piece_bitboards.w_king == 0:
                print("Black wins")
                game_going = False
            elif self.game_state.piece_bitboards.b_king == 0:
                print("White wins")
                game_going = False
            else:
                self.game_state.find_moves()
                if self.game_state.move_list.__len__() == 0:
                    print("Black wins") if self.game_state.white_turn else print("White wins")
                    game_going = False
                else:
                    if self.game_state.white_turn == player_is_white:
                        move = input()
                        if move == "Stop":
                            # game_going = False
                            break
                        elif move.__len__()<3:
                            print("try again")
                            move=0b0
                        pgn = self.make_pgn(move,pgn)
                    else:
                        t1 = time()
                        eval = self.engine.engine(game_state=self.game_state)
                        t2 = time()
                        move = eval[1]

                        move_name = self.game_state.num_to_alg(move)

                        print(t2-t1)
                        t.append(t2-t1)
                        self.read_move_out(move_name)
                        print(f"eval: {eval[0]}, move:{move_name}")

                    made_move = self.game_state.make_move(move=move)
                    if made_move:
                        # self.game_state.white_turn = not self.game_state.white_turn
                        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
        times = np.array(t)
        print(times.max())
        print(times.min())
        print(times.mean())

        print(pgn)

    def game_loop_eve(self, max_moves: int):
        pgn = ""
        t = []
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.game_state.set_game_state_from_fen(fen=fen)
        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
        game_going = True
        while game_going:
            if self.game_state.full_moves>=max_moves:
                game_going = False
            if self.game_state.piece_bitboards.w_king == 0:
                print("Black wins")
                game_going = False
            elif self.game_state.piece_bitboards.b_king == 0:
                print("White wins")
                game_going = False
            else:
                self.game_state.find_moves()
                if self.game_state.move_list.__len__() == 0:
                    print("stale_mate")
                    game_going = False
                else:
                    t1=time()


                    eval = self.engine.engine(game_state=self.game_state)
                    t2 = time()

                    t.append(t2-t1)
                    move = eval[1]

                    pgn = self.make_pgn(move,pgn)
                    ta = time()
                    matrix = self.engine.matrix_board(self.game_state.piece_bitboards)
                    tb = time()
                    print(tb-ta)

                    print(f"eval: {eval[0]}, move:{self.game_state.num_to_alg(move)}")
                    made_move = self.game_state.make_move(move=move)
                    if made_move:
                        # self.game_state.white_turn = not self.game_state.white_turn
                        self.grid_renderer.render_grid(self.game_state.piece_bitboards)
        times = np.array(t)
        print(times.max())
        print(times.min())
        print(times.mean())

        print(pgn)



if __name__=="__main__":
    new_game = Game()
    new_game.game_loop_eve(max_moves=1)

