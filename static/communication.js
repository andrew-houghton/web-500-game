var connectionEnabled = true;

function setupSocketHandlers(socket) {
    socket.on('lobby games', (games) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = false;
        document.getElementById("waitingDetails").hidden = true;
        document.getElementById("gameContainer").hidden = true;

        gamesList = document.getElementById("gamesList")
        gamesList.innerHTML = '';
        for (let i = 0; i < games.length; i++) {
            listItem = document.createElement('li');
            listItem.textContent = games[i].name + ' - ' + games[i].spots;
            listItem.onclick = function(event) {
                socket.emit('lobby join', games[i].id);
            };
            gamesList.appendChild(listItem);

        }
    });

    document.getElementById("createGameButton").onclick = function(event) {
        socket.emit('lobby create');
    };

    document.getElementById("leaveGameButton").onclick = function(event) {
        socket.emit('lobby exit');
    };

    socket.on('lobby waiting', (players) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = true;
        document.getElementById("waitingDetails").hidden = false;
        document.getElementById("gameContainer").hidden = true;
        waitingPlayersList = document.getElementById("waitingPlayersList")
        waitingPlayersList.innerHTML = '';
        for (let i = 0; i < players.length; i++) {
            listItem = document.createElement('li');
            listItem.textContent = players[i];
            waitingPlayersList.appendChild(listItem);
        }
    });

    socket.on('deal', (playerHand) => {
        document.getElementById("connectionDetails").hidden = true;
        document.getElementById("gamesDetails").hidden = true;
        document.getElementById("waitingDetails").hidden = true;
        document.getElementById("gameContainer").hidden = false;
        drawHand(playerHand, 0);
        for (let i = 1; i < 5; i++) {
            drawHand(Array(10).fill("back"), i);
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