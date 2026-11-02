from dataclasses import dataclass
from random import Random

from ..entities.character import Character
from ..entities.enemy import Enemy, EnemyType
from ..entities.game_session import GameSession
from ..entities.item import Item, ItemType


@dataclass(frozen=True)
class AttackResult:
    hit: bool
    damage: int = 0
    target_defeated: bool = False
    treasure_awarded: int = 0
    special_effect: str | None = None


class CombatRules:
    def __init__(
        self,
        rng: Random | None = None,
        hit_base_percent: int = 50,
        hit_percent_per_dexterity: int = 5,
        minimum_hit_percent: int = 5,
        maximum_hit_percent: int = 95,
        snake_sleep_chance: float = 0.25,
    ) -> None:
        if not 0 <= minimum_hit_percent <= maximum_hit_percent <= 100:
            raise ValueError("Hit chance limits must be between 0 and 100")
        if not 0 <= snake_sleep_chance <= 1:
            raise ValueError("Sleep chance must be between 0 and 1")
        self.rng = rng or Random()
        self.hit_base_percent = hit_base_percent
        self.hit_percent_per_dexterity = hit_percent_per_dexterity
        self.minimum_hit_percent = minimum_hit_percent
        self.maximum_hit_percent = maximum_hit_percent
        self.snake_sleep_chance = snake_sleep_chance

    def hit_chance(self, attacker: Character | Enemy, target: Character | Enemy) -> int:
        chance = self.hit_base_percent + (
            attacker.dexterity - target.dexterity
        ) * self.hit_percent_per_dexterity
        return max(self.minimum_hit_percent, min(self.maximum_hit_percent, chance))

    def character_attack(self, session: GameSession, enemy: Enemy) -> AttackResult:
        character = session.character
        if not character.is_alive or not enemy.is_alive:
            return AttackResult(hit=False)

        if enemy.enemy_type == EnemyType.GHOST:
            enemy.is_visible = True
        enemy.is_chasing = True

        session.statistics.attacks_made += 1
        if enemy.enemy_type == EnemyType.VAMPIRE and enemy.first_player_attack:
            enemy.first_player_attack = False
            return AttackResult(hit=False, special_effect="vampire_first_attack_misses")

        enemy.first_player_attack = False
        if not self._roll_hit(character, enemy):
            return AttackResult(hit=False)

        damage = self.rng.randint(1, character.attack_strength)
        actual_damage = enemy.take_damage(damage)
        if enemy.is_alive:
            return AttackResult(hit=True, damage=actual_damage)

        reward = self._treasure_reward(enemy)
        session.enemies.remove(enemy)
        session.statistics.enemies_defeated += 1
        session.statistics.treasure_collected += reward
        session.character.backpack.add_item(
            Item(item_type=ItemType.TREASURE, value=reward)
        )
        return AttackResult(
            hit=True,
            damage=actual_damage,
            target_defeated=True,
            treasure_awarded=reward,
        )

    def enemy_attack(self, session: GameSession, enemy: Enemy) -> AttackResult:
        character = session.character
        if not character.is_alive or not enemy.is_alive:
            return AttackResult(hit=False)

        if enemy.resting_turns > 0:
            enemy.resting_turns -= 1
            return AttackResult(hit=False, special_effect="enemy_resting")

        guaranteed_hit = enemy.guaranteed_next_hit
        enemy.guaranteed_next_hit = False
        if guaranteed_hit or self._roll_hit(enemy, character):
            damage = self.rng.randint(1, max(1, enemy.strength))
            actual_damage = character.take_damage(damage)
            session.statistics.hits_taken += 1
            effect: str | None = None

            if enemy.enemy_type == EnemyType.VAMPIRE:
                health_stolen = max(1, enemy.strength // 4)
                character.lose_max_health(health_stolen)
                effect = "maximum_health_stolen"
            elif (
                enemy.enemy_type == EnemyType.SNAKE_MAGE
                and self.rng.random() < self.snake_sleep_chance
            ):
                character.sleep_turns = max(character.sleep_turns, 1)
                effect = "character_sleeps"

            enemy.resting_turns = 1 if enemy.enemy_type == EnemyType.OGRE else 0
            if enemy.enemy_type == EnemyType.OGRE:
                enemy.guaranteed_next_hit = True
            return AttackResult(
                hit=True,
                damage=actual_damage,
                target_defeated=not character.is_alive,
                special_effect=effect,
            )

        enemy.resting_turns = 1 if enemy.enemy_type == EnemyType.OGRE else 0
        if enemy.enemy_type == EnemyType.OGRE:
            enemy.guaranteed_next_hit = True
        return AttackResult(hit=False)

    def _roll_hit(self, attacker: Character | Enemy, target: Character | Enemy) -> bool:
        return self.rng.randrange(100) < self.hit_chance(attacker, target)

    def _treasure_reward(self, enemy: Enemy) -> int:
        upper_bound = max(
            1,
            (enemy.max_health + enemy.dexterity + enemy.strength + enemy.hostility) // 4,
        )
        return self.rng.randint(1, upper_bound)
