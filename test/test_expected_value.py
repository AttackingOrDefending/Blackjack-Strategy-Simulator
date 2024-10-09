"""Test the expected value (EV) calculator."""
from expected_value import expected_value
from action_strategies import SimpleMover
from betting_strategies import SimpleBetter


def test_expected_value() -> None:
    """Test the expected value (EV) calculator."""
    ev = expected_value(SimpleMover(), SimpleBetter(), 100_000, plot_profits=False)
    assert ev < -0.02
