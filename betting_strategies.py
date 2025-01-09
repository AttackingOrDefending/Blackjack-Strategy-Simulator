"""Betting strategies to be used in expected value."""
from utils import get_hilo_running_count


class BaseBetter:
    """Base better. The parent class of all betters."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Raise `NotImplementedError`. To be overridden in the other classes.

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        raise NotImplementedError("The `get_bet` method hasn't been overridden.")


class SimpleBetter(BaseBetter):
    """Simple better. Bets the same amount every time."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Bet 1 every time. The bet doesn't change.

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        return 1


class CardCountBetter(BaseBetter):
    """Change the bet according to the true count."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Bet true_count ^ 2 / 2 if true_count >= +1 else 1. Cap at 15 (using a 1-15 spread).

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        running_count = get_hilo_running_count(cards_seen)
        cards_left = deck_number * 52 - len(cards_seen) - 1
        true_count = running_count / (cards_left / 52)
        if true_count >= 1:
            return max(min(int(true_count ** 2 / 2), 15), 1)
        return 1


class ConservativeCardCountBetter(BaseBetter):
    """Change the bet according to the true count conservatively."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Bet true_count if true_count >= +1 else 1. Cap at 5 (using a 1-5 spread).

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        running_count = get_hilo_running_count(cards_seen)
        cards_left = deck_number * 52 - len(cards_seen) - 1
        true_count = running_count / (cards_left / 52)
        if true_count >= 1:
            return max(min(int(true_count), 5), 1)
        return 1


class WongingCardCountBetter(BaseBetter):
    """Change the bet according to the true count and use wonging (don't play if TC < 1)."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Bet true_count ^ 2 / 2 if true_count >= +1 else 0. Cap at 15 (using a 1-15 spread).

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        running_count = get_hilo_running_count(cards_seen)
        cards_left = deck_number * 52 - len(cards_seen) - 1
        true_count = running_count / (cards_left / 52)
        if true_count >= 1:
            return max(min(int(true_count ** 2 / 2), 15), 1)
        return 0


class WongingConservativeCardCountBetter(BaseBetter):
    """Change the bet according to the true count conservatively and use wonging (don't play if TC < 1)."""

    @staticmethod
    def get_bet(cards_seen: list[int], deck_number: int) -> int:
        """
        Bet true_count if true_count >= +1 else 0. Cap at 5 (using a 1-5 spread).

        :param cards_seen: The cards we have already seen from the shoe. Used when card counting.
        :param deck_number: The number of decks in the starting shoe.
        :return: How much money to bet.
        """
        running_count = get_hilo_running_count(cards_seen)
        cards_left = deck_number * 52 - len(cards_seen) - 1
        true_count = running_count / (cards_left / 52)
        if true_count >= 1:
            return max(min(int(true_count), 5), 1)
        return 0
