import csv
import re
from collections import defaultdict
from pathlib import Path

QUIZ_TSV = Path("chiatro_setlist_merged.tsv")
RATE_TSV = Path("chiatro_rate_refine.tsv")
OUTPUT_TXT = Path("chiatro_check_participants.txt")

def split_rate_col(value: str):
    """
    rate.tsv 用
    "274A"   -> (274, "A")
    "274"    -> (274, None)
    "278D2"  -> (278, "D2")
    """
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

with RATE_TSV.open(encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    header = next(reader)

    parsed_cols = [split_rate_col(c) for c in header[2:]]

    for row in reader:
        name = row[0].strip()
        for (r, g), value in zip(parsed_cols, row[2:]):
            if r is None:
                continue
            if value and value != "--":
                expected[(r, g)].add(name)

# ==================================
# ② quiz.tsv（★修正点）
# ==================================
actual = defaultdict(set)

with QUIZ_TSV.open(encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if not row or not row[8]:
            continue

        try:
            r = int(row[8])
        except ValueError:
            continue

        g = row[9].strip() if len(row) > 9 and row[9].strip() else None

        for i in range(11, len(row), 2):
            name = row[i].strip()
            if name:
                actual[(r, g)].add(name)

# ==================================
# ③ デバッグ print
# ==================================
# print("===== DEBUG: participants per round =====")
# for (r, g) in sorted(actual, key=lambda x: (x[0], x[1] or "")):
#     label = f"{r}{g or ''}"

#     exp = sorted(expected.get((r, g), set()))
#     act = sorted(actual.get((r, g), set()))

#     print(f"[DEBUG] Round {label}")
#     print("  rate.tsv :", ", ".join(exp) if exp else "(なし)")
#     print("  quiz.tsv :", ", ".join(act) if act else "(なし)")
# print("========================================")

# ==================================
# ④ quiz.tsv にある回のみチェック
# ==================================
with OUTPUT_TXT.open("w", encoding="utf-8") as out:
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
            out.write("[レート表にいるが結果TSVにいない]\n")
            for name in missing:
                out.write(f"{name}\n")

        if extra:
            out.write("[結果TSVにいるがレート表にいない]\n")
            for name in extra:
                out.write(f"{name}\n")

        out.write("\n")
