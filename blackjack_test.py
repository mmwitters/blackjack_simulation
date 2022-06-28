import unittest

from cards import Deck, Suit, Rank, Card
from blackjack import Hand


class BlackjackTests(unittest.TestCase):
    def test_hand_values(self):
        self.assertEqual(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]).card_totals(), {16, 6})
        self.assertEqual(Hand([Card(Rank.KING, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]).card_totals(), {15})
        self.assertEqual(Hand([Card(Rank.FIVE, Suit.HEART), Card(Rank.FOUR, Suit.SPADE)]).card_totals(), {9})
        self.assertEqual(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.SPADE)]).card_totals(), {2, 12, 22})

    def test_is_busted(self):
        self.assertFalse(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]).is_busted())
        self.assertFalse(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.KING, Suit.SPADE)]).is_busted())
        self.assertFalse(
            Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.FIVE, Suit.SPADE), Card(Rank.SIX, Suit.SPADE)]).is_busted())
        self.assertTrue(
            Hand([Card(Rank.TEN, Suit.HEART), Card(Rank.SIX, Suit.SPADE), Card(Rank.SIX, Suit.HEART)]).is_busted())
        self.assertTrue(
            Hand([Card(Rank.SIX, Suit.HEART), Card(Rank.SEVEN, Suit.SPADE), Card(Rank.NINE, Suit.HEART)]).is_busted())
        self.assertTrue(
            Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.SPADE), Card(Rank.TEN, Suit.HEART),
                  Card(Rank.TEN, Suit.SPADE)]).is_busted())
        self.assertFalse(Hand([]).is_busted())

    def test_hit(self):
        self.assertEqual(Hand([]).hit(Card(Rank.KING, Suit.HEART)), Hand([Card(Rank.KING, Suit.HEART)]))
        self.assertEqual(Hand([Card(Rank.KING, Suit.HEART)]).hit(Card(Rank.KING, Suit.SPADE)), Hand([Card(Rank.KING, Suit.HEART), Card(Rank.KING, Suit.SPADE)]))

if __name__ == '__main__':
    unittest.main()
