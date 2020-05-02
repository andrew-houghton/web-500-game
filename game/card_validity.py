def _get_card_lead(trick_cards):
    for card in trick_cards:
        if card:
            return card


def _get_card_suit(bid_suit, card):
    if card == "heart_jack" and bid_suit == "d":
        return "d"
    if card == "diamond_jack" and bid_suit == "h":
        return "h"
    if card == "spade_jack" and bid_suit == "c":
        return "c"
    if card == "club_jack" and bid_suit == "s":
        return "s"
    if card == "joker":
        return bid_suit if bid_suit != "n" else "h"
    return card.split("_")[0][0]


def is_card_valid(trick_cards, bid_suit, cards, index):
    # If the player is leading they can play any card
    if set(trick_cards) == {''}:
        return True

    # Joker in no trumps played any time TODO fix this
    if cards[index] == "joker" and bid_suit == "n":
        return True

    # Otherwise they must follow suit
    suit_lead = _get_card_suit(bid_suit, _get_card_lead(trick_cards))
    card_suit = _get_card_suit(bid_suit, cards[index])

    # If they are following suit then card is valid
    if card_suit == suit_lead:
        return True

    # If they are not following suit they must be unable to follow suit
    has_lead_suit = any(_get_card_suit(bid_suit, card) == suit_lead for card in cards)
    return not has_lead_suit


def _get_card_number(bid_suit, card):
    if card == "joker":
        return 17

    _, number = card.split("_")
    if number.isdigit():
        return int(number)

    # Only face cards remaining now
    number_mappings = {"queen": 12, "king": 13, "ace": 14}
    if number in number_mappings:
        return number_mappings[number]
    # Handle jacks
    card_suit = _get_card_suit(bid_suit, card)
    if bid_suit == card_suit:
        if card[0] == bid_suit:
            return 16
        else:
            return 15
    return 11

def winning_card_index(trick_cards, bid_suit, lead_index):
    trick_cards = list(trick_cards.values())
    if bid_suit != 'n':
        trumps_played = [card for card in trick_cards if _get_card_suit(bid_suit, card) == bid_suit]
        if len(trumps_played) > 0:
            winning_card = max(trumps_played, key=lambda card: _get_card_number(bid_suit, card))
            return trick_cards.index(winning_card)

    lead_suit = _get_card_suit(bid_suit, trick_cards[lead_index])
    cards_following_suit = [card for card in trick_cards if _get_card_suit(bid_suit, card) == lead_suit]
    # Return index of winning card following suit
    winning_card = max(cards_following_suit, key=lambda card: _get_card_number(bid_suit, card))
    return trick_cards.index(winning_card)
