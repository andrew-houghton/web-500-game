const cardWidth = 112;
const cardHeight = 163;
const holderWidth = 620;
const holderHeight = 230;
const perCardDegrees = 6;
const cardSpread = 500;

handLocations = [
    [0.5, 1, 0],
    [0, 0.5, 90],
    [0.3, 0, 180],
    [0.7, 0, 180],
    [1, 0.5, 270],  
];

cardLocations = [
    [0.5, 0.7, 0],
    [0.3, 0.5, 90],
    [0.3, 0.3, 180],
    [0.7, 0.3, 180],
    [0.7, 0.5, 270],
]

var blackHole = [];


function drawPlayedCard(card, playerId){
    blackHole[playerId] = new Image();
    blackHole[playerId].classList.add("trickCardImage");
    blackHole[playerId].addEventListener('load', function() {
        let x = cardLocations[playerId][0] * window.innerWidth;
        let y = cardLocations[playerId][1] * window.innerHeight;
        draw(blackHole[playerId], x, y, cardLocations[playerId][2]);
    });
    if (cardData[card] == undefined) {
        console.error("Could not find info for "+card);
    }
    blackHole[playerId].src = "data:image/png;base64," + cardData[card];
    document.getElementById("player"+playerId+"Cards").appendChild(blackHole[playerId]);
}


function drawHand(cards, playerId) {
    console.log(playerId)
    document.querySelectorAll('img.cardPlayer'+playerId).forEach(e => e.remove());
    var images = [];
    for (let i = 0; i < cards.length; i++) {
        images.push(new Image());
        images[i].classList.add("cardPlayer" + playerId);
        images[i].addEventListener('load', function() {
            direction = handLocations[playerId][2]
            cardDegrees = -cards.length * perCardDegrees / 2 + 3 + perCardDegrees * i;
            var cardX = holderWidth/2 - cardWidth/2 + Math.floor(Math.sin(cardDegrees * Math.PI / 180) * cardSpread)
            var cardY = 70 + Math.floor(Math.cos(cardDegrees * Math.PI / 180) * cardSpread) - cardSpread;
            draw(images[i], cardX, cardY, cardDegrees);
        });
        images[i].src = "data:image/png;base64," + cardData[cards[i]];
        if (playerId == 0){
            images[i].setAttribute('data', cards[i]);
        } else {
            images[i].setAttribute('data',playerId);
        }
        document.getElementById("player"+playerId+"Cards").appendChild(images[i]);
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
