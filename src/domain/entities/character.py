from dataclasses import dataclass, field
from enum import Enum

from .backpack import Backpack
from .item import Item
from .position import Position


class CharacterAttribute(str, Enum):
    MAX_HEALTH = "max_health"
    DEXTERITY = "dexterity"
    STRENGTH = "strength"


@dataclass
class TemporaryEffect:
    attribute: CharacterAttribute
    amount: int
    turns_remaining: int


@dataclass
class Character:
    position: Position
    max_health: int
    health: int
    dexterity: int
    strength: int
    backpack: Backpack = field(default_factory=Backpack)
    current_weapon: Item | None = None
    temporary_effects: list[TemporaryEffect] = field(default_factory=list)
    sleep_turns: int = 0

    def __post_init__(self) -> None:
        if self.max_health < 1:
            raise ValueError("Maximum health must be positive")
        if self.health < 0:
            raise ValueError("Health cannot be negative")
        if self.dexterity < 0 or self.strength < 0:
            raise ValueError("Attributes cannot be negative")
        self.health = min(self.health, self.max_health)
        if self.current_weapon is not None and self.current_weapon not in self.backpack.items:
            if not self.backpack.add_item(self.current_weapon):
                raise ValueError("Current weapon does not fit in the backpack")

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    @property
    def attack_strength(self) -> int:
        weapon_bonus = self.current_weapon.strength if self.current_weapon else 0
        return max(1, self.strength + weapon_bonus)

    def move_to(self, position: Position) -> None:
        self.position = position

    def take_damage(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Damage cannot be negative")
        actual_damage = min(self.health, amount)
        self.health -= actual_damage
        return actual_damage

    def heal(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Healing amount cannot be negative")
        restored = min(amount, self.max_health - self.health)
        self.health += restored
        return restored

    def apply_attribute_change(
        self,
        attribute: CharacterAttribute,
        amount: int,
        duration_turns: int | None = None,
    ) -> None:
        if amount == 0:
            return
        if duration_turns is not None and duration_turns < 1:
            raise ValueError("Temporary effect duration must be positive")
        self._change_attribute(attribute, amount)
        if duration_turns is not None:
            self.temporary_effects.append(
                TemporaryEffect(attribute, amount, duration_turns)
            )

    def tick_temporary_effects(self) -> None:
        active_effects: list[TemporaryEffect] = []
        for effect in self.temporary_effects:
            effect.turns_remaining -= 1
            if effect.turns_remaining <= 0:
                self._change_attribute(effect.attribute, -effect.amount)
            else:
                active_effects.append(effect)
        self.temporary_effects = active_effects
        self.sleep_turns = max(0, self.sleep_turns - 1)

    def lose_max_health(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Health loss cannot be negative")
        self.max_health = max(1, self.max_health - amount)
        self.health = min(self.health, self.max_health)

    def _change_attribute(self, attribute: CharacterAttribute, amount: int) -> None:
        if attribute == CharacterAttribute.MAX_HEALTH:
            old_max_health = self.max_health
            self.max_health = max(1, self.max_health + amount)
            actual_change = self.max_health - old_max_health
            self.health += actual_change
            if self.health <= 0:
                self.health = 1
            self.health = min(self.health, self.max_health)
        elif attribute == CharacterAttribute.DEXTERITY:
            self.dexterity = max(0, self.dexterity + amount)
        elif attribute == CharacterAttribute.STRENGTH:
            self.strength = max(0, self.strength + amount)
