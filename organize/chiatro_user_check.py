import csv
import json
import re
from collections import defaultdict
from pathlib import Path
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RATE_TSV = os.path.join(BASE_DIR, "chiatro_rate_refine.tsv")
QUIZ_DIR = Path("data/quizzes")
OUTPUT_TXT = os.path.join(BASE_DIR, "chiatro_check_participants.txt")

NAME_MAP = {
    "かがみん": "かがみおん",
    "おはげ": "はげお",
    "特攻隊長": "隊長",
    "祝(公式)": "祝公式",
    "ヌュラ": "ぬゅら",
    "うなぷれこ": "くらこ",
    "ﾏ゛ｯｯｯ": "ﾏﾞｯｯｯ",
    "suumo": "スーモ",
    "ばさ氏": "ばさし",
    "いみな": "汐波諱",
    "くすのき": "クスノキ",
    "らーくす": "ラークス",
    
    "SPEED STAR": "SPEED_STAR",
    "定禅寺 透": "定禅寺透",
    "汐波 諱": "汐波諱",
    "雪にゃ～": "雪にゃ〜",
    "がお～": "がお〜",
}

def split_rate_col(value: str):
    m = re.fullmatch(r"(\d+)([A-Za-z0-9]*)", value.strip())
    if not m:
        return None, None

    round_no = int(m.group(1))
    group = m.group(2) or None
    return round_no, group


# ==================================
# ① rate.tsv
# ==================================
expected = defaultdict(set)

with open(RATE_TSV, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    header = next(reader)

    parsed_cols = [split_rate_col(c) for c in header[2:]]

    for row in reader:
        name = row[0].strip()
        
        name = NAME_MAP.get(name, name)

        for (r, g), value in zip(parsed_cols, row[2:]):
            if r is None:
                continue

            if value and value != "--":
                expected[(r, g)].add(name)

# ==================================
# ② quiz_*.json
# ==================================
actual = defaultdict(set)

for json_file in QUIZ_DIR.glob("quiz_*.json"):
    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        r = data.get("quiz_no")
        if r is None:
            continue

        g = data.get("group")
        if g == "":
            g = None

        participants = data.get("participants", [])

        for name in participants:
            name = str(name).strip()
            if name:
                actual[(r, g)].add(name)

    except Exception as e:
        print(f"Error: {json_file} -> {e}")

# ==================================
# ③ quiz に存在する回のみチェック
# ==================================
with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
    for (r, g) in sorted(actual, key=lambda x: (x[0], x[1] or "")):
        exp = expected.get((r, g), set())
        act = actual[(r, g)]

        missing = sorted(exp - act)
        extra = sorted(act - exp)

        if not missing and not extra:
            continue

        label = f"{r}{g or ''}"
        out.write(f"=== Round {label} ===\n")

        if missing:
            out.write("[レート表にいるがJSONにいない]\n")
            for name in missing:
                out.write(f"{name}\n")

        if extra:
            out.write("[JSONにいるがレート表にいない]\n")
            for name in extra:
                out.write(f"{name}\n")

        out.write("\n")

print(f"出力完了: {OUTPUT_TXT}")
print("expected rounds:", len(expected))
print("actual rounds:", len(actual))
print("JSON files:", len(list(QUIZ_DIR.glob("quiz_*.json"))))