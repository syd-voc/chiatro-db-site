from pathlib import Path

# ===== 設定 =====
IDS_TXT = Path("organize/content_ids.txt") 
TSV_FILE = Path("songs_all.tsv")
ID_COL_INDEX = 11   # contentId が入っている列（0始まり）
HAS_HEADER = True # tsvにヘッダーがあるか

# ===== IDリスト読み込み =====
with IDS_TXT.open(encoding="utf-8") as f:
    target_ids = {line.strip() for line in f if line.strip()}

# ===== TSVチェック =====
with TSV_FILE.open(encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 0 and HAS_HEADER:
            continue

        cols = line.rstrip("\n").split("\t")
        if len(cols) <= ID_COL_INDEX:
            continue

        cid = cols[ID_COL_INDEX]

        if cid in target_ids:
            print(f"一致: {cid}\t行{i+1}")
            print(line.rstrip())
        
    print("チェック完了")
