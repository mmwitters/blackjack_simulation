import typing
from abc import ABC, abstractmethod
from random import choice
from typing import NamedTuple, Tuple, overload, Any
from collections import Counter

from blackjack import HandResult, Table, PlayerAction


class SimulationResult(NamedTuple):
    result_counter: typing.Counter[HandResult]
    total_winnings: int

    def __add__(self, x):
        return SimulationResult(self.result_counter + x.result_counter, self.total_winnings + x.total_winnings)

class Strategy(NamedTuple):
    get_action: typing.Callable[[Table], PlayerAction]
    # actions chosen randomly
    # always staying
    # use "optimal" blackjack rules
    # card counting (?)


always_stay_strategy = Strategy(lambda table: PlayerAction.Stand)
choose_random_strategy = Strategy(lambda table: choice(list(PlayerAction)))


# INDEPENDENT GAMES
def run_single_simulation(strategy) -> SimulationResult:
    return SimulationResult(Counter([HandResult.Win]), 5)


def run_simulation(strategy, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter(), 0)
    for i in range(num_runs):
        simulation_result += run_single_simulation(strategy)
    return simulation_result

def foo(x: int, y: float) -> str:
    return str(x + y)
