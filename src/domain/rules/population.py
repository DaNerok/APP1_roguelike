from random import Random

from ..entities.enemy import Enemy, EnemyType
from ..entities.item import Item, ItemAttribute, ItemType
from ..entities.position import Position
from ..generation.level import Level


class LevelPopulationRules:
    ENEMY_TYPES = tuple(EnemyType)
    USEFUL_ITEM_TYPES = (ItemType.FOOD, ItemType.ELIXIR, ItemType.SCROLL, ItemType.WEAPON)

    def __init__(self, rng: Random | None = None) -> None:
        self.rng = rng or Random()

    def populate(self, level: Level) -> tuple[list[Enemy], list[Item]]:
        room_tiles = self._available_room_tiles(level)
        enemy_count = min(len(room_tiles), 2 + level.level_number // 2)
        enemy_positions = self._take_positions(room_tiles, enemy_count)
        enemies = [
            Enemy.create(
                self.rng.choice(self.ENEMY_TYPES),
                position,
                level.level_number,
            )
            for position in enemy_positions
        ]

        remaining_positions = [
            position for position in room_tiles if position not in set(enemy_positions)
        ]
        useful_item_count = max(1, 9 - level.level_number // 2)
        item_count = min(len(remaining_positions), useful_item_count)
        item_positions = self._take_positions(remaining_positions, item_count)
        items = [
            self._create_item(position, level.level_number)
            for position in item_positions
        ]
        return enemies, items

    def _available_room_tiles(self, level: Level) -> list[Position]:
        start_room = next(
            (room for room in level.rooms if room.contains(level.start_position)),
            None,
        )
        return [
            position
            for room in level.rooms
            if room is not start_room
            for position in room.tiles
            if position != level.exit_position
        ]

    def _take_positions(
        self,
        positions: list[Position],
        count: int,
    ) -> list[Position]:
        if count <= 0:
            return []
        return self.rng.sample(positions, count)

    def _create_item(self, position: Position, level_number: int) -> Item:
        item_type = self.rng.choice(self.USEFUL_ITEM_TYPES)
        if item_type == ItemType.FOOD:
            return Item(
                item_type=ItemType.FOOD,
                health=self.rng.randint(4, 8),
                position=position,
            )
        if item_type == ItemType.ELIXIR:
            attribute = self.rng.choice(tuple(ItemAttribute))
            return self._attribute_item(
                ItemType.ELIXIR,
                attribute,
                max(1, 1 + level_number // 5),
                self.rng.randint(5, 9),
                position,
            )
        if item_type == ItemType.SCROLL:
            attribute = self.rng.choice(tuple(ItemAttribute))
            return self._attribute_item(
                ItemType.SCROLL,
                attribute,
                max(1, 1 + level_number // 7),
                None,
                position,
            )
        return Item(
            item_type=ItemType.WEAPON,
            strength=self.rng.randint(1, max(1, 3 + level_number // 7)),
            position=position,
        )

    def _attribute_item(
        self,
        item_type: ItemType,
        attribute: ItemAttribute,
        amount: int,
        duration_turns: int | None,
        position: Position,
    ) -> Item:
        values = {
            ItemAttribute.MAX_HEALTH: {"max_health": amount},
            ItemAttribute.DEXTERITY: {"dexterity": amount},
            ItemAttribute.STRENGTH: {"strength": amount},
        }
        return Item(
            item_type=item_type,
            subtype=attribute,
            duration_turns=duration_turns,
            position=position,
            **values[attribute],
        )
