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


class BettingBox:
    hand: Hand
    pass
    # limited to 5-9 betting boxes total
    # player cannot play more than 3 boxes (US rules)

class Dealer:
    hand: Hand
    deck: Deck #added -- will need to accomodate multiple decks (1-8 decks total)

class Player:
    betting_box: BettingBox
    # I think this makes more sense than a Hand, but I'm unsure which a player is assigned to first

@dataclass(frozen=True)
class Table:
    betting_boxes: list[BettingBox]
    dealer: Dealer

# Player Action
