from pathlib import Path

# ===== 設定 =====
TARGET_DIR = Path("data")  # 置換対象のディレクトリ

OLD_WORD = "sm8999864"
NEW_WORD = "sm8233245"

# ===== JSONファイルを処理 =====
for json_file in TARGET_DIR.glob("*.json"):
    try:
        # UTF-8で読み込み
        text = json_file.read_text(encoding="utf-8")

        # 置換
        new_text = text.replace(OLD_WORD, NEW_WORD)

        # 変更があった場合のみ保存
        if text != new_text:
            json_file.write_text(new_text, encoding="utf-8")
            print(f"置換: {json_file.name}")

    except Exception as e:
        print(f"エラー: {json_file.name} - {e}")

print("完了しました。")