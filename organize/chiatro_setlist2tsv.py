import re
import unicodedata
from collections import defaultdict
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "chiatro_setlist_new.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "chiatro_setlist_new.tsv")
USERS_ALIAS_FILE = os.path.join(BASE_DIR, "chiatro_users.tsv")
TITLES_ALIAS_FILE = os.path.join(BASE_DIR, "chiatro_titles.tsv")
ARTISTS_ALIAS_FILE = os.path.join(BASE_DIR, "chiatro_artists.tsv")
ROUND_MAP_FILE = os.path.join(BASE_DIR, "chiatro_round_map.tsv")
ERROR_LINES_FILE = os.path.join(BASE_DIR, "error_lines.txt")
ERROR_ROWS_FILE = os.path.join(BASE_DIR, "error_rows.tsv")
ERROR_USERS_FILE = os.path.join(BASE_DIR, "error_users.txt")

# タイトル中に「/」を含む例外パターン
EXCEPTION_PATTERNS = [
    "1/6",
    "7/8",
    "1/100",
    "D/N/A",
    "m/es",
    "ST/A#R", 
    "1/f", 
    "葵ちゃんはチョコミントアイスエイヤッ↑(/＞_＜)/", 
    "4/1", 
    "/ / // / /", 
    "パラサイト/ M.I.K.U.", 
    "w/o U",
    "ロベリア / Lobelia",
    "16.7km/s",
    "ハロ/ハワユ",
    "/(so42911532)",
    "/hidden",
    "ARTICUTION/奇術師の告白",
    "DYE/Re:flection+",
    "ウタハコ://H",
    "6/11",
    "a.r.t../?",
    "ChaiN De/structioN",
    "EXEC_RESOLUTION/.",
    "Feedback/Artery",
    "III & III/SAKURA",
    "Inner Lock Word / インナーロックワード",
    "Plus/Space",
    "病ンデレ///Sickness",
    "恋ノート////"
]

SPLIT_ARTIST_EXCEPTIONS = {
    "ユリイ・カノン",
    "ユリィ・カノン",
    "ニャン・トンロン",
    "きっと、ずっと、ぼっち",
    "きっと、ずっと、ぼっち。",
    "シアン・キノ",
    "つきみぐー、",
    "灯下はこ、",
    "LOVE&P",
    "s×c",
    "J・ミラ",
    "Ｊ・ミラ",
    "ふゅゅ××",
    "△〇□×",
    "△○□×",
    "ウィリアム・シェイクスピア",
    "まだ、誰も知らない小説の盗作",
    "メガテラ・ゼロ",
    "sasakure,UK",
    "犀は火曜日、山羊は海",
    "タケ・ヨシキ",
    "マリー・アンドロイド",
    "もう、ダメ",
    "キャプテン・ミライ",
    "キャプテン・ソプラノ"
}

ARTIST_TAIL_EXCEPTIONS = [
    "ふゅゅ××",
    "△〇□×",
    "△○□×",
    "B9☆",
    "Jille.Starz☆",
    "Ryu☆"
]


SPECIAL_ARTIST_GROUPS = {
    "ora-bunbun-star": ["Orangestar", "n-buna"],
    "1640mP": ["164", "40mP"],
    "1640㍍P": ["164", "40mP"],
    "またごめんなさいが言えなくて切ない世界を生きる": ["また切ない世界を生きる", "ごめんなさいが言えなくて"],
    "みきーの": ["みきとP", "keeno"],
    "ギガれをる": ["ギガ", "れをる"],
    "しいくる": ["椎乃味醂", "ていくる"],
    "CIRCRUSH": ["Crusher", "CircusP"],
    "minato396": ["mikuru396", "流星P"],
    "ヴァイスショコラーデ": ["regulus", "ですとろい"],
    "桑爺": ["クワガタP", "buzzG"]
}

ANSWER_START_PATTERN = re.compile(
    r"(×スルー|・?スルー|×|★|☆|[①-⑤○◯])"
)

MAX_ARTISTS = 6

def normalize_key(text):
    """
    表記ゆれ吸収用キー生成
    """
    if not text:
        return ""

    # 全角→半角（英数・記号）
    text = unicodedata.normalize("NFKC", text)

    # 英字を小文字化
    text = text.lower()

    # 前後空白除去
    text = text.strip()

    return text

# ---------- 回答者解析 ----------
def parse_answers(answer_text, alias_map, unknown_users):
    results = []

    for part in answer_text.split("→"):
        part = part.strip()

        # スルー
        if part in ("スルー", "・スルー", "×スルー"):
            results.append(("", "SKIP"))
            continue

        # 失格
        if re.match(r"×{2,}", part):
            name = part.lstrip("×")
            name = normalize_user(name, alias_map, unknown_users)
            results.append((name, "LOSE"))
            continue

        # 不正解
        if part.startswith("×"):
            name = part[1:]
            name = normalize_user(name, alias_map, unknown_users)
            results.append((name, "NG"))
            continue

        # 正解
        if re.match(r"[①-⑤○◯]", part):
            name = part[1:]
            name = normalize_user(name, alias_map, unknown_users)
            results.append((name, "OK"))
            continue

        # 上がり
        if part.startswith(("★", "☆")):
            name = re.sub(
                r"^[★☆](?:[（(]?\d+[）)]?|[①-⑳⑴-⒇])?",
                "",
                part
            )
            name = normalize_user(name, alias_map, unknown_users)
            results.append((name, "WIN"))
            continue

        name = normalize_user(part, alias_map, unknown_users)
        results.append((name, "UNKNOWN"))

    return results


def load_alias_tsv(path):
    alias_map = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            cols = [c.strip() for c in line.rstrip("\n").split("\t") if c.strip()]
            if not cols:
                continue

            main = normalize_key(cols[0])
            for name in cols:
                alias_map[normalize_key(name)] = cols[0]
    return alias_map

def load_round_map(path):
    round_map = {}
    
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            cols = line.split("\t")
            if len(cols) < 2:
                # 回番号しかない行は無視 or エラー
                continue

            round_no = cols[0].strip()
            dates = cols[1:]

            for d in dates:
                d = d.strip()
                if not d:
                    continue

                if d in round_map:
                    # 同じ日付が複数回に属していたらエラー検出したい場合
                    print(
                        f"[WARN] duplicate date in round_map: "
                        f"date={d}, round={round_no}, "
                        f"previous={round_map[d]}, line={lineno}"
                    )

                round_map[d] = round_no
    return round_map



alias_map = load_alias_tsv(USERS_ALIAS_FILE)
title_alias_map = load_alias_tsv(TITLES_ALIAS_FILE)
artist_alias_map = load_alias_tsv(ARTISTS_ALIAS_FILE)
round_map = load_round_map(ROUND_MAP_FILE)
unknown_users = set()

def normalize_user(name, alias_map, unknown_users):
    if not name:
        return name

    key = normalize_key(name)

    if key in alias_map:
        return alias_map[key]

    unknown_users.add(name)
    return name

def normalize_title(title, title_alias_map):
    key = normalize_key(title)
    return title_alias_map.get(key, title)

def normalize_artists(artists, artist_alias_map):
    normalized = []
    for a in artists:
        key = normalize_key(a)
        normalized.append(artist_alias_map.get(key, a))
    return normalized


# ---------- アーティスト名分割 ----------

def split_artists_with_special_rules(artist_str: str):
    artist_str = artist_str.strip()

    # 順位表記を除去
    artist_str = re.sub(r"[（(]\d+位[）)]", "", artist_str).strip()

    # 特殊グループ名は最優先
    for key, artists in SPECIAL_ARTIST_GROUPS.items():
        if key.lower() in artist_str.lower():
            return artists

    # 例外語を一時置換（長い順・最優先）
    placeholders = {}
    tmp = artist_str
    for i, exc in enumerate(SPLIT_ARTIST_EXCEPTIONS):
        pattern = re.compile(re.escape(exc), re.IGNORECASE)
        if pattern.search(tmp):
            ph = f"__EXC{i}__"
            placeholders[ph] = exc
            tmp = pattern.sub(ph, tmp)

    parts = re.split(r"[、,，・×&＆]", tmp)

    # プレースホルダを元に戻す
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        for ph, exc in placeholders.items():
            p = p.replace(ph, exc)
        result.append(p)

    return result


# ---------- スラッシュ分割 ----------
def find_split_index(line):
    ignore_indices = set()
    for pat in EXCEPTION_PATTERNS:
        start = 0
        while True:
            pos = line.find(pat, start)
            if pos == -1:
                break
            for i, ch in enumerate(pat):
                if ch == "/":
                    ignore_indices.add(pos + i)
            start = pos + 1

    for i, ch in enumerate(line):
        if ch == "/" and i not in ignore_indices:
            return i
    return None


def parse_setlist(text):
    results = []
    errors = []
    current_date = ""
    current_group = ""
    ok_counter = defaultdict(int)
    win_counter = defaultdict(int)

    header_pattern = re.compile(
        r"""
        【\s*
        (?:
            (\d{4})[/-](\d{1,2})[/-](\d{1,2})
        |
            (\d{4})(\d{2})(\d{2})
        )
        """,
        re.VERBOSE
    )
    group_pattern = re.compile(r"([A-Z]\d?)\s*(?:グループ)?")


    for lineno, line in enumerate(text.splitlines(), start=1):
        original = line.rstrip()
        line = line.strip()
        if not line:
            continue

        # ヘッダー
        m = header_pattern.search(line)
        if m:
            if m.group(1):  # YYYY/MM/DD or YYYY-MM-DD
                y = m.group(1)
                mth = m.group(2)
                d = m.group(3)
            else:           # YYYYMMDD
                y = m.group(4)
                mth = m.group(5)
                d = m.group(6)

            current_date = f"{y}/{int(mth):02d}/{int(d):02d}"

            # グループ（無ければ空文字 or 任意ラベル）
            m_group = group_pattern.search(line)
            current_group = m_group.group(1) if m_group else ""
            
            ok_counter.clear()
            win_counter.clear()

            continue

        # 曲行
        m = re.match(r"\d+\.?\s*(.+)", line)
        if not m:
            errors.append(
                f"[{lineno}] INVALID_LINE (no header / no song): {original}"
            )
            continue

        if not current_date:
            errors.append(
                f"[{lineno}] SONG_WITHOUT_HEADER: {original}"
            )
            continue
    
        content = m.group(1).strip()
        if not content:
            errors.append(
                f"[{lineno}] EMPTY_TITLE: {original}"
            )
            continue
        
        split_idx = find_split_index(content)
        if split_idx is None:
            errors.append(
                f"[{lineno}] TITLE_ARTIST_SPLIT_FAILED ({current_date}, {current_group}) {original}"
            )
            continue

        title = content[:split_idx].strip()
        rest = content[split_idx + 1:].strip()

        artist_and_answers = rest
        artist = artist_and_answers.strip()

        if not artist:
            errors.append(
                f"[{lineno}] EMPTY_ARTIST: {original}"
            )
        
        answers = []
        
        
        # --- 例外アーティスト名による探索開始位置の固定 ---
        search_start = 0
        for exc in ARTIST_TAIL_EXCEPTIONS:
            idx = artist_and_answers.find(exc)
            if idx != -1:
                # 例外アーティスト名の「末尾」以降だけを回答者探索対象にする
                search_start = idx + len(exc)
                break
            
        
        pos = search_start
        while True:
            m_ans = ANSWER_START_PATTERN.search(artist_and_answers, pos)
            if not m_ans:
                break

            start = m_ans.start()
            token = m_ans.group()

            # --- スルーは即回答者扱い ---
            if token in ("・スルー", "スルー", "×スルー"):
                artist = artist_and_answers[:start].strip()
                answer_text = artist_and_answers[start:].strip()
                answers = parse_answers(answer_text, alias_map, unknown_users)
                break

            after_symbol = artist_and_answers[start + len(token):]

            name_match = re.match(r"\s*([^\s→]+)", after_symbol)
            if not name_match:
                pos = start + len(token)
                continue

            name_end = start + len(token) + name_match.end()
            rest_after_name = artist_and_answers[name_end:].lstrip()

            is_answer = False

            # ① 直後に →
            if rest_after_name.startswith("→"):
                is_answer = True

            # ② 行末
            elif rest_after_name == "":
                is_answer = True

            if is_answer:
                artist = artist_and_answers[:start].strip()
                answer_text = artist_and_answers[start:].strip()
                answers = parse_answers(answer_text, alias_map, unknown_users)
                break

            pos = start + len(token)
            
        title = normalize_title(title, title_alias_map)
        artist_list = split_artists_with_special_rules(artist)
        artist_list = normalize_artists(artist_list, artist_alias_map)

        artist_cols = artist_list[:MAX_ARTISTS]
        while len(artist_cols) < MAX_ARTISTS:
            artist_cols.append("")
            
        round_no = round_map.get(current_date, "")
        
        if not round_no:
            errors.append(f"ROUND_NOT_FOUND, date={current_date}, line={lineno}")
            
        if answers:
            last_name, last_result = answers[-1]
            if last_result in {"NG", "LOSE"}:
                answers.append(("", "SKIP"))

        row = [
            original,
            title,
            *artist_cols,
            round_no,
            current_group,
            current_date,
        ]

        for name, result in answers:
            new_result = result

            # ===== OK：回答者ごと =====
            if result == "OK":
                key = (current_date, current_group, name)
                ok_counter[key] += 1
                new_result = f"OK{ok_counter[key]}"

            # ===== WIN：回ごとの順番 =====
            elif result == "WIN":
                key = (current_date, current_group)
                win_counter[key] += 1
                new_result = f"WIN{win_counter[key]}"

            row.extend([name, new_result])

        results.append(row)
                    
    return results, errors

def validate_answers(answers):
    errors = []
    seen_terminal = False

    for name, result in answers:
        # 空セルは無視
        if not name and not result:
            continue

        # 名前ルール
        if result == "SKIP":
            if name:
                errors.append("SKIP_HAS_NAME")
        else:
            if not name:
                errors.append("RESULT_NO_NAME")

        # 終端後に回答が続く
        if seen_terminal:
            errors.append("AFTER_TERMINAL")

        if result.startswith(("WIN", "OK")) or result == "SKIP":
            seen_terminal = True

    return errors


def validate_session(rows):
    row_status = []

    current_key = None
    session_users = {}
    
    ROUND_COL = 2 + MAX_ARTISTS
    GROUP_COL = ROUND_COL + 1
    DATE_COL  = GROUP_COL + 1
    ANSWER_START_COL = DATE_COL + 1

    for row in rows:
        # group, date の位置は固定で取得
        group = row[GROUP_COL]
        date = row[DATE_COL]
        key = (group, date)

        # 回が変わったらリセット
        if key != current_key:
            current_key = key
            session_users = {}
            
            user_ok_count = {}
            user_ng_count = {}

            win_ok_base = None
            lose_ng_base = None
            
        ANSWER_START_COL = 2 + MAX_ARTISTS + 3

        # 回答抽出
        answers = []
        for i in range(ANSWER_START_COL, len(row), 2):
            if i + 1 >= len(row):
                break
            name = row[i].strip()
            result = row[i + 1].strip()
            if name or result:
                answers.append((name, result))
                

        errors = []

        # 曲内検証
        errors.extend(validate_answers(answers))
        
        if not answers:
            errors.append("NO_ANSWERS")
        
        # 回跨ぎ検証
        for name, result in answers:
            if not name:
                continue

            if name in session_users:
                errors.append("REAPPEAR_AFTER_WIN_OR_LOSE")
            
            # OK
            if result.startswith("OK"):
                user_ok_count[name] = user_ok_count.get(name, 0) + 1

                if win_ok_base is not None and user_ok_count[name] > win_ok_base:
                    errors.append(
                        f"OK_COUNT_EXCEEDED_BEFORE_WIN:"
                        f"user={name},current={user_ok_count[name]},base={win_ok_base}"
                    )

            # NG
            if result == "NG":
                user_ng_count[name] = user_ng_count.get(name, 0) + 1

                if lose_ng_base is not None and user_ng_count[name] > lose_ng_base:
                    errors.append(
                        f"NG_COUNT_EXCEEDED_BEFORE_LOSE:"
                        f"user={name},current={user_ng_count[name]},base={lose_ng_base}"
                    )

            # WIN
            if result.startswith("WIN"):
                ok_count = user_ok_count.get(name, 0)

                if win_ok_base is None:
                    win_ok_base = ok_count
                elif ok_count != win_ok_base:
                    errors.append(
                        f"OK_COUNT_MISMATCH_BEFORE_WIN:"
                        f"user={name},current={ok_count},base={win_ok_base}"
                    )

                session_users[name] = "WIN"

            # LOSE
            if result == "LOSE":
                ng_count = user_ng_count.get(name, 0)

                if lose_ng_base is None:
                    lose_ng_base = ng_count
                elif ng_count != lose_ng_base:
                    errors.append(
                        f"NG_COUNT_MISMATCH_BEFORE_LOSE:"
                        f"user={name},current={ng_count},base={lose_ng_base}"
                    )

                session_users[name] = "LOSE"
            
            #UNKNOWN
            if result == "UNKNOWN":
                errors.append("HAS_UNKNOWN_RESULT")
                

        row_status.append((row, errors))

    return row_status

def write_error_tsv(rows_with_errors, output_path):
    has_error = False

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        for row, errors in rows_with_errors:
            if not errors:
                continue

            has_error = True
            error_col = ";".join(sorted(set(errors)))
            f.write(error_col + "\t" + "\t".join(row) + "\n")

        if not has_error:
            f.write("NO_ERROR_ROWS\n")

def normalize_text(text: str) -> str:
    # ① Unicode正規化（合成濁点・半濁点を統合）
    # 例: は + ゙ → ば
    text = unicodedata.normalize("NFC", text)

    # ② 全角チルダ（U+FF5E）→ 波ダッシュ（U+301C）
    text = text.replace("\uFF5E", "\u301C")

    # ③ 0幅スペース類を除去
    # U+200B ZERO WIDTH SPACE
    # U+200C ZERO WIDTH NON-JOINER
    # U+200D ZERO WIDTH JOINER
    # U+FEFF ZERO WIDTH NO-BREAK SPACE (BOM)
    # U+202A LEFT-TO-RIGHT EMBEDDING
    text = re.sub(r"[\u200B\u200C\u200D\uFEFF\u202A]", "", text)

    return text

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()

    text = normalize_text(text)
    rows, errors = parse_setlist(text)
    validated = validate_session(rows)

    # ===== error_rows.tsv =====
    write_error_tsv(validated, ERROR_ROWS_FILE)

    # ===== TSV出力 =====
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for row in rows:
            f.write("\t".join(row) + "\n")

    # ===== error_lines.txt =====
    with open(ERROR_LINES_FILE, "w", encoding="utf-8") as f:
        if errors:
            f.write("\n".join(errors))
        else:
            f.write("NO_ERROR_LINES\n")

    # ===== error_users.txt =====
    with open(ERROR_USERS_FILE, "w", encoding="utf-8") as f:
        if unknown_users:
            for name in sorted(unknown_users):
                f.write(name + "\n")
        else:
            f.write("NO_UNKNOWN_USERS\n")

if __name__ == "__main__":
    main()
