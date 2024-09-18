import engine as eg
from engine import piece_count


def pawn_moves(piece_boards, enpassant_boards, player):
    move_list = []
    promotion_moves=[]
    b_tot_bitboard = piece_boards[0] | piece_boards[1] | piece_boards[2] | piece_boards[3] | piece_boards[4] | piece_boards[5]
    w_tot_bitboard = piece_boards[6] | piece_boards[7] | piece_boards[8] | piece_boards[9] | piece_boards[10] | piece_boards[11]
    tot_bitboard = b_tot_bitboard|w_tot_bitboard
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    promotion_mask = 0b1111111111111111

    #calculating the squares the pawns can move[1]to by pushing the pawns
    if player == True:
        pointer = 0b1 << 8
        # pawn pushes white
        pawn_push_mask = (piece_boards[6]) & ~(tot_bitboard>>8)
        move_bit = (0b1 << 16) + (0b1 << 8)
        for i in range(48):
            if pawn_push_mask & (pointer<<i)!=0:
                move_list.append(move_bit<<i)
                if (move_bit<<i) & (promotion_mask<<48)!=0:
                    promotion_moves.append(len(move_list)-1)

        pointer = 0b1 << 8
        pawn_double_push_mask = (piece_boards[6]&0b1111111100000000) & ~(tot_bitboard>>16) & ~(tot_bitboard>>8)
        move_bit = (0b1 << 24) + (0b1 << 8)
        for i in range(8):
            if pawn_double_push_mask & (pointer<<i)!=0:
                move_list.append(move_bit<<i)


        # pawn captures white
        pointer = 0b1 << 8
        capture_left_mask = piece_boards[6] & (((b_tot_bitboard|enpassant_boards)&not_hfile)>>9)
        capture_right_mask = piece_boards[6] & (((b_tot_bitboard|enpassant_boards)&not_afile)>>7)
        move_bit_left = (0b1<<8) + (0b1<<17)
        move_bit_right = (0b1<<8) + (0b1<<15)
        for i in range(47):
            if capture_left_mask & (pointer<<i)!=0:
                move_list.append(move_bit_left<<i)
                if (move_bit_left<<i) & (promotion_mask<<48)!=0:
                    promotion_moves.append(len(move_list)-1)
            if capture_right_mask & (pointer<<i+1)!=0:
                move_list.append(move_bit_right<<i+1)
                if (move_bit_right<<i) & (promotion_mask<<48)!=0:
                    promotion_moves.append(len(move_list)-1)

    elif player == False:
        pointer = 0b1
        # pawn push black
        pawn_push_mask = (piece_boards[0]>>8) & ~tot_bitboard
        move_bit =  (0b1<<8) + 0b1
        for i in range(48):
            if pawn_push_mask & (pointer<<i)!=0:
                move_list.append(move_bit<<i)
                if (move_bit<<i) & (promotion_mask)!=0:
                    promotion_moves.append(len(move_list)-1)

        pointer = 0b1
        pawn_double_push_mask = (((piece_boards[0]>>48) & 0b11111111) & ~(tot_bitboard>>40)) & ~(tot_bitboard>>32)
        move_bit = (0b1<<32) + (0b1<<48)
        for i in range(8):
            if pawn_double_push_mask & (pointer<<i)!=0:
                move_list.append(move_bit<<i)

        # pawn captures black
        pointer = 0b1
        capture_left_mask = ((piece_boards[0] & not_afile)>>7) & (w_tot_bitboard|enpassant_boards)
        capture_right_mask = (piece_boards[0] & not_hfile) >> 9 & (w_tot_bitboard | enpassant_boards)
        move_bit_left = 0b1 + (0b1 << 7)
        move_bit_right = 0b1 + (0b1 << 9)
        for i in range(47):
            if capture_left_mask & (pointer<<i+1)!=0:
                move_list.append(move_bit_left<<i+1)
                if (move_bit_left<<i) & (promotion_mask)!=0:
                    promotion_moves.append(len(move_list)-1)
            if capture_right_mask & (pointer<<i)!=0:
                move_list.append(move_bit_right<<i)
                if (move_bit_right<<i) & (promotion_mask)!=0:
                    promotion_moves.append(len(move_list)-1)


    return move_list, promotion_moves

def king_moves(piece_boards, castle_board, player):
    move_list = []
    b_tot_bitboard = piece_boards[0] | piece_boards[1] | piece_boards[2] | piece_boards[3] | piece_boards[4] | piece_boards[5]
    w_tot_bitboard = piece_boards[6] | piece_boards[7] | piece_boards[8] | piece_boards[9] | piece_boards[10] | piece_boards[11]
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    if player == True: #white to play
        king_up = piece_boards[11]&0b11111111111111111111111111111111111111111111111111111111
        king_down = piece_boards[11]&~0b11111111
        king_left = piece_boards[11]&not_afile
        king_right = piece_boards[11]&not_hfile
        move_up = king_up | (king_up<<8) & ~w_tot_bitboard
        move_ul = king_up&king_left | ((king_up&king_left)<<9) & ~w_tot_bitboard
        move_ur = king_up&king_right | ((king_up&king_right)<<7) & ~w_tot_bitboard
        move_left = king_left | (king_left<<1) & ~w_tot_bitboard
        move_right = king_right | (king_right>>1) & ~w_tot_bitboard
        move_down = king_down | (king_down>>8) & ~w_tot_bitboard
        move_dl = king_down&king_left | ((king_down&king_left)>>7) & ~w_tot_bitboard
        move_dr = king_down&king_right | ((king_down&king_right)>>9) & ~w_tot_bitboard
        if move_up.bit_count()==2:
            move_list.append(move_up)
        if move_ul.bit_count()==2:
            move_list.append(move_ul)
        if move_ur.bit_count()==2:
            move_list.append(move_ur)
        if move_left.bit_count()==2:
            move_list.append(move_left)
        if move_right.bit_count()==2:
            move_list.append(move_right)
        if move_down.bit_count()==2:
            move_list.append(move_down)
        if move_dl.bit_count()==2:
            move_list.append(move_dl)
        if move_dr.bit_count()==2:
            move_list.append(move_dr)
        if castle_board&0b1000!=0 and 0b110&(w_tot_bitboard|b_tot_bitboard)==0:
            move_list.append(0b1010)
        if castle_board&0b100!=0 and 0b1110000&(w_tot_bitboard|b_tot_bitboard)==0:
            move_list.append(0b101000)


    elif player == False:
        king_up = piece_boards[5] & 0b11111111111111111111111111111111111111111111111111111111
        king_down = piece_boards[5] & ~0b11111111
        king_left = piece_boards[5] & not_afile
        king_right = piece_boards[5] & not_hfile
        move_up = king_up | (king_up << 8) & ~b_tot_bitboard
        move_ul = king_up & king_left | ((king_up & king_left) << 9) & ~b_tot_bitboard
        move_ur = king_up & king_right | ((king_up & king_right) << 7) & ~b_tot_bitboard
        move_left = king_left | (king_left << 1) & ~b_tot_bitboard
        move_right = king_right | (king_right >> 1) & ~b_tot_bitboard
        move_down = king_down | (king_down >> 8) & ~b_tot_bitboard
        move_dl = king_down & king_left | ((king_down & king_left) >> 7) & ~b_tot_bitboard
        move_dr = king_down & king_right | ((king_down & king_right) >> 9) & ~b_tot_bitboard
        if move_up.bit_count() == 2:
            move_list.append(move_up)
        if move_ul.bit_count() == 2:
            move_list.append(move_ul)
        if move_ur.bit_count() == 2:
            move_list.append(move_ur)
        if move_left.bit_count() == 2:
            move_list.append(move_left)
        if move_right.bit_count() == 2:
            move_list.append(move_right)
        if move_down.bit_count() == 2:
            move_list.append(move_down)
        if move_dl.bit_count() == 2:
            move_list.append(move_dl)
        if move_dr.bit_count() == 2:
            move_list.append(move_dr)
        if castle_board & 0b10 != 0 and (0b110<<56) &(w_tot_bitboard | b_tot_bitboard) == 0:
            move_list.append(0b1010<<56)
        if castle_board & 0b1 != 0 and (0b1110000<<56) &(w_tot_bitboard | b_tot_bitboard) == 0:
            move_list.append(0b101000<<56)

    return move_list

def knight_moves(piece_boards, player):
    move_list = []
    b_tot_bitboard = piece_boards[0] | piece_boards[1] | piece_boards[2] | piece_boards[3] | piece_boards[4] | piece_boards[5]
    w_tot_bitboard = piece_boards[6] | piece_boards[7] | piece_boards[8] | piece_boards[9] | piece_boards[10] | piece_boards[11]
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_ghfile = 0b1111110011111100111111001111110011111100111111001111110011111100
    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_abfile = 0b111111100111111001111110011111100111111001111110011111100111111
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111
    not_78rank = 0b111111111111111111111111111111111111111111111111
    pointer = 0b1
    player = player
    for i in range(64):
        if piece_boards[8 if player else 2]&(pointer<<i)!=0:
            move1 = (pointer<<i & not_hfile) | (((pointer<<i)>>17)&~(w_tot_bitboard if player else b_tot_bitboard))
            move2 = (pointer<<i & not_afile) | (((pointer<<i)>>15)&~(w_tot_bitboard if player else b_tot_bitboard))
            move3 = (pointer<<i & not_abfile) | (((pointer<<i)>>6)&~(w_tot_bitboard if player else b_tot_bitboard))
            move4 = (pointer<<i & not_abfile & not_8rank) | ((pointer<<i+10)&~(w_tot_bitboard if player else b_tot_bitboard))
            move5 = (pointer<<i & not_afile & not_78rank) | ((pointer<<i+17)&~(w_tot_bitboard if player else b_tot_bitboard))
            move6 = (pointer<<i & not_hfile & not_78rank) | ((pointer<<i+15)&~(w_tot_bitboard if player else b_tot_bitboard))
            move7 = (pointer<<i & not_ghfile & not_8rank) | ((pointer<<i+6)&~(w_tot_bitboard if player else b_tot_bitboard))
            move8 = (pointer<<i & not_ghfile) | (((pointer<<i)>>10)&~(w_tot_bitboard if player else b_tot_bitboard))
            if move1.bit_count()==2:
                move_list.append(move1)
            if move2.bit_count()==2:
                move_list.append(move2)
            if move3.bit_count()==2:
                move_list.append(move3)
            if move4.bit_count()==2:
                move_list.append(move4)
            if move5.bit_count()==2:
                move_list.append(move5)
            if move6.bit_count()==2:
                move_list.append(move6)
            if move7.bit_count()==2:
                move_list.append(move7)
            if move8.bit_count()==2:
                move_list.append(move8)
    return move_list

def bishop_moves(piece_boards, player, piece = 9):
    move_list = []
    pointer = 0b1
    player = player
    b_tot_bitboard = piece_boards[0] | piece_boards[1] | piece_boards[2] | piece_boards[3] | piece_boards[4] | piece_boards[5]
    w_tot_bitboard = piece_boards[6] | piece_boards[7] | piece_boards[8] | piece_boards[9] | piece_boards[10] | piece_boards[11]

    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_1rank = 0b1111111111111111111111111111111111111111111111111111111100000000
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111


    for i in range(64):
        if pointer<<i & piece_boards[piece if player else piece-6]:
            counter_1=min(i%8,i//8)
            counter_2=min(i%8, 7-i//8)
            counter_3=min(7-i%8,i//8)
            counter_4=min(7-i%8,7-i//8)

            tr = pointer<<i
            tl = pointer<<i
            br = pointer<<i
            bl = pointer<<i
            for j in range(max(counter_1,counter_2,counter_3,counter_4)):
                tr = ((tr&not_hfile&not_8rank&~(b_tot_bitboard if player else w_tot_bitboard))<<7)&~(w_tot_bitboard if player else b_tot_bitboard)
                tl = ((tl & not_afile & not_8rank & ~(b_tot_bitboard if player else w_tot_bitboard)) << 9) & ~(w_tot_bitboard if player else b_tot_bitboard)
                br = ((br & not_hfile & not_1rank & ~(b_tot_bitboard if player else w_tot_bitboard)) >> 9) & ~(w_tot_bitboard if player else b_tot_bitboard)
                bl = ((bl & not_afile & not_1rank & ~(b_tot_bitboard if player else w_tot_bitboard)) >> 7) & ~(w_tot_bitboard if player else b_tot_bitboard)

                move_tr = pointer<<i | tr
                move_tl = pointer<<i | tl
                move_br = pointer<<i | br
                move_bl = pointer<<i | bl

                if move_tr.bit_count()==2:
                    move_list.append(move_tr)
                if move_tl.bit_count()==2:
                    move_list.append(move_tl)
                if move_br.bit_count()==2:
                    move_list.append(move_br)
                if move_bl.bit_count()==2:
                    move_list.append(move_bl)
    return move_list

def rook_moves(piece_boards, player, piece = 7):
    move_list = []
    pointer = 0b1
    b_tot_bitboard = piece_boards[0] | piece_boards[1] | piece_boards[2] | piece_boards[3] | piece_boards[4] | piece_boards[5]
    w_tot_bitboard = piece_boards[6] | piece_boards[7] | piece_boards[8] | piece_boards[9] | piece_boards[10] | piece_boards[11]

    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_1rank = 0b1111111111111111111111111111111111111111111111111111111100000000
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111


    player  = player
    for i in range(64):
        if pointer << i & piece_boards[piece if player else piece-6]:
            tp = pointer << i
            bt = pointer << i
            rt = pointer << i
            lt = pointer << i
            counter_1 = max(i % 8, i // 8)
            counter_2 = max(i % 8, 7 - i // 8)
            counter_3 = max(7 - i % 8, i // 8)
            counter_4 = max(7 - i % 8, 7 - i // 8)
            for j in range(max(counter_1,counter_2,counter_3,counter_4)):
                tp = ((tp & not_8rank & ~(b_tot_bitboard if player else w_tot_bitboard)) << 8) & ~(w_tot_bitboard if player else b_tot_bitboard)
                top = pointer<<i | tp

                bt = ((bt & not_1rank & ~(b_tot_bitboard if player else w_tot_bitboard)) >> 8) & ~(w_tot_bitboard if player else b_tot_bitboard)
                bot = pointer<<i | bt

                rt = ((rt & not_hfile  & ~(b_tot_bitboard if player else w_tot_bitboard)) >> 1) & ~(w_tot_bitboard if player else b_tot_bitboard)
                right = pointer<<i | rt

                lt = ((lt & not_afile & ~(b_tot_bitboard if player else w_tot_bitboard)) <<1) & ~(w_tot_bitboard if player else b_tot_bitboard)
                left = pointer<<i | lt

                if top.bit_count()==2:
                    move_list.append(top)
                if bot.bit_count()==2:
                    move_list.append(bot)
                if right.bit_count()==2:
                    move_list.append(right)
                if left.bit_count()==2:
                    move_list.append(left)
    return move_list

def queen_moves(piece_boards, player):
    move_list = rook_moves(piece_boards, player, piece=10)
    move_list.extend(bishop_moves(piece_boards, player, piece=10))
    return move_list

# @jit
def move_pawn(move,board_info:list):


    #single pawn push
    if move[0]/move[1]== 2**8 or move[1]/move[0] == 2**8:
        if move[1]& board_info[6] != 0b0:
            try:
                int(move[2])
                board_info[0][(6 if board_info[1]==True else 0) ] = (board_info[0][(6 if board_info[1]==True else 0)] & ~move[0]) | move[1]
            except:
                board_info[0][(6 if board_info[1] == True else 0)] = (board_info[0][(6 if board_info[1] == True else 0)] & ~move[0])
                board_info[0][(move[2].upper() if board_info[1] == True else move[2].lower())] = (board_info[0][(move[2].upper() if board_info[1] == True else move[2].lower())] | move[1])
        else:
            board_info[1] = not board_info[1]
            return board_info[0], board_info[1], board_info[3]

    #double pawn push
    elif move[0]/move[1]== 2**16 or move[1]/move[0] == 2**16:
        if move[1]& board_info[6] != 0b0:
            board_info[3] = move[0]>>8 & ~board_info[1] | move[0]<<8 & ~(board_info[1]==False)
            board_info[0][(6 if board_info[1]==True else 0)] = (board_info[0][(6 if board_info[1]==True else 0)] & ~move[0]) | move[1]
        else:
            board_info[1] = not board_info[1]
            return board_info[0], board_info[1], board_info[3]

    #captures and enpassant
    elif move[1] & board_info[7] != 0b0:
        if board_info[3] & ~move[1] == 0b0:
            board_info[0][0] = (board_info[0][0] & ~move[1]>>8)
            board_info[0][6] = (board_info[0][6] & ~move[1]<<8)
        for piece in board_info[0]:
            board_info[0][piece] = board_info[0][piece] & ~move[1]

        try:
            int(move[2])
            board_info[0][(6 if board_info[1]==True else 0)] = (board_info[0][(6 if board_info[1]==True else 0)] & ~move[0]) | move[1]
        except:
            board_info[0][(6 if board_info[1] == True else 0)] = (board_info[0][(6 if board_info[1] == True else 0)] & ~move[0])
            board_info[0][(move[2].upper() if board_info[1] == True else move[2].lower())] = (board_info[0][(move[2].upper() if board_info[1] == True else move[2].lower())] | move[1])

    #

    #else illegal move
    else:
        board_info[1] = not(board_info[1])
        print('smthng wrong bruv')
        return board_info[0], board_info[1], board_info[3]

    return board_info[0], board_info[1], board_info[3]

# @jit
def move_king(move,board_info:list)->list:

    if move[1]& board_info[8] == 0:
        board_info[1] = not(board_info[1])
        return board_info


    if move[0]/move[1] == 4:
        board_info[0][11 if board_info[1]==True else 5] = move[1]
        board_info[0][7 if board_info[1]==True else 1] = (board_info[0][7 if board_info[1]==True else 1] & ~ move[0]>>3) | move[1]<<1
        board_info[2] = board_info[2] & (0b0111 if board_info[1]==True else 0b1101)
        return board_info

    elif move[1]/move[0] == 4:
        board_info[0][11 if board_info[1] == True else 5] = move[1]
        board_info[0][7 if board_info[1] == True else 1] = (board_info[0][7 if board_info[1] == True else 1] & ~move[
            0] << 4) | move[1] >> 1
        board_info[2] = board_info[2] & (0b1011 if board_info[1]==True else 0b1110)

        return board_info


    elif board_info[1] == True:
        board_info[2] = board_info[2] & 0b0011
        for piece in range(12):
            board_info[0][piece] = board_info[0][piece] & ~move[1]
        board_info[0][11] = move[1]
        board_info[2] = board_info[2] & 0b0011

    elif board_info[1] == False:
        board_info[2] = board_info[2] & 0b1100
        for piece in range(12):
            board_info[0][piece] = board_info[0][piece] & ~move[1]
        board_info[0][5] = move[1]
        board_info[2] = board_info[2] & 0b1100
    return board_info

def move_knight(move,board_info):
    pass

def move_bishop(move,board_info):
    pass

def move_rook(move,board_info):
    pass

def move_queen(move,board_info):
    pass


def update_board_info(board_info:list)->list:
    board_info[6] = []

    piece_boards = board_info[0]
    enpassant_boards = board_info[3]
    player = board_info[1]
    castle_board = board_info[2]
    pawn_move_list, board_info[7] = pawn_moves(piece_boards, enpassant_boards, player) #done
    king_move_list = king_moves(piece_boards, castle_board, player) #done
    knight_move_list = knight_moves(piece_boards, player) #done
    bishop_move_list = bishop_moves(piece_boards, player) #done
    rook_move_list = rook_moves(piece_boards, player) #done
    queen_move_list = queen_moves(piece_boards, player) #done
    board_info[6].append(pawn_move_list)
    board_info[6].append(king_move_list)
    board_info[6].append(knight_move_list)
    board_info[6].append(bishop_move_list)
    board_info[6].append(rook_move_list)
    board_info[6].append(queen_move_list)
    return board_info


# @jit
def move(board_info, **kwargs):
    player = board_info[1]
    move_function = [move_pawn, move_king, move_knight, move_bishop, move_rook, move_queen]
    board_sqrs_dict = {
            "a8": 63, "b8": 62, "c8": 61, "d8": 60, "e8": 59, "f8": 58, "g8": 57, "h8": 56,
            "a7": 55, "b7": 54, "c7": 53, "d7": 52, "e7": 51, "f7": 50, "g7": 49, "h7": 48,
            "a6": 47, "b6": 46, "c6": 45, "d6": 44, "e6": 43, "f6": 42, "g6": 41, "h6": 40,
            "a5": 39, "b5": 38, "c5": 37, "d5": 36, "e5": 35, "f5": 34, "g5": 33, "h5": 32,
            "a4": 31, "b4": 30, "c4": 29, "d4": 28, "e4": 27, "f4": 26, "g4": 25, "h4": 24,
            "a3": 23, "b3": 22, "c3": 21, "d3": 20, "e3": 19, "f3": 18, "g3": 17, "h3": 16,
            "a2": 15, "b2": 14, "c2": 13, "d2": 12, "e2": 11, "f2": 10, "g2": 9,  "h2": 8,
            "a1": 7,  "b1": 6,  "c1": 5,  "d1": 4,  "e1": 3,  "f1": 2,  "g1": 1,  "h1": 0
        }
    try:
        move= kwargs["move"]
        if move=="0-0":
            move_bit_board = 0b1010 if player else 0b1010<<56
            piece_num = 1
        elif move=="0-0-0":
            move_bit_board = 0b101000 if player else 0b101000<<56
            piece_num = 1
        elif len(move)==4:
            try:
                move_bit_board = 0b1<<board_sqrs_dict[move[:2]] | 0b1<<board_sqrs_dict[move[2:]]
                for i,moves in enumerate(board_info[6]):
                    if move_bit_board in moves:
                        piece_num=i
                    else:
                        print("Error: not a legal move")
                        return board_info
            except:
                print("Error: not a legal move")
                return board_info
        elif len(move)==5:
            try:
                move_bit_board = 0b1<<board_sqrs_dict[move[:2]] | 0b1<<board_sqrs_dict[move[2:4]]
                if move_bit_board in board_info[6][0]:
                    piece_num=0
                else:
                    print("Error: not a legal move")
                    return board_info
            except:
                print("Error: not a legal move")
                return board_info


        movebit_board = 0b1<< board_sqrs_dict[move[:2]]|0b1<< board_sqrs_dict[move[2:4]]
    except:
        piece_idx, move_idx = eg.select_move(board_info)
        print(f"engine choses {piece_idx}, {move_idx}")
        move = board_info[6][piece_idx][move_idx]


