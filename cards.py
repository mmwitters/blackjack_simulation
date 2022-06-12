# card: suit, deck, rank
from enum import Enum


class Suit(Enum):
    SPADE = 1
    HEART = 2
    CLUB = 3
    DIAMOND = 4

    def __str__(self) -> str:
        if self == Suit.SPADE:
            return "♠"
        if self == Suit.DIAMOND:
            return "♦"
        if self == Suit.HEART:
            return "♥"
        if self == Suit.CLUB:
            return "♣"
