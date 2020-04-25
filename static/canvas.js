const cardWidth = 112;
const cardHeight = 163;
const perCardDegrees = 6;
const perCardRadians = perCardDegrees * Math.PI / 180;
const cardSpread = 300;
var cardContainer = document.getElementById("cardContainer");

function drawHand(cards, x, y, direction, playerId) {
    var images = [];
    for (let i = 0; i < cards.length; i++) {
        images.push(new Image());
        images[i].classList.add("cardPlayer"+playerId);
        images[i].addEventListener('load', function() {
            card_degrees = -cards.length * perCardDegrees / 2 + 3 + perCardDegrees * i + direction;
            var cardX = Math.floor(x + Math.sin(card_degrees * Math.PI / 180) * cardSpread);
            var cardY = Math.floor(y - Math.cos(card_degrees * Math.PI / 180) * cardSpread);
            cardX = cardX - cardSpread / 3 * Math.sin(direction * Math.PI / 180);
            cardY = cardY + cardSpread / 3 * Math.cos(direction * Math.PI / 180);
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
    // Sample data
    handLocations = [
        [0.5, 1, 0],
        [0, 0.5, 90],
        [0.3, 0, 180],
        [0.7, 0, 180],
        [1, 0.5, 270],
    ];
    hands = [
        ['diamond_7', 'diamond_jack', 'spade_jack', 'spade_queen', 'heart_10', 'heart_jack', 'heart_1', 'club_9', 'club_jack', 'joker_red'],
        ['back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back'],
        ['back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back'],
        ['back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back'],
        ['back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back', 'back'],
    ];
    recentBids = [
        "Pass",
        "Pass",
        "",
        "6 Spades",
        "6 Hearts",
    ];

    for (let i = 0; i < handLocations.length; i++) {
        drawHand(
            hands[i],
            handLocations[i][0] * window.innerWidth,
            handLocations[i][1] * window.innerHeight,
            handLocations[i][2],
            i,
        );

        // Set bid text locations
        var bidTextElement = document.getElementById("player" + i + "Bid");
        x = handLocations[i][0] * window.innerWidth + cardSpread * 1.2 * Math.sin(handLocations[i][2] * Math.PI / 180);
        y = handLocations[i][1] * window.innerHeight - cardSpread * 1.2 * Math.cos(handLocations[i][2] * Math.PI / 180);
        if (handLocations[i][2] != 180 && handLocations[i][2] != 0){
            bidTextElement.setAttribute("style", "transform: rotate(" + handLocations[i][2] + "deg)");
        }
        bidTextElement.style.left = x + 'px';
        bidTextElement.style.top = y + 'px';

        // Set bid text
        bidTextElement.innerHTML = recentBids[i];
    }

});

function kittyCardClicked(e) {
    console.log(e)
}

function giveKitty() {
    kitty = ['diamond_9', 'spade_10', 'heart_king']

    // Update the hand
    document.querySelectorAll('img.cardPlayer0').forEach(e => e.remove());
    images = drawHand(
        hands[0].concat(kitty),
        handLocations[0][0] * window.innerWidth,
        handLocations[0][1] * window.innerHeight,
        handLocations[0][2],
        0,
    );

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
    for (let playerId = 1; playerId < 5; playerId++){
        document.querySelectorAll('img.cardPlayer'+playerId).forEach(e => e.addEventListener('click', function() {
            document.querySelectorAll('img.chosen').forEach(j => j.classList.remove("chosen"))
            document.querySelectorAll('img.cardPlayer'+playerId).forEach(j => j.classList.add("chosen"))
        }));

    }
}
