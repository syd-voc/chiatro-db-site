import json
from pathlib import Path

# data/quizzes/quiz_*.json を対象
for json_file in Path("data/quizzes").glob("quiz_*.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # user を重複なしで収集
        participants = set()

        for song in data.get("songs", []):
            for answer in song.get("answers", []):
                user = answer.get("user")
                if user:
                    participants.add(user)

        # participants を追加（名前順にソート）
        data["participants"] = sorted(participants)

        # 上書き保存
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"更新完了: {json_file}")

    except Exception as e:
        print(f"エラー: {json_file} -> {e}")