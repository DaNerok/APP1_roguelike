from dataclasses import dataclass, field

from .item import Item, ItemType


@dataclass
class Backpack:
    items: list[Item] = field(default_factory=list)
    capacity_per_type: int = 9

    def add_item(self, item: Item) -> bool:
        ...

    def remove_item(self, item: Item) -> None:
        ...

    def items_of_type(self, item_type: ItemType) -> list[Item]:
        ...
