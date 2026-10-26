from random import Random

from .level import Level


class LevelGenerator:
    def __init__(self, rng: Random | None = None) -> None:
        ...

    def generate(self, level_number: int) -> Level:
        ...
