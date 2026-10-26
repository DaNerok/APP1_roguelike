from dataclasses import dataclass

from ..entities.position import Position
from .corridor import Corridor
from .room import Room


@dataclass
class Level:
    level_number: int
    rooms: list[Room]
    corridors: list[Corridor]
    start_position: Position
    exit_position: Position

    @property
    def walkable_tiles(self) -> set[Position]:
        ...

    def is_walkable(self, position: Position) -> bool:
        ...

    def room_at(self, position: Position) -> Room | None:
        ...
