const cardWidth = 112;
const cardHeight = 163;

document.addEventListener("DOMContentLoaded", function() {
    var cards = document.getElementById("card_container");

    function draw(img, x, y, rotation) {
        img.setAttribute("style", "transform: rotate(" + rotation + "deg)")
        cards.appendChild(img);
        img.style.left = (x-cardWidth/2) + 'px';
        img.style.top = (y-cardHeight/2) + 'px';
    }

    function drawHand(cards, x, y, direction) {
        console.log("Drawing hand at ", x, y, direction)
        for (let i = 0; i < cards.length; i++) {
            var img = new Image();
            img.addEventListener('load', function() {
                draw(img, x, y, direction);
            });
            img.src = "data:image/png;base64," + cardData[cards[i]];
        }
    }

    handLocations = [
        // [0.5, 0.9, 0],
        [0.1, 0.4, 90],
        // [0.3, 0.1, 180],
        // [0.7, 0.1, 180],
        // [0.9, 0.4, 270],
    ]

    for (let i = 0; i < handLocations.length; i++) {
        drawHand(
            ['club_6'],
            handLocations[i][0] * window.innerWidth,
            handLocations[i][1] * window.innerHeight,
            handLocations[i][2],
        );
    }
});