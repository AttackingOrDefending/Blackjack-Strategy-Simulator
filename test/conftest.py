"""Remove files created during testing."""
import os
from typing import Any


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """Remove files created during testing."""
    if os.path.exists("basic_strategy_generated_during_testing.csv"):
        os.remove("basic_strategy_generated_during_testing.csv")
