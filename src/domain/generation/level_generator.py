from random import Random

from ..entities.position import Position
from .corridor import Corridor
from .level import Level
from .room import Room


class LevelGenerator:
    GRID_ROWS = 3
    GRID_COLS = 3

    SECTION_WIDTH = 26
    SECTION_HEIGHT = 8 

    MIN_ROOM_WIDTH = 4
    MIN_ROOM_HEIGHT = 3
    PADDING = 2


    def __init__(self, rng: Random | None = None) -> None:
        self._rng = rng if rng is not None else Random()

    def generate(self, level_number: int) -> Level:
        rooms = self._generate_rooms()
        edges = self._generate_connected_edges()
        corridors = [self._carve_corridor(rooms[u], rooms[v]) for u, v in edges]

        start_room, exit_room = self._rng.sample(rooms, 2)
        start_position = self._random_point_in_room(start_room)
        exit_position = self._random_point_in_room(exit_room)

        return Level(
            level_number=level_number,
            rooms=rooms,
            corridors=corridors,
            start_position=start_position,
            exit_position=exit_position,
        )


    def _generate_rooms(self) -> list[Room]:
        rooms: list[Room] = []
        room_id = 0

        max_w = self.SECTION_WIDTH - self.PADDING * 2
        max_h = self.SECTION_HEIGHT - self.PADDING * 2 

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                sec_x = col * self.SECTION_WIDTH
                sec_y = row * self.SECTION_HEIGHT

                width = self._rng.randint(self.MIN_ROOM_WIDTH, max_w)
                height = self._rng.randint(self.MIN_ROOM_HEIGHT, max_h)

                x = sec_x + self.PADDING + self._rng.randint(0, max_w - width)
                y = sec_y + self.PADDING + self._rng.randint(0, max_h - height)

                rooms.append(Room(room_id=room_id, x=x, y=y, width=width, height=height))
                room_id += 1

        return rooms


    def _generate_connected_edges(self) -> list[tuple[int, int]]:
        adjacency: dict[int, list[int]] = {}

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                idx = row * self.GRID_COLS + col
                neighbors: list[int] = []

                if row > 0:
                    neighbors.append((row - 1) * self.GRID_COLS + col)
                if row < self.GRID_ROWS - 1:
                    neighbors.append((row + 1) * self.GRID_COLS + col)
                if col > 0:
                    neighbors.append(row * self.GRID_COLS + (col - 1))
                if col < self.GRID_COLS - 1:
                    neighbors.append(row * self.GRID_COLS + (col + 1))

                adjacency[idx] = neighbors

        visited: set[int] = set()
        edges: set[tuple[int, int]] = set()

        def dfs(current: int) -> None:
            visited.add(current)
            neighbors = list(adjacency[current])
            self._rng.shuffle(neighbors)

            for nxt in neighbors:
                if nxt not in visited:
                    edge = (min(current, nxt), max(current, nxt))
                    edges.add(edge)
                    dfs(nxt)

        start_node = self._rng.randint(0, self.GRID_ROWS * self.GRID_COLS - 1)
        dfs(start_node)

        all_edges = {
            (min(u, v), max(u, v))
            for u, nbrs in adjacency.items()
            for v in nbrs
        }

        remaining_edges = list(all_edges - edges)
        if remaining_edges:
            extra_count = self._rng.randint(1, min(3, len(remaining_edges)))
            for extra in self._rng.sample(remaining_edges, extra_count):
                edges.add(extra)

        return sorted(edges)


    def _carve_corridor(self, room_a: Room, room_b: Room) -> Corridor:
        col_a, row_a = room_a.room_id % self.GRID_COLS, room_a.room_id // self.GRID_COLS
        col_b, row_b = room_b.room_id % self.GRID_COLS, room_b.room_id // self.GRID_COLS

        tiles: set[Position] = set()

        if row_a == row_b:
            left, right = (room_a, room_b) if col_a < col_b else (room_b, room_a)
            start_x = left.x + left.width
            start_y = self._rng.randint(left.y, left.y + left.height - 1)
            end_x = right.x - 1
            end_y = self._rng.randint(right.y, right.y + right.height - 1)
            mid_x = (start_x + end_x) // 2

            for x in range(start_x, mid_x + 1):
                tiles.add((x, start_y))
            step_y = 1 if end_y >= start_y else -1
            for y in range(start_y, end_y + step_y, step_y):
                tiles.add((mid_x, y))
            for x in range(mid_x, end_x + 1):
                tiles.add((x, end_y))
        elif col_a == col_b:
            top, bottom = (room_a, room_b) if row_a < row_b else (room_b, room_a)
            start_x = self._rng.randint(top.x, top.x + top.width - 1)
            start_y = top.y + top.height
            end_x = self._rng.randint(bottom.x, bottom.x + bottom.width - 1)
            end_y = bottom.y - 1
            mid_y = (start_y + end_y) // 2

            for y in range(start_y, mid_y + 1):
                    tiles.add((start_x, y))
            step_x = 1 if end_x >= start_x else -1

            for x in range(start_x, end_x + step_x, step_x):
                tiles.add((x, mid_y))

            for y in range(mid_y, end_y + 1):
                tiles.add((end_x, y))

        return Corridor(tiles=tiles)


    def _random_point_in_room(self, room: Room) -> Position:
        x = self._rng.randint(room.x, room.x + room.width - 1)
        y = self._rng.randint(room.y, room.y + room.height - 1)

        return (x, y)