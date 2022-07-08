import typing
from abc import ABC, abstractmethod
from random import choice
from typing import NamedTuple, Tuple, overload, Any
from collections import Counter

from blackjack import HandResult, Table, PlayerAction, BettingBox, Player, Hand, Dealer, shoe, initial_draw, \
    table_payout, hit, stand, dealer_moves
from cards import Deck


class SimulationResult(NamedTuple):
    result_counter: typing.Counter[HandResult]
    total_winnings: int

    def __add__(self, x):
        return SimulationResult(self.result_counter + x.result_counter, self.total_winnings + x.total_winnings)


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
hit_below_16 = Strategy(lambda table: PlayerAction.Stand if min(
    table.current_player_betting_box().hand.card_totals()) >= 16 else PlayerAction.Hit, 10)


# INDEPENDENT GAMES
def run_single_simulation(strategy) -> SimulationResult:
    dealer = Dealer(Hand([]), shoe(Deck.standard_deck(), 6).shuffle())
    table = Table([BettingBox(Hand([]), Player("Maddie"), strategy.bet)], dealer, 0)
    table = initial_draw(table)
    for _ in table.betting_boxes:
        # TODO Automatically win if you have blackjack. Check if you can hit on 21.
        while not table.current_player_betting_box().hand.is_busted() and (action:=strategy.get_action(table)) != PlayerAction.Stand:
            if action == PlayerAction.Hit:
                table = hit(table)
            elif action == PlayerAction.Stand:
                table = stand(action)
            else:
                raise f"Unknown PlayerAction: {action}"
        table = table.advance_player()
    table = dealer_moves(table)
    result, payout = table_payout(table)[Player("Maddie")]  # We only care about Maddie for now
    sim_result = SimulationResult(Counter([result]), payout)
    return sim_result


def run_simulation(strategy, num_runs) -> SimulationResult:
    simulation_result = SimulationResult(Counter(), 0)
    for i in range(num_runs):
        simulation_result += run_single_simulation(strategy)
    return simulation_result


print(run_simulation(hit_below_16, 10_000))
print(run_simulation(always_stay_strategy, 10_000))
