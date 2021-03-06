import os
import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from game.game import Game


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('FLASK_SECRET_KEY', uuid.uuid4().hex)
socketio = SocketIO(app, logger=True)

games = []
player_names = {}
player_games = {}
game_room = set()


@app.route("/")
def hello_world():
    return render_template("index.html")


def get_games_to_display():
    games_to_display = []
    for i in range(len(games)):
        game = games[i]
        spots = 5 - len(game.player_sids)
        if spots > 0:
            games_to_display.append(
                {
                    "id": i,
                    "spots": f"{spots} spot{'s' if spots > 1 else ''} left",
                    "name": f"{player_names[game.owner]}'s game",
                }
            )
    return games_to_display


@socketio.on("connect")
def connect():
    player_names[request.sid] = request.args.get("playerName")
    emit("lobby games", get_games_to_display())
    game_room.add(request.sid)


def update_game_room():
    games_to_display = get_games_to_display()
    for sid in game_room:
        emit("lobby games", games_to_display, room=sid)


def player_leaving_game(sid):
    if sid in player_games:
        game = player_games[sid]
        game.remove_player(sid)
        if len(game.player_sids) == 0 and game in games:
            games.remove(game)
        del player_games[sid]
        update_game_room()


@socketio.on("disconnect")
def test_disconnect():
    if request.sid in game_room:
        game_room.remove(request.sid)
    player_leaving_game(request.sid)
    if request.sid in player_names:
        del player_names[request.sid]


@socketio.on("lobby create")
def create_game():
    game_room.remove(request.sid)
    game = Game()
    games.append(game)
    game.add_player(request.sid, player_names[request.sid])
    player_games[request.sid] = game
    update_game_room()


@socketio.on("lobby join")
def join_game(game_id):
    game = games[game_id]
    if len(game.player_sids) < 5:
        player_games[request.sid] = game
        game_room.remove(request.sid)
        game.add_player(request.sid, player_names[request.sid])
        update_game_room()


@socketio.on("lobby exit")
def exit_waiting():
    game_room.add(request.sid)
    player_leaving_game(request.sid)

@socketio.on("bid")
def bid(bid):
    player_games[request.sid].bid(request.sid, bid)

@socketio.on("lobby begin")
def start_game(scores, partner_mode):
    game = player_games[request.sid]
    if request.sid == game.owner:
        for player, point_score in scores.items():
            if type(point_score) != int or not (-500 < point_score < 500) or player not in '01234':
                return
        player_games[request.sid].points = {int(k):v for k,v in scores.items()}
        player_games[request.sid].partner_mode = partner_mode
        player_games[request.sid].start_round()

@socketio.on("kitty")
def kitty(discarded_kitty, player_data):
    player_games[request.sid].handle_kitty(request.sid, discarded_kitty, player_data)

@socketio.on("play")
def play_card(card):
    player_games[request.sid].play_card(request.sid, card, socketio)

@socketio.on("round again")
def round_again():
    pass

@socketio.on("round ready")
def round_ready():
    pass

if __name__ == "__main__":
    print("Starting")
    socketio.run(app, host="0.0.0.0")
