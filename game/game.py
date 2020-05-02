import os
import random
from game.card_list import card_list, all_bids
from collections import defaultdict
from flask_socketio import emit
from game.card_sorting import sort_card_list
from game.card_validity import is_card_valid, winning_card_index
import threading


class Game:
    def __init__(self):
        self.player_sids = []
        self.player_names = []
        self.owner = None
        self.hands = None
        self.trick_cards = None
        self.kitty = None
        self.dealer = 0
        self.player_to_bid = 0
        self.scores = None
        self.valid_bids = None
        self.bids = None
        self.player_winning_bid = None
        self.partner_winning_bid = None
        self.lead_player = None
        self.tricks_won = None
        self.tricks_record = None
        self.points = defaultdict(int)

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
        self.valid_bids = [bid for bid in all_bids]
        self.bids = {}
        scores = {self.player_names[i]: score for i, score in self.scores.items()}
        for i in range(5):
            # Send names from the perspective of the current player
            player_names = [self.player_names[(i + j) % 5] for j in range(5)]
            emit("bid deal", (sort_card_list(self.hands[i], "n"), scores, player_names), room=self.player_sids[i])

        self.player_to_bid = self.dealer
        self.dealer = (self.dealer + 1) % 5
        self.send_bid_requests()

    def bid_name(self, bid):
        if bid in all_bids:
            return all_bids[bid]["name"]
        elif bid == "p":
            return "Pass"
        return ""

    def send_bid_requests(self):
        for i in range(5):
            previous_bids = [self.bid_name(self.bids.get((i + j) % 5)) for j in range(5)]
            if i == self.player_to_bid:
                emit("bid request", (previous_bids, self.valid_bids), room=self.player_sids[i])
            else:
                emit("bid status", (previous_bids, self.player_names[self.player_to_bid]), room=self.player_sids[i])

    def send_kitty(self):
        player_winning_bid_name = self.player_names[self.player_winning_bid]
        self.winning_bid = self.bids[self.player_winning_bid]
        for i in range(5):
            if i == self.player_winning_bid:
                emit(
                    "kitty request",
                    sort_card_list(self.kitty + self.hands[self.player_winning_bid], self.winning_bid[1]),
                    room=self.player_sids[i],
                )
            else:
                emit(
                    "kitty status",
                    (player_winning_bid_name, all_bids[self.winning_bid]["name"]),
                    room=self.player_sids[i],
                )

    def bid(self, sid, bid):
        self.bids[self.player_sids.index(sid)] = bid
        number_of_passes = len([i for i in self.bids.values() if i == "p"])

        if number_of_passes == 5:
            # Everyone passed so redeal
            self.start_round()
        elif number_of_passes == 4 and len(self.bids) == 5:
            self.player_winning_bid = max(range(5), key=lambda i: all_bids.get(self.bids[i], {}).get("points", 0))
            self.send_kitty()
        else:
            bid_points = 0 if bid == "p" else all_bids[bid]["points"]
            self.valid_bids = [i for i in self.valid_bids if all_bids[i]["points"] > bid_points]
            for i in range(1, 5):
                if self.bids.get((self.player_to_bid + i) % 5) != "p":
                    self.player_to_bid = (self.player_to_bid + i) % 5
                    self.send_bid_requests()
                    return

    def handle_kitty(self, sid, discarded_kitty, partner_index):
        assert len(discarded_kitty) == 3
        self.partner_winning_bid = (self.player_winning_bid + partner_index) % 5
        self.hands[self.player_winning_bid] = list(
            set(self.hands[self.player_winning_bid] + self.kitty) - set(discarded_kitty)
        )

        winning_bid_name = all_bids[self.winning_bid]["name"]
        if partner_index == 0:
            status_string = f"{self.player_names[self.player_winning_bid]} bid {winning_bid_name}"
        else:
            status_string = f"{self.player_names[self.player_winning_bid]} and {self.player_names[self.partner_winning_bid]} bid {winning_bid_name}"

        for i in range(5):
            self.hands[i] = sort_card_list(self.hands[i], self.winning_bid[1])
            emit("round status", (status_string, self.hands[i]), room=self.player_sids[i])

        self.tricks_record = []
        self.trick_cards = {}
        self.tricks_won = defaultdict(int)
        self.lead_player = self.player_winning_bid
        self.send_play_request()

    def send_play_request(self):
        for i in range(5):
            current_trick_cards = [self.trick_cards.get((i + j) % 5, "") for j in range(0, 5)]
            hand_sizes = [len(self.hands[(i + j) % 5]) for j in range(1, 5)]
            card_validity = [
                is_card_valid(current_trick_cards, self.winning_bid[1], self.hands[i], j)
                for j in range(len(self.hands[i]))
            ]
            if card_validity:
                assert any(card_validity), f"{current_trick_cards}, {self.winning_bid}, {self.hands[i]}"

            bidding_player_name = self.player_names[(self.lead_player + len(self.trick_cards)) % 5]
            if i == (self.lead_player + len(self.trick_cards)) % 5:
                emit("play request", (current_trick_cards, hand_sizes, card_validity), room=self.player_sids[i])
            else:
                emit("play status", (current_trick_cards, bidding_player_name, hand_sizes), room=self.player_sids[i])

    def play_card(self, sid, card, socketio):
        # Save the played card
        player_index = self.player_sids.index(sid)
        self.trick_cards[player_index] = card
        self.hands[player_index].remove(card)

        # Is the round finished
        if len(self.trick_cards) < 5:
            self.send_play_request()
            return

        winner_index = winning_card_index([self.trick_cards[i] for i in range(5)], self.winning_bid[1], self.lead_player)
        self.tricks_won[winner_index] += 1
        self.tricks_record.append(self.trick_cards)
        self.lead_player = winner_index

        for i in range(5):
            emit(
                "play trick",
                (
                    [self.trick_cards.get((i + j) % 5, "") for j in range(0, 5)],
                    self.player_names[winner_index],
                    [self.tricks_won[(i + j) % 5] for j in range(5)],
                ),
                room=self.player_sids[i],
            )
        self.trick_cards = {}

        socketio.sleep(0)
        thread = threading.Thread(target=socketio.sleep, args=(2,))
        thread.start()
        thread.join()

        if len(self.tricks_record) == 10:
            self.end_round(socketio)
        else:
            self.send_play_request()

    @staticmethod
    def get_bid_number(bid):
        for i in range(6, 11):
            if str(i) in bid:
                return i

    def end_round(self, socketio):
        # Check if players got more tricks than bid
        attacking_tricks = self.tricks_won[self.player_winning_bid]
        if self.partner_winning_bid != self.player_winning_bid:
            attacking_tricks += self.tricks_won[self.partner_winning_bid]
        bid_made = attacking_tricks >= self.get_bid_number(self.winning_bid)

        # Deal with 250 points for slam
        if bid_made and attacking_tricks == 10:
            bid_points = max(all_bids[self.winning_bid]["points"], 250)
        else:
            bid_points = all_bids[self.winning_bid]["points"]

        # Deal with splitting points between attacking players
        if self.partner_winning_bid != self.player_winning_bid:
            attacker_points = bid_points / 2
        else:
            attacker_points = bid_points

        # Update point totals
        for i in range(5):
            if i in (self.partner_winning_bid, self.player_winning_bid):
                if bid_made:
                    self.points[i] +=attacker_points
                else:
                    self.points[i] -= attacker_points
            else:
                self.points[i] += 10 * self.tricks_won[i]

        made_not_made_string = "made" if bid_made else "didn't make"
        winning_bid_name = all_bids[self.winning_bid]["name"]
        if self.partner_winning_bid != self.player_winning_bid:
            status_string = f"{self.player_names[self.player_winning_bid]} and {self.player_names[self.partner_winning_bid]} {made_not_made_string} {winning_bid_name}"
        else:
            status_string = f"{self.player_names[self.player_winning_bid]} {made_not_made_string} {winning_bid_name}"

        for i in range(5):
            player_points = [self.points[(i+j)%5] for j in range(5)]
            emit("round result", (status_string, player_points), room=self.player_sids[i])

        socketio.sleep()
        thread = threading.Thread(target=socketio.sleep, args=(3,))
        thread.start()
        thread.join()

        self.start_round()
