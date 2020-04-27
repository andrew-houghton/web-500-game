import os
import random
from game.card_list import card_list
from collections import defaultdict
from flask_socketio import emit


class Game:
    def __init__(self):
        self.player_sids = []
        self.player_names = {}
        self.owner = None
        # self.bids = None
        # self.hands = []
        # self.scores = defaultdict(int)
        # self.dealer = 0

    def update_waiting_players(self):
        waiting_players = [self.player_names[player] for player in self.player_sids]
        for player in self.player_sids:
            emit("lobby waiting", waiting_players, room=player)

    def add_player(self, sid, name):
        if len(self.player_sids) == 0:
            self.owner = sid
        self.player_sids.append(sid)
        self.player_names[sid] = name
        self.update_waiting_players()

    def remove_player(self, sid):
        if len(self.player_sids) > 1 and self.owner == sid:
            self.owner = self.player_sids[1]
        self.player_sids.remove(sid)
        del self.player_names[sid]
        self.update_waiting_players()

    def deal(self):
        random.shuffle(card_list)
        players = [card_list[i : i + 10] for i in range(0, 50, 10)]
        kitty = card_list[-3:]
        return players, kitty
