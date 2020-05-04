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
            validity, joker_suits = is_card_valid(["", "", "", ""], [], suit, test_cards, i)
            assert validity == True
            if test_cards[i] == "joker" and suit == "n":
                assert joker_suits == {"h", "d", "c", "s"}
            else:
                assert joker_suits is None


def test_follow_suit():
    valid_indices = {0, 1, 3, 5, 7}
    for i in range(len(test_cards)):
        assert is_card_valid(["", "", "", "heart_7"], None, "h", test_cards, i) == (i in valid_indices, None)


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
        assert is_card_valid(trick_cards, None, "c", hand_cards, i) == (True, None)


def test_joker_nt_nothing_played():
    trick_cards = ["", "", "", "", ""]
    hand_cards = ["joker", "spade_ace", "heart_3", "heart_jack", "club_9", "club_king", "spade_jack"]
    previous_tricks = []
    assert is_card_valid(trick_cards, previous_tricks, "n", hand_cards, 0) == (True, {"h", "d", "c", "s"})


def test_joker_nt_hearts_unfinished():
    trick_cards = ["", "", "", "", ""]
    hand_cards = ["joker", "heart_3", "spade_ace", "club_9", "club_king", "spade_jack"]
    previous_tricks = [(0, 0, ["heart_jack", "heart_2", "heart_6", "heart_7", "heart_8"])]
    assert is_card_valid(trick_cards, previous_tricks, "n", hand_cards, 0) == (True, {"d", "c", "s"})


def test_joker_nt_hearts_finished():
    trick_cards = ["", "", "", "", ""]
    hand_cards = ["joker", "spade_ace", "spade_3", "club_9", "club_king", "spade_jack"]
    previous_tricks = [(0, 0, ["heart_jack", "heart_2", "heart_6", "heart_7", "heart_8"])]
    assert is_card_valid(trick_cards, previous_tricks, "n", hand_cards, 0) == (True, {"h", "d", "c", "s"})


def test_joker_nt_void_suit():
    # Spades already played, and hearts is void
    trick_cards = ["", "", "", "", ""]
    hand_cards = ["joker", "spade_ace", "spade_3", "club_9", "club_king", "spade_jack"]
    previous_tricks = [(1, 0, ["heart_jack", "spade_2", "heart_6", "heart_7", "heart_8"])]
    assert is_card_valid(trick_cards, previous_tricks, "n", hand_cards, 0) == (True, {"d", "c"})
