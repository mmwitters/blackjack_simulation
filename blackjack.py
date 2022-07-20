from collections import Counter
from dataclasses import dataclass
from enum import unique, Enum, auto
from itertools import product
from typing import NamedTuple

from cards import Deck, Card, Rank


def card_value(card: Card) -> set[int]:
    face_cards = [Rank.JACK,
                  Rank.QUEEN,
                  Rank.KING]
    if card.rank == Rank.ACE:
        return {1, 11}
    elif card.rank in face_cards:
        return {10}
    else:
        return {card.rank.value}


# TODO do I want to make the card order agnostic?
@dataclass(frozen=True)
class Hand:
    cards: list[Card]

    def card_totals(self) -> set[int]:
        return set(map(sum, product(*list(map(card_value, self.cards)))))

    def largest_card_total(self) -> int:
        totals = self.card_totals()
        rev_set = set()
        for total in totals:
            if total <= 21:
                rev_set.add(total)
        return max(rev_set)

    def is_busted(self) -> bool:
        for element in self.card_totals():
            if element <= 21:
                return False
        return True

    def add_card(self, card: Card):
        new_hand = self.cards.copy() + [card]
        return Hand(new_hand)

    def is_blackjack(self):
        if len(self.cards) == 2 and 21 in self.card_totals():
            return True
        return False

    def is_soft(self):
        return len(list(filter(lambda t: t <= 21, self.card_totals()))) > 1

    @classmethod
    def emptyHand(cls):
        return Hand([])

    def __repr__(self) -> str:
        cards = ",".join(map(repr, self.cards))
        return f"<{cards}>"


@dataclass(frozen=True)
class Player:
    name: str


class BettingBox(NamedTuple):
    hand: Hand
    player: Player
    bet: int
    split: bool = False

    def can_split(self) -> bool:
        if self.hand.is_busted() or len(self.hand.cards) != 2 or self.split:
            return False
        return card_value(self.hand.cards[0]) == card_value(self.hand.cards[1])

    def can_double_down(self):
        if len(self.hand.cards) != 2:
            return False
        if self.split:
            return False
        return True


class Dealer(NamedTuple):
    hand: Hand
    shoe: Deck

    @classmethod
    def emptyDealer(cls, deck: Deck):
        return Dealer(Hand.emptyHand(), deck)


class Table(NamedTuple):
    betting_boxes: list[BettingBox]
    dealer: Dealer
    player_turn: int

    def replace_betting_box(self, position: int, betting_box: BettingBox):
        betting_boxes = self.betting_boxes.copy()
        betting_boxes[position] = betting_box
        return self._replace(betting_boxes=betting_boxes)

    def current_player_betting_box(self) -> BettingBox:
        return self.betting_boxes[self.player_turn]

    def advance_player(self):
        return self._replace(player_turn=self.player_turn + 1)

    def play_in_progress(self) -> bool:
        return self.player_turn < len(self.betting_boxes)


@unique
class PlayerAction(Enum):
    Hit = auto()
    Stand = auto()
    DoubleDown = auto()
    Split = auto()


@unique
class HandResult(Enum):
    Win = auto()
    Tie = auto()
    Loss = auto()


def shoe(deck: Deck, num_of_decks: int) -> Deck:
    return Deck([card for card in deck.cards for _ in range(num_of_decks)])


# "hole card" games
def initial_draw(table: Table) -> Table:
    deck = table.dealer.shoe
    betting_boxes = []

    for betting_box in table.betting_boxes:
        hand = betting_box.hand
        card, deck = deck.draw_card()
        hand = hand.add_card(card)
        betting_boxes.append(betting_box._replace(hand=hand))
    card, deck = deck.draw_card()
    dealer_hand = table.dealer.hand.add_card(card)
    for i, betting_box in enumerate(betting_boxes):
        hand = betting_box.hand
        card, deck = deck.draw_card()
        hand = hand.add_card(card)
        betting_boxes[i] = betting_box._replace(hand=hand)

    return table._replace(dealer=Dealer(dealer_hand, deck), betting_boxes=betting_boxes)


def hit(table: Table) -> Table:
    current_betting_box = table.betting_boxes[table.player_turn]
    if current_betting_box.hand.is_busted():
        print(table)
        raise Exception("Can't Hit Busted Hand")

    card, deck = table.dealer.shoe.draw_card()
    hand = current_betting_box.hand.add_card(card)
    table = table.replace_betting_box(table.player_turn, current_betting_box._replace(hand=hand))

    return table._replace(dealer=table.dealer._replace(shoe=deck))


def stand(table: Table) -> Table:
    current_betting_box = table.betting_boxes[table.player_turn]

    if current_betting_box.hand.is_busted():
        print(table)
        raise Exception("Can't Stand Busted Hand")

    return table


def double_down(table: Table) -> Table:
    current_betting_box = table.betting_boxes[table.player_turn]

    if not current_betting_box.can_double_down():
        print(table)
        raise Exception("Can't double down after hitting")

    new_bet = current_betting_box.bet * 2
    card, deck = table.dealer.shoe.draw_card()
    hand = current_betting_box.hand.add_card(card)
    table = table.replace_betting_box(table.player_turn, current_betting_box._replace(hand=hand, bet=new_bet))

    return table._replace(dealer=table.dealer._replace(shoe=deck))


def split(table: Table) -> Table:
    current_betting_box = table.betting_boxes[table.player_turn]
    deck = table.dealer.shoe

    if not current_betting_box.can_split():
        print(table)
        raise Exception("Can't Split Busted Hand")

    card_1 = current_betting_box.hand.cards[0]
    card_2 = current_betting_box.hand.cards[1]

    card, deck = deck.draw_card()
    betting_box1 = BettingBox(Hand([card_1, card]), current_betting_box.player, current_betting_box.bet, split=True)
    card, deck = deck.draw_card()
    betting_box2 = BettingBox(Hand([card_2, card]), current_betting_box.player, current_betting_box.bet, split=True)

    betting_boxes = table.betting_boxes[:table.player_turn]
    betting_boxes += [betting_box1, betting_box2]
    betting_boxes += table.betting_boxes[table.player_turn + 1:]

    return table._replace(betting_boxes=betting_boxes, dealer=table.dealer._replace(shoe=deck))


def dealer_moves(table: Table) -> Table:
    deck = table.dealer.shoe
    card, deck = deck.draw_card()
    dealer_hand = table.dealer.hand.add_card(card)
    while max(dealer_hand.card_totals()) < 17:
        card, deck = deck.draw_card()
        dealer_hand = dealer_hand.add_card(card)
    return table._replace(dealer=table.dealer._replace(hand=dealer_hand, shoe=deck))


def individual_payout(betting_box: BettingBox, result: HandResult) -> int:
    """
    Calculates the payout to an individual for a single round
    :param betting_box: individual who is playing/making a bet
    :param result: whether individual won/tied/lost
    :return: amount of money received after current round
    """
    if result == HandResult.Win:
        return betting_box.bet
    elif result == HandResult.Tie:
        return 0
    return -1 * betting_box.bet


def hand_result(betting_box: BettingBox, dealer: Dealer) -> HandResult:
    if betting_box.hand.is_blackjack() and dealer.hand.is_blackjack():
        return HandResult.Tie
    elif betting_box.hand.is_blackjack():
        return HandResult.Win
    elif dealer.hand.is_blackjack():
        return HandResult.Loss
    elif betting_box.hand.is_busted():
        return HandResult.Loss
    elif dealer.hand.is_busted():
        return HandResult.Win
    else:
        filtered = list(filter(lambda x: x <= 21, betting_box.hand.card_totals()))
        dealer_filtered = list(filter(lambda x: x <= 21, dealer.hand.card_totals()))
        if max(filtered) > max(dealer_filtered):
            return HandResult.Win
        elif max(filtered) < max(dealer_filtered):
            return HandResult.Loss
        else:
            return HandResult.Tie


def table_payout(table: Table) -> Counter[Player, int]:
    results = Counter()
    for betting_box in table.betting_boxes:
        result = hand_result(betting_box, table.dealer)
        payout = individual_payout(betting_box, result)
        results[betting_box.player] += payout
    return results
