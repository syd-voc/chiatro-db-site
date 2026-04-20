import csv
import unicodedata

# =========================
# 設定項目
# =========================

INPUT_TSV = "chiatro_normalize_input.tsv"
OUTPUT_TSV = "chiatro_normalize_output.tsv"

TITLE_ALIAS_TSV = "chiatro_titles.tsv"
ARTIST_ALIAS_TSV = "chiatro_artists.tsv"

TITLE_INPUT_START_COL = 0
ARTIST_INPUT_START_COL = 2

ARTIST_COLUMNS = 9
ARTIST_INPUT_SPLIT = True  # True: 既に分割済み / False: 1列から分割

# =========================
# 正規化関数
# =========================

def normalize_key(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\uFF5E", "\u301C")
    return s.lower().strip()

# =========================
# エイリアス辞書
# =========================

def load_alias_tsv(path):
    alias_map = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            main = row[0].strip()
            alias_map[normalize_key(main)] = main
            for alias in row[1:]:
                if alias.strip():
                    alias_map[normalize_key(alias)] = main
    return alias_map

def load_artist_token_map(path):
    tokens = set()
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            for name in row:
                if name.strip():
                    tokens.add(normalize_key(name))
    return tokens

# =========================
# アーティスト分割
# =========================

def split_artists(raw, known_tokens):
    raw = raw.strip()
    if not raw:
        return []

    if normalize_key(raw) in known_tokens:
        return [raw]

    parts = raw.split(" ")
    result = []
    buf = []

    for p in parts:
        buf.append(p)
        joined = normalize_key(" ".join(buf))
        if joined in known_tokens:
            result.append(" ".join(buf))
            buf = []

    if buf:
        result.append(" ".join(buf))

    return result

# =========================
# メイン処理
# =========================

def normalize_tsv():
    title_map = load_alias_tsv(TITLE_ALIAS_TSV)
    artist_map = load_alias_tsv(ARTIST_ALIAS_TSV)
    artist_tokens = load_artist_token_map(ARTIST_ALIAS_TSV)

    with open(INPUT_TSV, encoding="utf-8") as fin, \
         open(OUTPUT_TSV, "w", encoding="utf-8", newline="") as fout:

        reader = csv.reader(fin, delimiter="\t")
        writer = csv.writer(fout, delimiter="\t")

        for row in reader:
            # index安全対策
            if len(row) < max(
                TITLE_INPUT_START_COL + 1,
                ARTIST_INPUT_START_COL + (ARTIST_COLUMNS if ARTIST_INPUT_SPLIT else 1)
            ):
                row = row + [""] * 100

            # ===== タイトル上書き =====
            raw_title = row[TITLE_INPUT_START_COL]
            row[TITLE_INPUT_START_COL] = title_map.get(
                normalize_key(raw_title), raw_title
            )

            # ===== アーティスト上書き =====
            if ARTIST_INPUT_SPLIT:
                # 既に分割済み
                for i in range(ARTIST_COLUMNS):
                    idx = ARTIST_INPUT_START_COL + i
                    raw = row[idx]
                    if raw:
                        row[idx] = artist_map.get(
                            normalize_key(raw), raw
                        )
            else:
                # 1列 → 分割して展開
                raw_artist = row[ARTIST_INPUT_START_COL]
                artists = split_artists(raw_artist, artist_tokens)
                artists_norm = [
                    artist_map.get(normalize_key(a), a) for a in artists
                ]
                artists_norm = (
                    artists_norm + [""] * ARTIST_COLUMNS
                )[:ARTIST_COLUMNS]

                for i in range(ARTIST_COLUMNS):
                    row[ARTIST_INPUT_START_COL + i] = artists_norm[i]

            # ===== 出力 =====
            writer.writerow(row)

# =========================
# 実行
# =========================

if __name__ == "__main__":
    normalize_tsv()
