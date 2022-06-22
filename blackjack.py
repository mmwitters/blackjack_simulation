from dataclasses import dataclass
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

# Hand / Dealer Hand
@dataclass(frozen=True)
class Hand:
    cards: list[Card]
    def card_totals(self) -> set[int]:
        return set(map(sum, product(*list(map(card_value, self.cards)))))



# Table

# Betting Box(es)

# Player Action

