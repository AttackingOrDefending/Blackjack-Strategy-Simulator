Expected Value (EV) Calculation
===============================

Command line options
--------------------

.. code-block:: console

    -c, --custom          Run custom user-defined movers and betters that require special initialization.
    --cores CORES         How many cores to use in the calculation. (default: 1, use -1 for all cores)
    -m MOVER, --mover MOVER
                          Use a predefined mover. Can also be the name of the class of a user-defined mover. (possible
                          values: card-count, basic-strategy, perfect, simple; default: card-count)
    -b BETTER, --better BETTER
                          Use a predefined better. Can also be the name of the class of a user-defined better. (possible
                          values: card-count, simple; default: card-count)
    -s SIMULATIONS, --simulations SIMULATIONS
                          How many simulations to run. Running more simulations gives more accurate results but they are
                          slower to calculate. (default: 500,000)
    --decks DECKS         How many decks the shoe starts with. (default: 6)
    --deck-penetration DECK_PENETRATION
                          When to reshuffle the shoe. Reshuffles when cards remaining < starting cards * deck
                          penetration. (default: 0.25)
    --stand17             Dealer should stand on soft 17. (default: true)
    --hit17               Dealer should hit on soft 17. (default: false)
    --das                 Allow double after split. (default: true)
    --no-das              Don't allow double after split. (default: false)
    --peek                Dealer peeks for blackjack. (default: true)
    --no-peek             Dealer doesn't peek for blackjack. (default: false)
    --surrender           Allow surrendering. (default: true)
    --no-surrender        Don't allow surrendering. (default: false)

See the help by running :code:`python expected_value.py -h`.

Calculate the expected value
----------------------------

.. autofunction:: expected_value.expected_value

Example:

.. code-block:: python

    from expected_value import expected_value
    from action_strategies import BaseMover
    from betting_strategies import BaseBetter
    from random import randint, choice

    class RandomBetter(BaseBetter):  # Create your own movers and betters.
        @staticmethod
        def get_bet(cards_seen: list[int], deck_number: int) -> int:
            return randint(1, 10)

    class RandomMover(BaseMover):
        @staticmethod
        def get_move(hand_value: int, hand_has_ace: bool, dealer_up_card: int, can_double: bool, can_split: bool,
                     can_surrender: bool, can_insure: bool, hand_cards: list[int], cards_seen: list[int], deck_number: int,
                     dealer_peeks_for_blackjack: bool, das: bool, dealer_stands_soft_17: bool) -> tuple[str, bool]:
            return choice(["s", "h"]), False  # Randomly select between stand ("s") and hit ("h"), and never take insurance (False is don't take insurance).

    mover = RandomMover()
    better = RandomBetter()
    average_profit = expected_value(action_class=mover, betting_class=better, simulations=1_000_000, deck_number=6,
                                    shoe_penetration=.2, dealer_peeks_for_blackjack=True, das=True,
                                    dealer_stands_soft_17=True, surrender_allowed=False, plot_profits=False)

.. autofunction:: expected_value.expected_value_multithreading

Simulate one hand
-----------------

.. autofunction:: expected_value.simulate_hand

.. autofunction:: expected_value.get_mover_and_better

.. autofunction:: expected_value.play_dealer

Utilities
---------

.. autofunction:: expected_value.get_card_from_shoe

.. autoclass:: expected_value.Hand
    :members:

Wrapper for multithreading
--------------------------

.. autofunction:: expected_value._expected_value_multithreading_wrapper
