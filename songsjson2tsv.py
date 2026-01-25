import json
import csv
from pathlib import Path

SONGS_DIR = Path("data/songs")
OUTPUT_TSV = "songs_data.tsv"

json_files = list(SONGS_DIR.glob("*.json"))
rows = []

max_sub_song = 0
max_artist = 0
max_sub_artist = 0
max_tags = 0

# ===== 1周目：読み込み & 最大長取得 =====
for path in json_files:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    rows.append(data)

    max_sub_song = max(max_sub_song, len(data.get("sub_song", [])))
    max_artist = max(max_artist, len(data.get("artist", [])))
    max_sub_artist = max(max_sub_artist, len(data.get("sub_artist", [])))
    max_tags = max(max_tags, len(data.get("tags", [])))

# ===== ヘッダ構築（順序固定） =====
headers = []

# 1. song
headers.append("song")

# 2. sub_song.*
headers.extend([f"sub_song.{i}" for i in range(max_sub_song)])

# 3. artist.*
headers.extend([f"artist.{i}" for i in range(max_artist)])

# 4. sub_artist.*
headers.extend([f"sub_artist.{i}" for i in range(max_sub_artist)])

# 5. contentId, title
headers.extend(["contentId", "title"])

# ===== 残りのキー（任意） =====
reserved = {
    "song", "sub_song", "artist", "sub_artist",
    "contentId", "title"
}

other_keys = set()
for r in rows:
    other_keys |= set(r.keys())

other_keys -= reserved | {"tags"}

# tags は最後にまとめて出す
headers.extend(sorted(other_keys))
headers.extend([f"tags.{i}" for i in range(max_tags)])

# ===== TSV出力 =====
with open(OUTPUT_TSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(headers)

    for data in rows:
        row = []

        for key in headers:
            if key == "song":
                row.append(data.get("song", ""))

            elif key.startswith("sub_song."):
                idx = int(key.split(".")[1])
                row.append(
                    data.get("sub_song", [])[idx]
                    if idx < len(data.get("sub_song", [])) else ""
                )

            elif key.startswith("artist."):
                idx = int(key.split(".")[1])
                row.append(
                    data.get("artist", [])[idx]
                    if idx < len(data.get("artist", [])) else ""
                )

            elif key.startswith("sub_artist."):
                idx = int(key.split(".")[1])
                row.append(
                    data.get("sub_artist", [])[idx]
                    if idx < len(data.get("sub_artist", [])) else ""
                )

            elif key.startswith("tags."):
                idx = int(key.split(".")[1])
                row.append(
                    data.get("tags", [])[idx]
                    if idx < len(data.get("tags", [])) else ""
                )

            else:
                row.append(data.get(key, ""))

        writer.writerow(row)

print(f"written: {OUTPUT_TSV}")
