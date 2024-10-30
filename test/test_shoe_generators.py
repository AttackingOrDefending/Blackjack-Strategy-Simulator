"""Test the shoe generators."""
from shoe_generators import hilo_generator
from utils import get_hilo_true_count


def test_hilo_true_count() -> None:
    """Test the Hi-Lo true count generator."""
    assert 3 <= get_hilo_true_count(hilo_generator(3, 6, .25, [2, 5, 7])) <= 3.3
