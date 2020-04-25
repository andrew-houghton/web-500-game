var connectionEnabled = true;

function setupSocketHandlers(socket) {
    socket.on('games', (games) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = false;
        document.getElementById("waitingDetails").hidden = true;

        gamesList = document.getElementById("gamesList")
        gamesList.innerHTML = '';
        for (let i = 0; i < games.length; i++) {
            listItem = document.createElement('li');
            listItem.textContent = games[i].name + ' - ' + games[i].spots;
            listItem.onclick = function(event) {
                socket.emit('join game', games[i].id);
            };
            gamesList.appendChild(listItem);

        }
    });

    document.getElementById("createGameButton").onclick = function(event) {
        socket.emit('create game')
    };

    document.getElementById("leaveGameButton").onclick = function(event) {
        socket.emit('exit waiting');
    };

    socket.on('waiting', (players) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = true;
        document.getElementById("waitingDetails").hidden = false;
        waitingPlayersList = document.getElementById("waitingPlayersList")
        waitingPlayersList.innerHTML = '';
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
            socket = io({ query: { playerName: name.trim() } });
            setupSocketHandlers(socket)
        }
        connectionEnabled = false;
    }
}