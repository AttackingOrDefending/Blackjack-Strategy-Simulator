"""Remove files created during testing."""
import os
from _pytest.config import ExitCode
from _pytest.main import Session


def pytest_sessionfinish(session: Session, exitstatus: int | ExitCode) -> None:
    """Remove files created during testing."""
    if os.path.exists("basic_strategy_generated_during_testing.csv"):
        os.remove("basic_strategy_generated_during_testing.csv")
