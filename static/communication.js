var connectionEnabled = true;
var currentHand = null;

function showScreen(screenName) {
    document.getElementById("connectionDetails").hidden = "connectionDetails" !== screenName;
    document.getElementById("gamesDetails").hidden = "gamesDetails" !== screenName;
    document.getElementById("waitingDetails").hidden = "waitingDetails" !== screenName;
    document.getElementById("gameContainer").hidden = "gameContainer" !== screenName;
    document.getElementById("lobbyHeading").hidden = "gameContainer" == screenName;
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
    document.getElementById("createGameButton").onclick = function(event) {
        socket.emit('lobby create');

    };
    document.getElementById("leaveGameButton").onclick = function(event) {
        socket.emit('lobby exit');
    };
    document.getElementById("startGameButton").onclick = function(event) {
        scores = {}
        waitingPlayersListChildren = document.getElementById("waitingPlayersList").children
        for (var i = 0; i < waitingPlayersListChildren.length; i++) {
            scores[i] = parseInt(waitingPlayersListChildren[i].children[0].value)
        }

        try {
            modeSelected = document.querySelector('input[name="partnerMode"]:checked').value;
        } catch (err) {
            return;
        }

        socket.emit('lobby begin', scores, modeSelected);
    };

    document.getElementById("kittyFinishedButton").onclick = function(event) {
        partnerSelectionMode = document.getElementById("kittyCardSelection").hidden;

        selected_cards = document.querySelectorAll('img.cardPlayer0.selected');
        if (selected_cards.length != 3) { return; }
        discarded_kitty = Array.from(selected_cards).map(e => e.getAttribute("data"));

        if (partnerSelectionMode){
            partner_cards = document.querySelectorAll('img.chosen');
            if (partner_cards.length == 0) {
                partner_data = 0;
            } else {
                partner_data = parseInt(partner_cards[0].getAttribute("data"));
            }
        } else {
            try {
                suitSelected = document.querySelector('input[name="suit"]:checked').value;
                numberSelected = document.querySelector('input[name="number"]:checked').value;
            } catch (err) {
                return;
            }
            partner_data = suitSelected + "_" + numberSelected
        }

        document.getElementById("kittyButtonControl").hidden = true;
        socket.emit('kitty', discarded_kitty, partner_data);
    };

    socket.on('lobby waiting', (players, isOwner) => {
        showScreen("waitingDetails")
        document.getElementById("waitingGameHeading").textContent = players.length + " out of 5 players in game."
        waitingPlayersList = document.getElementById("waitingPlayersList")
        waitingPlayersList.innerHTML = '';
        if (isOwner && players.length == 5){
            document.getElementById("gameSetupPartnerMode").hidden = false;
            document.getElementById("startGameButton").hidden = false;
        }
        for (let i = 0; i < players.length; i++) {
            scoreInput = document.createElement('li');
            if (isOwner && players.length == 5){
                inputBox = document.createElement('input');
                inputBox.setAttribute("type", "number");
                inputBox.value = 0;
                scoreInput.appendChild(inputBox);
            }

            nameText = document.createElement('div');
            nameText.textContent = players[i];
            scoreInput.appendChild(nameText);

            waitingPlayersList.appendChild(scoreInput);
        }
    });

    socket.on('bid deal', (playerHand, points, playerNames) => {
        showScreen("gameContainer")
        document.querySelectorAll('img.trickCardImage').forEach(e => e.remove());
        document.getElementById("kittyButtonControl").hidden = true;
        drawHand(playerHand, 0);

        for (let i = 1; i < 5; i++) {
            drawHand(Array(10).fill("back"), i);
        }

        for (let i = 0; i < playerNames.length; i++) {
            document.getElementById("player" + i + "Name").textContent = playerNames[i];
            document.getElementById("player" + i + "ScoreName").textContent = playerNames[i];
            document.getElementById("player" + i + "Score").textContent = points[i];
            document.getElementById("player" + i + "Tricks").textContent = "";
        }
    });

    socket.on('bid request', (previousBids, validBids) => {
        hideBidSection(false);
        document.getElementById("bid_button_pass").onclick = function(event) {
            hideBidSection(true);
            socket.emit("bid", "p");
        };
        allBids = ['5s', '5c', '5d', '5h', '5n', '6s', '6c', '6d', '6h', '6n', '7s', '7c', '7d', '7h', '7n', '8s', '8c', '8d', '8h', '8n', '9s', '9c', '9d', '9h', '9n', '10s', '10c', '10d', '10h', '10n']
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
        for (let i = 0; i < previousBids.length; i++) {
            var bidTextElement = document.getElementById("player" + i + "Bid");
            bidTextElement.textContent = previousBids[i];
        }
        document.getElementById("statusString").textContent = "Waiting for you to bid";
    });

    socket.on('bid status', (previousBids, biddingPlayerName) => {
        for (let i = 0; i < previousBids.length; i++) {
            var bidTextElement = document.getElementById("player" + i + "Bid");
            bidTextElement.textContent = previousBids[i];
        }
        document.getElementById("statusString").textContent = "Waiting for " + biddingPlayerName + " to bid";
    });

    socket.on('kitty request', (playerHand, winningBid, partnerMode) => {
        document.getElementById("kittyCardSelection").hidden = partnerMode == "select";
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
        if (partnerMode == "select"){
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
        }

        document.getElementById("statusString").textContent = "Select partner and discard kitty";
        for (let i = 0; i < 5; i++) {
            document.getElementById("player" + i + "Bid").textContent = "";
        }
        document.getElementById("currentBid").textContent = winningBid;
    });

    socket.on('kitty status', (biddingPlayerName, winningBid) => {
        document.getElementById("statusString").textContent = biddingPlayerName + " won " + winningBid + ". Waiting for " + biddingPlayerName + " to discard";
        for (let i = 0; i < 5; i++) {
            document.getElementById("player" + i + "Bid").textContent = "";
        }
        document.getElementById("currentBid").textContent = winningBid;
    });

    socket.on('round status', (biddingPlayers, playerHand) => {
        drawHand(playerHand, 0);
        currentHand = playerHand;
        document.getElementById("currentBidders").textContent = biddingPlayers;
        for (let i = 0; i < 5; i++) {
            document.getElementById("player" + i + "Tricks").textContent = " - 0";
        }
    });

    socket.on('play request', (currentTrickCards, handSizes, cardValidity, jokerSuitInfo, leadIndex) => {
        document.querySelectorAll('img.trickCardImage').forEach(e => e.remove());
        for (let i = 1; i < 5; i++) {
            drawHand(Array(handSizes[i - 1]).fill("back"), i);
            if (currentTrickCards[i] !== "") {
                drawPlayedCard(currentTrickCards[i], i, leadIndex);
            }
        }
        playerCards = document.querySelectorAll('img.cardPlayer0');
        suitMappings = { "h": "heart", "d": "diamond", "c": "club", "s": "spade" };
        for (let i = 0; i < playerCards.length; i++) {
            if (cardValidity[i]) {
                if (playerCards[i].getAttribute("data") == "joker" && jokerSuitInfo) {
                    playerCards[i].onclick = function(event) {
                        playedCard = playerCards[i].getAttribute("data");
                        currentHand.splice(currentHand.indexOf(playedCard), 1);
                        drawHand(currentHand, 0);

                        if (jokerSuitInfo.length == 1) {
                            // Play the joker as a specific suit
                            socket.emit('play', playedCard + "_" + suitMappings[jokerSuitInfo[0]]);
                        } else {
                            statusString = document.getElementById("statusString");
                            statusString.innerHTML = "<p>Which suit are you playing the joker in?</p>";
                            for (let j = 0; j < jokerSuitInfo.length; j++) {
                                var button = document.createElement('button');
                                button.innerHTML = suitMappings[jokerSuitInfo[j]];
                                button.onclick = function(event) {
                                    let joker_suit = playedCard + "_" + suitMappings[jokerSuitInfo[j]];
                                    socket.emit('play', joker_suit);
                                    document.getElementById("statusString").innerHTML = "";
                                };
                                statusString.appendChild(button);
                            }
                        }
                    };
                } else {
                    playerCards[i].onclick = function(event) {
                        playedCard = playerCards[i].getAttribute("data");
                        socket.emit('play', playedCard);
                        currentHand.splice(currentHand.indexOf(playedCard), 1);
                        drawHand(currentHand, 0);
                    };
                }
                playerCards[i].classList.add("playable")
            }
        }
        document.getElementById("statusString").textContent = "Waiting for you to play";
    });

    socket.on('play status', (currentTrickCards, currentPlayer, handSizes, leadIndex) => {
        document.querySelectorAll('img.trickCardImage').forEach(e => e.remove());
        for (let i = 0; i < 5; i++) {
            if (i !== 0) {
                drawHand(Array(handSizes[i - 1]).fill("back"), i);
            }
            if (currentTrickCards[i] !== "") {
                drawPlayedCard(currentTrickCards[i], i, leadIndex);
            }
        }
        document.getElementById("statusString").textContent = 'Waiting for ' + currentPlayer + ' to play';
    });

    socket.on('play trick', (currentTrickCards, winningPlayer, tricksWon, leadIndex) => {
        document.getElementById("statusString").textContent = winningPlayer + ' won the trick';
        for (let i = 0; i < 5; i++) {
            if (currentTrickCards[i] !== "") {
                drawPlayedCard(currentTrickCards[i], i, leadIndex);
            }
        }

        for (let i = 0; i < 5; i++) {
            document.getElementById("player" + i + "Tricks").textContent = " - " + tricksWon[i];
        }
    });

    socket.on('round result', (statusString, points) => {
        document.getElementById("statusString").textContent = statusString;
        for (let i = 0; i < 5; i++) {
            document.getElementById("player" + i + "Score").textContent = points[i];
        }
        document.getElementById("currentBidders").textContent = "";
        document.getElementById("currentBid").textContent = "";
    });

    socket.on('round complete', (statusString) => {
        document.getElementById("statusString").textContent = statusString;
    });
}

function lobbyConnect() {
    if (connectionEnabled) {
        name = document.getElementById("playerNameInput").value
        if (name.trim().length == 0) {
            names_pool = [
                "Winnie the Pooh",
                "Gandalf",
                "Sir Lancelot",
                "Patrick Bateman",
                "Shrek",
                "Eddard Stark",
                "Mr Krabs",
                "Patrick Star",
                "Wide Putin",
                "Admiral Ackbar",
                "Frodo Baggins",
                "Harambe",
                "Ricardo Milos",
                "Robbie Rotten",
                "Karen",
                "Flat Earth Fred",
            ]
            name = names_pool[Math.floor(Math.random() * names_pool.length)];
        }
        connectionEnabled = false;
        socket = io({ query: { playerName: name.trim() } });
        setupSocketHandlers(socket)
    }
}