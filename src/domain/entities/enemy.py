from dataclasses import dataclass
from enum import Enum

from .position import Position


class EnemyType(str, Enum):
    ZOMBIE = "zombie"
    VAMPIRE = "vampire"
    GHOST = "ghost"
    OGRE = "ogre"
    SNAKE_MAGE = "snake_mage"


@dataclass
class Enemy:
    enemy_type: EnemyType
    position: Position
    health: int
    dexterity: int
    strength: int
    hostility: int
