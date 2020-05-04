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
    if "joker" in card:
        if bid_suit != "n":
            return bid_suit
        else:
            if "heart" in card:
                return "h"
            elif "diamond" in card:
                return "d"
            elif "club" in card:
                return "c"
            else:
                return "s"
    return card.split("_")[0][0]


def _get_valid_joker_suits(trick_card_history, bid_suit, cards):
    void_suits = set()
    for player_index, lead_index, trick_cards in trick_card_history:
        if _get_card_suit(bid_suit, trick_cards[lead_index]) != _get_card_suit(bid_suit, trick_cards[player_index]):
            void_suits.add(_get_card_suit(bid_suit, trick_cards[lead_index]))

    def is_suit_in_hand(suit):
        return any(_get_card_suit(bid_suit, card) == suit for card in cards if card != "joker")

    def has_suit_been_played(suit):
        return any(
            _get_card_suit(bid_suit, trick_cards[player_index]) == suit
            for player_index, _, trick_cards in trick_card_history
        )

    valid_suits = set()
    for suit in "hdcs":
        if suit not in void_suits and (not has_suit_been_played(suit) or not is_suit_in_hand(suit)):
            valid_suits.add(suit)
    return valid_suits


def is_card_valid(trick_cards, trick_card_history, bid_suit, cards, index):
    # Joker in no trumps played any time TODO fix this
    if cards[index] == "joker" and bid_suit == "n":
        # If leading then must be first or last of suit
        # If following then joker follows suit (must be first or last)
        valid_suits = _get_valid_joker_suits(trick_card_history, bid_suit, cards)

        if not valid_suits:
            return False, None

        if set(trick_cards) == {""}:
            return True, valid_suits
        else:
            suit_lead = _get_card_suit(bid_suit, _get_card_lead(trick_cards))
            if len(cards) == 1 or suit_lead in valid_suits:
                return True, {suit_lead}
            return False, None
    # If the player is leading they can play any card
    if set(trick_cards) == {""}:
        return True, None

    # Otherwise they must follow suit
    suit_lead = _get_card_suit(bid_suit, _get_card_lead(trick_cards))
    card_suit = _get_card_suit(bid_suit, cards[index])

    # If they are following suit then card is valid
    if card_suit == suit_lead:
        return True, None

    # If they are not following suit they must be unable to follow suit
    has_lead_suit = any(_get_card_suit(bid_suit, card) == suit_lead for card in cards)
    return not has_lead_suit, None


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
    # Joker always wins
    for i in range(len(trick_cards)):
        if "joker" in trick_cards[i]:
            return i

    if bid_suit != "n":
        trumps_played = [card for card in trick_cards if _get_card_suit(bid_suit, card) == bid_suit]
        if len(trumps_played) > 0:
            winning_card = max(trumps_played, key=lambda card: _get_card_number(bid_suit, card))
            return trick_cards.index(winning_card)

    lead_suit = _get_card_suit(bid_suit, trick_cards[lead_index])
    cards_following_suit = [card for card in trick_cards if _get_card_suit(bid_suit, card) == lead_suit]
    # Return index of winning card following suit
    winning_card = max(cards_following_suit, key=lambda card: _get_card_number(bid_suit, card))
    return trick_cards.index(winning_card)
