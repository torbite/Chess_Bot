import chess.chess_functions as chess_functions, os


# chess.raw_move_piece(board, "g1","b4")
# chess.raw_move_piece(board, "b1","e5")
# moves = chess.get_piece_moves(board, "e5")
# print(moves)
# chess.mark_board(board, moves)

# # print()
# chess.render_board(board)


game = chess_functions.load_game()
board = game["board"]
# chess.raw_move_piece(board, 'e1', 'e4')

while True:
    os.system("clear")
    chess_functions.render_board(board)
    print(game["turn"])
    print(game["moves"])
    p1 = input("FROM -> ")
    if p1 == "rst" or p1 == 'r':
        game = chess_functions.create_game()
        board = game["board"]
        chess_functions.save_game(game)
        continue
    elif p1 == "u" or p1 == "un":
        game = chess_functions.unmove_piece(game)
        board = game["board"]
        chess_functions.save_game(game)
    if len(p1) != 2:
        continue
    moves = chess_functions.get_piece_moves(board, p1)
    if not moves:
        continue
    os.system("clear")
    chess_functions.render_board_with_marks(board, moves)

    p2 = input("TO   -> ")

    if len(p2) != 2:
        continue
    move = (p1, p2)
    chess_functions.move_piece(game, move)
    chess_functions.save_game(game)
