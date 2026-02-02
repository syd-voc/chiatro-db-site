import json
from pathlib import Path

quiz_dir = Path("data/quizzes")
song_dir = Path("data/songs")
user_dir = Path("data/users")

stats = {
    "quizCount": len(list(quiz_dir.glob("quiz_*.json"))),
    "songCount": len(list(song_dir.glob("*.json"))),
    "userCount": len(list(user_dir.glob("*.json"))),
}

with open("data/stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print("stats.json generated")
