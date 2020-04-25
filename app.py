from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, logger=True, engineio_logger=True)


player_names = {}
games = {}


@app.route("/")
def hello_world():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    print(f"Player {request.args.get('playerName')} joined")
    player_names[request.sid] = request.args.get("playerName")

    games_to_display = []
    for owner, players in games.items():
        spots = 5 - len(players)
        games_to_display.append(
            {
                "id": owner,
                "spots": f"{spots} spot{'s' if spots > 1 else ''} left",
                "name": f"{player_names[owner]}'s game",
            }
        )

    emit("games", games_to_display)


@socketio.on('disconnect')
def test_disconnect():
    if request.sid in player_names:
        del player_names[request.sid]
    for owner, players in games.items():
        if request.sid in players:
            players.remove(request.sid)
        if owner == request.sid:
            if len(players) > 0:
                games[players[0]] = players
                del games[request.sid]
            else:
                del games[request.sid]


@socketio.on("create game")
def start_game():
    print(f"Player started a game")
    games[request.sid] = [request.sid]
    emit("waiting", [player_names[sid] for sid in games[request.sid]])


if __name__ == "__main__":
    socketio.run(app, debug=True)
