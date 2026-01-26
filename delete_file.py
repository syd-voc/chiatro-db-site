from pathlib import Path

# ===== 設定 =====
SONGS_DIR = Path("data/songs")

# 削除したい json ファイル名（拡張子込み）
TARGET_FILES = [
    "sm36427372.json",
]

# ===== 削除処理 =====
for filename in TARGET_FILES:
    file_path = SONGS_DIR / filename

    if file_path.exists():
        file_path.unlink()
        print(f"削除しました: {file_path}")
    else:
        print(f"見つかりません: {file_path}")
