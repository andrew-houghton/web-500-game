import os
import random
from game.card_list import card_list, all_bids, pretty_card_str
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
        self.valid_bids = None
        self.bids = None
        self.player_winning_bid = None
        self.partner_winning_bid = None
        self.lead_player = None
        self.tricks_won = None
        self.tricks_record = None
        self.partner_mode = None
        self.points = defaultdict(int)

    def update_waiting_players(self):
        for player in self.player_sids:
            emit("lobby waiting", (self.player_names, player==self.owner), room=player)

    def add_player(self, sid, name):
        if len(self.player_sids) == 0:
            self.owner = sid
        self.player_sids.append(sid)
        self.player_names.append(name)
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
        for i in range(5):
            # Send names from the perspective of the current player
            player_names = [self.player_names[(i + j) % 5] for j in range(5)]
            player_points = [self.points[(i + j) % 5] for j in range(5)]
            emit(
                "bid deal", (sort_card_list(self.hands[i], "n"), player_points, player_names), room=self.player_sids[i]
            )

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
        self.winning_bid = self.bids[self.player_winning_bid]
        for i in range(5):
            if i == self.player_winning_bid:
                emit(
                    "kitty request",
                    (
                        sort_card_list(self.kitty + self.hands[self.player_winning_bid], self.winning_bid[-1]),
                        all_bids[self.winning_bid]["name"],
                        self.partner_mode,
                    ),
                    room=self.player_sids[i],
                )
            else:
                emit(
                    "kitty status",
                    (self.player_names[self.player_winning_bid], all_bids[self.winning_bid]["name"]),
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

    def handle_kitty(self, sid, discarded_kitty, partner_data):
        assert len(discarded_kitty) == 3
        self.hands[self.player_winning_bid] = list(
            set(self.hands[self.player_winning_bid] + self.kitty) - set(discarded_kitty)
        )

        if self.partner_mode == "card":
            partner_card = partner_data
            card_str = pretty_card_str(partner_data)
            bidding_player_partner_string = f"{self.player_names[self.player_winning_bid]} and {card_str}"
            for i in range(5):
                if partner_card in self.hands[i]:
                    self.partner_winning_bid = i
                    break
            if self.partner_winning_bid is None:  # Then player chose card in kitty
                self.partner_winning_bid = self.player_winning_bid
        else:
            partner_index = partner_data
            self.partner_winning_bid = (self.player_winning_bid + partner_index) % 5
            if partner_index == 0:
                bidding_player_partner_string = f"{self.player_names[self.player_winning_bid]}"
            else:
                bidding_player_partner_string = (
                    f"{self.player_names[self.player_winning_bid]} and {self.player_names[self.partner_winning_bid]}"
                )

        for i in range(5):
            self.hands[i] = sort_card_list(self.hands[i], self.winning_bid[-1])
            emit("round status", (bidding_player_partner_string, self.hands[i]), room=self.player_sids[i])

        self.tricks_record = []
        self.trick_cards = {}
        self.tricks_won = defaultdict(int)
        self.lead_player = self.player_winning_bid
        self.send_play_request()

    def send_play_request(self):
        for i in range(5):
            current_trick_cards = [self.trick_cards.get((i + j) % 5, "") for j in range(0, 5)]
            hand_sizes = [len(self.hands[(i + j) % 5]) for j in range(1, 5)]
            trick_card_history = [(i, lead, trick) for lead, trick in self.tricks_record]

            card_validity = []
            joker_suit_info = None
            for j in range(len(self.hands[i])):
                validity, joker_suits = is_card_valid(
                    current_trick_cards, trick_card_history, self.winning_bid[-1], self.hands[i], j
                )
                card_validity.append(validity)
                joker_suit_info = joker_suit_info or joker_suits

            if joker_suit_info:
                joker_suit_info = list(joker_suit_info)

            if card_validity:
                assert any(card_validity), f"{current_trick_cards}, {self.winning_bid}, {self.hands[i]}"

            bidding_player_name = self.player_names[(self.lead_player + len(self.trick_cards)) % 5]
            if i == (self.lead_player + len(self.trick_cards)) % 5:
                emit(
                    "play request",
                    (current_trick_cards, hand_sizes, card_validity, joker_suit_info, (i - self.lead_player) % 5),
                    room=self.player_sids[i],
                )
            else:
                emit("play status", (current_trick_cards, bidding_player_name, hand_sizes, (i - self.lead_player) % 5), room=self.player_sids[i])

    def play_card(self, sid, card, socketio):
        # Save the played card
        player_index = self.player_sids.index(sid)
        self.trick_cards[player_index] = card
        if "joker" in card:
            self.hands[player_index].remove("joker")
        else:
            self.hands[player_index].remove(card)

        # Is the round finished
        if len(self.trick_cards) < 5:
            self.send_play_request()
            return

        winner_index = winning_card_index(
            [self.trick_cards[i] for i in range(5)], self.winning_bid[-1], self.lead_player
        )
        self.tricks_won[winner_index] += 1
        for i in range(5):
            emit(
                "play trick",
                (
                    [self.trick_cards.get((i + j) % 5, "") for j in range(0, 5)],
                    self.player_names[winner_index],
                    [self.tricks_won[(i + j) % 5] for j in range(5)],
                    (i - self.lead_player) % 5,
                ),
                room=self.player_sids[i],
            )

        self.tricks_record.append((self.lead_player, self.trick_cards))
        self.lead_player = winner_index
        self.trick_cards = {}

        socketio.sleep(0)
        thread = threading.Thread(target=socketio.sleep, args=(5,))
        thread.start()
        thread.join()

        if len(self.tricks_record) == 10:
            self.end_round(socketio)
        else:
            self.send_play_request()

    @staticmethod
    def get_bid_number(bid):
        for i in range(5, 11):
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
                    self.points[i] += attacker_points
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
            player_points = [self.points[(i + j) % 5] for j in range(5)]
            emit("round result", (status_string, player_points), room=self.player_sids[i])

        socketio.sleep()
        thread = threading.Thread(target=socketio.sleep, args=(5,))
        thread.start()
        thread.join()

        winning_players = [i for i in range(5) if self.points[i] >= 500]
        losing_players = [i for i in range(5) if self.points[i] <= -500]
        if self.player_winning_bid in winning_players or self.partner_winning_bid in winning_players:
            self.end_game(winners=winning_players)
        elif losing_players:
            # Winners are players on most points (ties allowed)
            winning_players = [i for i in range(5) if self.points[i] == max(self.points.values())]
            self.end_game(losers=losing_players, winners=winning_players)
        else:
            self.start_round()

    def end_game(self, winners=None, losers=None):
        if losers:
            if (
                self.player_winning_bid != self.partner_winning_bid
                and self.partner_winning_bid in losers
                and self.player_winning_bid in losers
            ):
                status_string = f"{self.player_names[self.player_winning_bid]} and {self.player_names[self.partner_winning_bid]} lost!"
            elif self.player_winning_bid in losers:
                status_string = f"{self.player_names[self.player_winning_bid]} lost!"
            elif self.partner_winning_bid in losers:
                status_string = f"{self.player_names[self.partner_winning_bid]} lost!"
            if len(winners) == 1:
                status_string += f" {self.player_names[winners[0]]} won!"
            else:
                status_string += f" {', '.join(self.player_names[winner] for winner in winners[1:])} and {self.player_names[winners[0]]} won!"

        else:
            if (
                self.player_winning_bid != self.partner_winning_bid
                and self.partner_winning_bid in winners
                and self.player_winning_bid in winners
            ):
                status_string = f"{self.player_names[self.player_winning_bid]} and {self.player_names[self.partner_winning_bid]} won!"
            elif self.player_winning_bid in winners:
                status_string = f"{self.player_names[self.player_winning_bid]} won!"
            elif self.partner_winning_bid in winners:
                status_string = f"{self.player_names[self.partner_winning_bid]} won!"

        for i in range(5):
            emit("round complete", status_string, room=self.player_sids[i])
