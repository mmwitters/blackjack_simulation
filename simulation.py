import typing
from collections import Counter
from math import sqrt
from random import choice
from typing import NamedTuple

from blackjack import Table, PlayerAction, BettingBox, Player, Hand, Dealer, shoe, initial_draw, \
    table_payout, hit, stand, dealer_moves, double_down, split
from cards import Deck


# Assumes that the same bet is being used for each hand
# Assumes result is for a single hand (Split not handled)
class SimulationResult(NamedTuple):
    result_counter: Counter[int]

    def __add__(self, x):
        return SimulationResult(self.result_counter + x.result_counter)

    def total_games(self) -> int:
        return sum(self.result_counter.values())

    def expected_winnings(self) -> float:
        return self.total_winnings() / self.total_games()

    def sample_variance_winnings(self) -> float:
        expected_winnings = self.expected_winnings()

        variance_sum = 0
        for winnings, occurrences in self.result_counter.items():
            variance_sum += (winnings ** 2) * occurrences
        variance_sum /= self.total_games()
        return variance_sum - (expected_winnings ** 2)

    def sample_std_deviation(self) -> float:
        return sqrt(self.sample_variance_winnings())

# TODO rewrite this for use only when simulating multiple rounds with same strategy
    # def confidence_interval_winnings(self) -> tuple:
    #     expected_winnings = self.expected_winnings()
    #     sample_std_dev = self.sample_std_deviation()
    #     lower_bound = expected_winnings - 1.96*sample_std_dev/sqrt(self.total_games())
    #     upper_bound = expected_winnings + 1.96*sample_std_dev/sqrt(self.total_games())
    #     return lower_bound, upper_bound


    def total_winnings(self):
        return sum((winnings * occurrences for winnings, occurrences in self.result_counter.items()))


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
always_double_down = Strategy(lambda table: PlayerAction.DoubleDown, 10)


def double_down_on_eleven_fn(table):
    if len(table.current_player_betting_box().hand.cards) == 2 and table.current_player_betting_box().hand.card_totals() == {
        11}:
        return PlayerAction.DoubleDown
    else:
        return PlayerAction.Stand


double_down_on_eleven = Strategy(double_down_on_eleven_fn, 10)


def split_when_possible(table):
    betting_box = table.current_player_betting_box()
    if betting_box.can_split():
        return PlayerAction.Split
    return PlayerAction.Stand


always_split_when_possible = Strategy(split_when_possible, 10)

def known_strategy(table): #implemented when dealer stands on soft 17
    player_hand_totals = max(table.current_player_betting_box().hand.card_totals())
    dealer_hand_totals = table.dealer.hand.card_totals()[0]
    if table.current_player_betting_box().can_split():
        pass
    # TODO write logic for when a player can split their cards

    elif not player_hand_totals.is_soft(): #if player hand is hard
        if player_hand_totals <= 8:
            return PlayerAction.Hit
        elif player_hand_totals == 9:
            if dealer_hand_totals in [2,7,8,9,10,11]:
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals == 10:
            if dealer_hand_totals <= 9:
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 11:
            if dealer_hand_totals <= 10:
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 12:
            if dealer_hand_totals not in [4,5,6]:
                return PlayerAction.Hit
            else:
                return PlayerAction.Stand
        elif 13 <= player_hand_totals <= 16:
            if dealer_hand_totals <= 6:
                return PlayerAction.Stand
            else:
                return PlayerAction.Hit
        elif player_hand_totals >= 17:
            return PlayerAction.Stand
    elif player_hand_totals.is_soft(): #if player hand is soft
        if player_hand_totals <= 14:
            if dealer_hand_totals <= 4 or dealer_hand_totals >= 7:
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals <= 16:
            if dealer_hand_totals < 4 or dealer_hand_totals >= 7:
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals == 17:
            if dealer_hand_totals == 2 or dealer_hand_totals >= 7:
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals == 18:
            if dealer_hand_totals in [2,7,8]:
                return PlayerAction.Stand
            elif dealer_hand_totals > 2 and dealer_hand_totals <= 6:
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 19:
            return PlayerAction.Stand



# INDEPENDENT GAMES
def run_single_simulation(strategy) -> SimulationResult:
    dealer = Dealer(Hand([]), shoe(Deck.standard_deck(), 6).shuffle())
    table = Table([BettingBox(Hand([]), Player("Maddie"), strategy.bet)], dealer, 0)
    table = initial_draw(table)
    while table.play_in_progress():
        if table.current_player_betting_box().hand.is_blackjack():
            table = table.advance_player()
            continue

        action = strategy.get_action(table)
        if table.current_player_betting_box().hand.is_busted():
            table = table.advance_player()
        elif action == PlayerAction.Hit:
            table = hit(table)
        elif action == PlayerAction.Stand:
            table = stand(table)
            table = table.advance_player()
        elif action == PlayerAction.DoubleDown:
            table = double_down(table)
            table = table.advance_player()
        elif action == PlayerAction.Split:
            table = split(table)
        else:
            raise f"Unknown PlayerAction: {action}"

    table = dealer_moves(table)
    payout = table_payout(table)[Player("Maddie")]  # We only care about Maddie for now
    sim_result = SimulationResult(Counter([payout]))
    return sim_result


def run_simulation(strategy, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter())
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
        table.current_player_betting_box().hand.card_totals()) >= i else PlayerAction.Hit, 10), 10000)
    means.append(simulation.expected_winnings())
    print_simulation_result(f"Hit Below {i}", simulation)
#
# s = run_simulation(double_down_on_eleven, 10_000)
# print_simulation_result("Double down", s)
# s = run_simulation(always_stay_strategy, 10_000)
# print_simulation_result("Always stay", s)
# s = run_simulation(always_split_when_possible, 10_000)
# print_simulation_result("Split when possible", s)

# TODO if dealer runs out of cards, re-shuffle
# TODO implement ability to simulate multiple rounds with same strategy; then output mean result and min/max and CIs
# TODO implement "known" strategy (as closely as possible)