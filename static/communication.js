var connectionEnabled = true;

function setupSocketHandlers(socket) {
    socket.on('connection', function() {
        console.log("Connected")
    });
    socket.on('games', (msg) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = false;
        console.log("// TODO populate games list");
    });
    document.getElementById("createGameButton").onclick = function(event) {
        console.log("Creating game")
        socket.emit('create game')
    };
    socket.on('waiting', (players) => {
        document.getElementById("gamesDetails").hidden = true;
        document.getElementById("waitingDetails").hidden = false;
        waitingPlayersList = document.getElementById("waitingPlayersList")
        for (let i = 0; i < players.length; i++) {
            listItem = document.createElement('li');
            listItem.innerHTML = players[i];
            waitingPlayersList.appendChild(listItem);
        }
    });
}

function lobbyConnect() {
    if (connectionEnabled) {
        name = document.getElementById("playerNameInput").value
        if (name.trim().length > 1) {
            console.log("Connecting " + name.trim())
            socket = io({ query: { playerName: name.trim() } });
            setupSocketHandlers(socket)
        }
        connectionEnabled = false;
    }
}