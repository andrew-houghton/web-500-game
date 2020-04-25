from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, logger=True, engineio_logger=True)


@app.route("/")
def hello_world():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    print(f"Player {request.args.get('playerName')} joined")
    emit("games", [])


@socketio.on("create game")
def start_game():
    print(f"Player started a game")
    emit("waiting", ['Jeff', 'James'])


if __name__ == "__main__":
    socketio.run(app, debug=True)
