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
        tiles: set[Position] = set()
        for room in self.rooms:
            tiles.update(room.tiles)
        for corridor in self.corridors:
            tiles.update(corridor.tiles)
        return tiles 
    

    def is_walkable(self, position: Position) -> bool:
        if any(room.contains(position) for room in self.rooms):
            return True
        return any(position in corridor.tiles for corridor in self.corridors)        

    def room_at(self, position: Position) -> Room | None:
        for room in self.rooms:
            if room.contains(position):
                return room
        return None
        
