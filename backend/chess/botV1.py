import copy, time, os, random
from chess.chess_functions import *

ALL_PIECES = [Piece.BISHOP, Piece.KING, Piece.KNIGHT, Piece.PAWN, Piece.QUEEN, Piece.ROOK]
PIECES_POINTS = {
    Piece.BISHOP : 4,
    Piece.KING : 10, 
    Piece.KNIGHT : 3, 
    Piece.PAWN : 1, 
    Piece.QUEEN : 6, 
    Piece.ROOK : 5
}

def max_indices(arr):
    if not arr:
        return []
    m = max(arr)
    return [i for i, v in enumerate(arr) if v == m]

def count_points(board, turn):
    total_points = 0
    for p in ALL_PIECES:
        points = PIECES_POINTS[p]
        colpiece = p | turn
        amount = board.count(colpiece)
        total_points += points * amount
    return total_points

def piece_positions(board, turn):
    if len(board) != 64:
        raise ValueError("board must be a list of 64 elements")

    encoded_set = {p | turn for p in ALL_PIECES}
    positions = [idx for idx, cell in enumerate(board) if cell in encoded_set]
    return positions

def get_all_possible_moves(game):
    turn = game["turn"]
    board = game["board"]
    
    all_pieces_positions = piece_positions(board, turn)
    all_moves = []
    for p in all_pieces_positions:
        all_moves.extend([p, i] for i in get_piece_moves(board, p))
    
    return all_moves
    
def recursive_possible_moves(game, move, main_turn = Colour.WHITE,fund = 2):
    if fund <= 0:
        return count_points(game["board"], main_turn) - count_points(game["board"], Colour.BLACK if Colour.WHITE == main_turn else Colour.WHITE)
    move_piece(game, move)
    current_turn = game["turn"]
    allie = get_all_possible_moves(game)
    total = []
    for move in allie:
        total.append(recursive_possible_moves(game, move, main_turn=main_turn, fund=fund-1))
    unmove_piece(game)
    return max(total) if current_turn == main_turn else min(total)

def get_bot_move(game, main_turn):
    allie = get_all_possible_moves(game)
    # print(allie)
    tot = []
    for m in allie:
        tot.append(recursive_possible_moves(game, m, main_turn=main_turn, fund=3))
    maximuns = max_indices(tot)
    move_index = random.choice(maximuns)
    return allie[move_index]


if __name__ == "__main__":
    game = create_game()

    board = game["board"]
    while True:
        a = input("----")
        if a != "":
            unmove_piece(game)
        else:
            move = get_bot_move(game, game["turn"])
            move_piece(game, move)
        os.system("clear")
        render_board(board)


    
