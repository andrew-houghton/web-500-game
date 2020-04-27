var connectionEnabled = true;

function showScreen(screenName) {
    document.getElementById("connectionDetails").hidden = "connectionDetails" !== screenName;
    document.getElementById("gamesDetails").hidden = "gamesDetails" !== screenName;
    document.getElementById("waitingDetails").hidden = "waitingDetails" !== screenName;
    document.getElementById("gameContainer").hidden = "gameContainer" !== screenName;
}

function setupSocketHandlers(socket) {
    socket.on('lobby games', (games) => {
        showScreen("gamesDetails")
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

    document.getElementById("createGameButton").onclick = function(event) {socket.emit('lobby create');};
    document.getElementById("leaveGameButton").onclick = function(event) {socket.emit('lobby exit');};

    socket.on('lobby waiting', (players) => {
        showScreen("waitingDetails")
        waitingPlayersList = document.getElementById("waitingPlayersList")
        waitingPlayersList.innerHTML = '';
        for (let i = 0; i < players.length; i++) {
            listItem = document.createElement('li');
            listItem.textContent = players[i];
            waitingPlayersList.appendChild(listItem);
        }
    });

    socket.on('deal', (playerHand) => {
        showScreen("gameContainer")
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