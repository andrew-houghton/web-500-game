var canvas = document.querySelector('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var ctx = canvas.getContext('2d');

// TODO:
// Display a card
// Display a hand
// Display 5 hands
// Play a card from each hand

function draw(img, x, y, width, height, rotation){
    ctx.save();
    ctx.rotate(Math.PI * rotation);
    ctx.drawImage(img, x, y);
    ctx.restore();
}

function draw_hand(cards, x, y, direction){
    for (let i = 0; i < cards.length; i++) {
        console.log("drawing card "+i);
        console.log(card_data[cards[i]].length)
        img = new Image();
        img.src = "data:image/png;base64,"+card_data[cards[i]];
        draw(img, 140+20*i, 160+80*i, 50, 50, 0.03*i);
    }
}

document.addEventListener("DOMContentLoaded", function(){
    draw_hand(['club_6', 'club_5', 'club_3', 'club_2'], 200,200,0);
});