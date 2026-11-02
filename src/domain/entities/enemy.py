from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from .position import Position


class EnemyType(str, Enum):
    ZOMBIE = "zombie"
    VAMPIRE = "vampire"
    GHOST = "ghost"
    OGRE = "ogre"
    SNAKE_MAGE = "snake_mage"


@dataclass
class Enemy:
    BASE_STATS: ClassVar[dict[EnemyType, tuple[int, int, int, int]]] = {
        EnemyType.ZOMBIE: (14, 3, 4, 4),
        EnemyType.VAMPIRE: (16, 8, 5, 8),
        EnemyType.GHOST: (8, 9, 2, 9),
        EnemyType.OGRE: (24, 2, 10, 5),
        EnemyType.SNAKE_MAGE: (10, 12, 3, 10),
    }

    enemy_type: EnemyType
    position: Position
    health: int
    dexterity: int
    strength: int
    hostility: int
    max_health: int = 0
    is_visible: bool = True
    first_player_attack: bool = True
    resting_turns: int = 0
    guaranteed_next_hit: bool = False
    is_chasing: bool = False
    visibility_counter: int = 0
    diagonal_direction: Position = (1, 1)

    def __post_init__(self) -> None:
        if self.health < 1:
            raise ValueError("Enemy health must be positive")
        if self.max_health == 0:
            self.max_health = self.health
        if self.max_health < self.health:
            raise ValueError("Maximum health cannot be lower than current health")
        if min(self.dexterity, self.strength, self.hostility) < 0:
            raise ValueError("Enemy attributes cannot be negative")
        if self.enemy_type == EnemyType.GHOST:
            self.is_visible = False

    @classmethod
    def create(
        cls,
        enemy_type: EnemyType,
        position: Position,
        level_number: int = 1,
    ) -> Enemy:
        if level_number < 1:
            raise ValueError("Level number must be positive")
        health, dexterity, strength, hostility = cls.BASE_STATS[enemy_type]
        levels_beyond_first = level_number - 1
        health += levels_beyond_first * 2
        strength += levels_beyond_first // 3
        dexterity += levels_beyond_first // 4
        return cls(
            enemy_type=enemy_type,
            position=position,
            health=health,
            dexterity=dexterity,
            strength=strength,
            hostility=hostility,
            max_health=health,
            is_visible=enemy_type != EnemyType.GHOST,
        )

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Damage cannot be negative")
        actual_damage = min(self.health, amount)
        self.health -= actual_damage
        return actual_damage
