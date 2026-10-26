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
        return {
            (x, y)
            for x in range(self.x, self.x + self.width)
            for y in range(self.y, self.y + self.height)
        }
        

    def contains(self, position: Position) -> bool:
        px, py = position 
        return (
            self.x <= px < self.x + self.width
            and self.y <= py < self.y + self.height
        )
