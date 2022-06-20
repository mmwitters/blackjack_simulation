import unittest

from cards import Deck, Suit, Rank, Card


class DeckTests(unittest.TestCase):
    def test_standard_deck(self):
        self.assertEqual(Deck.standard_deck(), Deck.standard_deck())
        self.assertEqual(52, len(Deck.standard_deck()))
        self.assertEqual(52, len(set(Deck.standard_deck().cards)))

    def test_shuffle_deck(self):
        shuffle = Deck.standard_deck().shuffle()
        self.assertEqual(52, len(shuffle))
        self.assertEqual(Deck([]), Deck([]).shuffle())
        self.assertEqual(Deck([Card(Rank.KING, Suit.HEART)]), Deck([Card(Rank.KING, Suit.HEART)]).shuffle())
        self.assertEqual(frozenset([Card(Rank.KING, Suit.HEART), Card(Rank.QUEEN, Suit.HEART)]),
                         frozenset(Deck([Card(Rank.KING, Suit.HEART), Card(Rank.QUEEN, Suit.HEART)]).shuffle().cards))


if __name__ == '__main__':
    unittest.main()
