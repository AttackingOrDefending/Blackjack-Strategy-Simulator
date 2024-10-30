"""Test the expected value (EV) calculator."""
from expected_value import expected_value, expected_value_multithreading, get_mover_and_better
from action_strategies import SimpleMover, PerfectMover, BaseMover
from betting_strategies import SimpleBetter, BaseBetter


def test_expected_value() -> None:
    """Test the expected value (EV) calculator."""
    ev = expected_value(SimpleMover(), SimpleBetter(), 1_000, plot_profits=False)
    assert ev < -0.02

    mover, better = get_mover_and_better("basic-strategy", "simple")
    ev = expected_value_multithreading(mover, better, 1_000, 2)
    assert ev > -0.1

    mover, better = get_mover_and_better("card-count", "card-count")
    ev = expected_value_multithreading(mover, better, 1_000, 2)
    assert ev > -0.05

    try:
        BaseMover().get_move(12, True, 2, True, True, True,
                             True, [10, 2], [10, 2, 2], 6, True, True, True)
        assert False
    except NotImplementedError:
        pass

    try:
        BaseBetter().get_bet([10, 2, 2], 6)
        assert False
    except NotImplementedError:
        pass

    assert PerfectMover().get_move(12, True, 2, True, True, True,
                                   True, [10, 2], [10, 2, 2], 6, True,
                                   True, True) == ("hit", False)
