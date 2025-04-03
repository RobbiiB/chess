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

def eval(board_info:list)->int:
    evaluation = 0.0
    evaluation += piece_count(board_info)
    return evaluation

