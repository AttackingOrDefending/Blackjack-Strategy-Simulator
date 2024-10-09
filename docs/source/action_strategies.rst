Action Strategies
=================

Base class to create your own movers
------------------------------------

.. autoclass:: action_strategies.BaseMover
    :members:

Example custom mover:

.. code-block:: python

    class MyMover(BaseMover):
        @staticmethod
        def get_move(hand_value: int, hand_has_ace: bool, dealer_up_card: int, can_double: bool, can_split: bool,
                     can_surrender: bool, can_insure: bool, hand_cards: list[int], cards_seen: list[int], deck_number: int,
                     dealer_peeks_for_blackjack: bool, das: bool, dealer_stands_soft_17: bool) -> tuple[str, bool]:
            if hand_value < 17:
                return "d" if can_double and hand_value in [10, 11] else "h", False
            return "s", False

Pre-built movers
----------------

.. autoclass:: action_strategies.SimpleMover
    :members:

.. autoclass:: action_strategies.BasicStrategyMover
    :members:

.. autoclass:: action_strategies.CardCountMover
    :members:

.. autoclass:: action_strategies.PerfectMover
    :members:
