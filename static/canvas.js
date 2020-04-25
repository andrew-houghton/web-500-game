const cardWidth = 112;
const cardHeight = 163;
const perCardDegrees = 6;
const perCardRadians = perCardDegrees * Math.PI / 180;
const cardSpread = 200;

document.addEventListener("DOMContentLoaded", function() {
    var cardContainer = document.getElementById("cardContainer");

    function draw(img, x, y, rotation) {
        img.setAttribute("style", "transform: rotate(" + rotation + "deg)")
        img.style.left = (x-cardWidth/2) + 'px';
        img.style.top = (y-cardHeight/2) + 'px';
    }

    function drawHand(cards, x, y, direction) {
        console.log("Drawing hand at ", x, y, direction)
        var images = [];

        for (let i = 0; i < cards.length; i++) {
            images.push(new Image());
            images[i].addEventListener('load', function() {
                card_degrees = cards.length / 2 * -6 + 3 + perCardDegrees * i + direction;

                var cardX = Math.floor(x + Math.sin(card_degrees * Math.PI / 180) * cardSpread);
                var cardY = Math.floor(y - Math.cos(card_degrees * Math.PI / 180) * cardSpread)
                draw(images[i], cardX, cardY, card_degrees);
            });
            images[i].src = "data:image/png;base64," + cardData[cards[i]];
            cardContainer.appendChild(images[i]);
        }
    }

    handLocations = [
        [0.5, 1, 0],
        [0, 0.4, 90],
        [0.3, 0, 180],
        [0.7, 0, 180],
        [1, 0.4, 270],
    ]

    for (let i = 0; i < handLocations.length; i++) {
        drawHand(
            ['club_6', 'club_5', 'club_4', 'club_6', 'club_6', 'club_6', 'club_6', 'club_6', 'club_6', 'club_6'],
            handLocations[i][0] * window.innerWidth,
            handLocations[i][1] * window.innerHeight,
            handLocations[i][2],
        );
    }
});