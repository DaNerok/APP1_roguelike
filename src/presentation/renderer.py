import curses

from domain.entities.character import Character
from domain.entities.enemy import Enemy, EnemyType
from domain.entities.item import Item, ItemType
from domain.entities.position import Position
from domain.generation.level import Level


class Renderer:
    def __init__(self, screen: curses.window) -> None:
        ...

    def render(
        self,
        level: Level,
        character: Character,
        enemies: list[Enemy],
        items: list[tuple[Item, Position]],
    ) -> None:
        ...

    def draw_character(self, character: Character) -> None:
        ...

    def draw_enemy(self, enemy: Enemy) -> None:
        ...

    def draw_item(self, item: Item, position: Position) -> None:
        ...

    def draw_at(self, position: Position, symbol: str) -> None:
        ...

    def enemy_symbol(self, enemy_type: EnemyType) -> str:
        ...

    def item_symbol(self, item_type: ItemType) -> str:
        ...
