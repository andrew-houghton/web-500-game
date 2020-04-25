import os
import random


card_list = [i.replace('.png', '') for i in os.listdir('static/cards')]
card_list.remove('back')


def deal():
    random.shuffle(card_list)
    players = [card_list[i:i+10] for i in range(0,50,10)]
    kitty = card_list[-3:]
    return players, kitty
