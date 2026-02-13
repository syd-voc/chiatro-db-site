import json
import glob
from pathlib import Path

TARGET_DIR = Path("data/songs")

def to_int_maybe(val):
    """文字列の数値をintに変換（カンマ・空白対応）"""
    if not isinstance(val, str):
        return val

    s = val.strip()
    if not s:
        return val

    # カンマ除去
    s = s.replace(",", "")

    # 数字のみなら変換
    if s.isdigit():
        try:
            return int(s)
        except ValueError:
            return val

    return val


def convert_fields(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("viewCounter", "likeCounter", "mylistCounter", "commentCounter", "lengthSeconds", "userId"):
                obj[k] = to_int_maybe(v)
            else:
                convert_fields(v)

    elif isinstance(obj, list):
        for item in obj:
            convert_fields(item)


files = glob.glob(str(TARGET_DIR / "*.json"))

for fp in files:
    path = Path(fp)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    convert_fields(data)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("done.")
