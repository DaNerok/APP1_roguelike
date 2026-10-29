import json
from pathlib import Path

from ..domain.entities.game_session import GameSession
from ..domain.generation.level import Level
from ..domain.generation.room import Room
from ..domain.generation.corridor import Corridor


def _level_to_dict(level: Level) -> dict:
    return {
        "level_number": level.level_number,
        "rooms": [
            {"room_id": r.room_id, "x": r.x, "y": r.y, "width": r.width, "height": r.height}
            for r in level.rooms
        ],
        "corridors": [
            {"tiles": [list(pos) for pos in sorted(c.tiles)]}
            for c in level.corridors
        ],
        "start_position": list(level.start_position),
        "exit_position": list(level.exit_position)
    }


def _level_from_dict(data: dict) -> Level:
    rooms = [Room(**r_data) for r_data in data["rooms"]]
    corridors = [
        Corridor(tiles={tuple(pos) for pos in c_data["tiles"]})
        for c_data in data["corridors"]
    ]
    return Level(
        level_number=data["level_number"],
        rooms=rooms,
        corridors=corridors,
        start_position=tuple(data["start_position"]),
        exit_position=tuple(data["exit_position"])
    )


def session_to_dict(session: GameSession) -> dict:
    return {
        "level_number": session.level_number,
        "is_game_over": session.is_game_over,
        "level": _level_to_dict(session.level),
        "character": None  # Заглушка
    }


def session_from_dict(data: dict) -> GameSession:
    return GameSession(
        level_number=data["level_number"],
        is_game_over=data["is_game_over"],
        level=_level_from_dict(data["level"]),
        character=None  # Заглушка
    )


class SaveRepository:

    def __init__(self, path: Path):
        self.path = path

    def save(self, session: GameSession) -> None:
        data = session_to_dict(session)
        temp_path = self.path.with_suffix('.tmp')
        
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            temp_path.replace(self.path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Ошибка при сохранении игры: {e}")

    def load(self) -> GameSession | None:
        if not self.path.exists():
            return None
            
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return session_from_dict(data)
        except json.JSONDecodeError:
            print("Сохранение повреждено или имеет неверный формат.")
            return None