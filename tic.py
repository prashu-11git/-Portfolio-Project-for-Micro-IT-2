from flask import Flask, render_template, request, jsonify
import random  # For a simple AI, not Minimax

app = Flask(__name__)

# Initial game state
# 0: empty, 1: Player X (Human), 2: Player O (Computer)
game_board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
current_player = 1  # 1 for X (Human), 2 for O (Computer)
game_over = False
winner = None  # 0 for draw, 1 for X, 2 for O, None for not over

# Winning combinations (indices on the board)
WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
    [0, 4, 8], [2, 4, 6]  # Diagonals
]


@app.route('/')
def index():
    global game_board, current_player, game_over, winner
    # Reset game state when homepage is loaded
    game_board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    current_player = 1  # Human starts as Player X
    game_over = False
    winner = None
    return render_template('index.html')


@app.route('/make_move', methods=['POST'])
def make_move():
    global game_board, current_player, game_over, winner

    if game_over:
        return jsonify({"status": "game_over", "message": "Game is already over."}), 400

    data = request.get_json()
    cell_index = data.get('cell_index')

    if cell_index is None or not (0 <= cell_index < 9):
        return jsonify({"status": "error", "message": "Invalid cell index."}), 400

    if game_board[cell_index] != 0:
        return jsonify({"status": "invalid_move", "message": "Cell already taken."}), 400

    # Human's move
    game_board[cell_index] = current_player  # This will be 1 (X)

    # Check game status after human's move
    check_game_status()

    # If game not over, let computer make a move
    if not game_over:
        current_player = 2  # Switch to computer's turn
        computer_move()
        check_game_status()  # Check game status after computer's move
        if not game_over:
            current_player = 1  # Switch back to human's turn

    return jsonify({
        "status": "success",
        "board": game_board,
        "current_player": current_player,  # This will be 1 (Human) for the next turn if game is not over
        "game_over": game_over,
        "winner": winner
    })


@app.route('/reset_game', methods=['POST'])
def reset_game():
    global game_board, current_player, game_over, winner
    game_board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    current_player = 1  # Human starts
    game_over = False
    winner = None
    return jsonify({
        "status": "success",
        "board": game_board,
        "current_player": current_player,
        "game_over": game_over,
        "winner": winner
    })


def check_game_status():
    global game_over, winner

    # Check for a win
    for condition in WIN_CONDITIONS:
        a, b, c = condition
        if game_board[a] != 0 and \
                game_board[a] == game_board[b] and \
                game_board[a] == game_board[c]:
            winner = game_board[a]  # 1 for X, 2 for O
            game_over = True
            return

    # Check for a draw
    if 0 not in game_board:
        winner = 0  # 0 signifies a draw
        game_over = True
        return


def computer_move():
    global game_board, game_over

    if game_over:
        return

    # --- Simple AI Logic (Can be replaced with Minimax for an unbeatable AI) ---
    # 1. Try to win
    for condition in WIN_CONDITIONS:
        p1, p2, p3 = condition
        # Check if computer can win
        if game_board[p1] == 2 and game_board[p2] == 2 and game_board[p3] == 0:
            game_board[p3] = 2
            return
        if game_board[p1] == 2 and game_board[p3] == 2 and game_board[p2] == 0:
            game_board[p2] = 2
            return
        if game_board[p2] == 2 and game_board[p3] == 2 and game_board[p1] == 0:
            game_board[p1] = 2
            return

    # 2. Block human
    for condition in WIN_CONDITIONS:
        p1, p2, p3 = condition
        # Check if human can win and block them
        if game_board[p1] == 1 and game_board[p2] == 1 and game_board[p3] == 0:
            game_board[p3] = 2
            return
        if game_board[p1] == 1 and game_board[p3] == 1 and game_board[p2] == 0:
            game_board[p2] = 2
            return
        if game_board[p2] == 1 and game_board[p3] == 1 and game_board[p1] == 0:
            game_board[p1] = 2
            return

    # 3. Take center if available
    if game_board[4] == 0:
        game_board[4] = 2
        return

    # 4. Take a corner if available
    corners = [0, 2, 6, 8]
    available_corners = [c for c in corners if game_board[c] == 0]
    if available_corners:
        game_board[random.choice(available_corners)] = 2
        return

    # 5. Take any available side
    sides = [1, 3, 5, 7]
    available_sides = [s for s in sides if game_board[s] == 0]
    if available_sides:
        game_board[random.choice(available_sides)] = 2
        return

    # Fallback (shouldn't happen in a valid game but good for robustness)
    empty_cells = [i for i, val in enumerate(game_board) if val == 0]
    if empty_cells:
        game_board[random.choice(empty_cells)] = 2


if __name__ == '__main__':
    app.run(debug=True)