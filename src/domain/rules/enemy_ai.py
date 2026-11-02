from collections import deque
from random import Random

from ..entities.enemy import Enemy, EnemyType
from ..entities.game_session import GameSession
from ..entities.position import Position
from .combat import AttackResult, CombatRules


class EnemyAIRules:
    CARDINAL_STEPS: tuple[Position, ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))
    DIAGONAL_STEPS: tuple[Position, ...] = ((1, 1), (1, -1), (-1, 1), (-1, -1))

    def __init__(self, combat: CombatRules, rng: Random | None = None) -> None:
        self.combat = combat
        self.rng = rng or Random()

    def take_turn(self, session: GameSession, enemy: Enemy) -> AttackResult | None:
        if not enemy.is_alive or not session.character.is_alive:
            return None

        player_position = session.character.position
        distance = self._manhattan_distance(enemy.position, player_position)
        if distance <= enemy.hostility:
            enemy.is_chasing = True
        if enemy.is_chasing:
            enemy.is_visible = True
            if distance == 1:
                return self.combat.enemy_attack(session, enemy)
            next_position = self._shortest_step(session, enemy)
            if next_position is not None:
                enemy.position = next_position
                return None

        self._wander(session, enemy)
        return None

    def _shortest_step(self, session: GameSession, enemy: Enemy) -> Position | None:
        start = enemy.position
        target = session.character.position
        occupied = {
            other.position
            for other in session.enemies
            if other is not enemy and other.is_alive
        }
        queue = deque([start])
        previous: dict[Position, Position | None] = {start: None}
        goal: Position | None = None

        while queue:
            current = queue.popleft()
            if self._manhattan_distance(current, target) == 1:
                goal = current
                break
            for dx, dy in self.CARDINAL_STEPS:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in previous or neighbor in occupied or neighbor == target:
                    continue
                if not session.level.is_walkable(neighbor):
                    continue
                previous[neighbor] = current
                queue.append(neighbor)

        if goal is None or goal == start:
            return None
        step = goal
        while previous[step] != start:
            parent = previous[step]
            if parent is None:
                return None
            step = parent
        return step

    def _wander(self, session: GameSession, enemy: Enemy) -> None:
        if enemy.enemy_type == EnemyType.GHOST:
            self._ghost_move(session, enemy)
        elif enemy.enemy_type == EnemyType.OGRE:
            self._ogre_move(session, enemy)
        elif enemy.enemy_type == EnemyType.SNAKE_MAGE:
            self._snake_move(session, enemy)
        else:
            self._random_adjacent_move(session, enemy)

    def _ghost_move(self, session: GameSession, enemy: Enemy) -> None:
        enemy.visibility_counter = (enemy.visibility_counter + 1) % 4
        enemy.is_visible = enemy.visibility_counter in (0, 1)
        room = session.level.room_at(enemy.position)
        if room is None:
            self._random_adjacent_move(session, enemy)
            return
        choices = self._available(session, enemy, room.tiles)
        if choices:
            enemy.position = self.rng.choice(choices)

    def _ogre_move(self, session: GameSession, enemy: Enemy) -> None:
        room = session.level.room_at(enemy.position)
        if room is None:
            self._random_adjacent_move(session, enemy)
            return
        allowed = room.tiles
        for _ in range(2):
            choices = self._available_neighbors(session, enemy, allowed)
            if not choices:
                break
            enemy.position = self.rng.choice(choices)

    def _snake_move(self, session: GameSession, enemy: Enemy) -> None:
        room = session.level.room_at(enemy.position)
        allowed = room.tiles if room is not None else None
        dx, dy = enemy.diagonal_direction
        enemy.diagonal_direction = (-dx, -dy)
        target = (enemy.position[0] + dx, enemy.position[1] + dy)
        if self._is_available(session, enemy, target, allowed):
            enemy.position = target
            return
        choices = self._available_neighbors(session, enemy, allowed, diagonal=True)
        if choices:
            enemy.position = self.rng.choice(choices)

    def _random_adjacent_move(self, session: GameSession, enemy: Enemy) -> None:
        room = session.level.room_at(enemy.position)
        allowed = room.tiles if room is not None else None
        choices = self._available_neighbors(session, enemy, allowed)
        if choices:
            enemy.position = self.rng.choice(choices)

    def _available_neighbors(
        self,
        session: GameSession,
        enemy: Enemy,
        allowed: set[Position] | None,
        diagonal: bool = False,
    ) -> list[Position]:
        steps = self.DIAGONAL_STEPS if diagonal else self.CARDINAL_STEPS
        positions = (
            (enemy.position[0] + dx, enemy.position[1] + dy)
            for dx, dy in steps
        )
        return [
            position
            for position in positions
            if self._is_available(
                session,
                enemy,
                position,
                allowed,
            )
        ]

    def _available(
        self,
        session: GameSession,
        enemy: Enemy,
        positions: set[Position],
    ) -> list[Position]:
        return [
            position
            for position in positions
            if position != enemy.position
            and self._is_available(session, enemy, position, positions)
        ]

    def _is_available(
        self,
        session: GameSession,
        enemy: Enemy,
        position: Position,
        allowed: set[Position] | None,
    ) -> bool:
        if position == session.character.position:
            return False
        if allowed is not None and position not in allowed:
            return False
        if not session.level.is_walkable(position):
            return False
        return not any(
            other is not enemy and other.is_alive and other.position == position
            for other in session.enemies
        )

    def _manhattan_distance(self, first: Position, second: Position) -> int:
        return abs(first[0] - second[0]) + abs(first[1] - second[1])
