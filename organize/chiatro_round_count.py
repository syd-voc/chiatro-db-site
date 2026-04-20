import csv
from collections import defaultdict
from pathlib import Path

QUIZ_TSV = Path("chiatro_setlist_merged.tsv")
OUTPUT_TXT = Path("chiatro_count_per_round.txt")

# (round_no, group) -> 出題数
counts = defaultdict(int)

with QUIZ_TSV.open(encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if not row or len(row) <= 8 or not row[8]:
            continue

        try:
            round_no = int(row[8])
        except ValueError:
            continue

        group = row[9].strip() if len(row) > 9 and row[9].strip() else None

        # 1行 = 1問
        counts[(round_no, group)] += 1

# txt に出力
with OUTPUT_TXT.open("w", encoding="utf-8") as out:
    for (r, g) in sorted(counts, key=lambda x: (x[0], x[1] or "")):
        label = f"{r}{g or ''}"
        out.write(f"{label}\t{counts[(r, g)]}\n")

print(f"出題数集計を出力しました: {OUTPUT_TXT}")