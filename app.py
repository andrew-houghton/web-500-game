from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from game import deal


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, logger=True, engineio_logger=True)


player_names = {}
games = {}
game_room = set()
current_game = {}
hands = {}


def get_games_to_display():
    games_to_display = []
    for owner, players in games.items():
        spots = 5 - len(players)
        if spots > 0:
            games_to_display.append(
                {
                    "id": owner,
                    "spots": f"{spots} spot{'s' if spots > 1 else ''} left",
                    "name": f"{player_names[owner]}'s game",
                }
            )
    return games_to_display


@app.route("/")
def hello_world():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    player_names[request.sid] = request.args.get("playerName")
    emit("games", get_games_to_display())
    game_room.add(request.sid)


def update_game_room():
    games_to_display = get_games_to_display()
    for sid in game_room:
        emit("games", games_to_display, room=sid)


def update_waiting_players(game_id):
    waiting_players = [player_names[sid] for sid in games[game_id]]
    for player in games[game_id]:
        emit("waiting", waiting_players, room=player)


def remove_player_from_game(sid):
    games[current_game[sid]].remove(sid)
    update_waiting_players(current_game[sid])
    if current_game[sid] == sid:
        players = games[current_game[sid]]
        if len(players) > 0:
            games[players[0]] = players
            for player_id in players:
                current_game[player_id] = players[0]
        del games[sid]


@socketio.on("disconnect")
def test_disconnect():
    if request.sid in game_room:
        game_room.remove(request.sid)
    if request.sid in current_game:
        remove_player_from_game(request.sid)
        del current_game[request.sid]
    if request.sid in player_names:
        del player_names[request.sid]


@socketio.on("create game")
def start_game(): 
    game_room.remove(request.sid)
    games[request.sid] = [request.sid]
    current_game[request.sid] = request.sid
    emit("waiting", [player_names[sid] for sid in games[request.sid]])
    update_game_room()


@socketio.on("join game")
def join_game(game_id):
    print(game_id)
    game_room.remove(request.sid)
    games[game_id].append(request.sid)
    current_game[request.sid] = game_id
    if len(games[game_id]) < 2:
        update_waiting_players(game_id)
    else:
        player_hands, kitty = deal()
        hands[game_id] = (player_hands, kitty)
        for player, hand in zip(games[game_id], player_hands):
            emit("begin", hand, room=player)


@socketio.on("exit waiting")
def exit_waiting():
    game_room.add(request.sid)
    remove_player_from_game(request.sid)
    update_game_room()


if __name__ == "__main__":
    socketio.run(app, debug=True)
