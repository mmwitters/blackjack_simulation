from dataclasses import dataclass
from enum import unique, Enum, auto
from itertools import product
from typing import NamedTuple

from cards import Deck, Card, Rank


def card_value(card: Card) -> list[int]:
    face_cards = [Rank.JACK,
                  Rank.QUEEN,
                  Rank.KING]
    if card.rank == Rank.ACE:
        return [1, 11]
    elif card.rank in face_cards:
        return [10]
    else:
        return [card.rank.value]


# TODO do we want to make the card order agnostic?
@dataclass(frozen=True)
class Hand:
    cards: list[Card]

    def card_totals(self) -> set[int]:
        return set(map(sum, product(*list(map(card_value, self.cards)))))

    def is_busted(self) -> bool:
        for element in self.card_totals():
            if element <= 21:
                return False
        return True

    def add_card(self, card: Card):
        new_hand = self.cards.copy() + [card]
        return Hand(new_hand)

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

    # limited to 5-9 betting boxes total
    # player cannot play more than 3 boxes (US rules)


class Dealer(NamedTuple):
    hand: Hand
    shoe: Deck  # added -- will need to accomodate multiple decks (1-8 decks total)

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

    def advance_player(self):
        return self._replace(player_turn=self.player_turn + 1)


@unique
class PlayerAction(Enum):
    Hit = auto()
    Stand = auto()


# TODO add in remaining 3 actions: double down, split, and surrender

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
    if hand.is_busted():
        table = table.advance_player()

    return table._replace(dealer=table.dealer._replace(shoe=deck))


def stand(table: Table) -> Table:
    current_betting_box = table.betting_boxes[table.player_turn]
    if current_betting_box.hand.is_busted():
        print(table)
        raise Exception("Can't Stand Busted Hand")

    return table.advance_player()

def dealer_moves(table: Table) -> Table:
    deck = table.dealer.shoe
    card, deck = deck.draw_card()
    dealer_hand = table.dealer.hand.add_card(card) #dealer draws 2nd card
    if any(dealer_hand.card_totals()) >= 17:
        return table._replace(dealer=Dealer(dealer_hand, deck))
    while not any(dealer_hand.card_totals()) >= 17: #keep drawing cards until point totals exceeds 17
        card, deck = deck.draw_card()
        dealer_hand = table.dealer.hand.add_card(card)
    return table._replace(dealer=Dealer(dealer_hand, deck))


