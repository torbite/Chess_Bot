
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess.chess_functions as chess_functions
import chess.botV2 as bot

app = Flask(__name__)
CORS(app)

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "hello world"})

@app.route("/get_game", methods=["POST"])
def get_game():
    data = request.json
    print(data)
    name = data.get("matchname", "default")
    
    game = chess_functions.load_game(name)

    return jsonify(chess_functions.get_fancy_game(game))

@app.route("/move_piece", methods=["POST"])
def move_piece():
    data = request.json
    print(data)
    # print("aaah")
    matchname = data.get("matchname", "default")
    move_pos1, move_pos2 = data.get("move_positions", ['a1','a1'])
    print(move_pos1, flush=True)
    print(move_pos2, flush=True)
    move = (move_pos1, move_pos2)
    game = chess_functions.load_game(matchname)
    game = chess_functions.move_piece(game, move)
    chess_functions.save_game(game, matchname)
    game = chess_functions.get_fancy_game(game)

    return jsonify(game)

@app.route("/get_piece_moves", methods=["POST"])
def get_piece_moves():
    data = request.json
    matchname = data.get("matchname", "default")
    piece_pos = data.get("piece_position", 'a1')
    game = chess_functions.load_game(matchname)
    moves = chess_functions.get_piece_moves(game["board"], piece_pos)
    print(moves)
    new_board = game["board"]
    new_board = chess_functions.mark_board(new_board, moves)
    fancy_new_board = chess_functions.get_fancy_board(new_board)
    return jsonify(fancy_new_board)

@app.route("/get_bot_move", methods=["POST"])
def get_bot_move():
    data = request.json
    matchname = data.get("matchname", "default")
    game = chess_functions.load_game(matchname)
    if not game:
        return jsonify({"error": "MATCH_NOT_FOUND"}), 404

    possible_moves = bot.get_all_possible_moves(game)
    if not possible_moves:
        return jsonify({"error": "NO_MOVES_AVAILABLE"}), 409

    bot_move = bot.get_bot_move(game)
    game = chess_functions.move_piece(game, bot_move)
    chess_functions.save_game(game, matchname)

    fancy_game = chess_functions.get_fancy_game(game)

    def position_to_coordinate(position):
        if isinstance(position, str):
            return position
        files = "abcdefgh"
        file_index = position % 8
        rank_index = position // 8 + 1
        return f"{files[file_index]}{rank_index}"

    fancy_game["last_move"] = {
        "from": position_to_coordinate(bot_move[0]),
        "to": position_to_coordinate(bot_move[1]),
    }
    return jsonify(fancy_game)
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)