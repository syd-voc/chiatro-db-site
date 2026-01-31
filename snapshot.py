import requests
import csv
import json
import time
from pathlib import Path
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# =====================
# 基本設定（固定）
# =====================
TARGETS = "tagsExact"
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
    "tags"
]
SORT = "-mylistCounter"
LIMIT = 100
CONTEXT = "research"

QUERY_FILE = "queries.json"

RUN_MODE = "single"      # "single" | "batch"
QUERY_NAME = "snapshot"
BATCH_NAME = ""

# =====================
# 年の自動取得
# =====================
CURRENT_YEAR = date.today().year
END_DATE = date(CURRENT_YEAR + 1, 1, 1)

# =====================
# デフォルト設定
# =====================
DEFAULT_CONFIG = {
    "OUTPUT_MODE": "year",     # year | month | all
    "MERGE_2007_2008": True,
    "MAX_PER_PERIOD": 800,
    "OUTPUT_FORMAT": "tsv",    # tsv | json
    "ENABLE_RANK": False,
    "SLEEP_BETWEEN_REQUESTS": True,
    "SLEEP_SECONDS": 1.0
}

# =====================
# API 取得
# =====================
def fetch_period_data(query, start_date, end_date, config):
    all_items = []
    offset = 0

    while len(all_items) < config["MAX_PER_PERIOD"]:
        params = {
            "q": query,
            "targets": TARGETS,
            "fields": ",".join(FIELDS),
            "_sort": SORT,
            "_limit": LIMIT,
            "_offset": offset,
            "_context": CONTEXT,
            "filters[startTime][gte]": f"{start_date}T00:00:00+09:00",
            "filters[startTime][lt]": f"{end_date}T00:00:00+09:00"
        }

        r = requests.get(
            "https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search",
            params=params
        )

        if config["SLEEP_BETWEEN_REQUESTS"]:
            time.sleep(config["SLEEP_SECONDS"])

        if r.status_code != 200:
            print(f"⚠️ Error {r.status_code}")
            break

        data = r.json()
        items = data.get("data", [])
        if not items:
            break

        for item in items:
            if isinstance(item.get("tags"), str):
                item["tags"] = item["tags"].split(" ")

        all_items.extend(items)
        offset += LIMIT

        if offset >= data.get("meta", {}).get("totalCount", 0):
            break

    all_items = all_items[:config["MAX_PER_PERIOD"]]

    # ===== rank 付与 =====
    if config["ENABLE_RANK"]:
        for i, item in enumerate(all_items, start=1):
            item["rank"] = i

    return all_items

# =====================
# 出力
# =====================
def write_tsv(path, items, config):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")

        header = []
        if config["ENABLE_RANK"]:
            header.append("rank")

        header += [f for f in FIELDS if f != "tags"]
        header += [f"tags.{i}" for i in range(11)]
        writer.writerow(header)

        for it in items:
            row = []

            if config["ENABLE_RANK"]:
                row.append(it.get("rank", ""))

            for f in FIELDS:
                if f == "tags":
                    tags = it.get("tags", [])[:11]
                    row.extend(tags + [""] * (11 - len(tags)))
                else:
                    row.append(it.get(f, ""))
            writer.writerow(row)

def write_json(path, items):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        

# =====================
# snapshot version 取得
# =====================
def fetch_snapshot_version():
    r = requests.get(
        "https://snapshot.search.nicovideo.jp/api/v2/snapshot/version"
    )
    if r.status_code != 200:
        print("⚠️ Failed to fetch snapshot version")
        return None

    data = r.json()
    return {
        "last_modified": data.get("last_modified"),
        "fetched_at": datetime.now().isoformat(timespec="seconds")
    }

def write_snapshot_version(out_dir: Path):
    info = fetch_snapshot_version()
    if not info:
        return

    path = out_dir / "last_modified.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

# =====================
# 期間生成
# =====================
def generate_periods(config):
    mode = config["OUTPUT_MODE"]
    periods = []

    if mode == "all":
        return [(date(2007,1,1), END_DATE, f"2007-{CURRENT_YEAR}")]

    if mode == "month":
        cur = date(2007,1,1)
        while cur < END_DATE:
            nxt = cur + relativedelta(months=1)
            periods.append((cur, nxt, f"{cur.year}-{cur.month:02d}"))
            cur = nxt
        return periods

    if mode == "year":
        if config["MERGE_2007_2008"]:
            periods.append((date(2007,1,1), date(2009,1,1), "2007-2008"))
            start = 2009
        else:
            start = 2007

        for y in range(start, CURRENT_YEAR + 1):
            periods.append((date(y,1,1), date(y+1,1,1), str(y)))
        return periods

    raise ValueError("Invalid OUTPUT_MODE")

# =====================
# JSON 解決
# =====================
def load_queries():
    with open(QUERY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_query(name, data):
    q = data["queries"][name]
    config = DEFAULT_CONFIG.copy()
    config.update(q.get("config", {}))
    return name, q["query"], config, q.get("description", "")

# =====================
# 実行
# =====================
def run_query(name, query, config, description):
    print(f"\n🚀 {name}")
    if description:
        print(f"   {description}")

    out_dir = Path("data") / name
    out_dir.mkdir(parents=True, exist_ok=True)

    periods = generate_periods(config)
    all_items = []

    for s, e, label in periods:
        print(f"📅 {label}")
        items = fetch_period_data(query, s.isoformat(), e.isoformat(), config)

        if config["OUTPUT_MODE"] == "all":
            all_items.extend(items)
        else:
            path = out_dir / f"snapshot_{label}.{config['OUTPUT_FORMAT']}"
            if config["OUTPUT_FORMAT"] == "tsv":
                write_tsv(path, items, config)
            else:
                write_json(path, items)

    if config["OUTPUT_MODE"] == "all":
        path = out_dir / f"snapshot_all.{config['OUTPUT_FORMAT']}"
        if config["OUTPUT_FORMAT"] == "tsv":
            write_tsv(path, all_items, config)
        else:
            write_json(path, all_items)
            
    # ===== snapshot version を記録 =====
    write_snapshot_version(out_dir)
    
def main():
    data = load_queries()

    if RUN_MODE == "single":
        jobs = [resolve_query(QUERY_NAME, data)]
    else:
        batch = data["batches"][BATCH_NAME]
        jobs = [resolve_query(q, data) for q in batch["run"]]

    for job in jobs:
        run_query(*job)

if __name__ == "__main__":
    main()
