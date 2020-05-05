const cardWidth = 112;
const cardHeight = 163;
const holderWidth = 620;
const holderHeight = 230;
const perCardDegrees = 6;
const cardSpread = 500;

var blackHole = [];


function drawPlayedCard(card, playerId, leadIndex) {
    blackHole[playerId] = new Image();
    blackHole[playerId].classList.add("trickCardImage");
    blackHole[playerId].id = "playedCard" + playerId;
    blackHole[playerId].style.zIndex = (playerId + leadIndex) % 5;
    if (cardData[card] == undefined) {
        console.error("Could not find info for " + card);
    }
    blackHole[playerId].src = "data:image/png;base64," + cardData[card];
    document.getElementById("playedCardContainer").appendChild(blackHole[playerId]);
}


function drawHand(cards, playerId) {
    document.querySelectorAll('img.cardPlayer' + playerId).forEach(e => e.remove());
    var images = [];
    for (let i = 0; i < cards.length; i++) {
        images.push(new Image());
        images[i].classList.add("cardPlayer" + playerId);
        images[i].addEventListener('load', function() {
            cardDegrees = -cards.length * perCardDegrees / 2 + 3 + perCardDegrees * i;
            var cardX = holderWidth / 2 - cardWidth / 2 + Math.floor(Math.sin(cardDegrees * Math.PI / 180) * cardSpread)
            var cardY = 70 + Math.floor(Math.cos(cardDegrees * Math.PI / 180) * cardSpread) - cardSpread;
            draw(images[i], cardX, cardY, cardDegrees);
        });
        images[i].src = "data:image/png;base64," + cardData[cards[i]];
        if (playerId == 0) {
            images[i].setAttribute('data', cards[i]);
        } else {
            images[i].setAttribute('data', playerId);
        }
        document.getElementById("player" + playerId + "Cards").appendChild(images[i]);
    }
    return images
}

function draw(img, x, y, rotation) {
    img.setAttribute("style", "transform: rotate(" + rotation + "deg)");
    img.style.left = x + 'px';
    img.style.bottom = y + 'px';
}

document.getElementById("playerNameInput").addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) { lobbyConnect(); }
});


// document.addEventListener("DOMContentLoaded", function(event) {
//     document.getElementById("statusString").textContent = "Waiting you to play";
//     showScreen("gameContainer");
//     drawPlayedCard("heart_ace", 0);
//     drawPlayedCard("heart_2", 1);
//     drawPlayedCard("heart_3", 2);
//     drawPlayedCard("heart_4", 3);
//     drawPlayedCard("heart_5", 4);
// });