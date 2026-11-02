from dataclasses import dataclass
from random import Random

from ..entities.character import Character
from ..entities.enemy import Enemy
from ..entities.game_session import GameSession
from ..entities.item import Item
from ..entities.position import Position
from .combat import AttackResult, CombatRules
from .enemy_ai import EnemyAIRules
from .interactions import InteractionRules
from .population import LevelPopulationRules
from ..generation.level import Level
from ..generation.level_generator import LevelGenerator


@dataclass(frozen=True)
class TurnResult:
    action_succeeded: bool
    player_was_asleep: bool = False
    attack: AttackResult | None = None
    reached_exit: bool = False
    level_advanced: bool = False


class TurnRules:
    FINAL_LEVEL = 21

    def __init__(
        self,
        rng: Random | None = None,
        level_generator: LevelGenerator | None = None,
        population: LevelPopulationRules | None = None,
    ) -> None:
        self.rng = rng or Random()
        self.level_generator = level_generator
        self.population = population or LevelPopulationRules(self.rng)
        self.combat = CombatRules(rng=self.rng)
        self.interactions = InteractionRules()
        self.enemy_ai = EnemyAIRules(self.combat, self.rng)

    def start_session(self, character: Character, level: Level) -> GameSession:
        character.move_to(level.start_position)
        enemies, ground_items = self.population.populate(level)
        return GameSession(
            character=character,
            level=level,
            level_number=level.level_number,
            enemies=enemies,
            ground_items=ground_items,
        )

    def move(self, session: GameSession, position: Position) -> TurnResult:
        if session.is_game_over:
            return TurnResult(action_succeeded=False)
        if session.character.sleep_turns > 0:
            self._finish_turn(session)
            return TurnResult(action_succeeded=False, player_was_asleep=True)

        current = session.character.position
        is_adjacent = abs(position[0] - current[0]) + abs(position[1] - current[1]) == 1
        enemy = self._enemy_at(session, position) if is_adjacent else None
        if enemy is not None:
            attack = self.combat.character_attack(session, enemy)
            self._finish_turn(session)
            return TurnResult(action_succeeded=True, attack=attack)

        moved = self.interactions.move_character(session, position)
        reached_exit = moved and position == session.level.exit_position
        level_advanced = False
        if reached_exit and session.level_number >= self.FINAL_LEVEL:
            session.finish(completed=True)
        elif reached_exit and self.level_generator is not None:
            next_level = self.level_generator.generate(session.level_number + 1)
            session.advance_to_level(next_level)
            session.enemies, session.ground_items = self.population.populate(next_level)
            level_advanced = True
        self._finish_turn(session)
        return TurnResult(
            action_succeeded=moved,
            reached_exit=reached_exit,
            level_advanced=level_advanced,
        )

    def use_item(self, session: GameSession, item: Item) -> TurnResult:
        if session.is_game_over:
            return TurnResult(action_succeeded=False)
        if session.character.sleep_turns > 0:
            self._finish_turn(session)
            return TurnResult(action_succeeded=False, player_was_asleep=True)
        succeeded = self.interactions.use_item(session, item)
        self._finish_turn(session)
        return TurnResult(action_succeeded=succeeded)

    def wait(self, session: GameSession) -> TurnResult:
        if session.is_game_over:
            return TurnResult(action_succeeded=False)
        self._finish_turn(session)
        return TurnResult(action_succeeded=True)

    def _finish_turn(self, session: GameSession) -> None:
        if session.is_game_over:
            return
        for enemy in tuple(session.enemies):
            if not session.character.is_alive:
                break
            self.enemy_ai.take_turn(session, enemy)
        session.character.tick_temporary_effects()
        if not session.character.is_alive:
            session.finish()

    def _enemy_at(self, session: GameSession, position: Position) -> Enemy | None:
        return next(
            (
                enemy
                for enemy in session.enemies
                if enemy.is_alive and enemy.position == position
            ),
            None,
        )
