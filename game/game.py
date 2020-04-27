import os
import random
from game.card_list import card_list, all_bids
from collections import defaultdict
from flask_socketio import emit


class Game:
    def __init__(self):
        self.player_sids = []
        self.player_names = []
        self.owner = None
        self.hands = None
        self.kitty = None
        self.dealer = 0
        self.player_to_bid = 0
        self.scores = None
        self.valid_bids = [bid for bid in all_bids]
        self.bids = {}
        self.player_winning_bid = None

    def update_waiting_players(self):
        for player in self.player_sids:
            emit("lobby waiting", self.player_names, room=player)

    def add_player(self, sid, name):
        if len(self.player_sids) == 0:
            self.owner = sid
        self.player_sids.append(sid)
        self.player_names.append(name)
        if len(self.player_sids) == 5:
            self.scores = {i: 0 for i in range(5)}
            self.start_round()
        else:
            self.update_waiting_players()

    def remove_player(self, sid):
        if len(self.player_sids) > 1 and self.owner == sid:
            self.owner = self.player_sids[1]
        del self.player_names[self.player_sids.index(sid)]
        self.player_sids.remove(sid)
        self.update_waiting_players()

    def deal(self):
        random.shuffle(card_list)
        self.hands = [card_list[i : i + 10] for i in range(0, 50, 10)]
        self.kitty = card_list[-3:]

    def start_round(self):
        self.deal()
        self.bids = {}
        scores = {self.player_names[i]: score for i, score in self.scores.items()}
        for i in range(5):
            # Send names from the perspective of the current player
            player_names = [self.player_names[(i + j) % 5] for j in range(5)]
            emit("bid deal", (self.hands[i], scores, player_names), room=self.player_sids[i])

        self.player_to_bid = self.dealer
        self.dealer = (self.dealer + 1) % 5
        self.send_bid_requests()

    def send_bid_requests(self):
        for i in range(5):
            previous_bids = [self.bids.get((i + j) % 5) for j in range(5)]
            if i == self.player_to_bid:
                emit("bid request", (previous_bids, self.valid_bids), room=self.player_sids[i])
            else:
                emit("bid status", (previous_bids, self.player_names[i]), room=self.player_sids[i])

    def bid(self, sid, bid):
        self.bids[self.player_sids.index(sid)] = bid
        bid_points = 0 if bid == "p" else all_bids[bid]["points"]
        self.valid_bids = [i for i in self.valid_bids if all_bids[i]["points"] > bid_points]

        print(self.bids)
        print(self.player_to_bid)
        for i in range(1, 5):
            if self.bids.get((self.player_to_bid + i) % 5) != "p":
                self.player_to_bid = (self.player_to_bid + i) % 5
                self.send_bid_requests()
                return

        if set(self.bids.values()) == {"p"}:
            # Everyone passed so redeal
            self.start_round()
        else:
            self.player_winning_bid = max(range(5), key=lambda i: all_bids.get(self.bids[i], {}).get("points", 0))
            player_winning_bid_name = self.player_names[self.player_winning_bid]
            for i in range(5):
                if i == self.player_winning_bid:
                    emit("kitty request", self.kitty, room=self.player_sids[i])
                else:
                    emit(
                        "kitty status",
                        (player_winning_bid_name, self.bids[self.player_winning_bid]),
                        room=self.player_sids[i],
                    )
