"""Test the utilities."""
from utils import short_to_long_action, long_to_short_action, readable_number, list_range_str


def test_utils():
    """Test the utilities."""
    assert short_to_long_action("s") == "stand"
    assert short_to_long_action("h") == "hit"
    assert short_to_long_action("d") == "double"
    assert short_to_long_action("p") == "split"
    assert short_to_long_action("u") == "surrender"
    assert short_to_long_action("i") == "insurance"

    assert long_to_short_action("stand") == "s"
    assert long_to_short_action("hit") == "h"
    assert long_to_short_action("double") == "d"
    assert long_to_short_action("split") == "p"
    assert long_to_short_action("surrender") == "u"
    assert long_to_short_action("insurance") == "i"

    assert readable_number(1_000) == "1.0K"
    assert readable_number(2_580_000) == "2.6M"

    assert list_range_str(1, 3) == ["1", "2"]
