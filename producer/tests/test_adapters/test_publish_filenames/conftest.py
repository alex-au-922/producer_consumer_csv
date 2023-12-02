import string
import random
import pytest


@pytest.fixture
def random_filenames() -> list[str]:
    return [
        "".join(random.choices(string.ascii_letters, k=10))
        + "."
        + "".join(random.choices(string.ascii_letters, k=3))
        for _ in range(10)
    ]
