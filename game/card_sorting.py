from functools import partial


def _get_card_suit_and_number(card):
    if card == "joker":
        return "j", 0

    suit, number = card.split("_")

    number_mappings = {"jack": 11, "queen": 12, "king": 13, "ace": 14}
    if number.isdigit():
        number = int(number)
    else:
        number = number_mappings[number]

    return suit, number


def _convert_to_sorting_order(suit, card_suit, number):
    paired_suit = {"d": "heart", "h": "diamond", "s": "club", "c": "spade"}
    matching_suit = {"h": "heart", "d": "diamond", "c": "club", "s": "spade"}

    # Deal with bowers
    if suit != "n" and number == 11:
        if matching_suit[suit] == card_suit:
            number = 16
        elif paired_suit[suit] == card_suit:
            number = 15
            card_suit = matching_suit[suit]

    suit_orderings = {
        "n": ["spade", "diamond", "club", "heart", "j"],
        "s": ["diamond", "club", "heart", "spade", "j"],
        "c": ["diamond", "spade", "heart", "club", "j"],
        "d": ["spade", "heart", "club", "diamond", "j"],
        "h": ["spade", "diamond", "club", "heart", "j"],
    }

    return (suit_orderings[suit].index(card_suit), number)


def sort_card_list(cards, suit):
    return sorted(cards, key=lambda card: _convert_to_sorting_order(suit, *_get_card_suit_and_number(card)))
