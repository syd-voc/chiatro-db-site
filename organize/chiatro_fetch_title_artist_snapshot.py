import requests
import csv
import time
import re

# ===== 設定 =====
INPUT_TSV = "chiatro_input.tsv"
OUTPUT_TSV = "chiatro_output.tsv"

WRITE_HEADER = False

API_URL = "https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search"

FIELDS = [
    "contentId",
    "title",
    "startTime",
    "userId",
    "channelId",
    "thumbnailUrl",
    "viewCounter",
    "mylistCounter",
    "likeCounter",
    "commentCounter",
    "lengthSeconds",
    "tags",
]

PARAMS_BASE = {
    "targets": "title",
    "_sort": "-mylistCounter",
    "_limit": 1,
    "_context": "fetch-script",
}

TAG_COLS = 11  # tags.0 ～ tags.10

# ===== ユーティリティ =====
def normalize_text(s: str) -> str:
    """ハイフン類をスペースに置換"""
    return re.sub(r"[‐-–—−-]", " ", s).strip()

# ===== TSV読み込み（ヘッダ有無自動判定）=====
with open(INPUT_TSV, newline="", encoding="utf-8") as fin:
    reader = csv.reader(fin, delimiter="\t")
    rows = list(reader)

if not rows:
    raise RuntimeError("入力TSVが空です")

first_row = rows[0]

# ヘッダ判定
has_header = (
    len(first_row) >= 2
    and first_row[0].lower() == "title"
    and first_row[1].lower() == "artist"
)

data_rows = rows[1:] if has_header else rows

# ===== 出力 =====
with open(OUTPUT_TSV, "w", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout, delimiter="\t")

    if WRITE_HEADER:
        header = FIELDS[:-1] + [f"tags.{i}" for i in range(TAG_COLS)]
        writer.writerow(header)

    for row in data_rows:
        if len(row) < 2:
            continue

        # title / artist 取得（ヘッダなし前提でもOK）
        title_raw = row[0]
        artist_raw = row[1]

        # - をスペースに置換
        title = normalize_text(title_raw)
        artist = normalize_text(artist_raw)

        query = f"{title} -歌ってみた"

        params = PARAMS_BASE | {
            "q": query,
            "fields": ",".join(FIELDS),
        }

        try:
            res = requests.get(API_URL, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

            if not data.get("data"):
                continue

            video = data["data"][0]

            # tags 分解（不足分は空文字）
            tags = video.get("tags", "").split()
            tags = tags[:TAG_COLS] + [""] * (TAG_COLS - len(tags))

            out_row = [
                video.get("contentId", ""),
                video.get("title", ""),
                video.get("startTime", ""),
                video.get("userId", ""),
                video.get("channelId", ""),
                video.get("thumbnailUrl", ""),
                video.get("viewCounter", ""),
                video.get("mylistCounter", ""),
                video.get("likeCounter", ""),
                video.get("commentCounter", ""),
                video.get("lengthSeconds", ""),
                *tags,
            ]

            writer.writerow(out_row)
            time.sleep(1.0)

        except Exception as e:
            print(f"Error ({query}): {e}")