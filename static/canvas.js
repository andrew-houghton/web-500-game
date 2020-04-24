// TODO:
// Display a card
// Display a hand
// Display 5 hands
// Play a card from each hand
document.addEventListener("DOMContentLoaded", function() {
    var cards = document.getElementById("card_container");

    function draw(img, x, y, rotation) {
        cards.appendChild(img);
        img.setAttribute("style", "transform: rotate(" + rotation + "deg)")
        img.style.left = x + 'px';
        img.style.top = y + 'px';
    }

    function draw_hand(cards, x, y, direction) {
        for (let i = 0; i < cards.length; i++) {
            img = new Image();
            img.src = "data:image/png;base64," + card_data[cards[i]];
            console.log(x + i * 40, y, direction)
            draw(img, x + i * 40, y, direction);
        }
    }

    hand_locations = [
        [0.5, 0.8, 0],
        [0.1, 0.4, 90],
        [0.3, 0.1, 180],
        [0.7, 0.1, 180],
        [0.9, 0.4, 270],
    ]

    for (let i = 0; i < hand_locations.length; i++) {
        draw_hand(
            ['club_6', 'club_5'],
            hand_locations[i][0] * window.innerWidth,
            hand_locations[i][1] * window.innerHeight,
            hand_locations[i][2],
        );
    }
});