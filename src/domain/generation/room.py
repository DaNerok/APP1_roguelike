from dataclasses import dataclass

from ..entities.position import Position


@dataclass
class Room:
    room_id: int
    x: int
    y: int
    width: int
    height: int

    @property
    def tiles(self) -> set[Position]:
        ...

    def contains(self, position: Position) -> bool:
        ...
