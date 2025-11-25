from enum import IntEnum
from chess.utils import get_hv_rules
import json, copy

BOARDS_PATH = "/Users/tiagocastroorbite/Tiago/Python/2025-files/chess_botsie/backend/boards"

BOARD_SIZE = 64

INTERVALS = [0, 8, 16, 24, 32, 40, 48, 56, 64]
INTERVALS_AMOUNT = len(INTERVALS)

COLOUR_BITS = 0b11000
PIECE_BITS = 0b111
SPECIAL_MARK_BITS = 0b100000

IDS_TO_PIECES = {
    1 : "P",
    2 : "N",
    3 : "B",
    4 : "R",
    5 : "Q",
    6 : "K",
    0 : ""
}

IDS_TO_COLOUR = {
    0b01000 : "b",
    0b10000 : "w",
    0 : ""
}

IDS_TO_SPECIAL_MARK = {
    0b100000 : "X",
    0 : ""
}

EMPTY = 0b0

class Piece(IntEnum):
    PAWN = 0b001
    KNIGHT = 0b010
    BISHOP = 0b011
    ROOK = 0b100
    QUEEN = 0b101
    KING = 0b110


class Colour(IntEnum):
    BLACK = 0b01000
    WHITE = 0b10000


TOP_ROW = [i for i in range(64-8, 64)]
BOTTOM_ROW = [i for i in range(8)]
LEFT_ROW = [i*8 for i in range(8)]
RIGHT_ROW = [(i*8 + 7) for i in range(8)]

KNIGHT_TOP_ROW = [i - 8 for i in TOP_ROW]
KNIGHT_BOTTOM_ROW = [i + 8 for i in BOTTOM_ROW]
KNIGHT_LEFT_ROW = [i + 1 for i in LEFT_ROW]
KNIGHT_RIGHT_ROW = [i - 1 for i in RIGHT_ROW]


# ------------------------------------------------------------------------------------------ #
# --------------------------------- BOARD VISUALIZATION ------------------------------------ #
# ------------------------------------------------------------------------------------------ #

def mark_board(board, positions):
    for p in positions:
        # print(board[p])
        board[p] = board[p] | SPECIAL_MARK_BITS
        # print(board[p])
        # input()
    return board

def get_piece_notation(piece):
    piece_bits = piece & PIECE_BITS
    colour_bits = piece & COLOUR_BITS
    special_mark_bits = piece & SPECIAL_MARK_BITS
    return f'{IDS_TO_COLOUR[colour_bits]}{IDS_TO_PIECES[piece_bits]}{IDS_TO_SPECIAL_MARK[special_mark_bits]}'

def get_fancy_board(board):
    new_board = [get_piece_notation(i) for i in board]

    render_board = new_board
    rows = []
    for i in range(INTERVALS_AMOUNT):
        if i + 1 >= INTERVALS_AMOUNT:
            break
        n1 = INTERVALS[i]
        n2 = INTERVALS[i + 1]
        rows.append(render_board[n1:n2])

    
    render_rows = rows[::-1]
    return render_rows

def render_board(board):
    fancy_board = get_fancy_board(board)
    for row in fancy_board:
        fancy_row = ""
        for item in row:
            length = len(item)
            match length:
                case 0:
                    fancy_row += f'|    '
                case 1:
                    fancy_row += f'|  {item} '
                case 2:
                    fancy_row += f'| {item} '
                case 3:
                    fancy_row += f'| {item}'
        fancy_row += '|'
        print(fancy_row)
        print('-----------------------------------------')

def render_board_with_marks(board, positions):
    b = copy.deepcopy(board)
    mark_board(b, positions)
    render_board(b)

def get_fancy_game(game):
    game["turn"] = IDS_TO_COLOUR[game["turn"]]
    game["board"] = get_fancy_board(game["board"])
    return game



# ------------------------------------------------------------------------------------------ #
# --------------------------------- BOARD CREATION ----------------------------------------- #
# ------------------------------------------------------------------------------------------ #



def load_game(matchname = "default"):
    try:
        with open(f"{BOARDS_PATH}/{matchname}.json", 'r') as arq:
            game = json.load(arq)
    except Exception as e:
        print(e)
        game = None
    return game


def create_game(matchname = "default"):
    board = [EMPTY for i in range(64)]
    # White back rank (a1-h1)
    board[0:8] = [Colour.WHITE | Piece.ROOK, Colour.WHITE | Piece.KNIGHT, 
                  Colour.WHITE | Piece.BISHOP, Colour.WHITE | Piece.QUEEN,
                  Colour.WHITE | Piece.KING, Colour.WHITE | Piece.BISHOP,
                  Colour.WHITE | Piece.KNIGHT, Colour.WHITE | Piece.ROOK]
    # White pawns (a2-h2)
    board[8:16] = [Colour.WHITE | Piece.PAWN] * 8
    # Black pawns (a7-h7)
    board[48:56] = [Colour.BLACK | Piece.PAWN] * 8
    # Black back rank (a8-h8)
    board[56:64] = [Colour.BLACK | Piece.ROOK, Colour.BLACK | Piece.KNIGHT,
                    Colour.BLACK | Piece.BISHOP, Colour.BLACK | Piece.QUEEN,
                    Colour.BLACK | Piece.KING, Colour.BLACK | Piece.BISHOP,
                    Colour.BLACK | Piece.KNIGHT, Colour.BLACK | Piece.ROOK]
    
    game = {
        "board" : board,
        "turn" : Colour.WHITE,
        "moves": []
    }

    with open(f"{BOARDS_PATH}/{matchname}.json", "w") as mn:
        mn.write(json.dumps(game))
    return game

def save_game(game, matchname = "default"):
    with open(f"{BOARDS_PATH}/{matchname}.json", "w") as mn:
        mn.write(json.dumps(game))
    return game



# ------------------------------------------------------------------------------------------ #
# ------------------------------- GAME MANIPULATION ---------------------------------------- #
# ------------------------------------------------------------------------------------------ #



def get_position(string_pos):
    """
    string_pos : 'a1' -> 0
    """
    letter_numbers = list("abcdefgh")
    letter = letter_numbers.index(string_pos[0])
    number = int(string_pos[1])
    pos = letter + (number-1)*8
    return pos

def raw_move_piece(board, move):
    """
    board : list,
    initial_position_str : str 'a1' OR raw number pos,
    initial_position_str : str 'a2' OR OR raw number pos
    """
    
    initial_pos = get_position(move[0]) if isinstance(move[0], str) else move[0]
    final_pos = get_position(move[1]) if isinstance(move[1], str) else move[1]

    piece = board[initial_pos]

    board[final_pos] = piece
    board[initial_pos] = EMPTY
    return board

def get_moves_by_rules(board, colour, rules):
    _moves = []
    
    for range_rule in rules:
        for i in range_rule:
            if board[i] != EMPTY:
                i_colour = board[i] & COLOUR_BITS
                if i_colour != colour:
                    _moves.append(i)
                    break
                break        
            _moves.append(i)
    return _moves


def get_piece_moves(board, piece_position):
    """
    board : list,
    piece_position : str 'a1' OR raw number pos
    """
    bit_pos = get_position(piece_position) if isinstance(piece_position, str) else piece_position
    full_piece = board[bit_pos]
    prime_piece_colour = full_piece & COLOUR_BITS
    prime_piece_type = full_piece & PIECE_BITS
    moves = []

    match prime_piece_type:
        case Piece.PAWN:

            if prime_piece_colour == Colour.WHITE:
                last_row = TOP_ROW
                tl_off = 7
                tr_off = 9
                up_off = 8
            else:
                last_row = BOTTOM_ROW
                tl_off = -9
                tr_off = -7
                up_off = -8

            if bit_pos in last_row:
                return []
            top_square = bit_pos + up_off
            top_piece = board[top_square]
            if top_piece == EMPTY:
                moves.append(top_square)

            if bit_pos not in LEFT_ROW:
                top_left = bit_pos + tl_off
                tl_piece = board[top_left]
                if tl_piece != EMPTY and (tl_piece & COLOUR_BITS) != prime_piece_colour:
                    moves.append(top_left)

            if bit_pos not in RIGHT_ROW:
                top_right = bit_pos + tr_off
                tr_piece = board[top_right]
                if tr_piece != EMPTY and (tr_piece & COLOUR_BITS) != prime_piece_colour:
                    moves.append(top_right)
        
        case Piece.ROOK:
            hor, vert, _ = get_hv_rules(bit_pos)
            total_rules = [*hor, *vert]
            moves = get_moves_by_rules(board, prime_piece_colour, total_rules)
        
        case Piece.BISHOP:
            _, _, diags = get_hv_rules(bit_pos)
            moves = get_moves_by_rules(board, prime_piece_colour, diags)
        
        case Piece.QUEEN:
            hor, vert, diags = get_hv_rules(bit_pos)
            total_rules = [*hor, *vert, *diags]
            moves = get_moves_by_rules(board, prime_piece_colour, total_rules)
        
        case Piece.KING:
            hor, vert, diags = get_hv_rules(bit_pos, limit_range=True)
            total_rules = [*hor, *vert, *diags]
            moves = get_moves_by_rules(board, prime_piece_colour, total_rules)
        
        case Piece.KNIGHT:
            KNIGHT_OFFSETS = [15,17,6,10, -15,-17,-6,-10]

            moves_to_remove = []

            if bit_pos in TOP_ROW:
                moves_to_remove.extend([15, 16, 6, 10])
            elif bit_pos in KNIGHT_TOP_ROW:
                moves_to_remove.extend([15, 16])
            elif bit_pos in BOTTOM_ROW:
                moves_to_remove.extend([-15, -16, -6, -10])
            elif bit_pos in KNIGHT_BOTTOM_ROW:
                moves_to_remove.extend([-15, -16])
            
            if bit_pos in LEFT_ROW:
                moves_to_remove.extend([15, 6, -17, -10])
            elif bit_pos in KNIGHT_LEFT_ROW:
                moves_to_remove.extend([6, -10])
            elif bit_pos in RIGHT_ROW:
                moves_to_remove.extend([-15, -6, 17, 10])
            elif bit_pos in KNIGHT_RIGHT_ROW:
                moves_to_remove.extend([-6, 10])
            
            for mv in moves_to_remove:
                if mv in KNIGHT_OFFSETS:
                    KNIGHT_OFFSETS.remove(mv)
            moves = []

            for move in KNIGHT_OFFSETS:
                move_pos = bit_pos + move
                if move_pos < 0 or move_pos > 63:
                    continue
                piece_colour_in_pos = board[move_pos] & COLOUR_BITS
                if piece_colour_in_pos == prime_piece_colour:
                    continue
                moves.append(move_pos)
        
    return moves


def move_piece(game, move):
    board = game["board"]
    initial_position_str = move[0]
    final_position_str = move[1]
    initial_pos = get_position(initial_position_str) if isinstance(initial_position_str, str) else initial_position_str
    final_pos = get_position(final_position_str) if isinstance(final_position_str, str) else final_position_str
    piece_colour = board[initial_pos] & COLOUR_BITS

    if piece_colour != game["turn"]:

        print("WRONG TURN")
        render_board(board)
        raise ValueError("WRONG TURN ERROR")
        input()
        return game

    possible_moves = get_piece_moves(board, initial_pos)
    if final_pos in possible_moves:
        game["moves"].append((move, (board[initial_pos], board[final_pos])))
        board = raw_move_piece(board, (initial_pos, final_pos))
        game["turn"] = Colour.BLACK if game["turn"] == Colour.WHITE else Colour.WHITE
    return game

def unmove_piece(game):
    if len(game["moves"]) < 1:
        return game
    lastmove = game["moves"][-1]
    unmove = (lastmove[1], lastmove[0])
    # game["board"] = raw_move_piece(game["board"], unmove)
    game["board"][lastmove[0][0]] = lastmove[1][0]
    game["board"][lastmove[0][1]] = lastmove[1][1]
    game["turn"] = Colour.BLACK if game["turn"] == Colour.WHITE else Colour.WHITE
    game["moves"].pop(-1)
    return game

