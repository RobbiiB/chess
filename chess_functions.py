def get_bitboards_and_other_stuff(fen):
    Castle_dict = {
        "K": 0b1000,
        "Q": 0b0100,
        "k": 0b0010,
        "q": 0b0001,
        0b1000: "O-O",
        0b0100: "O-O-O",
        0b0010: "O-O",
        0b0001: "O-O-O"
    }

    Enpassant_dict = {
        "a6": 16,
        "b6": 17,
        "c6": 18,
        "d6": 19,
        "e6": 20,
        "f6": 21,
        "g6": 22,
        "h6": 23,
        "a3": 40,
        "b3": 41,
        "c3": 42,
        "d3": 43,
        "e3": 44,
        "f3": 45,
        "g3": 46,
        "h3": 47
    }

    Piece_bitboard_dict = {
        "p": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "r": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "n": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "b": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "q": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "k": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "P": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "R": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "N": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "B": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "Q": 0b0000000000000000000000000000000000000000000000000000000000000000,
        "K": 0b0000000000000000000000000000000000000000000000000000000000000000
    }

    bit_adder = 0b1000000000000000000000000000000000000000000000000000000000000000
    fen_elements = fen.split(' ')  # splitting the fen, so it can be used to initialize the other parameters

    full_moves = fen_elements[5]  # initializing the full move[1]int

    half_moves = fen_elements[4]  # initializing the half move[1]int

    # Initializing the en passant squares
    enpassant_bitboard = 0b0
    if fen_elements[3] != "-":
        enpassant_bitboard = bit_adder >> Enpassant_dict[fen_elements[3]]

    # Initializing the castle rights
    castle_rights_bitboard = 0b0000
    for element in fen_elements[2]:
        castle_rights_bitboard = castle_rights_bitboard | Castle_dict[element]

    # Initializing the board_info[1] bool w=True, b=False
    if fen_elements[1] == "w":
        player = True
    else:
        player = False

    # Initializing the piece bitboards
    for element in fen_elements[0]:
        if element == "/":
            pass
        else:
            try:
                i = int(element)
                bit_adder = bit_adder >> i
            except:
                Piece_bitboard_dict[element] = Piece_bitboard_dict[element] | bit_adder
                bit_adder = bit_adder >> 1

    Piece_bitboard_list = list(Piece_bitboard_dict.values())
    # returning the important values
    return Piece_bitboard_list, player, castle_rights_bitboard, enpassant_bitboard, half_moves, full_moves

def render_grid(grid):
    #making the chessboard, might add the numbers and letters idk yet
    print("+---++---++---++---++---++---++---++---+")
    print("\n+---++---++---++---++---++---++---++---+\n".join(["".join(row) for row in grid]))
    print("+---++---++---++---++---++---++---++---+")


def make_grid(board_info):
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
        0:'p',
        1:'r',
        2:'n',
        3:'b',
        4:'q',
        5:'k',
        6: 'P',
        7: 'R',
        8: 'N',
        9: 'B',
        10: 'Q',
        11: 'K'
    }

    for ind in range(len(board_info[0])):
        bit_adder = 0b1000000000000000000000000000000000000000000000000000000000000000
        new_piece = "| " + piece_bitboard_dict_list[ind] + " |"

        for i in range(64):
            if board_info[0][ind] & bit_adder != 0:
                grid[i//8][i%8] = new_piece

            bit_adder = bit_adder >> 1


    render_grid(grid)
    return grid



# @jit
def pawn_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][10] | board_info[0][11]
    tot_bitboard = b_tot_bitboard|w_tot_bitboard
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111

    #calculating the squares the pawns can move[1]to by pushing the pawns
    if board_info[1] == True:
        pointer = 0b1 << 8
        # pawn pushes white
        pawn_push_mask = (board_info[0][6]) & ~(tot_bitboard>>8)
        move_bit = (0b1 << 16) + (0b1 << 8)
        for i in range(48):
            if pawn_push_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit<<i)

        pointer = 0b1 << 8
        pawn_double_push_mask = (board_info[0][6]&0b1111111100000000) & ~(tot_bitboard>>16) & ~(tot_bitboard>>8)
        move_bit = (0b1 << 24) + (0b1 << 8)
        for i in range(8):
            if pawn_double_push_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit<<i)


        # pawn captures white
        pointer = 0b1 << 8
        capture_left_mask = board_info[0][6] & (((b_tot_bitboard|board_info[3])&not_hfile)>>9)
        capture_right_mask = board_info[0][6] & (((b_tot_bitboard|board_info[3])&not_afile)>>7)
        print(bin(capture_right_mask))
        print(bin(capture_left_mask))
        print(bin(board_info[3]), "enpassant")
        move_bit_left = (0b1<<8) + (0b1<<17)
        move_bit_right = (0b1<<8) + (0b1<<15)
        for i in range(47):
            if capture_left_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit_left<<i)
            if capture_right_mask & (pointer<<i+1)!=0:
                board_info[6].append(move_bit_right<<i+1)

    elif board_info[1] == False:
        pointer = 0b1
        # pawn push black
        pawn_push_mask = (board_info[0][0]>>8) & ~tot_bitboard
        move_bit =  (0b1<<8) + 0b1
        for i in range(48):
            if pawn_push_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit<<i)

        pointer = 0b1
        pawn_double_push_mask = (((board_info[0][0]>>48) & 0b11111111) & ~(tot_bitboard>>40)) & ~(tot_bitboard>>32)
        move_bit = (0b1<<32) + (0b1<<48)
        for i in range(8):
            if pawn_double_push_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit<<i)

        # pawn captures black
        pointer = 0b1
        capture_left_mask = ((board_info[0][0] & not_afile)>>7) & (w_tot_bitboard|board_info[3])
        capture_right_mask = (board_info[0][0] & not_hfile) >> 9 & (w_tot_bitboard | board_info[3])
        move_bit_left = 0b1 + (0b1 << 7)
        move_bit_right = 0b1 + (0b1 << 9)
        for i in range(47):
            if capture_left_mask & (pointer<<i+1)!=0:
                board_info[6].append(move_bit_left<<i+1)
            if capture_right_mask & (pointer<<i)!=0:
                board_info[6].append(move_bit_right<<i)


    return board_info

# @jit
def king_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][10] | board_info[0][11]
    not_afile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_hfile = 0b111111101111111011111110111111101111111011111110111111101111111
    if board_info[1] == True: #white to play
        move_up_or_down = (board_info[0][11]<<8 & ~w_tot_bitboard &~0b10000000000000000000000000000000000000000000000000000000000000000000) | (board_info[0][11]>>8 & ~w_tot_bitboard)
        move_left = ((board_info[0][11]<<9 & not_afile) | (board_info[0][11]<<1 & not_afile) | (board_info[0][11]>>7 & not_afile)) & ~w_tot_bitboard
        move_right = ((board_info[0][11]>>9 & not_hfile) | (board_info[0][11]>>1 & not_hfile) | (board_info[0][11]<<7 & not_hfile)) & ~w_tot_bitboard
        castle_rights = (0b10 if (0b1000 & board_info[2]) !=0b0 else 0b0) | (0b100000 if (0b100 & board_info[2]) != 0b0 else 0b0)
        castle_rights = castle_rights & ~(0b1110110 & (b_tot_bitboard|w_tot_bitboard))
        #print(castle_rights,board_info[2])

        board_info[8] = move_up_or_down | move_left | move_right | castle_rights


    elif board_info[1] == False:
        move_up_or_down = (board_info[0][5] << 8 & ~b_tot_bitboard &~0b10000000000000000000000000000000000000000000000000000000000000000000) | (
                    board_info[0][5] >> 8 & ~b_tot_bitboard)
        move_left = ((board_info[0][5] >> 9 & not_afile) | (board_info[0][5] >> 1 & not_afile) | (
                    board_info[0][5] << 7 & not_afile)) & ~b_tot_bitboard
        move_right = ((board_info[0][5] << 9 & not_hfile) | (board_info[0][5] << 1 & not_hfile) | (
                    board_info[0][5] >> 7 & not_hfile)) & ~b_tot_bitboard
        castle_rights = (0b1000000000000000000000000000000000000000000000000000000000 if (0b10 & board_info[2]) != 0b0 else 0b0) | (0b10000000000000000000000000000000000000000000000000000000000000 if (0b1 & board_info[2]) != 0b0 else 0b0)
        castle_rights = castle_rights & ~(0b111011000000000000000000000000000000000000000000000000000000000 & (b_tot_bitboard | w_tot_bitboard))


        board_info[8] = move_up_or_down | move_left | move_right | castle_rights

    return board_info

# @jit
def knight_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][10] | board_info[0][11]
    knight_move_mask=0b10100001000100000000000100010000101

    # move like L
    # centre_knights = 0b0000000000000000001111000011110000111100001111000000000000000000
    # left_one_knights = 0b0000000000000000010000000100000001000000010000000000000000000000
    # left_two_knights = 0b0000000000000000100000001000000010000000100000000000000000000000
    # right_one_knights = 0b000000000000000000000010000000100000001000000010000000000000000000000
    # right_two_knights = 0b000000000000000000000001000000010000000100000001000000000000000000000
    # up_one_knights = 0b0000000000111100000000000000000000000000000000000000000000000000
    # up_two_knights = 0b0011110000000000000000000000000000000000000000000000000000000000
    # down_one_knights = 0b0000000000000000000000000000000000000000000000000011110000000000
    # down_two_knights = 0b0000000000000000000000000000000000000000000000000000000000111100

    if board_info[1] ==True:

        pass

# @jit
def bishop_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][10] | board_info[0][11]

    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_1rank = 0b1111111111111111111111111111111111111111111111111111111100000000
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111

    top_right=0b0
    top_left =0b0
    bot_right=0b0
    bot_left =0b0
    if board_info[1]==True:
        tr = board_info[0][9]
        tl = board_info[0][9]
        br = board_info[0][9]
        bl = board_info[0][9]
        for i in range(7):
            tr = ((tr&not_hfile&not_8rank&~b_tot_bitboard)<<7)&~w_tot_bitboard
            top_right=top_right | tr

            tl = ((tl & not_afile & not_8rank & ~b_tot_bitboard) << 9) & ~w_tot_bitboard
            top_left = top_left | tl

            br = ((br & not_hfile & not_1rank & ~b_tot_bitboard) >> 9) & ~w_tot_bitboard
            bot_right = bot_right | br

            bl = ((bl & not_afile & not_1rank & ~b_tot_bitboard) >> 7) & ~w_tot_bitboard
            bot_left = bot_left | bl

    else:
        tr = board_info[0][3]
        tl = board_info[0][3]
        br = board_info[0][3]
        bl = board_info[0][3]
        for i in range(7):
            tr = ((tr & not_hfile & not_8rank & ~w_tot_bitboard) << 7) & ~b_tot_bitboard
            top_right = top_right | tr

            tl = ((tl & not_afile & not_8rank & ~w_tot_bitboard) << 9) & ~b_tot_bitboard
            top_left = top_left | tl

            br = ((br & not_hfile & not_1rank & ~w_tot_bitboard) >> 9) & ~b_tot_bitboard
            bot_right = bot_right | br

            bl = ((bl & not_afile & not_1rank & ~w_tot_bitboard) >> 7) & ~b_tot_bitboard
            bot_left = bot_left | bl

    board_info[10] = bot_left|bot_right|top_right|top_left
    return board_info
# @jit
def rook_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][10] | board_info[0][11]

    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_1rank = 0b1111111111111111111111111111111111111111111111111111111100000000
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111

    top = 0b0
    bot = 0b0
    right = 0b0
    left = 0b0
    if board_info[1] == True:
        tp = board_info[0][7]
        bt = board_info[0][7]
        rt = board_info[0][7]
        lt = board_info[0][7]
        for i in range(7):
            tp = ((tp & not_8rank & ~b_tot_bitboard) << 8) & ~w_tot_bitboard
            top = top | tp

            bt = ((bt & not_1rank & ~b_tot_bitboard) >> 8) & ~w_tot_bitboard
            bot = bot | bt

            rt = ((rt & not_hfile  & ~b_tot_bitboard) >> 1) & ~w_tot_bitboard
            right = right | rt

            lt = ((lt & not_afile & ~b_tot_bitboard) <<1) & ~w_tot_bitboard
            left = left | lt

    else:
        tp = board_info[0][1]
        bt = board_info[0][1]
        rt = board_info[0][1]
        lt = board_info[0][1]
        for i in range(7):
            tp = ((tp & not_8rank & ~w_tot_bitboard) << 8) & ~b_tot_bitboard
            top = top | tp

            bt = ((bt & not_1rank & ~w_tot_bitboard) >> 8) & ~b_tot_bitboard
            bot = bot | bt

            rt = ((rt & not_hfile & ~w_tot_bitboard) >> 1) & ~b_tot_bitboard
            right = right | rt

            lt = ((lt & not_afile & ~w_tot_bitboard) << 1) & ~b_tot_bitboard
            left = left | lt

    board_info[11] = bot | top | right | left
    return board_info

# @jit
def queen_moves(board_info):
    b_tot_bitboard = board_info[0][0] | board_info[0][1] | board_info[0][2] | board_info[0][3] | board_info[0][
        4] | board_info[0][5]
    w_tot_bitboard = board_info[0][6] | board_info[0][7] | board_info[0][8] | board_info[0][9] | board_info[0][
        10] | board_info[0][11]

    not_afile = 0b111111101111111011111110111111101111111011111110111111101111111
    not_hfile = 0b1111111011111110111111101111111011111110111111101111111011111110
    not_1rank = 0b1111111111111111111111111111111111111111111111111111111100000000
    not_8rank = 0b11111111111111111111111111111111111111111111111111111111

    top_right = 0b0
    top_left = 0b0
    bot_right = 0b0
    bot_left = 0b0
    top = 0b0
    bot = 0b0
    right = 0b0
    left = 0b0
    if board_info[1] == True:
        tr = board_info[0][10]
        tl = board_info[0][10]
        br = board_info[0][10]
        bl = board_info[0][10]
        tp = board_info[0][10]
        bt = board_info[0][10]
        rt = board_info[0][10]
        lt = board_info[0][10]
        for i in range(7):
            tr = ((tr & not_hfile & not_8rank & ~b_tot_bitboard) << 7) & ~w_tot_bitboard
            top_right = top_right | tr

            tl = ((tl & not_afile & not_8rank & ~b_tot_bitboard) << 9) & ~w_tot_bitboard
            top_left = top_left | tl

            br = ((br & not_hfile & not_1rank & ~b_tot_bitboard) >> 9) & ~w_tot_bitboard
            bot_right = bot_right | br

            bl = ((bl & not_afile & not_1rank & ~b_tot_bitboard) >> 7) & ~w_tot_bitboard
            bot_left = bot_left | bl

            tp = ((tp & not_8rank & ~b_tot_bitboard) << 8) & ~w_tot_bitboard
            top = top | tp

            bt = ((bt & not_1rank & ~b_tot_bitboard) >> 8) & ~w_tot_bitboard
            bot = bot | bt

            rt = ((rt & not_hfile & ~b_tot_bitboard) >> 1) & ~w_tot_bitboard
            right = right | rt

            lt = ((lt & not_afile & ~b_tot_bitboard) << 1) & ~w_tot_bitboard
            left = left | lt

    else:
        tr = board_info[0][4]
        tl = board_info[0][4]
        br = board_info[0][4]
        bl = board_info[0][4]
        tp = board_info[0][4]
        bt = board_info[0][4]
        rt = board_info[0][4]
        lt = board_info[0][4]
        for i in range(7):
            tr = ((tr & not_hfile & not_8rank & ~w_tot_bitboard) << 7) & ~b_tot_bitboard
            top_right = top_right | tr

            tl = ((tl & not_afile & not_8rank & ~w_tot_bitboard) << 9) & ~b_tot_bitboard
            top_left = top_left | tl

            br = ((br & not_hfile & not_1rank & ~w_tot_bitboard) >> 9) & ~b_tot_bitboard
            bot_right = bot_right | br

            bl = ((bl & not_afile & not_1rank & ~w_tot_bitboard) >> 7) & ~b_tot_bitboard
            bot_left = bot_left | bl

            tp = ((tp & not_8rank & ~w_tot_bitboard) << 8) & ~b_tot_bitboard
            top = top | tp

            bt = ((bt & not_1rank & ~w_tot_bitboard) >> 8) & ~b_tot_bitboard
            bot = bot | bt

            rt = ((rt & not_hfile & ~w_tot_bitboard) >> 1) & ~b_tot_bitboard
            right = right | rt

            lt = ((lt & not_afile & ~w_tot_bitboard) << 1) & ~b_tot_bitboard
            left = left | lt

    board_info[12] = bot_left | bot_right | top_right | top_left | bot | top | right | left

    return board_info

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
    board_info = pawn_moves(board_info)
    # board_info = king_moves(board_info)
    # # board_info = knight_moves(board_info)
    # board_info = bishop_moves(board_info)
    # board_info = rook_moves(board_info)
    # board_info = queen_moves(board_info)
    return board_info

def piece_count(board_info:list)->float:
    pieces = board_info[0]
    piece_count = 0.0
    piece_count += float(pieces[6].bit_count())
    piece_count -= float(pieces[0].bit_count())
    piece_count += 5 * float(pieces[7].bit_count())
    piece_count -= 5 * float(pieces[1].bit_count())
    piece_count += 3 * float(pieces[8].bit_count())
    piece_count -= 3 * float(pieces[2].bit_count())
    piece_count += 3 * float(pieces[9].bit_count())
    piece_count -= 3 * float(pieces[3].bit_count())
    piece_count += 9 * float(pieces[10].bit_count())
    piece_count -= 9 * float(pieces[4].bit_count())
    piece_count += 300 * float(pieces[11].bit_count())
    piece_count -= 300 * float(pieces[5].bit_count())
    return piece_count

def eval(board_info:list)->str:
    evaluation = 0.0
    evaluation += piece_count(board_info)
    if evaluation>=150:
        return 'M'
    elif evaluation<=-150:
        return '-M'
    else:
        return str(evaluation)

# @jit
def move(move,board_info):


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
    move = (2 ** board_sqrs_dict[move[:2]],2 ** board_sqrs_dict[move[2:4]],move[-1])


    if move[0] & (board_info[0][11] | board_info[0][5]) != 0:
        move_king(move, board_info)
        return board_info
    elif move[0] & (board_info[0][10] | board_info[0][4]) != 0:
        move_queen(move,board_info)
        pass
    elif move[0] & (board_info[0][9] | board_info[0][3]) != 0:
        move_bishop(move,board_info)
        return board_info
    elif move[0] & (board_info[0][8] | board_info[0][2]) != 0:
        move_knight(move,board_info)
        pass
    elif move[0] & (board_info[0][7] | board_info[0][1]) != 0:
        move_rook(move,board_info)
        pass
    elif move[0] & (board_info[0][6] | board_info[0][0]) != 0:
        move_pawn(move, board_info)
        return board_info
    else:
        print('error')

