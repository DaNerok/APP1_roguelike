from dataclasses import dataclass, field

from .backpack import Backpack
from .item import Item
from .position import Position


@dataclass
class Character:
    position: Position
    max_health: int
    health: int
    dexterity: int
    strength: int
    backpack: Backpack = field(default_factory=Backpack)
    current_weapon: Item | None = None

    def move_to(self, position: Position) -> None:
        ...

    def take_damage(self, amount: int) -> None:
        ...

    def heal(self, amount: int) -> None:
        ...
