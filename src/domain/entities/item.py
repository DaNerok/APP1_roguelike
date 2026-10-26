from dataclasses import dataclass
from enum import Enum


class ItemType(str, Enum):
    TREASURE = "treasure"
    FOOD = "food"
    ELIXIR = "elixir"
    SCROLL = "scroll"
    WEAPON = "weapon"


@dataclass
class Item:
    item_type: ItemType
    subtype: str | None = None
    health: int = 0
    max_health: int = 0
    dexterity: int = 0
    strength: int = 0
    value: int = 0
