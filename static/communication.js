var connectionEnabled = true;

function setupSocketHandlers(socket) {
    socket.on('connection', function() {
        console.log("Connected")
    });
    socket.on('games', (games) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = false;
        gamesList = document.getElementById("gamesList")
        for (let i = 0; i < games.length; i++) {
            listItem = document.createElement('li');
            listItem.textContent = games[i].name + ' - ' + games[i].spots;
            gamesList.appendChild(listItem);
        }
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
            listItem.textContent = players[i];
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