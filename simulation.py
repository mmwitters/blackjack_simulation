import csv
import typing
from collections import Counter
from math import sqrt
from random import choice, seed
from typing import NamedTuple

from matplotlib import pyplot as plt
from progressbar import progressbar

from blackjack import Table, PlayerAction, BettingBox, Player, Hand, Dealer, shoe, initial_draw, \
    table_payout, hit, stand, dealer_moves, double_down, split
from cards import Deck, Rank

seed(5)


# Assumes that the same bet is being used for each hand
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

    def confidence_interval_winnings(self) -> tuple:
        expected_winnings = self.expected_winnings()
        sample_std_dev = self.sample_std_deviation()
        lower_bound = expected_winnings - 1.96 * sample_std_dev / sqrt(self.total_games())
        upper_bound = expected_winnings + 1.96 * sample_std_dev / sqrt(self.total_games())
        return lower_bound, upper_bound

    def total_winnings(self):
        return sum((winnings * occurrences for winnings, occurrences in self.result_counter.items()))

    def percentage_games_profitable(self):
        count = 0
        for winnings, occurrences in self.result_counter.items():
            if winnings >= 0:
                count += occurrences
        return count / self.total_games()

    def range(self) -> tuple:
        min_winnings = min(self.result_counter)
        max_winnings = max(self.result_counter)
        return min_winnings, max_winnings

    def create_hist(self, name, color):
        labels, values = zip(*sorted(self.result_counter.items()))
        plt.bar(labels, values, 10, linewidth=1, edgecolor="black", alpha=0.4, label=name, color=color)
        plt.xlabel("Winnings")
        plt.ylabel("Frequency")


class Strategy(NamedTuple):
    get_action: typing.Callable[[Table], PlayerAction]
    bet: int
    name: str
    color: str


always_stand_strategy = Strategy(lambda table: PlayerAction.Stand, 10, "Always Stand", "orange")
always_hit_strategy = Strategy(lambda table: PlayerAction.Hit, 10, "Always Hit", "pink")
always_double_down = Strategy(lambda table: PlayerAction.DoubleDown, 10, "Always Double Down", "green")


def hit_under_seventeen_fn(table):
    if min(table.current_player_betting_box().hand.card_totals()) < 17:
        return PlayerAction.Hit
    else:
        return PlayerAction.Stand


hit_under_seventeen = Strategy(hit_under_seventeen_fn, 10, "Hit Under 17", "purple")


def random_strategy_fn(table):
    choices = [PlayerAction.Hit, PlayerAction.Stand]
    if table.current_player_betting_box().can_double_down():
        choices.append(PlayerAction.DoubleDown)
    if table.current_player_betting_box().can_split():
        choices.append(PlayerAction.Split)
    return choice(choices)


choose_random_strategy = Strategy(random_strategy_fn, 10, "Random Action", "red")


def double_down_on_eleven_fn(table):
    if len(table.current_player_betting_box().hand.cards) == 2 and table.current_player_betting_box().hand.card_totals() == {
        11}:
        return PlayerAction.DoubleDown
    else:
        return PlayerAction.Stand


double_down_on_eleven = Strategy(double_down_on_eleven_fn, 10, "Double Down on 11", "aqua")


def split_when_possible(table):
    betting_box = table.current_player_betting_box()
    if betting_box.can_split():
        return PlayerAction.Split
    return PlayerAction.Stand


always_split_when_possible = Strategy(split_when_possible, 10, "Split When Possible", "yellow")


def known_strategy(table):  # implemented when dealer stands on soft 17
    player_hand_totals = table.current_player_betting_box().hand.largest_card_total()
    dealer_hand_totals = max(table.dealer.hand.card_totals())
    if table.current_player_betting_box().can_split():
        if player_hand_totals == 4 or player_hand_totals == 6:
            if dealer_hand_totals < 4 or dealer_hand_totals > 7:
                return PlayerAction.Hit
            else:
                return PlayerAction.Split
        elif player_hand_totals == 8:
            return PlayerAction.Hit
        elif player_hand_totals == 10:
            if dealer_hand_totals < 10 and table.current_player_betting_box().can_double_down():
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif table.current_player_betting_box().hand.cards[0].rank == Rank.ACE:
            return PlayerAction.Split
        elif player_hand_totals == 12:
            if dealer_hand_totals == 2 or dealer_hand_totals >= 7:
                return PlayerAction.Hit
            else:
                return PlayerAction.Split
        elif player_hand_totals == 14:
            if dealer_hand_totals <= 7:
                return PlayerAction.Split
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 16:
            return PlayerAction.Split
        elif player_hand_totals == 18:
            if dealer_hand_totals not in [7, 10, 11]:
                return PlayerAction.Split
            else:
                return PlayerAction.Stand
        elif player_hand_totals == 20:
            return PlayerAction.Stand
    elif not table.current_player_betting_box().hand.is_soft():  # if player hand is hard
        if player_hand_totals <= 8:
            return PlayerAction.Hit
        elif player_hand_totals == 9:
            if dealer_hand_totals in [2, 7, 8, 9, 10, 11]:
                return PlayerAction.Hit
            elif table.current_player_betting_box().can_double_down():
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 10:
            if dealer_hand_totals <= 9 and table.current_player_betting_box().can_double_down():
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 11:
            if dealer_hand_totals <= 10 and table.current_player_betting_box().can_double_down():
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals == 12:
            if dealer_hand_totals not in [4, 5, 6]:
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
    else:  # if player hand is soft
        if player_hand_totals <= 14:
            if dealer_hand_totals <= 4 or dealer_hand_totals >= 7:
                return PlayerAction.Hit
            elif table.current_player_betting_box().can_double_down():
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals <= 16:
            if dealer_hand_totals < 4 or dealer_hand_totals >= 7 or not table.current_player_betting_box().can_double_down():
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals == 17:
            if dealer_hand_totals <= 2 or dealer_hand_totals >= 7 or not table.current_player_betting_box().can_double_down():
                return PlayerAction.Hit
            else:
                return PlayerAction.DoubleDown
        elif player_hand_totals == 18:
            if dealer_hand_totals <= 8 and (
                    dealer_hand_totals in [2, 7, 8] or not table.current_player_betting_box().can_double_down()):
                return PlayerAction.Stand
            elif dealer_hand_totals > 2 and dealer_hand_totals <= 6:
                return PlayerAction.DoubleDown
            else:
                return PlayerAction.Hit
        elif player_hand_totals >= 19:
            return PlayerAction.Stand


play_known_strategy = Strategy(known_strategy, 10, "Known Strategy", "blue")


def run_single_simulation(strategy) -> SimulationResult:
    dealer = Dealer(Hand([]), shoe(Deck.standard_deck(), 6).shuffle())
    table = Table([BettingBox(Hand([]), Player("Maddie"), strategy.bet)], dealer, 0)
    table = initial_draw(table)
    while table.play_in_progress():
        if table.current_player_betting_box().hand.is_blackjack():
            table = table.advance_player()
            continue

        if table.current_player_betting_box().hand.is_busted():
            table = table.advance_player()
            continue

        action = strategy.get_action(table)
        if action == PlayerAction.Hit:
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
            raise Exception(f"Unknown PlayerAction: {action}")

    table = dealer_moves(table)
    payout = table_payout(table)[Player("Maddie")]
    sim_result = SimulationResult(Counter([payout]))
    return sim_result


def run_simulation(strategy, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter())
    for i in range(num_runs):
        simulation_result += run_single_simulation(strategy)
    return simulation_result


def run_simulation_multi_round(strategy, num_rounds, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter())
    for i in progressbar(range(num_runs)):
        individual_performance = run_simulation(strategy, num_rounds)
        simulation_result += SimulationResult(Counter([individual_performance.total_winnings()]))
    return simulation_result


def print_simulation_result(simulation, strategy):
    print(strategy.name)
    print(simulation)
    # for k, v in simulation.result_counter.items():
    #     print(f"{k}, {v}")
    print(f"Sample Mean: {simulation.expected_winnings()}")
    print(f"Sample Variance: {simulation.sample_variance_winnings()}")
    print(f"Sample Standard Deviation: {simulation.sample_std_deviation()} ")
    print(f"95% Confidence Interval: {simulation.confidence_interval_winnings()}")
    print(f"% of Games Profitable (winnings >= 0): {simulation.percentage_games_profitable()}")
    print(f"Range of Winnings: {simulation.range()}")
    # print(f"Showing Histogram {simulation.create_hist()}")
    print("")


num_runs = 15_000
num_rounds = 100


def joint_histogram(strategies: [(Strategy, SimulationResult)], num_rounds=num_rounds, num_runs=num_runs):
    for strategy, simulation_result in strategies:
        simulation_result.create_hist(strategy.name, strategy.color)
    plt.legend()
    plt.title(f"Profit/Loss for {num_rounds} Rounds Simulated {num_runs} Times")


def individual_histogram(strategy, simulation_result, num_rounds=num_rounds, num_runs=num_runs):
    mean = simulation_result.expected_winnings()
    simulation_result.create_hist(strategy.name, strategy.color)
    plt.axvline(mean, linewidth=2, linestyle="--", color="black")
    plt.legend()
    plt.title(f"Profit/Loss for {num_rounds} Rounds Simulated {num_runs} Times")


def output_simulation_results(results: {Strategy: SimulationResult}):
    with open("results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Sample Mean",
                                               "Sample Variance",
                                               "Sample Standard Deviation",
                                               "95% Confidence Interval",
                                               "% of Games Profitable (winnings >=0)",
                                               "Range of Winnings"])
        writer.writeheader()
        for strategy, result in results.items():
            strategy: Strategy = strategy
            result: SimulationResult = result
            writer.writerow({"Name": strategy.name,
                             "Sample Mean": result.expected_winnings(),
                             "Sample Variance": result.sample_variance_winnings(),
                             "Sample Standard Deviation": result.sample_std_deviation(),
                             "95% Confidence Interval": result.confidence_interval_winnings(),
                             "% of Games Profitable (winnings >=0)": result.percentage_games_profitable(),
                             "Range of Winnings": result.range()})


joint_strategies = [play_known_strategy,
                    always_stand_strategy,
                    always_double_down]
individual_strategies = [choose_random_strategy,
                         hit_under_seventeen,
                         always_split_when_possible]

plt.figure(1)

all_strategies = [choose_random_strategy, always_stand_strategy, hit_under_seventeen, always_double_down,
                  always_split_when_possible, play_known_strategy]

simulation_results = {strategy: run_simulation_multi_round(strategy, num_rounds, num_runs) for strategy in
                      all_strategies}

output_simulation_results(simulation_results)

joint_histogram([(strategy, simulation_results[strategy]) for strategy in joint_strategies])

for i, strategy in enumerate(all_strategies):
    plt.figure(i + 2)
    individual_histogram(strategy, simulation_results[strategy])

plt.show()
