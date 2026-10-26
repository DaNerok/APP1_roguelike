from dataclasses import dataclass, field

from ..entities.position import Position


@dataclass
class Corridor:
    tiles: set[Position] = field(default_factory=set)
