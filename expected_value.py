"""Estimate the expected value of a given strategy."""
from __future__ import annotations
from utils import get_cards_seen, DECK, readable_number
from action_strategies import BaseMover
from betting_strategies import BaseBetter
from typing import Iterable
import matplotlib.pyplot as plt
import random
import betting_strategies
import action_strategies
import argparse
import multiprocessing


class Hand:
    """Hold information about the hand of the player and the dealer."""

    def __init__(self, cards: Iterable[int]) -> None:
        """
        Save the initial cards.

        :param cards: The cards the hand started with.
        """
        self.cards = list(cards)

    def add_card(self, card: int) -> None:
        """
        Add a new card to the hand.

        :param card: The new card to add for the hand (an ace is symbolised as 11).
        """
        self.cards.append(card)

    def value_ace(self) -> tuple[int, int]:
        """
        Return the value of a hand and how many aces that count as 11 it has.

        :return: The hand's value and how many aces are counted as 11 (0 or 1).
        """
        value = sum(self.cards)
        aces = self.cards.count(11)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value, aces

    def aces(self) -> int:
        """
        Return the number of aces that count as 11.

        :return: The number of aces counted as 11.
        """
        return self.value_ace()[1]

    def value(self) -> int:
        """
        Return the value of a hand.

        :return: The hand's value.
        """
        return self.value_ace()[0]


def get_card_from_shoe(shoe: list[int]) -> int:
    """
    Get a card from the shoe. Always returns the last item from the shoe, so the shoe must be shuffled before.

    :param shoe: The shoe to get a card from.
    :return: The card we got from the shoe.
    """
    card = shoe.pop()
    return card


def get_mover_and_better(mover_name: str, better_name: str
                         ) -> tuple[action_strategies.BaseMover, betting_strategies.BaseBetter]:
    """
    Get the mover and the better from the arguments passed by the user.

    :param mover_name: The name of the mover to use. If it isn't one of the recognized names,
        then in checks if there is a class of that name.
    :param better_name: The name of the better to use. If it isn't one of the recognized names,
        then in checks if there is a class of that name.
    :return: The mover and the better to use, already set up.
    """
    mover_class: action_strategies.BaseMover
    better_class: betting_strategies.BaseBetter
    if mover_name == "card-count":
        mover_class = action_strategies.CardCountMover(
            {(-1000, -10): "data/6deck_s17_das_peek_tc_minus_10.csv",
             (-10, -9): "data/6deck_s17_das_peek_tc_minus_9.csv",
             (-9, -8): "data/6deck_s17_das_peek_tc_minus_8.csv",
             (-8, -7): "data/6deck_s17_das_peek_tc_minus_7.csv",
             (-7, -6): "data/6deck_s17_das_peek_tc_minus_6.csv",
             (-6, -5): "data/6deck_s17_das_peek_tc_minus_5.csv",
             (-5, -4): "data/6deck_s17_das_peek_tc_minus_4.csv",
             (-4, -3): "data/6deck_s17_das_peek_tc_minus_3.csv",
             (-3, -2): "data/6deck_s17_das_peek_tc_minus_2.csv",
             (-2, -1): "data/6deck_s17_das_peek_tc_minus_1.csv",
             (-1, 1): "data/6deck_s17_das_peek_tc_0.csv",
             (1, 2): "data/6deck_s17_das_peek_tc_plus_1.csv",
             (2, 3): "data/6deck_s17_das_peek_tc_plus_2.csv",
             (3, 4): "data/6deck_s17_das_peek_tc_plus_3.csv",
             (4, 5): "data/6deck_s17_das_peek_tc_plus_4.csv",
             (5, 6): "data/6deck_s17_das_peek_tc_plus_5.csv",
             (6, 7): "data/6deck_s17_das_peek_tc_plus_6.csv",
             (7, 8): "data/6deck_s17_das_peek_tc_plus_7.csv",
             (8, 9): "data/6deck_s17_das_peek_tc_plus_8.csv",
             (9, 10): "data/6deck_s17_das_peek_tc_plus_9.csv",
             (10, 1000): "data/6deck_s17_das_peek_tc_plus_10.csv"})
    elif mover_name == "basic-strategy":
        mover_class = action_strategies.BasicStrategyMover("data/6deck_s17_das_peek_basic_strategy.csv")
    elif mover_name == "perfect":
        mover_class = action_strategies.PerfectMover()
    elif mover_name == "simple":
        mover_class = action_strategies.SimpleMover()
    else:  # Run a user-defined class.
        mover_class = getattr(action_strategies, mover_name)()
    if better_name == "card-count":
        better_class = betting_strategies.CardCountBetter()
    elif better_name == "simple":
        better_class = betting_strategies.SimpleBetter()
    else:  # Run a user-defined class.
        better_class = getattr(betting_strategies, better_name)()
    return mover_class, better_class


def play_dealer(dealer_cards: Iterable[int], shoe: list[int], dealer_stands_soft_17: bool) -> int:
    """
    Play the dealers hand to get its final value.

    :param dealer_cards: The cards the dealer already has.
    :param shoe: The shoe.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :return: The final value of the dealer's hand. If the dealer busted, the value is 0.
    """
    dealer = Hand(dealer_cards)
    while dealer.value() < 17 or not dealer_stands_soft_17 and dealer.value() == 17 and 11 in dealer_cards:
        dealer.add_card(get_card_from_shoe(shoe))
    dealer_value = dealer.value()
    return dealer_value if dealer_value <= 21 else 0


def simulate_hand(action_class: action_strategies.BaseMover, betting_class: betting_strategies.BaseBetter,
                  cards: list[int], dealer_up_card: int,
                  dealer_down_card: int, shoe: list[int], initial_hand: bool,
                  splits_remaining: int, deck_number: int, dealer_peeks_for_blackjack: bool = True, das: bool = True,
                  dealer_stands_soft_17: bool = True, surrender_allowed: bool = True) -> tuple[float, int]:
    """
    Play one hand.

    :param action_class: The class that chooses the action.
    :param betting_class: The class that chooses the bet.
    :param cards: The cards in our hand.
    :param dealer_up_card: The dealer's up card.
    :param dealer_down_card: The dealer's down card.
    :param shoe: The shoe.
    :param initial_hand: Whether this is our initial hand and haven't gotten any other card.
    :param splits_remaining: How many more splits we can do.
    :param deck_number: The number of decks in the initial shoe.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :param surrender_allowed: Whether the game rules allow surrendering.
    :return: The profit/loss from the hand, and how many times we split.
    """
    can_split = (splits_remaining > 0 and len(cards) == 2 and cards[0] == cards[1]
                 and (not cards[0] == 11 or splits_remaining == 3))
    can_double = len(cards) == 2 and (das or splits_remaining == 3)
    can_surrender_now = initial_hand and surrender_allowed
    can_insure = initial_hand and dealer_up_card == 11
    bet = 1
    insurance_profit = 0.
    dealer_has_blackjack = dealer_up_card + dealer_down_card == 21
    player_has_blackjack = initial_hand and cards[0] + cards[1] == 21
    player_loses_all_bets = dealer_has_blackjack and not dealer_peeks_for_blackjack and not player_has_blackjack
    cards_seen = get_cards_seen(deck_number, shoe)
    cards_seen.remove(dealer_down_card)
    if initial_hand:
        bet = betting_class.get_bet(cards_seen, deck_number)
    hand = Hand(cards)
    initial_hand_value, initial_hand_has_ace = hand.value_ace()
    action, insure = action_class.get_move(initial_hand_value, bool(initial_hand_has_ace), dealer_up_card, can_double,
                                           can_split, can_surrender_now, can_insure, cards, cards_seen, deck_number,
                                           dealer_peeks_for_blackjack, das, dealer_stands_soft_17)

    if insure and can_insure:
        insurance_profit = 1 if dealer_down_card == 10 else -.5

    if initial_hand:
        if dealer_peeks_for_blackjack:
            if dealer_has_blackjack and player_has_blackjack:  # Push
                return (0 + insurance_profit) * bet, 0
            elif dealer_has_blackjack:  # Dealer blackjack
                return (-1 + insurance_profit) * bet, 0
            elif player_has_blackjack:  # Player blackjack
                return (1 * 3 / 2 + insurance_profit) * bet, 0
        else:
            if player_has_blackjack and dealer_has_blackjack:
                return (0 + insurance_profit) * bet, 0
            elif player_has_blackjack:
                return (1 * 3 / 2 + insurance_profit) * bet, 0

    if action == "u" and can_surrender_now:
        return (-.5 + insurance_profit) * bet, 0

    elif action == "s":
        dealer_value = play_dealer((dealer_up_card, dealer_down_card), shoe, dealer_stands_soft_17)
        if player_loses_all_bets:
            return (-1 + insurance_profit) * bet, 0
        if initial_hand_value > dealer_value:
            return (1 + insurance_profit) * bet, 0
        elif initial_hand_value < dealer_value:
            return (-1 + insurance_profit) * bet, 0
        return (0 + insurance_profit) * bet, 0

    elif action == "d" and can_double:
        card = get_card_from_shoe(shoe)
        hand.add_card(card)
        if player_loses_all_bets:
            return (-2 + insurance_profit) * bet, 0
        if hand.value() > 21:
            return (-2 + insurance_profit) * bet, 0
        dealer_value = play_dealer((dealer_up_card, dealer_down_card), shoe, dealer_stands_soft_17)
        if hand.value() > dealer_value:
            return (+2 + insurance_profit) * bet, 0
        elif hand.value() < dealer_value:
            return (-2 + insurance_profit) * bet, 0
        return (0 + insurance_profit) * bet, 0

    elif action == "h":
        card = get_card_from_shoe(shoe)
        hand.add_card(card)
        if player_loses_all_bets:
            return (-1 + insurance_profit) * bet, 0
        if hand.value() > 21:
            return (-1 + insurance_profit) * bet, 0
        return (simulate_hand(action_class, betting_class, hand.cards, dealer_up_card, dealer_down_card, shoe,
                              False, splits_remaining, deck_number
                              )[0] + insurance_profit) * bet, 0

    elif action == "p" and can_split:
        hand1 = Hand([hand.cards[0]])
        hand2 = Hand([hand.cards[1]])
        card1 = get_card_from_shoe(shoe)
        hand1.add_card(card1)
        profit1, splits_used1 = simulate_hand(action_class, betting_class, hand1.cards, dealer_up_card,
                                              dealer_down_card, shoe, False,
                                              splits_remaining - 1, deck_number)
        card2 = get_card_from_shoe(shoe)
        hand2.add_card(card2)
        profit2, splits_used2 = simulate_hand(action_class, betting_class, hand2.cards, dealer_up_card,
                                              dealer_down_card, shoe, False,
                                              splits_remaining - 1 - splits_used1, deck_number)
        split_profit = profit1 + profit2
        if player_loses_all_bets:
            split_profit = -(2 + splits_used1 + splits_used2)
        return (split_profit + insurance_profit) * bet, 1 + splits_used1 + splits_used2

    raise ValueError(f"invalid action: {action}.")


def expected_value(action_class: action_strategies.BaseMover, betting_class: betting_strategies.BaseBetter,
                   simulations: int, deck_number: int = 6, shoe_penetration: float = .25,
                   dealer_peeks_for_blackjack: bool = True, das: bool = True,
                   dealer_stands_soft_17: bool = True, surrender_allowed: bool = True,
                   plot_profits: bool = True, print_info: bool = True) -> float:
    """
    Estimate the expected value of a strategy.

    :param action_class: The class that chooses the action.
    :param betting_class: The class that chooses the bet.
    :param simulations: How many hands to play.
    :param deck_number: The number of decks in the initial shoe.
    :param shoe_penetration: When to reshuffle the shoe. Reshuffles when cards remaining < starting cards * deck penetration.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :param surrender_allowed: Whether the game rules allow surrendering.
    :param plot_profits: Whether a plot showing how the profit changed over time should be made at the end.
    :param print_info: Whether to print information about the progress of the simulation. Disabled for multithreading.
    :return: The average return of a hand.
    """
    starting_shoe = DECK * deck_number
    starting_number = len(starting_shoe)
    reshuffle_at = starting_number * shoe_penetration
    shoe = starting_shoe.copy()
    random.shuffle(shoe)
    profit = 0.
    profits_over_time = [profit]
    for i in range(simulations):
        if print_info and i % 100_000 == 0:
            print(f"Games played: {readable_number(i)}/{readable_number(simulations)}")
        if len(shoe) < reshuffle_at:
            shoe = starting_shoe.copy()
            random.shuffle(shoe)

        dealer_up_card = get_card_from_shoe(shoe)
        dealer_down_card = get_card_from_shoe(shoe)
        player_cards = [get_card_from_shoe(shoe), get_card_from_shoe(shoe)]

        reward, _ = simulate_hand(action_class, betting_class, player_cards, dealer_up_card, dealer_down_card, shoe,
                                  True, 3, deck_number,
                                  dealer_peeks_for_blackjack, das, dealer_stands_soft_17, surrender_allowed)
        profit += reward
        profits_over_time.append(profit)

    avg_profit = profit / simulations
    if print_info:
        print(f"Total profit: {profit}, Average profit: {avg_profit}")
    if plot_profits:
        plt.plot(profits_over_time, label="Total profit")
        plt.xlabel("Games played")
        plt.ylabel("Total profit")
        plt.title("Profits over time")
        plt.legend()
        plt.show()

    return avg_profit


def _expected_value_multithreading_wrapper(results: multiprocessing.Queue[float], action_class: action_strategies.BaseMover,
                                           betting_class: betting_strategies.BaseBetter,
                                           simulations: int, deck_number: int = 6, shoe_penetration: float = .25,
                                           dealer_peeks_for_blackjack: bool = True, das: bool = True,
                                           dealer_stands_soft_17: bool = True, surrender_allowed: bool = True) -> None:
    """
    Estimate the expected value of a strategy. Used inside multithreading. Don't use this function directly.

    :param action_class: The class that chooses the action.
    :param betting_class: The class that chooses the bet.
    :param simulations: How many hands to play.
    :param deck_number: The number of decks in the initial shoe.
    :param shoe_penetration: When to reshuffle the shoe. Reshuffles when cards remaining < starting cards * deck penetration.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :param surrender_allowed: Whether the game rules allow surrendering.
    """
    results.put(expected_value(action_class, betting_class, simulations, deck_number, shoe_penetration,
                               dealer_peeks_for_blackjack, das, dealer_stands_soft_17, surrender_allowed, False, False))


def expected_value_multithreading(action_class: action_strategies.BaseMover, betting_class: betting_strategies.BaseBetter,
                                  total_simulations: int, cores: int = 2, deck_number: int = 6, shoe_penetration: float = .25,
                                  dealer_peeks_for_blackjack: bool = True, das: bool = True,
                                  dealer_stands_soft_17: bool = True, surrender_allowed: bool = True) -> float:
    """
    Estimate the expected value of a strategy, using multithreading to speed up the process. Can't plot the results.

    :param action_class: The class that chooses the action.
    :param betting_class: The class that chooses the bet.
    :param total_simulations: How many hands to play in total.
    :param cores: How many cores to use for the simulation.
    :param deck_number: The number of decks in the initial shoe.
    :param shoe_penetration: When to reshuffle the shoe. Reshuffles when cards remaining < starting cards * deck penetration.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :param surrender_allowed: Whether the game rules allow surrendering.
    :return: The average return of a hand.
    """
    core_results: multiprocessing.Queue[float] = multiprocessing.Queue()
    worker_pool = []
    for _ in range(cores):
        p = multiprocessing.Process(target=_expected_value_multithreading_wrapper,
                                    args=(core_results, action_class, betting_class, total_simulations // cores,
                                          deck_number, shoe_penetration, dealer_peeks_for_blackjack, das,
                                          dealer_stands_soft_17, surrender_allowed))
        p.start()
        worker_pool.append(p)
    for p in worker_pool:
        p.join()  # Wait for all the workers to finish.
    total_profit = 0.
    for _ in range(cores):
        total_profit += core_results.get()
    avg_profit = total_profit / cores
    print(f"Total profit: {total_profit * (total_simulations // cores)}, Average profit: {avg_profit}")
    return avg_profit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Expected Value (EV) Calculation',
                                     description='Evaluate the profitability of different blackjack strategies by calculating'
                                                 ' their expected value (EV).')
    parser.add_argument("-c", "--custom", action='store_true',
                        help='Run custom user-defined movers and betters that require special initialization.')
    parser.add_argument("--cores", default=1, type=int,
                        help='How many cores to use in the calculation. (default: 1, use -1 for all cores)')
    parser.add_argument("-m", "--mover", default="card-count",
                        help='Use a predefined mover. Can also be the name of the class of a user-defined mover. '
                             '(possible values: card-count, basic-strategy, perfect, simple; default: card-count)')
    parser.add_argument("-b", "--better", default="card-count",
                        help='Use a predefined better. Can also be the name of the class of a user-defined better. '
                             '(possible values: card-count, simple; default: card-count)')
    parser.add_argument("-s", "--simulations", default=500_000, type=int,
                        help='How many simulations to run. Running more simulations gives more accurate '
                             'results but they are slower to calculate. (default: 500,000)')
    parser.add_argument("--decks", default=6, type=int, help='How many decks the shoe starts with. (default: 6)')
    parser.add_argument("--deck-penetration", default=.25, type=float,
                        help='When to reshuffle the shoe. Reshuffles when cards remaining < starting cards'
                             ' * deck penetration. (default: 0.25)')
    parser.add_argument("--stand17", action='store_true', help='Dealer should stand on soft 17. (default: true)')
    parser.add_argument("--hit17", action='store_true', help='Dealer should hit on soft 17. (default: false)')
    parser.add_argument("--das", action='store_true', help='Allow double after split. (default: true)')
    parser.add_argument("--no-das", action='store_true', help='Don\'t allow double after split. (default: false)')
    parser.add_argument("--peek", action='store_true', help='Dealer peeks for blackjack. (default: true)')
    parser.add_argument("--no-peek", action='store_true', help="Dealer doesn't peek for blackjack. (default: false)")
    parser.add_argument("--surrender", action='store_true', help='Allow surrendering. (default: true)')
    parser.add_argument("--no-surrender", action='store_true', help='Don\'t allow surrendering. (default: false)')
    args = parser.parse_args()

    decks_number = args.decks
    stand_soft_17 = args.stand17 or (not args.hit17)
    das_allowed = args.das or (not args.no_das)
    peek_for_bj = args.peek or (not args.no_peek)
    can_surrender = args.surrender or (not args.no_surrender)

    cores = args.cores if args.cores != -1 else multiprocessing.cpu_count()

    if args.custom:
        # ADD CUSTOM CODE HERE IF YOU HAVE BUILT YOUR OWN MOVER OR BETTER.
        mover = BaseMover()  # Replace BaseMover with your own class.
        better = BaseBetter()  # Replace BaseBetter with your own class.
    else:
        mover, better = get_mover_and_better(args.mover, args.better)

    if cores > 1:
        expected_value_multithreading(mover, better, args.simulations, cores, args.decks, args.deck_penetration,
                                      peek_for_bj, das_allowed, stand_soft_17, can_surrender)
    else:
        expected_value(mover, better, args.simulations, args.decks, args.deck_penetration, peek_for_bj, das_allowed,
                       stand_soft_17, can_surrender)
