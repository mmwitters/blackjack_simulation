from dataclasses import dataclass
from enum import unique, Enum, auto
from itertools import product

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

    def hit(self, card: Card):
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


@dataclass(frozen=True)
class BettingBox:
    hand: Hand
    player: Player
    bet: int

    # limited to 5-9 betting boxes total
    # player cannot play more than 3 boxes (US rules)
    def with_hand(self, hand):
        return BettingBox(hand, self.player, self.bet)


@dataclass(frozen=True)
class Dealer:
    hand: Hand
    shoe: Deck  # added -- will need to accomodate multiple decks (1-8 decks total)

    @classmethod
    def emptyDealer(cls, deck: Deck):
        return Dealer(Hand.emptyHand(), deck)


@dataclass(frozen=True)
class Table:
    betting_boxes: list[BettingBox]
    dealer: Dealer


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
        for i in range(2):
            card, deck = deck.draw_card()
            hand = hand.hit(card)
        betting_boxes.append(betting_box.with_hand(hand))

    return Table(betting_boxes, Dealer(table.dealer.hand, deck))
