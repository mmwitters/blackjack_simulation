import typing
from abc import ABC, abstractmethod
from math import sqrt
from random import choice
from typing import NamedTuple, Tuple, overload, Any
from collections import Counter

from blackjack import HandResult, Table, PlayerAction, BettingBox, Player, Hand, Dealer, shoe, initial_draw, \
    table_payout, hit, stand, dealer_moves
from cards import Deck


# Assumes that the same bet is being used for each hand
# Assumes result is for a single hand (Split not handled)
class SimulationResult(NamedTuple):
    result_counter: Counter[HandResult]
    total_winnings: int
    hand_bet: int

    def __add__(self, x):
        if self.hand_bet != x.hand_bet:
            raise f"Hand Bets must be the same but were {self.hand_bet} != {x.hand_bet}"
        return SimulationResult(self.result_counter + x.result_counter, self.total_winnings + x.total_winnings,
                                x.hand_bet)

    def total_games(self) -> int:
        return sum(self.result_counter.values())

    def expected_winnings(self) -> float:
        return self.total_winnings / self.total_games()

    def sample_variance_winnings(self) -> float:
        expected_winnings = self.expected_winnings()

        lost_games = ((-1 * self.hand_bet) - expected_winnings) ** 2 * self.result_counter[HandResult.Loss]
        won_games = (self.hand_bet - expected_winnings) ** 2 * self.result_counter[HandResult.Win]
        tie_games = (self.hand_bet - expected_winnings) ** 2 * self.result_counter[HandResult.Tie]
        return (lost_games + won_games + tie_games) / (self.total_games() - 1)

    def sample_std_deviation(self) -> float:
        return sqrt(self.sample_variance_winnings())


class Strategy(NamedTuple):
    get_action: typing.Callable[[Table], PlayerAction]
    bet: int
    # actions chosen randomly
    # always staying
    # use "optimal" blackjack rules
    # card counting (?)


always_stay_strategy = Strategy(lambda table: PlayerAction.Stand, 10)
always_hit = Strategy(lambda table: PlayerAction.Hit, 10)
choose_random_strategy = Strategy(lambda table: choice(list(PlayerAction)), 10)


# INDEPENDENT GAMES
def run_single_simulation(strategy) -> SimulationResult:
    dealer = Dealer(Hand([]), shoe(Deck.standard_deck(), 6).shuffle())
    table = Table([BettingBox(Hand([]), Player("Maddie"), strategy.bet)], dealer, 0)
    table = initial_draw(table)
    for _ in table.betting_boxes:
        # TODO Automatically win if you have blackjack. Check if you can hit on 21.
        while not table.current_player_betting_box().hand.is_busted() and (
                action := strategy.get_action(table)) != PlayerAction.Stand:
            if action == PlayerAction.Hit:
                table = hit(table)
            elif action == PlayerAction.Stand:
                table = stand(action)
            else:
                raise f"Unknown PlayerAction: {action}"
        table = table.advance_player()
    table = dealer_moves(table)
    result, payout = table_payout(table)[Player("Maddie")]  # We only care about Maddie for now
    sim_result = SimulationResult(Counter([result]), payout, strategy.bet)
    return sim_result


def run_simulation(strategy, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter(), 0, strategy.bet)
    for i in range(num_runs):
        simulation_result += run_single_simulation(strategy)
    return simulation_result


def print_simulation_result(name, simulation):
    print(name)
    print(simulation)
    print(f"Mean: {simulation.expected_winnings()}")
    print(f"Sample Variance: {simulation.sample_variance_winnings()}")
    print(f"Sample standard deviation: {simulation.sample_std_deviation()} ")
    print("")


means = []
for i in range(1, 20):
    simulation = run_simulation(Strategy(lambda table: PlayerAction.Stand if min(
        table.current_player_betting_box().hand.card_totals()) >= i else PlayerAction.Hit, 10), 25_000)
    means.append(simulation.expected_winnings())
    print_simulation_result(f"Hit Below {i}", simulation)
print(means)