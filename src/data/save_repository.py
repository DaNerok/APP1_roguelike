import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from domain.entities.backpack import Backpack
from domain.entities.character import Character, CharacterAttribute, TemporaryEffect
from domain.entities.enemy import Enemy, EnemyType
from domain.entities.game_session import GameSession, RunStatistics
from domain.entities.item import Item, ItemAttribute, ItemType
from domain.entities.position import Position
from domain.generation.corridor import Corridor
from domain.generation.level import Level
from domain.generation.room import Room


class SaveRepository:
    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path = "save.json") -> None:
        self.path = Path(path)

    def save(self, session: GameSession) -> None:
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "session": self._session_to_data(session),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)

    def load(self) -> GameSession | None:
        if not self.path.exists():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            raise ValueError("Unsupported save file version")
        return self._session_from_data(payload["session"])

    def _session_to_data(self, session: GameSession) -> dict[str, Any]:
        character = session.character
        current_weapon_index = next(
            (
                index
                for index, item in enumerate(character.backpack.items)
                if item is character.current_weapon
            ),
            None,
        )
        return {
            "character": {
                "position": list(character.position),
                "max_health": character.max_health,
                "health": character.health,
                "dexterity": character.dexterity,
                "strength": character.strength,
                "backpack": [self._item_to_data(item) for item in character.backpack.items],
                "capacity_per_type": character.backpack.capacity_per_type,
                "current_weapon_index": current_weapon_index,
                "temporary_effects": [
                    {
                        "attribute": effect.attribute.value,
                        "amount": effect.amount,
                        "turns_remaining": effect.turns_remaining,
                    }
                    for effect in character.temporary_effects
                ],
                "sleep_turns": character.sleep_turns,
            },
            "level": {
                "level_number": session.level.level_number,
                "rooms": [
                    {
                        "room_id": room.room_id,
                        "x": room.x,
                        "y": room.y,
                        "width": room.width,
                        "height": room.height,
                    }
                    for room in session.level.rooms
                ],
                "corridors": [
                    {"tiles": [list(position) for position in sorted(corridor.tiles)]}
                    for corridor in session.level.corridors
                ],
                "start_position": list(session.level.start_position),
                "exit_position": list(session.level.exit_position),
            },
            "level_number": session.level_number,
            "enemies": [self._enemy_to_data(enemy) for enemy in session.enemies],
            "ground_items": [self._item_to_data(item) for item in session.ground_items],
            "statistics": asdict(session.statistics),
            "is_game_over": session.is_game_over,
            "is_completed": session.is_completed,
        }

    def _session_from_data(self, data: dict[str, Any]) -> GameSession:
        character_data = data["character"]
        backpack = Backpack(
            items=[self._item_from_data(item) for item in character_data["backpack"]],
            capacity_per_type=character_data["capacity_per_type"],
        )
        character = Character(
            position=self._position(character_data["position"]),
            max_health=character_data["max_health"],
            health=character_data["health"],
            dexterity=character_data["dexterity"],
            strength=character_data["strength"],
            backpack=backpack,
            temporary_effects=[
                TemporaryEffect(
                    attribute=CharacterAttribute(effect["attribute"]),
                    amount=effect["amount"],
                    turns_remaining=effect["turns_remaining"],
                )
                for effect in character_data["temporary_effects"]
            ],
            sleep_turns=character_data["sleep_turns"],
        )
        weapon_index = character_data["current_weapon_index"]
        if weapon_index is not None:
            character.current_weapon = backpack.items[weapon_index]

        level_data = data["level"]
        level = Level(
            level_number=level_data["level_number"],
            rooms=[Room(**room) for room in level_data["rooms"]],
            corridors=[
                Corridor(tiles={self._position(position) for position in corridor["tiles"]})
                for corridor in level_data["corridors"]
            ],
            start_position=self._position(level_data["start_position"]),
            exit_position=self._position(level_data["exit_position"]),
        )
        return GameSession(
            character=character,
            level=level,
            level_number=data["level_number"],
            enemies=[self._enemy_from_data(enemy) for enemy in data["enemies"]],
            ground_items=[self._item_from_data(item) for item in data["ground_items"]],
            statistics=RunStatistics(**data["statistics"]),
            is_game_over=data["is_game_over"],
            is_completed=data["is_completed"],
        )

    def _item_to_data(self, item: Item) -> dict[str, Any]:
        return {
            "item_type": item.item_type.value,
            "subtype": item.subtype.value if isinstance(item.subtype, ItemAttribute) else item.subtype,
            "health": item.health,
            "max_health": item.max_health,
            "dexterity": item.dexterity,
            "strength": item.strength,
            "value": item.value,
            "duration_turns": item.duration_turns,
            "quantity": item.quantity,
            "position": list(item.position) if item.position is not None else None,
        }

    def _item_from_data(self, data: dict[str, Any]) -> Item:
        subtype = data["subtype"]
        if subtype is not None:
            try:
                subtype = ItemAttribute(subtype)
            except ValueError:
                pass
        position = data["position"]
        return Item(
            item_type=ItemType(data["item_type"]),
            subtype=subtype,
            health=data["health"],
            max_health=data["max_health"],
            dexterity=data["dexterity"],
            strength=data["strength"],
            value=data["value"],
            duration_turns=data["duration_turns"],
            quantity=data["quantity"],
            position=self._position(position) if position is not None else None,
        )

    def _enemy_to_data(self, enemy: Enemy) -> dict[str, Any]:
        return {
            "enemy_type": enemy.enemy_type.value,
            "position": list(enemy.position),
            "health": enemy.health,
            "max_health": enemy.max_health,
            "dexterity": enemy.dexterity,
            "strength": enemy.strength,
            "hostility": enemy.hostility,
            "is_visible": enemy.is_visible,
            "first_player_attack": enemy.first_player_attack,
            "resting_turns": enemy.resting_turns,
            "guaranteed_next_hit": enemy.guaranteed_next_hit,
            "is_chasing": enemy.is_chasing,
            "visibility_counter": enemy.visibility_counter,
            "diagonal_direction": list(enemy.diagonal_direction),
        }

    def _enemy_from_data(self, data: dict[str, Any]) -> Enemy:
        enemy = Enemy(
            enemy_type=EnemyType(data["enemy_type"]),
            position=self._position(data["position"]),
            health=data["health"],
            max_health=data["max_health"],
            dexterity=data["dexterity"],
            strength=data["strength"],
            hostility=data["hostility"],
            first_player_attack=data["first_player_attack"],
            resting_turns=data["resting_turns"],
            guaranteed_next_hit=data["guaranteed_next_hit"],
            is_chasing=data["is_chasing"],
            visibility_counter=data["visibility_counter"],
            diagonal_direction=self._position(data["diagonal_direction"]),
        )
        enemy.is_visible = data["is_visible"]
        return enemy

    def _position(self, value: list[int]) -> Position:
        return int(value[0]), int(value[1])
