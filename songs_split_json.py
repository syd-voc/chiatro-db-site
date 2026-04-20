import csv
import json
from pathlib import Path

INPUT_TSV = "songs_data.tsv"

BASE_DIR = Path(__file__).resolve().parent
SONGS_DIR = BASE_DIR / "data" / "songs"
ANOTHER_SONGS_DIR = BASE_DIR / "data" / "another_songs"

SONGS_DIR.mkdir(parents=True, exist_ok=True)
ANOTHER_SONGS_DIR.mkdir(parents=True, exist_ok=True)

with open(INPUT_TSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        content_id = row.get("contentId")
        if not content_id:
            continue

        data = {}
        artist = []
        sub_artist = []
        sub_song = []
        tags = []

        for key, value in row.items():
            if not value:
                continue

            if key == "song":
                data["song"] = value

            elif key.startswith("sub_song."):
                sub_song.append(value)

            elif key.startswith("artist."):
                artist.append(value)

            elif key.startswith("sub_artist."):
                sub_artist.append(value)

            elif key.startswith("tags."):
                tags.append(value)

            else:
                data[key] = value

        # 配列は存在する場合のみ入れる
        if artist:
            data["artist"] = artist
        if sub_artist:
            data["sub_artist"] = sub_artist
        if sub_song:
            data["sub_song"] = sub_song
        if tags:
            data["tags"] = tags

        # ===== 出力先分岐 =====
        if data.get("original"):
            output_dir = ANOTHER_SONGS_DIR
        else:
            output_dir = SONGS_DIR
            
        output_path = output_dir / f"{content_id}.json"

        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)