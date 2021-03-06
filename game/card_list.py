card_list = [
    "club_10",
    "club_2",
    "club_3",
    "club_4",
    "club_5",
    "club_6",
    "club_7",
    "club_8",
    "club_9",
    "club_ace",
    "club_jack",
    "club_king",
    "club_queen",
    "diamond_10",
    "diamond_2",
    "diamond_3",
    "diamond_4",
    "diamond_5",
    "diamond_6",
    "diamond_7",
    "diamond_8",
    "diamond_9",
    "diamond_ace",
    "diamond_jack",
    "diamond_king",
    "diamond_queen",
    "heart_10",
    "heart_2",
    "heart_3",
    "heart_4",
    "heart_5",
    "heart_6",
    "heart_7",
    "heart_8",
    "heart_9",
    "heart_ace",
    "heart_jack",
    "heart_king",
    "heart_queen",
    "spade_10",
    "spade_2",
    "spade_3",
    "spade_4",
    "spade_5",
    "spade_6",
    "spade_7",
    "spade_8",
    "spade_9",
    "spade_ace",
    "spade_jack",
    "spade_king",
    "spade_queen",
    "joker",
]

all_bids = {}
_suits = ["Spades", "Clubs", "Diamonds", "Hearts", "No trumps"]
for number in range(5, 11):
    for suit_num, suit in enumerate(_suits):
        all_bids[f"{number}{suit[0].lower()}"] = {"points": 100 * number + 20 * suit_num - 460, "name": f"{number} {suit}"}

def pretty_card_str(card):
    assert card in card_list
    if card == "joker":
        return "Joker"
    suit, number = card.split("_")
    return f"{number.title()} of {suit.title()}s"
