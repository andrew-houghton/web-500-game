var connectionEnabled = true;

function showScreen(screenName) {
    document.getElementById("connectionDetails").hidden = "connectionDetails" !== screenName;
    document.getElementById("gamesDetails").hidden = "gamesDetails" !== screenName;
    document.getElementById("waitingDetails").hidden = "waitingDetails" !== screenName;
    document.getElementById("gameContainer").hidden = "gameContainer" !== screenName;
    hideBidSection(true)
}

function hideBidSection(is_bid_section_shown) {
    document.getElementById("bid_section").hidden = is_bid_section_shown;
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

    document.getElementById("createGameButton").onclick = function(event) { socket.emit('lobby create'); };
    document.getElementById("leaveGameButton").onclick = function(event) { socket.emit('lobby exit'); };
    document.getElementById("kittyFinishedButton").onclick = function(event) {
        selected_cards = document.querySelectorAll('img.cardPlayer0.selected');
        if (selected_cards.length != 3) {return;}
        discarded_kitty = Array.from(selected_cards).map(e => e.getAttribute("data"));
        partner_cards = document.querySelectorAll('img.chosen');
        if (partner_cards.length == 0){
            partner_index = 0;
        } else {
            partner_index = parseInt(partner_cards[0].getAttribute("data"));
        }
        document.getElementById("kittyButtonControl").hidden = true;
        socket.emit('kitty', discarded_kitty, partner_index);
    };

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

    socket.on('bid deal', (playerHand, scores, playerNames) => {
        showScreen("gameContainer")
        drawHand(playerHand, 0);

        for (let i = 1; i < 5; i++) {
            drawHand(Array(10).fill("back"), i);
        }

        for (let i=0; i< playerNames.length; i++) {
            var bidTextElement = document.getElementById("player" + i + "Name");
            bidTextElement.textContent = playerNames[i];
        }
    });

    socket.on('bid request', (previousBids, validBids) => {
        hideBidSection(false);
        document.getElementById("bid_button_pass").onclick = function(event) {
            hideBidSection(true);
            socket.emit("bid", "p");
        };
        allBids = ['6s', '6c', '6d', '6h', '6n', '7s', '7c', '7d', '7h', '7n', '8s', '8c', '8d', '8h', '8n', '9s', '9c', '9d', '9h', '9n', '10s', '10c', '10d', '10h', '10n']
        for (let i = 0; i < allBids.length; i++) {
            button = document.getElementById("bid_button_" + allBids[i])
            if (validBids.includes(allBids[i])) {
                button.hidden = false;
                button.onclick = function(event) {
                    hideBidSection(true);
                    socket.emit("bid", allBids[i]);
                };
            } else {
                button.hidden = true;
                button.onclick = null;
            }
        }
        for (let i=0; i< previousBids.length; i++) {
            var bidTextElement = document.getElementById("player" + i + "Bid");
            bidTextElement.textContent = previousBids[i];
        }
    });

    socket.on('bid status', (previousBids, biddingPlayerName) => {
        for (let i=0; i< previousBids.length; i++) {
            var bidTextElement = document.getElementById("player" + i + "Bid");
            bidTextElement.textContent = previousBids[i];
        }
    });

    socket.on('kitty request', (playerHand) => {
        document.getElementById("kittyButtonControl").hidden = false;
        images = drawHand(playerHand, 0);

        // Allow selecting and deselecting cards
        for (let i = 0; i < images.length; i++) {
            images[i].addEventListener('click', function() {
                if (images[i].classList.contains("selected")) {
                    images[i].classList.remove("selected");
                } else if (document.querySelectorAll('img.cardPlayer0.selected').length < 3) {
                    images[i].classList.add("selected");
                }
            });
        }

        // Allow selecting and delesecting opponents
        for (let playerId = 1; playerId < 5; playerId++) {
            document.querySelectorAll('img.cardPlayer' + playerId).forEach(e => e.addEventListener('click', function() {
                if (document.querySelectorAll('img.cardPlayer' + playerId)[0].classList.contains("chosen")) {
                    document.querySelectorAll('img.chosen').forEach(j => j.classList.remove("chosen"))
                } else {
                    document.querySelectorAll('img.chosen').forEach(j => j.classList.remove("chosen"))
                    document.querySelectorAll('img.cardPlayer' + playerId).forEach(j => j.classList.add("chosen"))   
                }
            }));
        }
    });

    socket.on('round status', (status_string, playerHand) => {
        drawHand(playerHand, 0);
        document.getElementById("statusString").textContent = status_string;
    });

    socket.on('play request', (current_trick_cards, hand_sizes, card_validity) => {
        console.log(current_trick_cards)
        console.log(hand_sizes)
        console.log(card_validity)
        document.querySelectorAll('img.trickCardImage').forEach(e => e.remove());
        for (let i = 1; i < 5; i++) {
            drawHand(Array(hand_sizes[i-1]).fill("back"), i);
            if (current_trick_cards[i-1] !== ""){
                drawPlayedCard(current_trick_cards[i-1], i);
            }
        }
        playerCards = document.querySelectorAll('img.cardPlayer0')
        for (let i=0; i < playerCards.length; i++){
            if (card_validity[i]){
                playerCards[i].onclick = function(event) {
                    socket.emit('play', playerCards[i].getAttribute("data"));
                };
                playerCards[i].classList.add("playable")
            }
        }
    });
}

function lobbyConnect() {
    if (connectionEnabled) {
        name = document.getElementById("playerNameInput").value
        if (name.trim().length > 1) {
            connectionEnabled = false;
            socket = io({ query: { playerName: name.trim() } });
            setupSocketHandlers(socket)
        }
    }
}