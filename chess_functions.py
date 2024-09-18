import typing

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

