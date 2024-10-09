"""Action strategies to be used in expected value."""
from best_move import perfect_mover_cache
from utils import get_cards_seen, get_hilo_running_count
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
        true_count = get_hilo_running_count(cards_seen) / (deck_number - len(cards_seen) / 52)

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
