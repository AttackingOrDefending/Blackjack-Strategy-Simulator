Best Move Analysis
==================

Command line options
--------------------

.. code-block:: console

    -c CARDS, --cards CARDS
                          The cards the player has. (examples: A,10 or 2,8,4)
    -d DEALER_CARD, --dealer-card DEALER_CARD
                          The up card of the dealer (examples: A or 3)
    --splits SPLITS       How many times the player can split (min: 1=fastest, fairly accurate; max: 3=slowest, super
                          accurate; default: 1)
    --decks DECKS         How many decks the shoe starts with. (default: 6)
    --shoe SHOE           The cards in the shoe before the cards were dealt. Overrides --decks. (format:
                          2,6,5,8,6,2,A,10,9,...)
    --stand17             Dealer should stand on soft 17. (default: true)
    --hit17               Dealer should hit on soft 17. (default: false)
    --das                 Allow double after split. (default: true)
    --no-das              Don't allow double after split. (default: false)
    --peek                Dealer peeks for blackjack. (default: true)
    --no-peek             Dealer doesn't peek for blackjack. (default: false)
    --surrender           Allow surrendering. (default: true)
    --no-surrender        Don't allow surrendering. (default: false)

See the help by running :code:`python best_move.py -h`.

Calculate the best action
-------------------------

.. autofunction:: best_move.perfect_mover_cache

Example:

.. code-block:: python

    from best_move import perfect_mover_cache
    from utils import DECK

    shoe = DECK * 6
    for card in (3, 5, 11):  # Remove the cards the player and the dealer have.
        shoe.remove(card)

    expected_return, best_action, insurance_return = perfect_mover_cache(cards=(3, 5), dealer_up_card=11, cards_not_seen=shoe,
                                                                         can_double=True, can_insure=True, can_surrender=True,
                                                                         max_splits=3, dealer_peeks_for_blackjack=False, das=False,
                                                                         dealer_stands_soft_17=False, return_all_profits=False,
                                                                         print_profits=True, plot_profits=True)

.. autofunction:: best_move.perfect_mover

Calculate our chances of beating the dealer
-------------------------------------------

.. autofunction:: best_move.chances_of_beating_dealer

Adjust the probabilities if the dealer peeks for blackjack
----------------------------------------------------------

.. autofunction:: best_move.probabilities_if_dealer_peeks_for_blackjack

Utilities
---------

.. autofunction:: best_move.create_deck_from_counts_cache

.. autofunction:: best_move.create_deck_from_counts

.. autofunction:: best_move.argmax

.. autofunction:: best_move.dict_to_tuple

.. autofunction:: best_move.can_never_split

.. autofunction:: best_move.tuple_sort

.. autoclass:: best_move.HandPlayer
    :members:

.. autoclass:: best_move.HandDealer
    :members:
