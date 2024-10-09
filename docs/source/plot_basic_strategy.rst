Plot Basic Strategy
===================

Command line options
--------------------

.. code-block:: console

    -f FILENAME, --filename FILENAME
                          The filename where the basic strategy is stored.

See the help by running :code:`python plot_basic_strategy.py -h`.

Plot the basic strategy
-----------------------

.. autofunction:: plot_basic_strategy.plot_csv

Example:

.. code-block:: python

    from plot_basic_strategy import plot_csv

    plot_csv("data/basic_strategy.csv")


