import os
import random

card_list = [
    "club_10",
    "heart_jack",
    "diamond_10",
    "diamond_3",
    "club_7",
    "heart_ace",
    "club_2",
    "spade_queen",
    "diamond_5",
    "spade_ace",
    "heart_king",
    "diamond_queen",
    "club_4",
    "heart_8",
    "spade_10",
    "spade_4",
    "heart_6",
    "diamond_9",
    "diamond_ace",
    "spade_2",
    "club_3",
    "club_6",
    "heart_3",
    "spade_7",
    "heart_10",
    "spade_5",
    "heart_9",
    "diamond_4",
    "club_9",
    "diamond_7",
    "spade_jack",
    "diamond_6",
    "club_5",
    "spade_3",
    "club_queen",
    "diamond_2",
    "spade_8",
    "heart_7",
    "heart_2",
    "diamond_8",
    "heart_5",
    "club_jack",
    "spade_6",
    "heart_queen",
    "spade_king",
    "diamond_jack",
    "heart_4",
    "diamond_king",
    "club_king",
    "spade_9",
    "club_ace",
    "club_8",
]


def deal():
    random.shuffle(card_list)
    players = [card_list[i : i + 10] for i in range(0, 50, 10)]
    kitty = card_list[-3:]
    return players, kitty
