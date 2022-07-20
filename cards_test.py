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

    def test_draw_card_from_standard_deck(self):
        card, deck = Deck.standard_deck().draw_card()
        self.assertEqual(51, len(deck))
        self.assertIsNotNone(card)

    def test_draw_card_empty_deck(self):
        self.assertEqual((None, Deck([])), Deck([]).draw_card())

    def test_ensure_same_card_not_drawn_each_time(self):
        deck = Deck([Card(Rank.TEN, Suit.CLUB), Card(Rank.JACK, Suit.SPADE)])
        card, deck2 = deck.draw_card()
        self.assertEqual(card, Card(Rank.TEN, Suit.CLUB))
        self.assertEqual(deck2, Deck([Card(Rank.JACK, Suit.SPADE)]))
        card2, deck3 = deck2.draw_card()
        self.assertEqual(card2, Card(Rank.JACK, Suit.SPADE))
        self.assertEqual(deck3, Deck([]))


if __name__ == '__main__':
    unittest.main()
