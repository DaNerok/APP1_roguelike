from dataclasses import dataclass
from enum import Enum

from .position import Position


class ItemType(str, Enum):
    TREASURE = "treasure"
    FOOD = "food"
    ELIXIR = "elixir"
    SCROLL = "scroll"
    WEAPON = "weapon"


class ItemAttribute(str, Enum):
    MAX_HEALTH = "max_health"
    DEXTERITY = "dexterity"
    STRENGTH = "strength"


@dataclass
class Item:
    item_type: ItemType
    subtype: ItemAttribute | str | None = None
    health: int = 0
    max_health: int = 0
    dexterity: int = 0
    strength: int = 0
    value: int = 0
    duration_turns: int | None = None
    quantity: int = 1
    position: Position | None = None

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("Item quantity must be positive")
        if self.value < 0 or self.health < 0 or self.max_health < 0:
            raise ValueError("Item values cannot be negative")
        if self.duration_turns is not None and self.duration_turns < 1:
            raise ValueError("Temporary effect duration must be positive")
