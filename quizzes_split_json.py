import json
import csv
import unicodedata
from pathlib import Path
from collections import defaultdict

# ===== 設定 =====
INPUT_TSV = "quizzes_data.tsv"
SONGS_DIR = Path("data/songs")
QUIZZES_DIR = Path("data/quizzes")
UNMATCHED_LOG = Path("data/unmatched_quizzes.tsv")

MAX_ARTISTS = 6

QUIZZES_DIR.mkdir(parents=True, exist_ok=True)

# ===== 正規化関数 =====
def normalize(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).lower().strip()

# ===== 楽曲インデックス構築 =====
# (song_normalized, artist_normalized) -> contentId
song_artist_index = {}

for path in SONGS_DIR.glob("*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    content_id = data.get("contentId")

    song_names = set()
    song_names.add(data.get("song", ""))
    for s in data.get("sub_song", []):
        song_names.add(s)

    artist_names = set()
    for a in data.get("artist", []):
        artist_names.add(a)
    for a in data.get("sub_artist", []):
        artist_names.add(a)

    for song in song_names:
        ns = normalize(song)
        if not ns:
            continue
        for artist in artist_names:
            na = normalize(artist)
            if not na:
                continue
            song_artist_index[(ns, na)] = content_id

# ===== クイズデータ処理 =====
quizzes = {}
unmatched_logs = []

with open(INPUT_TSV, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")

    for row_no, row in enumerate(reader, start=1):
        if not row:
            continue

        song_raw = row[1]
        song_n = normalize(song_raw)

        artists_raw = row[2:2 + MAX_ARTISTS]
        artists_n = [normalize(a) for a in artists_raw if a.strip()]

        idx = 2 + MAX_ARTISTS
        quiz_no = int(row[idx])
        group = row[idx + 1]
        date = row[idx + 2].replace("/", "-")

        answers_raw = row[idx + 3:]

        # --- contentId 検索（高速） ---
        content_id = None
        for a in artists_n:
            key = (song_n, a)
            if key in song_artist_index:
                content_id = song_artist_index[key]
                break

        if not content_id:
            unmatched_logs.append({
                "row": row_no,
                "song": song_raw,
                "artists": artists_raw
            })
            continue

        quiz_key = f"{quiz_no}{group}"

        if quiz_key not in quizzes:
            quizzes[quiz_key] = {
                "quiz_no": quiz_no,
                "group": group,
                "date": date,
                "songs": []
            }

        order = len(quizzes[quiz_key]["songs"]) + 1

        answers = []
        for i in range(0, len(answers_raw), 2):
            user = answers_raw[i].strip() if i < len(answers_raw) else ""
            result = answers_raw[i + 1].strip() if i + 1 < len(answers_raw) else ""
            
            if not user and not result:
                continue
            
            answers.append({
                "user": user,
                "result": result
            })

        quizzes[quiz_key]["songs"].append({
            "order": order,
            "contentId": content_id,
            "answers": answers
        })

# ===== JSON出力 =====
for key, data in quizzes.items():
    out_path = QUIZZES_DIR / f"quiz_{key}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== ログ出力 =====
if unmatched_logs:
    with open(UNMATCHED_LOG, "w", encoding="utf-8", newline="") as f:
        # ヘッダー
        headers = ["row", "song"] + [f"artists.{i}" for i in range(MAX_ARTISTS)]
        f.write("\t".join(headers) + "\n")

        for u in unmatched_logs:
            row = [str(u["row"]), u["song"]]
            artists = u["artists"][:MAX_ARTISTS]
            artists += [""] * (MAX_ARTISTS - len(artists))
            row.extend(artists)
            f.write("\t".join(row) + "\n")
