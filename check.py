from pathlib import Path
import re
from collections import defaultdict

# ===== 設定 =====
QUIZ_DIR = Path("data/quizzes")

PHASES = [
    {
        "name": "Phase0_no_suffix",
        "start": 21,
        "end": 94,
        "suffixes": None,  # suffixなし
    },
    {
        "name": "Phase1_A-B",
        "start": 95,
        "end": 161,
        "suffixes": ["A", "B"],
    },
    {
        "name": "Phase2_A-D",
        "start": 162,
        "end": 209,
        "suffixes": ["A", "B", "C", "D"],
    },
    {
        "name": "Phase3_A-F",
        "start": 210,
        "end": 274,
        "suffixes": ["A", "B", "C", "D", "E", "F"],
    },
    {
        "name": "Phase3_split",
        "start": 275,
        "end": 450,
        "suffixes": ["A", "B", "C1", "C2", "D1", "D2"],
    },
]

CHECK_START = 21
CHECK_END = 283

# ===== ファイル名解析 =====
pattern = re.compile(r"quiz_(\d+)([A-Z]\d*)?\.json")

existing = defaultdict(set)

for path in QUIZ_DIR.glob("quiz_*.json"):
    m = pattern.fullmatch(path.name)
    if not m:
        continue
    num = int(m.group(1))
    suffix = m.group(2)  # None の場合あり
    existing[num].add(suffix)

# ===== チェック =====
total_missing = 0
total_unexpected = 0

print(f"チェック範囲: {CHECK_START}–{CHECK_END}")

for phase in PHASES:
    phase_start = max(phase["start"], CHECK_START)
    phase_end = min(phase["end"], CHECK_END)

    if phase_start > phase_end:
        continue

    expected_suffixes = phase["suffixes"]

    print(f"\n=== {phase['name']} ({phase_start}–{phase_end}) ===")

    missing = []
    unexpected = []

    for num in range(phase_start, phase_end + 1):
        found = existing.get(num, set())

        # --- suffixなし phase ---
        if expected_suffixes is None:
            if None not in found:
                missing.append(f"quiz_{num}.json")
            for s in found:
                if s is not None:
                    unexpected.append(f"quiz_{num}{s}.json")
            continue

        # --- suffixあり phase ---
        for s in expected_suffixes:
            if s not in found:
                missing.append(f"quiz_{num}{s}.json")

        for s in found:
            if s not in expected_suffixes:
                name = f"quiz_{num}.json" if s is None else f"quiz_{num}{s}.json"
                unexpected.append(name)

    if not missing and not unexpected:
        print("✅ 問題なし")
        continue

    if missing:
        print(f"❌ 不足 {len(missing)} 件")
        for m in missing:
            print("  MISSING   ", m)

    if unexpected:
        print(f"⚠️ 想定外 {len(unexpected)} 件")
        for u in unexpected:
            print("  UNEXPECTED", u)

    total_missing += len(missing)
    total_unexpected += len(unexpected)

# ===== サマリ =====
print("\n====================")
print(f"不足: {total_missing} 件")
print(f"想定外: {total_unexpected} 件")
