import json
import os
import time

from config import PAUSE_FILE_PATH, PROGRESS_FILE_PATH


class ProgressTracker:
    def __init__(self, total: int):
        self.total = total
        self.done = 0
        self.started_at = time.time()
        self._recent_times: list[float] = []
        self._save()

    def update(self, card_id, card_name: str, elapsed_seconds: float):
        self.done += 1
        self._recent_times.append(elapsed_seconds)
        if len(self._recent_times) > 10:
            self._recent_times.pop(0)
        self._save(card_id, card_name)

    def _save(self, current_id=None, current_name=None):
        remaining = self.total - self.done
        avg = sum(self._recent_times) / len(self._recent_times) if self._recent_times else None
        eta = int(avg * remaining) if avg is not None else None
        data = {
            "total": self.total,
            "done": self.done,
            "percentage": round(self.done / self.total * 100, 1) if self.total else 0,
            "current_id": current_id,
            "current_name": current_name,
            "eta_seconds": eta,
            "paused": self.is_paused(),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(PROGRESS_FILE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def is_paused() -> bool:
        return os.path.exists(PAUSE_FILE_PATH)

    @staticmethod
    def pause():
        open(PAUSE_FILE_PATH, "w").close()

    @staticmethod
    def resume():
        if os.path.exists(PAUSE_FILE_PATH):
            os.remove(PAUSE_FILE_PATH)
