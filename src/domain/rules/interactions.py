from ..entities.character import CharacterAttribute
from ..entities.game_session import GameSession
from ..entities.item import Item, ItemAttribute, ItemType
from ..entities.position import Position


class InteractionRules:
    DEFAULT_ELIXIR_DURATION = 10

    def move_character(self, session: GameSession, position: Position) -> bool:
        current_x, current_y = session.character.position
        target_x, target_y = position
        if abs(target_x - current_x) + abs(target_y - current_y) != 1:
            return False
        if not session.level.is_walkable(position):
            return False
        if any(enemy.is_alive and enemy.position == position for enemy in session.enemies):
            return False
        session.move_character(position)
        for item in tuple(session.ground_items):
            if item.position == position:
                self.pick_up_item(session, item)
        return True

    def pick_up_item(self, session: GameSession, item: Item) -> bool:
        ground_item = next(
            (candidate for candidate in session.ground_items if candidate is item),
            None,
        )
        if (
            ground_item is None
            or item.item_type == ItemType.TREASURE
            or not session.character.backpack.add_item(item)
        ):
            return False
        session.ground_items.remove(ground_item)
        item.position = None
        return True

    def use_item(self, session: GameSession, item: Item) -> bool:
        character = session.character
        stored_item = next(
            (candidate for candidate in character.backpack.items if candidate is item),
            None,
        )
        if stored_item is None:
            return False

        if item.item_type == ItemType.WEAPON:
            character.current_weapon = item
            return True

        if item.item_type == ItemType.FOOD:
            character.heal(item.health)
            character.backpack.remove_item(item)
            session.statistics.food_consumed += 1
            return True

        if item.item_type in (ItemType.ELIXIR, ItemType.SCROLL):
            attribute = self._attribute_for_item(item)
            if attribute is None:
                return False
            amount = self._amount_for_attribute(item, attribute)
            if amount <= 0:
                return False
            duration = None
            if item.item_type == ItemType.ELIXIR:
                duration = item.duration_turns or self.DEFAULT_ELIXIR_DURATION
                session.statistics.elixirs_used += 1
            else:
                session.statistics.scrolls_read += 1
            character.apply_attribute_change(attribute, amount, duration)
            character.backpack.remove_item(item)
            return True

        return False

    def unequip_weapon(
        self,
        session: GameSession,
        drop_position: Position | None = None,
    ) -> Item | None:
        weapon = session.character.current_weapon
        if weapon is None:
            return None
        session.character.current_weapon = None
        if drop_position is not None:
            session.character.backpack.remove_item(weapon)
            weapon.position = drop_position
            session.ground_items.append(weapon)
        return weapon

    def tick_player_turn(self, session: GameSession) -> None:
        session.character.tick_temporary_effects()

    def _attribute_for_item(self, item: Item) -> CharacterAttribute | None:
        subtype = item.subtype.value if isinstance(item.subtype, ItemAttribute) else item.subtype
        try:
            return CharacterAttribute(subtype)
        except (ValueError, TypeError):
            if item.max_health > 0:
                return CharacterAttribute.MAX_HEALTH
            if item.dexterity > 0:
                return CharacterAttribute.DEXTERITY
            if item.strength > 0:
                return CharacterAttribute.STRENGTH
            return None

    def _amount_for_attribute(
        self,
        item: Item,
        attribute: CharacterAttribute,
    ) -> int:
        if attribute == CharacterAttribute.MAX_HEALTH:
            return item.max_health
        if attribute == CharacterAttribute.DEXTERITY:
            return item.dexterity
        if attribute == CharacterAttribute.STRENGTH:
            return item.strength
        return 0
