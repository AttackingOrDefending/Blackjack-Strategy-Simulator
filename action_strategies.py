"""Action strategies to be used in expected value."""
from best_move import perfect_mover_cache
from utils import get_cards_seen, get_hilo_running_count
from collections import Counter
from functools import lru_cache
import math
import csv


class BaseMover:
    """Base mover. The parent class of all movers."""

    @staticmethod
    def get_move(hand_value: int, hand_has_ace: bool, dealer_up_card: int, can_double: bool, can_split: bool,
                 can_surrender: bool, can_insure: bool, hand_cards: list[int], cards_seen: list[int], deck_number: int,
                 dealer_peeks_for_blackjack: bool, das: bool, dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Raise `NotImplementedError`. To be overwritten in the other classes.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """

        raise NotImplementedError("The `get_move` method hasn't been overridden.")


class SimpleMover(BaseMover):
    """Simple mover. Moves like the dealer in a Stand 17 game."""

    @staticmethod
    def get_move(hand_value: int, hand_has_ace: bool, dealer_up_card: int, can_double: bool, can_split: bool,
                 can_surrender: bool, can_insure: bool, hand_cards: list[int], cards_seen: list[int], deck_number: int,
                 dealer_peeks_for_blackjack: bool, das: bool, dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Hit (value <= 16) or stand (value >= 17). Never take insurance.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """
        if hand_value < 17:
            return "h", False
        return "s", False


class BasicStrategyMover(BaseMover):
    """Move according to the basic strategy."""

    def __init__(self, filename: str) -> None:
        """
        Get the move to play for each hand-dealer combination.

        :param filename: The file where the basic strategy is stored.
        """
        self.filename = filename
        self.no_ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
        self.ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
        self.split = {k: {d: "s" for d in range(2, 12)} for k in range(12)}
        self.read_file()

    def read_file(self) -> None:
        """Read the file with the basic strategy."""
        with open(self.filename, newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                identifier = row[0]
                hand_value = int(identifier[1:])
                column = 1
                if identifier.startswith("n"):
                    for dealer_up_card in range(2, 12):
                        self.no_ace[hand_value][dealer_up_card] = row[column]
                        column += 1
                elif identifier.startswith("a"):
                    for dealer_up_card in range(2, 12):
                        self.ace[hand_value][dealer_up_card] = row[column]
                        column += 1
                elif identifier.startswith("s"):
                    for dealer_up_card in range(2, 12):
                        self.split[hand_value][dealer_up_card] = row[column]
                        column += 1
                else:
                    raise ValueError

    def get_move(self, hand_value: int, hand_has_ace: bool, dealer_up_card: int,  # type: ignore[override]
                 can_double: bool, can_split: bool, can_surrender: bool, can_insure: bool, hand_cards: list[int],
                 cards_seen: list[int], deck_number: int, dealer_peeks_for_blackjack: bool, das: bool,
                 dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Get the move to play from basic strategy.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """
        insure = False
        if can_split:
            card = hand_cards[0]
            action = self.split[card][dealer_up_card]
        elif hand_has_ace:
            action = self.ace[hand_value][dealer_up_card]
        else:
            action = self.no_ace[hand_value][dealer_up_card]
        if can_insure and action[0] == "i":
            insure = True

        if action[0] == "i":
            action = action[1:]
        if action[0] == "u" and not can_surrender:
            action = action[1:]
        if action[0] == "d" and not can_double:
            action = action[1:]

        return action[0], insure


class BasicStrategyDeviationsMover(BaseMover):
    """Move according to the basic strategy with the most common deviations."""

    def __init__(self, filename: str) -> None:
        """
        Get the move to play for each hand-dealer combination.

        :param filename: The file where the basic strategy is stored.
        """
        self.filename = filename
        self.no_ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
        self.ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
        self.split = {k: {d: "s" for d in range(2, 12)} for k in range(12)}
        self.read_file()

    def read_file(self) -> None:
        """Read the file with the basic strategy with the most common deviations."""
        with open(self.filename, newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                identifier = row[0]
                hand_value = int(identifier[1:])
                column = 1
                if identifier.startswith("n"):
                    for dealer_up_card in range(2, 12):
                        self.no_ace[hand_value][dealer_up_card] = row[column]
                        column += 1
                elif identifier.startswith("a"):
                    for dealer_up_card in range(2, 12):
                        self.ace[hand_value][dealer_up_card] = row[column]
                        column += 1
                elif identifier.startswith("s"):
                    for dealer_up_card in range(2, 12):
                        self.split[hand_value][dealer_up_card] = row[column]
                        column += 1
                else:
                    raise ValueError

    def get_move(self, hand_value: int, hand_has_ace: bool, dealer_up_card: int,  # type: ignore[override]
                 can_double: bool, can_split: bool, can_surrender: bool, can_insure: bool, hand_cards: list[int],
                 cards_seen: list[int], deck_number: int, dealer_peeks_for_blackjack: bool, das: bool,
                 dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Get the move to play from basic strategy.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """
        true_count = get_hilo_running_count(cards_seen) / (deck_number - (len(cards_seen) + 1) / 52)
        insure = False
        if can_split:
            card = hand_cards[0]
            action = self.split[card][dealer_up_card]
        elif hand_has_ace:
            action = self.ace[hand_value][dealer_up_card]
        else:
            action = self.no_ace[hand_value][dealer_up_card]
        if can_insure and action[0] == "i":
            insure = True

        if hand_has_ace is False:
            if hand_value == 12 and dealer_up_card == 2 and true_count >= 3:
                action = "s"
            if hand_value == 12 and dealer_up_card == 3 and true_count >= 2:
                action = "s"
            if hand_value == 12 and dealer_up_card == 4 and true_count < 0:
                action = "h"
            if hand_value == 12 and dealer_up_card == 5 and true_count < -2:
                action = "h"
            if hand_value == 12 and dealer_up_card == 6 and true_count < -1:
                action = "h"
            if hand_value == 13 and dealer_up_card == 2 and true_count < -1:
                action = "h"
            if hand_value == 13 and dealer_up_card == 3 and true_count < -2:
                action = "h"
            if hand_value == 15 and dealer_up_card == 10 and true_count >= 4:
                action = "us"
            if hand_value == 16 and dealer_up_card == 10 and true_count >= 1:
                action = "us"
            if hand_value == 16 and dealer_up_card == 9 and true_count >= 5:
                action = "us"
            if hand_value == 10 and dealer_up_card == 10 and true_count >= 4:
                action = "dh"
            if hand_value == 10 and dealer_up_card == 11 and true_count >= 4:
                action = "dh"
            if hand_value == 11 and dealer_up_card == 11 and true_count >= 1:
                action = "dh"
            if (hand_value == 20 and len(hand_cards) == 2 and hand_cards[0] == 10 and dealer_up_card == 5
                    and true_count >= 5 and can_split):
                action = "ps"
            if (hand_value == 20 and len(hand_cards) == 2 and hand_cards[0] == 10 and dealer_up_card == 6
                    and true_count >= 4 and can_split):
                action = "ps"
            if hand_value == 14 and dealer_up_card == 10 and true_count >= 3:
                action = "u" + action
            if hand_value == 15 and dealer_up_card == 10 and true_count < 0:
                action = "h"
            if hand_value == 15 and dealer_up_card == 9 and true_count >= 2:
                action = "u" + action
            if hand_value == 15 and dealer_up_card == 11 and true_count >= 1:
                action = "u" + action
        if true_count >= 3:
            action = "i" + action

        if action[0] == "i":
            action = action[1:]
        if action[0] == "u" and not can_surrender:
            action = action[1:]
        if action[0] == "d" and not can_double:
            action = action[1:]

        return action[0], insure


class CardCountMover(BaseMover):
    """Move according to the basic strategy and the deviations using the card count."""

    def __init__(self, filenames: dict[tuple[float, float], str]) -> None:
        """
        Get the move to play for each hand-dealer combination.

        The format of filenames is:
        Key: Minimum TC to play a strategy (inclusive), Maximum TC to play a strategy (exclusive).
        Value: The filename of the strategy to follow for a range of TCs (TC can be decimal).

        Example:
        (-1000, 2.5): General Basic Strategy
        (2.5, 5): Basic Strategy TC +4
        (5, 1000): Basic strategy TC +6

        :param filenames: The filenames where the basic strategy and deviations are stored,
            and when should each strategy be played.
        """
        self.filenames = filenames
        self.no_ace: dict[tuple[float, float], dict[int, dict[int, str]]] = {}
        self.ace: dict[tuple[float, float], dict[int, dict[int, str]]] = {}
        self.split: dict[tuple[float, float], dict[int, dict[int, str]]] = {}
        self.read_files()

    def read_files(self) -> None:
        """Read the files with the basic strategy and deviations."""
        for min_tc_max_tc in self.filenames:
            no_ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
            ace = {k: {d: "s" for d in range(2, 12)} for k in range(22)}
            split = {k: {d: "s" for d in range(2, 12)} for k in range(12)}
            with open(self.filenames[min_tc_max_tc], newline='') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                for row in reader:
                    identifier = row[0]
                    hand_value = int(identifier[1:])
                    column = 1
                    if identifier.startswith("n"):
                        for dealer_up_card in range(2, 12):
                            no_ace[hand_value][dealer_up_card] = row[column]
                            column += 1
                    elif identifier.startswith("a"):
                        for dealer_up_card in range(2, 12):
                            ace[hand_value][dealer_up_card] = row[column]
                            column += 1
                    elif identifier.startswith("s"):
                        for dealer_up_card in range(2, 12):
                            split[hand_value][dealer_up_card] = row[column]
                            column += 1
                    else:
                        raise ValueError
            self.no_ace[min_tc_max_tc] = no_ace
            self.ace[min_tc_max_tc] = ace
            self.split[min_tc_max_tc] = split

    def get_move(self, hand_value: int, hand_has_ace: bool, dealer_up_card: int,  # type: ignore[override]
                 can_double: bool, can_split: bool, can_surrender: bool, can_insure: bool, hand_cards: list[int],
                 cards_seen: list[int], deck_number: int, dealer_peeks_for_blackjack: bool, das: bool,
                 dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Get the move to play.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """
        true_count = get_hilo_running_count(cards_seen) / (deck_number - (len(cards_seen) + 1) / 52)

        for min_tc, max_tc in self.filenames:
            if min_tc <= true_count < max_tc:
                split = self.split[(min_tc, max_tc)]
                ace = self.ace[(min_tc, max_tc)]
                no_ace = self.no_ace[(min_tc, max_tc)]
                break
        else:
            raise IndexError(f"There is no file provided for a true count of {true_count}.")

        insure = False
        if can_split:
            card = hand_cards[0]
            action = split[card][dealer_up_card]
        elif hand_has_ace:
            action = ace[hand_value][dealer_up_card]
        else:
            action = no_ace[hand_value][dealer_up_card]
        if can_insure and action[0] == "i":
            insure = True

        if action[0] == "i":
            action = action[1:]
        if action[0] == "u" and not can_surrender:
            action = action[1:]
        if action[0] == "d" and not can_double:
            action = action[1:]

        return action[0], insure


class PerfectMover(BaseMover):
    """Get the best move to play using all available information."""

    @staticmethod
    def get_move(hand_value: int, hand_has_ace: bool, dealer_up_card: int, can_double: bool, can_split: bool,
                 can_surrender: bool, can_insure: bool, hand_cards: list[int], cards_seen: list[int], deck_number: int,
                 dealer_peeks_for_blackjack: bool, das: bool, dealer_stands_soft_17: bool) -> tuple[str, bool]:
        """
        Get the best move to play by taking into account every available information. Uses the best move analysis.

        Very slow to be used in large EV calculations.

        :param hand_value: The value of the hand (e.g. 18).
        :param hand_has_ace: Whether the hand has an ace that is counted as 11.
        :param dealer_up_card: The dealer's up card.
        :param can_double: Whether we can double.
        :param can_split: Whether we can split.
        :param can_surrender: Whether we can surrender.
        :param can_insure: Whether we can take insurance.
        :param hand_cards: The cards in our hand (e.g. 8, 7, 3).
        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :param dealer_peeks_for_blackjack: Whether the dealer peeks for blackjack.
        :param das: Whether we can double after splitting.
        :param dealer_stands_soft_17: Whether the dealer stands on soft 17.
        :return: The action to do, and whether to take insurance.
        """
        cards_not_seen = get_cards_seen(deck_number, cards_seen)
        profits = perfect_mover_cache(tuple(hand_cards), dealer_up_card, tuple(cards_not_seen), can_double, can_insure,
                                      can_surrender, int(can_split), dealer_peeks_for_blackjack, das, dealer_stands_soft_17)
        return str(profits[1]), profits[2] > 0  # profit[1] is a string. str is there for mypy.

class ExpectimaxMover(BaseMover):
    """
    Selects an action using a depth-limited Expectimax search over
    player actions and stochastic card draws.
    """

    MAX_DEPTH = 1

    @staticmethod
    def get_move(
        hand_value,
        hand_has_ace,
        dealer_up_card,
        can_double,
        can_split,
        can_surrender,
        can_insure,
        hand_cards,
        cards_seen,
        deck_number,
        dealer_peeks_for_blackjack,
        das,
        dealer_stands_soft_17
    ):
        # Build unseen deck
        full_deck = []
        for _ in range(deck_number):
            full_deck.extend([2,3,4,5,6,7,8,9,10,10,10,10,11])

        deck_counter = Counter(full_deck)
        for c in cards_seen:
            if deck_counter[c] > 0:
                deck_counter[c] -= 1

        @lru_cache(None)
        def expectimax(player_total, usable_ace, deck_tuple, depth):
            # Terminal conditions
            if player_total > 21 or depth == 0:
                return ExpectimaxMover.evaluate_state(
                    player_total,
                    usable_ace,
                    dealer_up_card,
                    hand_cards,
                    cards_seen,
                    deck_number,
                    dealer_peeks_for_blackjack,
                    das,
                    dealer_stands_soft_17
                )

            best_value = -math.inf

            # STAND
            stand_value = ExpectimaxMover.evaluate_state(
                player_total,
                usable_ace,
                dealer_up_card,
                hand_cards,
                cards_seen,
                deck_number,
                dealer_peeks_for_blackjack,
                das,
                dealer_stands_soft_17
            )
            best_value = max(best_value, stand_value)

            # HIT (Chance Node)
            hit_value = 0.0
            total_cards = sum(deck_tuple)

            if total_cards > 0:
                for card, count in enumerate(deck_tuple):
                    if count == 0:
                        continue

                    prob = count / total_cards
                    new_total, new_ace = ExpectimaxMover.apply_card(
                        player_total, usable_ace, card
                    )

                    new_deck = list(deck_tuple)
                    new_deck[card] -= 1

                    hit_value += prob * expectimax(
                        new_total,
                        new_ace,
                        tuple(new_deck),
                        depth - 1
                    )

                best_value = max(best_value, hit_value)

            return best_value

        # Convert deck counter to tuple indexed by card value
        max_card = max(deck_counter.keys())
        deck_tuple = [0] * (max_card + 1)
        for card, count in deck_counter.items():
            deck_tuple[card] = count

        # Evaluate top-level actions
        move_values = {}

        move_values["s"] = expectimax(
            hand_value, hand_has_ace, tuple(deck_tuple), 0
        )

        move_values["h"] = expectimax(
            hand_value, hand_has_ace, tuple(deck_tuple), ExpectimaxMover.MAX_DEPTH
        )

        if can_double:
            move_values["d"] = move_values["s"]

        if can_surrender:
            move_values["u"] = -0.5

        best_move = max(move_values, key=move_values.get)

        return best_move, False

    @staticmethod
    def apply_card(total, usable_ace, card):
        total += card
        if card == 11:
            usable_ace = True
        if total > 21 and usable_ace:
            total -= 10
            usable_ace = False
        return total, usable_ace

    @staticmethod
    def evaluate_state(
        player_total,
        usable_ace,
        dealer_up_card,
        hand_cards,
        cards_seen,
        deck_number,
        dealer_peeks_for_blackjack,
        das,
        dealer_stands_soft_17
    ):
        # Simple heuristic terminal evaluation
        if player_total > 21:
            return -1.0
        if player_total >= 17:
            return 0.5
        return 0.0