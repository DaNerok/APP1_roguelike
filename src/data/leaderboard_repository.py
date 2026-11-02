import json
from dataclasses import asdict
from pathlib import Path

from domain.entities.game_session import RunStatistics


class LeaderboardRepository:
    def __init__(self, path: str | Path = "leaderboard.json") -> None:
        self.path = Path(path)

    def load(self) -> list[RunStatistics]:
        if not self.path.exists():
            return []
        entries = json.loads(self.path.read_text(encoding="utf-8"))
        return [RunStatistics(**entry) for entry in entries]

    def record(self, statistics: RunStatistics) -> list[RunStatistics]:
        entries = self.load()
        entries.append(statistics)
        entries.sort(
            key=lambda entry: entry.treasure_collected,
            reverse=True,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps([asdict(entry) for entry in entries], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)
        return entries
