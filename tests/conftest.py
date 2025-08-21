from pathlib import Path

import pytest


@pytest.fixture()
def signal_directory() -> Path:
    return Path(__file__).parent / "data"
