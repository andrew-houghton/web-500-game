from game.card_validity import is_card_valid, winning_card_index

test_cards = [
    "heart_ace",
    "heart_10",
    "spade_9",
    "joker",
    "spade_5",
    "heart_king",
    "spade_king",
    "diamond_jack",
    "spade_8",
    "club_4",
]


def test_nothing_played():
    for i in range(10):
        for suit in "scdhn":
            assert is_card_valid(["", "", "", ""], None, suit, test_cards, i)


def test_follow_suit():
    valid_indices = {0, 1, 3, 5, 7}
    for i in range(len(test_cards)):
        assert is_card_valid(["", "", "", "heart_7"], None, "h", test_cards, i) == (i in valid_indices)


def test_winner_index_trumps():
    trick_cards = ["diamond_2", "diamond_king", "diamond_4", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "d", 0) == 1


def test_winner_index_trump_last():
    trick_cards = ["diamond_2", "diamond_king", "diamond_4", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "s", 0) == 4


def test_winner_index_off_suit():
    trick_cards = ["diamond_2", "diamond_king", "diamond_4", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "c", 0) == 1


def test_winner_index_bower():
    trick_cards = ["diamond_2", "diamond_king", "heart_jack", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "d", 0) == 2


def test_winner_index_joker():
    trick_cards = ["diamond_2", "diamond_king", "joker", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "c", 0) == 2


def test_winner_index_royals():
    trick_cards = ["diamond_2", "diamond_jack", "diamond_ace", "diamond_3", "spade_4"]
    assert winning_card_index(trick_cards, "d", 0) == 1


def test_card_validity():
    trick_cards = ["diamond_6", "", "", "diamond_9", "diamond_5"]
    hand_cards = ["spade_7", "spade_ace", "heart_3", "heart_jack", "club_9", "club_king", "spade_jack"]

    for i in range(len(hand_cards)):
        assert is_card_valid(trick_cards, None, "c", hand_cards, i)
