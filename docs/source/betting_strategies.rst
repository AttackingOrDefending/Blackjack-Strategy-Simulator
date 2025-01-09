Betting Strategies
==================

Base class to create your own betters
-------------------------------------

.. autoclass:: betting_strategies.BaseBetter
    :members:

Example custom better:

.. code-block:: python

    class MyBetter(BaseBetter):
        @staticmethod
        def get_bet(cards_seen: list[int], deck_number: int) -> int:
            running_count = get_hilo_running_count(cards_seen)
            cards_left = deck_number * 52 - len(cards_seen)
            true_count = running_count / (cards_left / 52)
            return min(max(int(true_count), 1), 8)

Pre-built betters
-----------------

.. autoclass:: betting_strategies.SimpleBetter
    :members:

.. autoclass:: betting_strategies.CardCountBetter
    :members:

.. autoclass:: betting_strategies.ConservativeCardCountBetter
    :members:

.. autoclass:: betting_strategies.WongingCardCountBetter
    :members:

.. autoclass:: betting_strategies.WongingConservativeCardCountBetter
    :members:
