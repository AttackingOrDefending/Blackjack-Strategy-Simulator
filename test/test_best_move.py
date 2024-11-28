"""Test the best move analysis."""
from best_move import perfect_mover_cache
from utils import DECK


def test_best_move() -> None:
    """Test the best move analysis."""
    shoe = DECK * 6

    for card in [11, 11, 11]:
        shoe.remove(card)
    results = perfect_mover_cache((11, 11), 11, tuple(shoe), max_splits=1, return_all_profits=True)
    assert results == (-0.6664582487827273, -0.022205703672547265, -0.6202385156597964, 0.12714379565459186, -0.5,
                       -0.033980582524271885)

    results = perfect_mover_cache((10, 10), 10, tuple(shoe), max_splits=2, return_all_profits=True)
    assert results == (0.5542589949582133, -0.8662002899228858, -1.7324005798457716, 0.03264991092613637, -0.5, -1000.0)
