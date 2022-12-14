from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import List
from itertools import product
from random import shuffle


@unique
class Suit(Enum):
    SPADE = auto()
    HEART = auto()
    CLUB = auto()
    DIAMOND = auto()

    def __str__(self) -> str:
        if self == Suit.SPADE:
            return "♠"
        if self == Suit.DIAMOND:
            return "♦"
        if self == Suit.HEART:
            return "♥"
        if self == Suit.CLUB:
            return "♣"


@unique
class Rank(Enum):
    ACE = "A"
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass(frozen=True)
class Deck:
    cards: List[Card]

    @staticmethod
    def standard_deck():
        return Deck([Card(*tup) for tup in product(Rank, Suit)])

    def shuffle(self):
        copy = self.cards.copy()
        shuffle(copy)
        return Deck(copy)

    def __len__(self):
        return len(self.cards)

    def draw_card(self):
        if len(self) == 0:
            return None, Deck([])
        return self.cards[0], Deck(self.cards[1:])

    def __repr__(self) -> str:
        cards = "".join(map(repr, self.cards))
        return f"({cards})"
