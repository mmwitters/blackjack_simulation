import unittest

from cards import Deck, Suit, Rank, Card
from blackjack import Hand

class BlackjackTests(unittest.TestCase):
    def test_hand_values(self):
        self.assertEqual(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]).card_totals(), {16, 6})
        self.assertEqual(Hand([Card(Rank.KING, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]).card_totals(), {15})
        self.assertEqual(Hand([Card(Rank.FIVE, Suit.HEART), Card(Rank.FOUR, Suit.SPADE)]).card_totals(), {9})


if __name__ == '__main__':
    unittest.main()
