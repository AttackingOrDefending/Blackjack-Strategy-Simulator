Basic Strategy Generation
=========================

Command line options
--------------------

.. code-block:: console

    -e EFFORT, --effort EFFORT
                          How many different hand combinations to test. (min: 0=fastest, very accurate; max: 5=very
                          slow, super accurate; default: 0)
    --cores CORES         How many cores to use in the calculation. (default: 1, use -1 for all cores)
    -f FILENAME, --filename FILENAME
                          Where to save the basic strategy generated. Leave empty to not save. (default: don't save)
    -tc TRUE_COUNT, --true-count TRUE_COUNT
                          Generate deviations from basic strategy for a specific true count. Leave empty to generate
                          basic strategy. (default: generate basic strategy)
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

See the help by running :code:`python basic_strategy_generator.py -h`.

Creating the basic strategy plots
---------------------------------

.. autofunction:: basic_strategy_generator.draw_and_export_tables

Example:

.. code-block:: python

    from basic_strategy_generator import draw_and_export_tables

    hard_totals, soft_totals, pair_splitting = draw_and_export_tables(effort=1, cores=2, filename="strategy.csv", true_count=2,
                                                                      number_of_decks=8, deck_penetration=.25, dealer_peeks_for_blackjack=True,
                                                                      das=True, dealer_stands_soft_17=True, can_surrender=True, plot_results=False)


Generating basic strategy
-------------------------

.. autofunction:: basic_strategy_generator.no_ace_table_generator

.. autofunction:: basic_strategy_generator.ace_table_generator

.. autofunction:: basic_strategy_generator.split_table_generator

Utilities
---------

.. autofunction:: basic_strategy_generator.argmax

.. autoclass:: basic_strategy_generator.Hand
    :members:
