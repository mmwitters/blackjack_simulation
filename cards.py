from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import List
from itertools import product


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

@dataclass
class Card:
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

@dataclass
class Deck:
    cards: List[Card]

    @staticmethod
    def standard_deck():
        cards = [Card(*tup) for tup in product(Rank, Suit)]
        return Deck(cards)


