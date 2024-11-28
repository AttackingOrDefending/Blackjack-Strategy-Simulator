"""Calculate the best move to play by taking into account all available information."""
from functools import lru_cache
from utils import DECK
from typing import Iterable
import matplotlib.pyplot as plt
import argparse


class HandPlayer:
    """Hold information about the player's hand."""

    def __init__(self, cards: tuple[int, ...]) -> None:
        """
        Calculate the value of the hand the number of aces it has.

        :param cards: The cards the hand has at the moment.
        """
        self.cards = cards
        value = sum(cards)
        aces = cards.count(11)
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        self.value = value
        self.aces = aces


class HandDealer:
    """Hold information about the dealer's hand."""

    def __init__(self, value: int, aces: int) -> None:
        """
        Calculate the value of the hand the number of aces it has.

        :param value: The hand's value (can be over 21).
        :param aces: How many aces that are counted as 11 the hand has.
        """
        if value > 21 and aces:
            value -= 10
            aces -= 1
        self.value = value
        self.aces = aces


def tuple_sort(cards: Iterable[int]) -> tuple[int, ...]:
    """
    Sort a tuple. Used to increase cache hits.

    :param cards: The cards in the shoe.
    :return: The shoe with its cards sorted.
    """
    return tuple(sorted(cards))


def probabilities_if_dealer_peeks_for_blackjack(counts: dict[int, int], dealer_up_card: int) -> dict[int, float]:
    """
    Account for the fact that if the dealer has an ace and doesn't have blackjack, then we know they don't have a 10.

    As such, our chances of getting a 10 are slightly higher and out chances of getting any other card are slightly lower.
    Similarly, if the dealer has a 10 and doesn't have blackjack, then we know they don't have an ace.

    :param counts: How many times each card is in the deck. (e.g. {2: 12, 3: 11, 4: 15, ...})
    :param dealer_up_card: The dealer's up card.
    :return: The probabilities of getting each card if the dealer peeks for blackjack.
    """
    amount_of_cards_not_seen = sum(counts.values())
    counts_no_blackjacks = {k: counts[k] for k in range(2, 12) if k + dealer_up_card != 21}
    amount_of_cards_not_seen_no_blackjack = sum(counts_no_blackjacks.values())
    probabilities_no_blackjack = {k: counts_no_blackjacks[k] / amount_of_cards_not_seen_no_blackjack for k in
                                  range(2, 12) if k + dealer_up_card != 21}
    new_probabilities = {k: 0. for k in range(2, 12)}
    for possible_dealer_down_card in range(2, 12):
        if possible_dealer_down_card + dealer_up_card == 21:
            continue
        counts_after_down_card = counts.copy()
        counts_after_down_card[possible_dealer_down_card] -= 1
        amount_of_cards_not_seen_after_down_card = amount_of_cards_not_seen - 1
        probabilities_after_down_card = {k: counts_after_down_card[k] / amount_of_cards_not_seen_after_down_card for k
                                         in range(2, 12)}
        for k in range(2, 12):
            new_probabilities[k] += probabilities_after_down_card.get(k, 0) * probabilities_no_blackjack[
                possible_dealer_down_card]
    return new_probabilities


@lru_cache(maxsize=100_000)
def can_never_split(cards: tuple[int, ...]) -> bool:
    """
    Get if the player can't split.

    :param cards: The player's hand.
    :return: Whether the player will not be able to split their hand now and in the future.
    """
    return not (len(cards) == 1 or len(cards) == 2 and cards[0] == cards[1])


def argmax(*profits: float) -> tuple[float, str]:
    """
    Return the maximum profit and the action that gets you that profit.

    :param profits: The profits generated by each action.
    :return: The best profit, and the best action.
    """
    max_profit = max(profits)
    index_to_action = {0: "stand", 1: "hit", 2: "double", 3: "split", 4: "surrender", 5: "insurance"}
    for index, profit in enumerate(profits):
        if profit == max_profit:
            return max_profit, index_to_action[index]
    return 0., ""


def dict_to_tuple(counts: dict[int, int]) -> tuple[int, ...]:
    """
    Convert the dict of the counts of every card to a tuple, so it can be used with @cache.

    :param counts: How many times each card is in the deck. (e.g. {2: 12, 3: 11, 4: 15, ...})
    :return: A tuple containing the number of times each card is in the shoe, but the keys are now the indices.
        (e.g. {2: 12, 3: 11, 4: 15, ...} becomes (0, 0, 12, 11, 15, ...))
    """
    return (0, 0) + tuple([counts[k] for k in range(2, 12)])


@lru_cache(maxsize=100_000)
def create_deck_from_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    """
    Create a deck from the counts of every card.

    :param counts: How many times each card is in the deck. (e.g. (0, 0, 12, 11, 15, ...))
    :return: A shoe with these cards.
    """
    # Use with `dict_to_tuple` to use `@cache`.
    deck = []
    for card in range(2, 12):
        deck += [card] * counts[card]
    return tuple(deck)


def create_deck_from_counts_cache(counts: dict[int, int]) -> tuple[int, ...]:
    """
    Create a deck from the counts of every card.

    :param counts: How many times each card is in the deck. (e.g. {2: 12, 3: 11, 4: 15, ...})
    :return: A shoe with these cards.
    """
    return create_deck_from_counts(dict_to_tuple(counts))


@lru_cache(maxsize=1_000_000)
def chances_of_beating_dealer(hand_value: int, dealer_value: int, dealer_has_ace: bool, counts: tuple[int, ...],
                              dealer_more_than_1_card: bool, dealer_peeks_for_blackjack: bool,
                              dealer_stands_soft_17: bool) -> float:
    """
    Assumes that if the player got 21, it wasn't a blackjack. If it was a blackjack, then we don't call this function.

    If dealer_peeks_for_blackjack is true, then the dealer can't have blackjack.

    :param hand_value: The player's final hand value.
    :param dealer_value: The dealer's hand value at the moment.
    :param dealer_has_ace: Whether the dealer has an ace that is counted as 11.
    :param counts: How many times each card is in the deck. (e.g. (0, 0, 12, 11, 15, ...))
    :param dealer_more_than_1_card: Whether the dealer has more than 1 card (not including the down card).
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :return: The chances of beating the dealer.
    """
    if hand_value > 21:
        return 0
    ignore_blackjacks = not dealer_more_than_1_card and dealer_peeks_for_blackjack
    if ignore_blackjacks:
        counts_no_blackjacks = {k: counts[k] for k in range(2, 12) if k + dealer_value != 21}
        amount_of_cards_not_seen_no_blackjack = sum(counts_no_blackjacks.values())
        probabilities = {k: (counts_no_blackjacks[k] / amount_of_cards_not_seen_no_blackjack if k + dealer_value != 21 else 0)
                         for k in range(2, 12)}
    else:
        amount_of_cards_not_seen = sum(counts)
        probabilities = {k: counts[k] / amount_of_cards_not_seen for k in range(2, 12)}

    beat_probability = 0.
    for card in range(2, 12):
        # In this loop, you probably need to use dealer.property instead of dealer_property.
        # e.g. dealer.value instead of dealer_value.
        if probabilities[card] == 0:
            continue
        dealer = HandDealer(dealer_value + card, dealer_has_ace + (card == 11))
        # If dealer_peeks_for_blackjack is true, then we use the probabilities of the card occurring without the one
        # that would have caused the blackjack.
        if dealer.value < 17 or dealer.value == 17 and dealer.aces > 0 and not dealer_stands_soft_17:
            counts_copy = list(counts)
            counts_copy[card] -= 1
            beat_probability += (chances_of_beating_dealer(hand_value, dealer.value, dealer.aces > 0,
                                                           tuple(counts_copy),
                                                           True, dealer_peeks_for_blackjack,
                                                           dealer_stands_soft_17) * probabilities[card])
        else:
            if hand_value > dealer.value or dealer.value > 21:
                beat_probability += probabilities[card]
            elif hand_value == dealer.value and (dealer_more_than_1_card or dealer.value != 21):
                beat_probability += probabilities[card] * .5
    return beat_probability


@lru_cache(maxsize=100_000)
def perfect_mover(cards: tuple[int, ...], dealer_up_card: int, cards_not_seen: tuple[int, ...],
                  can_double: bool = True, can_insure: bool = True, can_surrender: bool = True, max_splits: int = 3,
                  dealer_peeks_for_blackjack: bool = True, das: bool = True, dealer_stands_soft_17: bool = True
                  ) -> tuple[float, ...]:
    """
    Get the best move to play by taking into account even the cards that we have already seen.

    :param cards: The cards in the player's hand.
    :param dealer_up_card: The dealer's up card.
    :param cards_not_seen: The cards the player hasn't already seen.
    :param can_double: Whether the player can double.
    :param can_insure: Whether the player can take insurance.
    :param can_surrender: Whether the player can surrender.
    :param max_splits: How many times the player can split their hand.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :return: The expected returns of all 6 possible actions
        (`stand`, `hit`, `double`, `split`, `surrender`, and `insurance`, in that order).
    """
    double_profit = -1000.
    split_profit = -1000.
    surrender_profit = -1000.
    insurance_profit = -1000.

    # Stand
    hand = HandPlayer(cards)
    if hand.value > 21:
        return -1., -1000., -1000., -1000., -1000., -1000.

    amount_of_cards_not_seen = len(cards_not_seen)
    counts = {k: cards_not_seen.count(k) for k in range(2, 12)}
    probabilities = {k: counts[k] / amount_of_cards_not_seen for k in range(2, 12)}
    if dealer_up_card in (10, 11) and dealer_peeks_for_blackjack:
        probabilities = probabilities_if_dealer_peeks_for_blackjack(counts, dealer_up_card)

    stand_profit = chances_of_beating_dealer(hand.value, dealer_up_card, dealer_up_card == 11, dict_to_tuple(counts),
                                             False, dealer_peeks_for_blackjack,
                                             dealer_stands_soft_17) * 2 - 1

    # Double
    if can_double and len(cards) == 2:
        profit = 0.
        for card in range(2, 12):
            if counts[card] == 0:
                continue
            hand = HandPlayer(cards + (card,))
            counts_copy = counts.copy()
            counts_copy[card] -= 1
            profit += (chances_of_beating_dealer(hand.value, dealer_up_card, dealer_up_card == 11,
                                                 dict_to_tuple(counts_copy),
                                                 False, dealer_peeks_for_blackjack,
                                                 dealer_stands_soft_17) * 2 - 1
                       ) * (probabilities[card])
        double_profit = profit * 2

    # Surrender
    if len(cards) == 2 and can_surrender:
        surrender_profit = -.5

    # Insurance
    if dealer_up_card == 11 and len(cards) == 2 and can_insure:
        # We use counts[10] / amount_of_cards_not_seen and not probabilities[10] as we choose whether we want insurance
        # before the dealer checks for blackjack.
        insurance_profit = (1 * counts[10] / amount_of_cards_not_seen - .5 * (1 - counts[10] / amount_of_cards_not_seen))

    # Hit
    profit = 0
    for card in range(2, 12):
        if counts[card] == 0:
            continue
        hand = HandPlayer(cards + (card,))
        if hand.value <= 21:
            counts_copy = counts.copy()
            counts_copy[card] -= 1
            profit += (perfect_mover_cache(hand.cards, dealer_up_card, create_deck_from_counts_cache(counts_copy),
                                           can_double, False, False, max_splits, dealer_peeks_for_blackjack,
                                           das, dealer_stands_soft_17)[0]
                       * (probabilities[card]))
        else:
            profit -= 1 * probabilities[card]
    hit_profit = profit

    # Split
    if len(cards) == 2 and cards[0] == cards[1] and max_splits >= 1:
        max_splits -= 1

        if cards[0] == 11:
            profit = 0
            for card in range(2, 12):
                if counts[card] == 0:
                    continue
                counts_copy = counts.copy()
                counts_copy[card] -= 1
                probabilities_copy = {k: counts_copy[k] / (amount_of_cards_not_seen - 1) for k in range(2, 12)}
                if dealer_up_card in (10, 11) and dealer_peeks_for_blackjack:
                    probabilities_copy = probabilities_if_dealer_peeks_for_blackjack(counts_copy, dealer_up_card)

                for card2 in range(2, 12):
                    if counts_copy[card] == 0:
                        continue
                    counts_copy2 = counts_copy.copy()
                    counts_copy2[card2] -= 1
                    profit += ((chances_of_beating_dealer(HandPlayer((card, 11)).value, dealer_up_card, dealer_up_card == 11,
                                                          dict_to_tuple(counts_copy2),
                                                          False, dealer_peeks_for_blackjack,
                                                          dealer_stands_soft_17) * 2 - 1)
                               + (chances_of_beating_dealer(HandPlayer((card2, 11)).value, dealer_up_card,
                                                            dealer_up_card == 11,
                                                            dict_to_tuple(counts_copy2),
                                                            False, dealer_peeks_for_blackjack,
                                                            dealer_stands_soft_17) * 2 - 1)
                               ) * (probabilities[card] * probabilities_copy[card2])
            split_profit = profit

        else:
            profit = 0
            for card in range(2, 12):
                if counts[card] == 0:
                    continue
                counts_copy = counts.copy()
                counts_copy[card] -= 1
                probabilities_copy = {k: counts_copy[k] / (amount_of_cards_not_seen - 1) for k in range(2, 12)}
                if dealer_up_card in (10, 11) and dealer_peeks_for_blackjack:
                    probabilities_copy = probabilities_if_dealer_peeks_for_blackjack(counts_copy, dealer_up_card)

                for card2 in range(2, 12):
                    if counts_copy[card] == 0:
                        continue
                    counts_copy2 = counts_copy.copy()
                    counts_copy2[card2] -= 1
                    if cards[0] == card:
                        profit += (perfect_mover_cache((cards[0], card), dealer_up_card,
                                                       create_deck_from_counts_cache(counts_copy2), can_double and das,
                                                       False, False,
                                                       max_splits, dealer_peeks_for_blackjack, das,
                                                       dealer_stands_soft_17)[0]
                                   + perfect_mover_cache((cards[0], card2), dealer_up_card,
                                                         create_deck_from_counts_cache(counts_copy2), can_double and das,
                                                         False, False,
                                                         0, dealer_peeks_for_blackjack, das,
                                                         dealer_stands_soft_17)[0]
                                   ) * (probabilities[card] * probabilities_copy[card2])
                    else:
                        profit += (perfect_mover_cache((cards[0], card), dealer_up_card,
                                                       create_deck_from_counts_cache(counts_copy2), can_double and das,
                                                       False, False, 0,
                                                       dealer_peeks_for_blackjack, das, dealer_stands_soft_17)[0]
                                   + perfect_mover_cache((cards[0], card2), dealer_up_card,
                                                         create_deck_from_counts_cache(counts_copy2), can_double and das,
                                                         False, False,
                                                         max_splits, dealer_peeks_for_blackjack, das,
                                                         dealer_stands_soft_17)[0]
                                   ) * (probabilities[card] * probabilities_copy[card2])
            split_profit = profit

    return stand_profit, hit_profit, double_profit, split_profit, surrender_profit, insurance_profit


def perfect_mover_cache(cards: Iterable[int], dealer_up_card: int, cards_not_seen: Iterable[int],
                        can_double: bool = True, can_insure: bool = True, can_surrender: bool = True,
                        max_splits: int = 3, dealer_peeks_for_blackjack: bool = True,
                        das: bool = True, dealer_stands_soft_17: bool = True, return_all_profits: bool = False,
                        print_profits: bool = False, plot_profits: bool = False
                        ) -> tuple[float, ...] | tuple[float, str, float]:
    """
    Increase cache hits in `perfect_mover`. Use this instead of `perfect_mover` for faster results.

    :param cards: The cards in the player's hand.
    :param dealer_up_card: The dealer's up card.
    :param cards_not_seen: The cards the player hasn't already seen.
    :param can_double: Whether the player can double.
    :param can_insure: Whether the player can take insurance.
    :param can_surrender: Whether the player can surrender.
    :param max_splits: How many times the player can split their hand.
    :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
    :param das: Whether we can double after splitting.
    :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
    :param return_all_profits: Whether we should return the expected returns of all 6 possible actions, or only the
        best expected return, the action that gets this return, and the expected profit of taking insurance.
    :param print_profits: Whether we should print the expected returns of all the actions.
    :param plot_profits: Whether we should create a table showing the expected returns of all possible actions,
        with the best move highlighted.
    :return: The expected returns of all 6 possible actions, or only the best expected return,
        the action that gets this return, and the expected profit of taking insurance.
    """
    cards = tuple(cards)
    if can_never_split(cards):
        max_splits = 0
    if len(cards) > 2:
        can_double = False
        can_insure = False
        can_surrender = False
    cards = tuple_sort(cards)
    cards_not_seen = tuple_sort(cards_not_seen)

    stand_profit, hit_profit, double_profit, split_profit, surrender_profit, insurance_profit = (
        perfect_mover(cards=cards, dealer_up_card=dealer_up_card, cards_not_seen=cards_not_seen,
                      can_double=can_double, can_insure=can_insure, can_surrender=can_surrender,
                      max_splits=max_splits, dealer_peeks_for_blackjack=dealer_peeks_for_blackjack,
                      das=das, dealer_stands_soft_17=dealer_stands_soft_17))

    if print_profits:
        print(f"Profits: Stand: {stand_profit}, Hit: {hit_profit}, Double: {double_profit}, Split: {split_profit}, "
              f"Surrender: {surrender_profit}, Insurance: {insurance_profit}")

    if plot_profits:
        profit_dict = {"stand": stand_profit, "hit": hit_profit}
        if double_profit > -10:
            profit_dict["double"] = double_profit
        if split_profit > -10:
            profit_dict["split"] = split_profit
        if surrender_profit > -10:
            profit_dict["surrender"] = surrender_profit
        if insurance_profit > -10:
            profit_dict["insurance"] = insurance_profit
        get_insurance = insurance_profit > 0
        best_action = argmax(stand_profit, hit_profit, double_profit, split_profit, surrender_profit)[1]
        result_table = [[action.title(), str(round(profit_dict[action], 10))] for action in profit_dict]
        result_table_colors = [(["y", "y"] if action == best_action or action == "insurance" and get_insurance else ["w", "w"]
                                ) for action in profit_dict]
        fig, ax = plt.subplots(dpi=200)
        fig.patch.set_visible(False)
        fig.set_size_inches(4, 2)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        table = ax.table(result_table, result_table_colors, loc='center', cellLoc='center')
        table.scale(1, 1.5)
        ax.set_title("Actions and their expected returns")
        ax.set_ylabel("Actions")
        ax.set_xlabel("Expected Returns")
        plt.tight_layout()
        plt.show()

    if return_all_profits:
        return stand_profit, hit_profit, double_profit, split_profit, surrender_profit, insurance_profit

    return argmax(stand_profit, hit_profit, double_profit, split_profit, surrender_profit) + (insurance_profit,)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Best Move Analysis',
                                     description='Accurately calculate the best possible action for any blackjack hand.')
    parser.add_argument("-c", "--cards", required=True, help='The cards the player has. (examples: A,10 or 2,8,4)')
    parser.add_argument("-d", "--dealer-card", required=True, help='The up card of the dealer. (examples: A or 3)')
    parser.add_argument("--splits", default=1, type=int, help='How many times the player can split. '
                                                              '(min: 1=fastest, fairly accurate; '
                                                              'max: 3=slowest, super accurate; default: 1)')
    parser.add_argument("--decks", default=6, type=int, help='How many decks the shoe starts with. (default: 6)')
    parser.add_argument("--shoe", help='The cards in the shoe before the cards were dealt. Overrides --decks. '
                                       '(format: 2,6,5,8,6,2,A,10,9,...)')
    parser.add_argument("--stand17", action='store_true', help='Dealer should stand on soft 17. (default: true)')
    parser.add_argument("--hit17", action='store_true', help='Dealer should hit on soft 17. (default: false)')
    parser.add_argument("--das", action='store_true', help='Allow double after split. (default: true)')
    parser.add_argument("--no-das", action='store_true', help='Don\'t allow double after split. (default: false)')
    parser.add_argument("--peek", action='store_true', help='Dealer peeks for blackjack. (default: true)')
    parser.add_argument("--no-peek", action='store_true', help="Dealer doesn't peek for blackjack. (default: false)")
    parser.add_argument("--surrender", action='store_true', help='Allow surrendering. (default: true)')
    parser.add_argument("--no-surrender", action='store_true', help='Don\'t allow surrendering. (default: false)')
    args = parser.parse_args()

    player_cards = tuple(map(lambda card: int(card.replace("A", "11")), args.cards.split(",")))
    dealers_up_card = int(args.dealer_card.replace("A", "11"))
    splits = args.splits
    decks_number = args.decks
    stand_soft_17 = args.stand17 or (not args.hit17)
    das_allowed = args.das or (not args.no_das)
    peek_for_bj = args.peek or (not args.no_peek)
    surrender_allowed = args.surrender or (not args.no_surrender)

    if args.shoe:
        shoe = list(map(lambda shoe_card: int(shoe_card.replace("A", "11")), args.shoe.split(",")))
    else:
        shoe = DECK * decks_number

    for player_or_dealer_card in player_cards + (dealers_up_card,):  # Remove the cards the player and the dealer have.
        shoe.remove(player_or_dealer_card)

    best_profit, max_action, insurance_return = perfect_mover_cache(player_cards, dealers_up_card, shoe, True,
                                                                    True, surrender_allowed, splits,
                                                                    dealer_peeks_for_blackjack=peek_for_bj, das=das_allowed,
                                                                    dealer_stands_soft_17=stand_soft_17, print_profits=True,
                                                                    plot_profits=True)
