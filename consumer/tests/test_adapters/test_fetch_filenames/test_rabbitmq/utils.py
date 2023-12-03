import random
import string


def random_csv_filenames() -> list[str]:
    return [
        "".join(random.choices(string.ascii_letters, k=10)) + ".csv" for _ in range(5)
    ]
