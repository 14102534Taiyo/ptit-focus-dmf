"""
field_mapping.py - ตาราง Mapping แหล่งผลิตข้ามปี (Field Group Mapping)

DMF เปลี่ยนชื่อ / สะกด / รวม / แยกแหล่งผลิตหลายครั้ง (เช่น เปลี่ยนรูปแบบรายงานปี 2559 และเปลี่ยนสัมปทานปี 2565–2566)
ไฟล์ `field_group_mapping.xlsx` ให้ผู้ดูแลระบบกำหนดว่าชื่อแหล่งตามรายงาน DMF (แหล่ง_ไฟล์ดิบ) แต่ละชื่อ
นับเป็น "กลุ่มติดตาม" ใด เพื่อให้ติดตามการผลิตได้ต่อเนื่องหลายปี

กติกา: ใช้ "กลุ่มติดตาม" เฉพาะแถวที่สถานะเป็น "ยืนยันแล้ว" — แถวที่เป็น "ร่าง" จะยังใช้ชื่อตาม DMF เดิม
ใช้ร่วมกันทั้ง app.py (หน้าจัดการ) และ .github/scripts/sync_dmf.py (ETL)
"""
import datetime
import glob
import json
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_XLSX = os.path.join(BASE_DIR, "field_group_mapping.xlsx")
MAPPING_JSON = os.path.join(BASE_DIR, "field_group_mapping.json")
PRODUCTION_CACHE_DIR = os.path.join(BASE_DIR, "data", "cache", "production")

COL_FIELD = "แหล่ง_ไฟล์ดิบ"
COL_GROUP = "กลุ่มติดตาม"
COL_RELATION = "ความสัมพันธ์"
COL_STATUS = "สถานะ"
COL_NOTE = "หมายเหตุ"
COL_YEARS = "ปีที่พบในข้อมูล"
COL_BLOCKS = "แปลงที่พบ"
COL_AREA = "พื้นที่"
COL_UPDATED = "แก้ไขล่าสุด"

COLUMNS = [COL_FIELD, COL_GROUP, COL_RELATION, COL_STATUS, COL_NOTE, COL_YEARS, COL_BLOCKS, COL_AREA, COL_UPDATED]
# Columns derived from DMF data — refreshed automatically, never edited by hand
AUTO_COLUMNS = [COL_YEARS, COL_BLOCKS, COL_AREA]

RELATION_OPTIONS = [
    "ชื่อเดิม (ไม่เปลี่ยน)",
    "สะกดต่าง / พิมพ์ต่าง",
    "เปลี่ยนชื่อ",
    "รวมเป็นกลุ่ม (หลายแหล่ง → 1 ชื่อ)",
    "แยกย่อย (1 ชื่อ → หลายแหล่ง)",
    "อื่นๆ (ดูหมายเหตุ)",
]
STATUS_CONFIRMED = "ยืนยันแล้ว"
STATUS_DRAFT = "ร่าง"
STATUS_OPTIONS = [STATUS_DRAFT, STATUS_CONFIRMED]


def field_inventory(cache_dir=PRODUCTION_CACHE_DIR):
    """Every DMF field name seen in the per-year production cache, with years / blocks / area."""
    inv = {}
    for path in sorted(glob.glob(os.path.join(cache_dir, "*.json"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if not stem.isdigit():
            continue
        year = int(stem)
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        cols = payload.get("columns", [])
        try:
            i_field, i_block, i_area = cols.index(COL_FIELD), cols.index("แปลง_ไฟล์ดิบ"), cols.index("พื้นที่")
        except ValueError:
            continue
        for row in payload.get("rows", []):
            name = str(row[i_field] or "").strip()
            if not name:
                continue
            entry = inv.setdefault(name, {"years": set(), "blocks": set(), "areas": set()})
            entry["years"].add(year)
            block = str(row[i_block] or "").strip()
            if block and block != "-":
                entry["blocks"].add(block)
            if row[i_area]:
                entry["areas"].add(str(row[i_area]).strip())
    return inv


def _years_label(years):
    if not years:
        return ""
    ys = sorted(years)
    # Compress to ranges: 2546–2558, 2565–2569
    ranges, start, prev = [], ys[0], ys[0]
    for y in ys[1:]:
        if y != prev + 1:
            ranges.append((start, prev))
            start = y
        prev = y
    ranges.append((start, prev))
    return ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b in ranges)


def load_mapping(path_xlsx=MAPPING_XLSX, path_json=MAPPING_JSON):
    """Load the mapping table (Excel preferred so hand edits in Excel win; JSON as fallback)."""
    df = None
    if os.path.exists(path_xlsx):
        try:
            df = pd.read_excel(path_xlsx, dtype=str)
        except Exception:
            df = None
    if df is None and os.path.exists(path_json):
        try:
            with open(path_json, "r", encoding="utf-8") as f:
                df = pd.DataFrame(json.load(f).get("rows", []))
        except Exception:
            df = None
    if df is None:
        df = pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS].fillna("").astype(str)
    df[COL_FIELD] = df[COL_FIELD].str.strip()
    return df[df[COL_FIELD] != ""].drop_duplicates(COL_FIELD, keep="last").reset_index(drop=True)


def merge_with_inventory(df_map, inventory):
    """Add newly seen DMF names as their own (draft) group and refresh the auto columns."""
    df = df_map.copy()
    known = set(df[COL_FIELD])
    new_rows = [
        {COL_FIELD: name, COL_GROUP: name, COL_RELATION: RELATION_OPTIONS[0], COL_STATUS: STATUS_DRAFT,
         COL_NOTE: "ชื่อใหม่จาก DMF — รอตรวจสอบ", COL_UPDATED: ""}
        for name in sorted(inventory) if name not in known
    ]
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df[COL_YEARS] = df[COL_FIELD].map(lambda n: _years_label(inventory.get(n, {}).get("years", set())))
    df[COL_BLOCKS] = df[COL_FIELD].map(lambda n: ", ".join(sorted(inventory.get(n, {}).get("blocks", set()))))
    df[COL_AREA] = df[COL_FIELD].map(lambda n: " / ".join(sorted(inventory.get(n, {}).get("areas", set()))))
    df[COL_GROUP] = df.apply(lambda r: str(r[COL_GROUP]).strip() or r[COL_FIELD], axis=1)
    first_year = df[COL_FIELD].map(lambda n: min(inventory.get(n, {}).get("years", {9999})))
    return df.assign(_y=first_year).sort_values([COL_GROUP, "_y", COL_FIELD]).drop(columns="_y")[COLUMNS].reset_index(drop=True)


def save_mapping(df, previous=None, path_xlsx=MAPPING_XLSX, path_json=MAPPING_JSON):
    """Write Excel + JSON. Rows that changed versus `previous` get today's date in แก้ไขล่าสุด."""
    out = df.copy().fillna("").astype(str)
    for col in COLUMNS:
        if col not in out.columns:
            out[col] = ""
    out = out[COLUMNS]
    out[COL_FIELD] = out[COL_FIELD].str.strip()
    out[COL_GROUP] = out.apply(lambda r: r[COL_GROUP].strip() or r[COL_FIELD], axis=1)
    out = out[out[COL_FIELD] != ""].drop_duplicates(COL_FIELD, keep="last")
    if previous is not None and not previous.empty:
        editable = [COL_GROUP, COL_RELATION, COL_STATUS, COL_NOTE]
        prev = previous.set_index(COL_FIELD)[editable].astype(str)
        today = datetime.date.today().isoformat()

        def stamp(row):
            if row[COL_FIELD] not in prev.index:
                return today
            changed = any(str(row[c]) != str(prev.loc[row[COL_FIELD], c]) for c in editable)
            return today if changed else row[COL_UPDATED]

        out[COL_UPDATED] = out.apply(stamp, axis=1)
    out = out.reset_index(drop=True)
    with pd.ExcelWriter(path_xlsx, engine="openpyxl") as writer:
        out.to_excel(writer, sheet_name="Field_Group_Mapping", index=False)
        ws = writer.sheets["Field_Group_Mapping"]
        widths = {COL_FIELD: 34, COL_GROUP: 34, COL_RELATION: 28, COL_STATUS: 12, COL_NOTE: 70,
                  COL_YEARS: 22, COL_BLOCKS: 24, COL_AREA: 14, COL_UPDATED: 14}
        for idx, col in enumerate(COLUMNS, start=1):
            ws.column_dimensions[ws.cell(1, idx).column_letter].width = widths.get(col, 16)
        ws.freeze_panes = "B2"
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump({"columns": COLUMNS, "rows": out.to_dict(orient="records")}, f, ensure_ascii=False, indent=2)
    return out


def confirmed_group_lookup(df_map):
    """{DMF field name: tracking group} for confirmed rows only."""
    if df_map is None or df_map.empty:
        return {}
    ok = df_map[df_map[COL_STATUS].str.strip() == STATUS_CONFIRMED]
    return {r[COL_FIELD]: (r[COL_GROUP].strip() or r[COL_FIELD]) for _, r in ok.iterrows()}


def public_payload(df_map):
    """Read-only copy for the web dashboard (field tracker + reference table)."""
    rows = df_map[[COL_FIELD, COL_GROUP, COL_RELATION, COL_STATUS, COL_NOTE, COL_YEARS, COL_BLOCKS, COL_AREA, COL_UPDATED]]
    return {
        "generated": datetime.datetime.now().isoformat(),
        "rule": "ใช้กลุ่มติดตามเฉพาะแถวที่สถานะ = ยืนยันแล้ว",
        "rows": rows.to_dict(orient="records"),
    }
