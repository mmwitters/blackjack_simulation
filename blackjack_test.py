import unittest

from cards import Deck, Suit, Rank, Card
from blackjack import Hand, Table, Dealer, initial_draw, BettingBox, Player, hit, stand, dealer_moves


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

    def test_add_card(self):
        self.assertEqual(Hand([]).add_card(Card(Rank.KING, Suit.HEART)), Hand([Card(Rank.KING, Suit.HEART)]))
        self.assertEqual(Hand([Card(Rank.KING, Suit.HEART)]).add_card(Card(Rank.KING, Suit.SPADE)),
                         Hand([Card(Rank.KING, Suit.HEART), Card(Rank.KING, Suit.SPADE)]))

    def test_empty_table_step_does_nothing(self):
        table = Table([], Dealer.emptyDealer(Deck([Card(Rank.ACE, Suit.HEART)])), 0)
        self.assertEqual(Table([], Dealer(Hand([Card(Rank.ACE, Suit.HEART)]), Deck([])), 0), initial_draw(table))

    def test_single_player_empty_table(self):
        box = BettingBox(Hand.emptyHand(), Player("Maddie"), 5)
        table = Table([box], Dealer.emptyDealer(
            Deck([Card(Rank.ACE, Suit.HEART), Card(Rank.TWO, Suit.HEART), Card(Rank.THREE, Suit.HEART)])), 0)
        expected_table = Table(
            [BettingBox(Hand([Card(Rank.ACE, Suit.HEART), Card(Rank.THREE, Suit.HEART)]), Player("Maddie"), 5)],
            Dealer(Hand([Card(Rank.TWO, Suit.HEART)]), Deck([])), 0)
        self.assertEqual(expected_table, initial_draw(table))

    def test_hit(self):
        table = Table([BettingBox(Hand([Card(Rank.ACE, Suit.HEART),
                                        Card(Rank.THREE, Suit.HEART)]),
                                  Player("Maddie"),
                                  5)],
                      Dealer(Hand([Card(Rank.TWO, Suit.HEART)]),
                             Deck([Card(Rank.TWO, Suit.CLUB)])),
                      0)
        expected_table = Table([BettingBox(Hand([Card(Rank.ACE, Suit.HEART),
                                                 Card(Rank.THREE, Suit.HEART),
                                                 Card(Rank.TWO, Suit.CLUB)]),
                                           Player("Maddie"), 5)],
                               Dealer(Hand([Card(Rank.TWO,
                                                 Suit.HEART)]),
                                      Deck([])),
                               0)
        self.assertEqual(expected_table, hit(table))

    def test_hit_busts(self):
        table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                        Card(Rank.TEN, Suit.HEART)]),
                                  Player("Maddie"), 5)],
                      Dealer(Hand([Card(Rank.TWO, Suit.HEART)]),
                             Deck([Card(Rank.TWO, Suit.CLUB)])),
                      0)
        expected_table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                                 Card(Rank.TEN, Suit.HEART),
                                                 Card(Rank.TWO, Suit.CLUB)]),
                                           Player("Maddie"),
                                           5)],
                               Dealer(Hand([Card(Rank.TWO, Suit.HEART)]),
                                      Deck([])),
                               1)
        self.assertEqual(expected_table, hit(table))

    def test_stand(self):
        table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                        Card(Rank.TEN, Suit.HEART)]),
                                  Player("Maddie"), 5)],
                      Dealer(Hand([Card(Rank.TWO, Suit.HEART)]),
                             Deck([Card(Rank.TWO, Suit.CLUB)])),
                      0)
        expected_table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                                 Card(Rank.TEN, Suit.HEART)]),
                                           Player("Maddie"),
                                           5)],
                               Dealer(Hand([Card(Rank.TWO, Suit.HEART)]),
                                      Deck([Card(Rank.TWO, Suit.CLUB)])),
                               1)
        self.assertEqual(expected_table, stand(table))

    def test_dealer_moves(self):
        table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                        Card(Rank.TEN, Suit.HEART)]),
                                  Player("Maddie"),
                                  5)],
                      Dealer(Hand([Card(Rank.EIGHT, Suit.HEART)]),
                             Deck([Card(Rank.NINE, Suit.CLUB), Card(Rank.FIVE, Suit.CLUB)])),
                      1)
        expected_table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                                 Card(Rank.TEN, Suit.HEART)]),
                                           Player("Maddie"),
                                           5)],
                               Dealer(Hand([Card(Rank.EIGHT, Suit.HEART), Card(Rank.NINE, Suit.CLUB)]),
                                      Deck([Card(Rank.FIVE, Suit.CLUB)])),
                               1)
        self.assertEqual(expected_table, dealer_moves(table))

    def test_dealer_moves_draws3(self):
        table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                        Card(Rank.TEN, Suit.HEART)]),
                                  Player("Maddie"),
                                  5)],
                      Dealer(Hand([Card(Rank.NINE, Suit.HEART)]),
                             Deck([Card(Rank.SEVEN, Suit.CLUB),
                                   Card(Rank.ACE, Suit.CLUB),
                                   Card(Rank.EIGHT, Suit.DIAMOND)])),
                      1)
        expected_table = Table([BettingBox(Hand([Card(Rank.TEN, Suit.SPADE),
                                                 Card(Rank.TEN, Suit.HEART)]),
                                           Player("Maddie"),
                                           5)],
                               Dealer(Hand([Card(Rank.NINE, Suit.HEART),
                                            Card(Rank.SEVEN, Suit.CLUB),
                                            Card(Rank.ACE, Suit.CLUB)]),
                                      Deck([Card(Rank.EIGHT, Suit.DIAMOND)])),
                               1)
        self.assertEqual(expected_table, dealer_moves(table))


if __name__ == '__main__':
    unittest.main()
