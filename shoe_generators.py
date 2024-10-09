"""Shoe generators."""
from utils import get_hilo_true_count, DECK
import random


def hilo_generator(true_count: int, decks: int, deck_penetration: float, cards_present: list[int]) -> list[int]:
    """
    Generate a random shoe with a specific true count.

    :param true_count: The target true count.
    :param decks: The maximum number of decks in the shoe.
    :param deck_penetration: When to reshuffle the shoe. Reshuffles when cards remaining < starting cards * deck penetration.
        So the cards in the returned shoe must be at least starting cards * deck penetration.
    :param cards_present: The cards we have already seen, so that we don't get shoe with more cards of one type than possible.
    :return: A shoe with a specific true count.
    """
    max_true_count = true_count + .3 if true_count >= 0 else true_count
    min_true_count = true_count - .3 if true_count <= 0 else true_count

    all_cards = DECK * decks
    for card in cards_present:
        all_cards.remove(card)

    while True:
        shoe = all_cards.copy()
        random.shuffle(shoe)
        good_shoes = []

        while len(shoe) >= 52 * decks * deck_penetration:
            if min_true_count <= get_hilo_true_count(shoe) <= max_true_count:
                good_shoes.append(shoe.copy())
            shoe.pop()

        if good_shoes:
            break
    return random.choice(good_shoes)
