from pathlib import Path
from collections import defaultdict
import csv

# ===== 設定 =====
TSV_FILE = Path("chiatro_setlist_merged.tsv")

PHASES = [
    {
        "name": "Phase0_no_groups",
        "start": 21,
        "end": 94,
        "groups": None,
    },
    {
        "name": "Phase1_A-B",
        "start": 95,
        "end": 161,
        "groups": ["A", "B"],
    },
    {
        "name": "Phase2_A-D",
        "start": 162,
        "end": 209,
        "groups": ["A", "B", "C", "D"],
    },
    {
        "name": "Phase3_A-F",
        "start": 210,
        "end": 274,
        "groups": ["A", "B", "C", "D", "E", "F"],
    },
    {
        "name": "Phase3_split",
        "start": 275,
        "end": 450,
        "groups": ["A", "B", "C1", "C2", "D1", "D2"],
    },
]

CHECK_START = 21
CHECK_END = 283

ROUND_COL = 8
GROUP_COL = 9

OUT_FILE =  Path(f"chiatro_round_group_check_{CHECK_START}_{CHECK_END}.txt")

# ===== TSV 読み込み =====
existing = defaultdict(set)

with TSV_FILE.open(encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if len(row) <= max(ROUND_COL, GROUP_COL):
            continue
        try:
            round_no = int(row[ROUND_COL])
        except ValueError:
            continue

        group = row[GROUP_COL].strip()
        group = group if group != "" else None
        existing[round_no].add(group)

# ===== チェック & ログ生成 =====
lines = []
total_missing = 0
total_unexpected = 0

lines.append(f"チェック範囲: round_no {CHECK_START}–{CHECK_END}")
lines.append("")

print(f"チェック範囲: round_no {CHECK_START}–{CHECK_END}")

for phase in PHASES:
    start = max(phase["start"], CHECK_START)
    end = min(phase["end"], CHECK_END)

    if start > end:
        continue

    expected_groups = phase["groups"]

    header = f"=== {phase['name']} ({start}–{end}) ==="
    lines.append(header)
    print("\n" + header)

    missing = []
    unexpected = []

    for r in range(start, end + 1):
        found = existing.get(r, set())

        # group なし phase
        if expected_groups is None:
            if None not in found:
                missing.append(f"round {r} (groupなし)")
            for g in found:
                if g is not None:
                    unexpected.append(f"round {r} group={g}")
            continue

        # group あり phase
        for g in expected_groups:
            if g not in found:
                missing.append(f"round {r} group={g}")

        for g in found:
            if g not in expected_groups:
                label = "(なし)" if g is None else g
                unexpected.append(f"round {r} group={label}")

    if not missing and not unexpected:
        lines.append("OK")
        print("OK")
        lines.append("")
        continue

    if missing:
        lines.append(f"[MISSING] {len(missing)} 件")
        print(f"❌ 不足 {len(missing)} 件")
        for m in missing:
            lines.append("  " + m)
            print("  ", m)

    if unexpected:
        lines.append(f"[UNEXPECTED] {len(unexpected)} 件")
        print(f"⚠️ 想定外 {len(unexpected)} 件")
        for u in unexpected:
            lines.append("  " + u)
            print("  ", u)

    lines.append("")

    total_missing += len(missing)
    total_unexpected += len(unexpected)

# ===== サマリ =====
lines.append("====================")
lines.append(f"不足: {total_missing} 件")
lines.append(f"想定外: {total_unexpected} 件")

print("\n====================")
print(f"不足: {total_missing} 件")
print(f"想定外: {total_unexpected} 件")

# ===== txt 出力 =====
with OUT_FILE.open("w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n📄 結果を書き出しました: {OUT_FILE}")
