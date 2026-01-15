import csv
import json
from pathlib import Path
from datetime import datetime

INPUT_TSV = "songs_data.tsv"
OUTPUT_DIR = Path("data/songs")
LOG_FILE = OUTPUT_DIR / "diff_log.tsv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def write_log(rows):
    """ rows: list[list[str]] """
    is_new = not LOG_FILE.exists()
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        if is_new:
            writer.writerow(["timestamp", "contentId", "field", "base_value", "new_value"])
        writer.writerows(rows)

with open(INPUT_TSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        content_id = row.get("contentId")
        if not content_id:
            continue

        timestamp = datetime.now().isoformat(timespec="seconds")

        song = row.get("song")

        artists = [
            v for k, v in row.items()
            if k.startswith("artist.") and v
        ]

        tags = [
            v for k, v in row.items()
            if k.startswith("tags.") and v
        ]

        json_path = OUTPUT_DIR / f"{content_id}.json"
        log_rows = []

        # ===== 新規 =====
        if not json_path.exists():
            data = {
                k: v for k, v in row.items()
                if v and not (
                    k.startswith("artist.") or k.startswith("tags.")
                )
            }
            data["song"] = song
            data["artist"] = artists
            data["tags"] = tags
            save_json(json_path, data)
            continue

        # ===== 既存あり =====
        data = load_json(json_path)

        # --- song 差分 ---
        if song and song != data.get("song"):
            data.setdefault("sub_song", [])
            if song not in data["sub_song"]:
                data["sub_song"].append(song)
                log_rows.append([
                    timestamp,
                    content_id,
                    "sub_song",
                    data.get("song"),
                    song
                ])

        # --- artist 差分 ---
        base_artists = set(data.get("artist", []))
        diff_artists = [a for a in artists if a not in base_artists]

        if diff_artists:
            data.setdefault("sub_artist", [])
            for a in diff_artists:
                if a not in data["sub_artist"]:
                    data["sub_artist"].append(a)
                    log_rows.append([
                        timestamp,
                        content_id,
                        "sub_artist",
                        ",".join(sorted(base_artists)),
                        a
                    ])

        save_json(json_path, data)

        if log_rows:
            write_log(log_rows)
