import json
from pathlib import Path


class LeaderboardRepository:

    def __init__(self, path: Path):
        self.path = path

    def save_attempt(self, stats: dict) -> None:
        leaderboard = self.get_leaderboard()
        leaderboard.append(stats)
        
        leaderboard.sort(key=lambda x: x.get("treasures", 0), reverse=True)
        
        temp_path = self.path.with_suffix('.tmp')
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(leaderboard, file, indent=4)
            temp_path.replace(self.path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Ошибка при сохранении рекордов: {e}")

    def get_leaderboard(self) -> list[dict]:
        if not self.path.exists():
            return []
            
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Файл рекордов поврежден, начинаем с чистой таблицы.")
            return []