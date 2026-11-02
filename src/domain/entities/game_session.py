from dataclasses import dataclass, field

from .character import Character
from .enemy import Enemy
from .item import Item
from ..generation.level import Level
from .position import Position


@dataclass
class RunStatistics:
    treasure_collected: int = 0
    deepest_level_reached: int = 1
    enemies_defeated: int = 0
    food_consumed: int = 0
    elixirs_used: int = 0
    scrolls_read: int = 0
    attacks_made: int = 0
    hits_taken: int = 0
    tiles_traversed: int = 0


@dataclass
class GameSession:
    character: Character
    level: Level
    level_number: int = 1
    enemies: list[Enemy] = field(default_factory=list)
    ground_items: list[Item] = field(default_factory=list)
    statistics: RunStatistics = field(default_factory=RunStatistics)
    is_game_over: bool = False
    is_completed: bool = False

    def __post_init__(self) -> None:
        if self.level_number < 1:
            raise ValueError("Level number must be positive")
        self.statistics.deepest_level_reached = max(
            self.statistics.deepest_level_reached,
            self.level_number,
        )
        if not self.character.is_alive:
            self.is_game_over = True

    def move_character(self, position: Position) -> None:
        if position != self.character.position:
            self.character.move_to(position)
            self.statistics.tiles_traversed += 1

    def advance_to_level(self, level: Level) -> None:
        if level.level_number <= self.level_number:
            raise ValueError("Next level number must be greater than current level")
        self.level = level
        self.level_number = level.level_number
        self.enemies.clear()
        self.ground_items.clear()
        self.character.move_to(level.start_position)
        self.statistics.deepest_level_reached = max(
            self.statistics.deepest_level_reached,
            self.level_number,
        )

    def finish(self, completed: bool = False) -> None:
        self.is_completed = completed
        self.is_game_over = True
