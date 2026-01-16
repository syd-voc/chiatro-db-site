import json
from pathlib import Path

# ===== パス設定 =====
SONGS_DIR = Path("data/songs")
SNAPSHOT_DIR = Path("data/snapshot")
LOG_FILE = Path("data/missing_songs.log")

# ===== snapshot 側をすべて読み込み、contentId で統合 =====
snapshot_by_id = {}

for snapshot_file in SNAPSHOT_DIR.glob("snapshot_*.json"):
    with snapshot_file.open(encoding="utf-8") as f:
        data = json.load(f)

    # snapshot は配列
    for item in data:
        cid = item.get("contentId")
        if not cid:
            continue

        # 既存 + 新規 を論理和（後勝ち）
        if cid not in snapshot_by_id:
            snapshot_by_id[cid] = item
        else:
            snapshot_by_id[cid] = {
                **snapshot_by_id[cid],
                **item
            }

# ===== songs 側を処理（上書き） =====
missing_in_snapshot = []

for song_file in SONGS_DIR.glob("*.json"):
    with song_file.open(encoding="utf-8") as f:
        song_data = json.load(f)

    cid = song_data.get("contentId")
    if not cid:
        continue

    if cid in snapshot_by_id:
        snapshot_data = snapshot_by_id[cid]

        # snapshot 優先で論理和
        merged = {
            **song_data,
            **snapshot_data
        }

        # ★ data/songs に上書き保存
        with song_file.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

    else:
        # snapshot に存在しなかった曲を記録
        missing_in_snapshot.append({
            "contentId": cid,
            "file": song_file.name,
            "song": song_data.get("song"),
            "title": song_data.get("title")
        })

# ===== ログ出力 =====
with LOG_FILE.open("w", encoding="utf-8") as f:
    for item in missing_in_snapshot:
        f.write(
            f"{item['contentId']}\t{item['file']}\t"
            f"{item.get('song','')}\t{item.get('title','')}\n"
        )

print(f"songs 上書き更新完了")
print(f"snapshot に存在しなかった曲: {len(missing_in_snapshot)}")
print(f"ログ出力先: {LOG_FILE}")
