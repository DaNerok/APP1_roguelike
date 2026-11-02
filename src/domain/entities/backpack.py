from dataclasses import dataclass, field

from .item import Item, ItemType


@dataclass
class Backpack:
    items: list[Item] = field(default_factory=list)
    capacity_per_type: int = 9

    def add_item(self, item: Item) -> bool:
        if item.item_type == ItemType.TREASURE:
            existing = next(
                (stored for stored in self.items if stored.item_type == ItemType.TREASURE),
                None,
            )
            if existing is not None:
                existing.value += item.value
                existing.quantity += item.quantity
                return True
            self.items.append(item)
            return True

        if sum(stored.item_type == item.item_type for stored in self.items) >= self.capacity_per_type:
            return False

        self.items.append(item)
        return True

    def remove_item(self, item: Item) -> None:
        for index, stored in enumerate(self.items):
            if stored is item:
                del self.items[index]
                return
        raise ValueError("Item is not in the backpack")

    def items_of_type(self, item_type: ItemType) -> list[Item]:
        return [item for item in self.items if item.item_type == item_type]

    def can_add(self, item: Item) -> bool:
        if item.item_type == ItemType.TREASURE:
            return True
        return sum(stored.item_type == item.item_type for stored in self.items) < self.capacity_per_type
