import json
from pathlib import Path

# ===== パス設定 =====
SONGS_DIR = Path("data/songs")
SNAPSHOT_DIR = Path("data/snapshot")
LOG_FILE = Path("data/missing_songs.log")

# ===== JSON 安全ロード関数 =====
def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print("===================================")
        print("JSONDecodeError が発生しました")
        print(f"ファイル: {path}")
        print(f"内容: {e}")
        print("===================================")
        raise  # どこで止まったか分かるように再送出

# ===== snapshot 側をすべて読み込み、contentId で統合 =====
snapshot_by_id = {}

for snapshot_file in SNAPSHOT_DIR.glob("snapshot_*.json"):
    data = load_json(snapshot_file)

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
    song_data = load_json(song_file)

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

        # data/songs に上書き保存
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

print("songs 上書き更新完了")
print(f"snapshot に存在しなかった曲: {len(missing_in_snapshot)}")
print(f"ログ出力先: {LOG_FILE}")
