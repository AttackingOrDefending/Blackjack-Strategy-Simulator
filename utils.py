"""Utilities for the rest of the program."""

from collections import Counter


"""The card that a suit contains."""
SUIT: list[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]

"""The cards that a deck contains."""
DECK: list[int] = SUIT * 4


def list_range_str(start: int, end: int, step: int = 1) -> list[str]:
    """
    Return a list of string numbers.

    :param start: The starting number (inclusive) for the range generator.
    :param end: The ending number (exclusive) for the range generator.
    :param step: The step parameter for the range generator.
    :return: A list with the results of `range(start, end, step)` converted to strings.
    """
    return list(map(str, range(start, end, step)))


def short_to_long_action(action: str) -> str:
    """
    Convert a shorthand to the name of the action.

    :param action: A shorthand for each possible action. s for stand, h for hit, d for double, p for split, u for surrender,
        and i for insurance.
    :return: The name of the action. (e.g. returns stand for s and split for p)
    """
    short_to_long = {"s": "stand", "h": "hit", "d": "double", "p": "split", "u": "surrender", "i": "insurance"}
    return short_to_long[action]


def long_to_short_action(action: str) -> str:
    """
    Convert the action to its shorthand.

    :param action: The name of each action. split, hit, double, split, surrender, and insurance.
    :return: The shorthand for each action. (e.g. returns h for hit and u for surrender)
    """
    long_to_short = {"stand": "s", "hit": "h", "double": "d", "split": "p", "surrender": "u", "insurance": "i"}
    return long_to_short[action]


def get_cards_seen(deck_number: int, shoe: list[int]) -> list[int]:
    """
    Get the cards that we have already seen from the umber of decks and the shoe.

    :param deck_number: How many decks the shoe started with
    :param shoe: The cards that are still in the shoe.
    :return: The cards that we have seen.
    """
    counts = {card: 4 * deck_number for card in range(2, 12)}
    counts[10] *= 4
    shoe_counts = Counter(shoe)
    for card in range(2, 12):
        counts[card] -= shoe_counts[card]
    cards_seen = []
    for card, count in counts.items():
        cards_seen += [card] * count
    return cards_seen


def get_hilo_running_count(cards_seen: list[int]) -> int:
    """
    Get the running count from the cards we have seen.

    :param cards_seen: The cards we have seen.
    :return: The running count of the shoe.
    """
    hilo = 0
    for card in cards_seen:
        hilo -= card > 9
        hilo += card < 7
    return hilo


def get_hilo_true_count(shoe: list[int]) -> float:
    """
    Get the true count from the shoe.

    :param shoe: The shoe (cards we haven't seen).
    :return: The true count of the shoe.
    """
    running_count = 0
    deck_num = len(shoe) / 52
    for card in shoe:
        # The +1 and -1 are reversed as this is calculated for the unseen cards.
        if card <= 6:
            running_count -= 1
        elif card >= 10:
            running_count += 1
    return running_count / deck_num


def readable_number(number: int) -> str:
    """
    Turn a number into a more readable format.

    :param number: An integer.
    :return: An easier-to-read format for the number (e.g. 15_000_000 becomes 15.0M).
    """
    if number >= 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    if number >= 1_000:
        return f"{round(number / 1_000, 1)}K"
    return str(number)
