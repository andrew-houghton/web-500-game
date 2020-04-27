const cardWidth = 112;
const cardHeight = 163;
const perCardDegrees = 6;
const perCardRadians = perCardDegrees * Math.PI / 180;
const cardSpread = 500;
var cardContainer = document.getElementById("cardContainer");

handLocations = [
    [0.5, 1, 0],
    [0, 0.5, 90],
    [0.3, 0, 180],
    [0.7, 0, 180],
    [1, 0.5, 270],
];

function drawHand(cards, playerId) {
    var images = [];
    for (let i = 0; i < cards.length; i++) {
        images.push(new Image());
        images[i].classList.add("cardPlayer" + playerId);
        images[i].addEventListener('load', function() {
            direction = handLocations[playerId][2]
            x = handLocations[playerId][0] * window.innerWidth
            y = handLocations[playerId][1] * window.innerHeight
            card_degrees = -cards.length * perCardDegrees / 2 + 3 + perCardDegrees * i + direction;
            var cardX = Math.floor(x + Math.sin(card_degrees * Math.PI / 180) * cardSpread);
            var cardY = Math.floor(y - Math.cos(card_degrees * Math.PI / 180) * cardSpread);
            cardX = cardX - cardSpread / 1.6 * Math.sin(direction * Math.PI / 180);
            cardY = cardY + cardSpread / 1.6 * Math.cos(direction * Math.PI / 180);
            draw(images[i], cardX, cardY, card_degrees);
        });
        images[i].src = "data:image/png;base64," + cardData[cards[i]];
        cardContainer.appendChild(images[i]);
    }
    return images
}

function draw(img, x, y, rotation) {
    img.setAttribute("style", "transform: rotate(" + rotation + "deg)");
    img.style.left = (x - cardWidth / 2) + 'px';
    img.style.top = (y - cardHeight / 2) + 'px';
}

document.addEventListener("DOMContentLoaded", function() {
    for (let i = 0; i < handLocations.length; i++) {
        // Set bid text locations
        var statusElement = document.getElementById("player" + i + "Status");
        x = handLocations[i][0] * window.innerWidth + cardSpread * 0.7 * Math.sin(handLocations[i][2] * Math.PI / 180);
        y = handLocations[i][1] * window.innerHeight - cardSpread * 0.7 * Math.cos(handLocations[i][2] * Math.PI / 180);
        if (handLocations[i][2] != 180 && handLocations[i][2] != 0) {
            statusElement.setAttribute("style", "transform: rotate(" + handLocations[i][2] + "deg)");
        }
        statusElement.style.left = x + 'px';
        statusElement.style.top = y + 'px';
    }
});

document.getElementById("playerNameInput").addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) { lobbyConnect(); }
});
