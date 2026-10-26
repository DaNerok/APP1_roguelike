from dataclasses import dataclass

from .character import Character
from ..generation.level import Level


@dataclass
class GameSession:
    character: Character
    level: Level
    level_number: int = 1
    is_game_over: bool = False
