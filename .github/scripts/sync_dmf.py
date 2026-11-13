#!/usr/bin/env python3
"""
sync_dmf.py - Headless ETL Pipeline for DMF Hydrocarbon Data Sync
Executed via GitHub Actions (scheduled / workflow_dispatch) or CLI.
Extracts, validates, cleans, maps, and normalizes domestic production & sales data.
Outputs clean static JSON for Next.js frontend and Excel flat tables for PTIT analysts.
"""

import os
import sys
import re
import io
import json
import glob
import time
import hashlib
import datetime
import math
from pathlib import Path

import openpyxl
import pandas as pd

# Ensure UTF-8 stdout for Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def clean_for_json(data):
    """Recursively clean data structures to ensure 100% valid JSON (no NaN or Infinity)."""
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_for_json(v) for v in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
        return data
    elif pd.isna(data):
        return None
    return data

# Path configurations
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Input Master Files
MASTER_MAPPING_FILE = REPO_ROOT / "master_mapping.xlsx"
SALE_MAPPING_FILE = REPO_ROOT / "sale_master_mapping.xlsx"
FANG_MASTER_JSON = REPO_ROOT / "fang_production_master.json"
FANG_MASTER_XLSX = REPO_ROOT / "fang_production_master.xlsx"

# Output Locations
DATA_DIR = REPO_ROOT / "data"
FRONTEND_DATA_DIR = REPO_ROOT / "frontend" / "public" / "data"
STANDALONE_PUBLIC_DATA_DIR = Path("D:/ptit-dashboard-next/public/data")
STANDALONE_DATA_DIR = Path("D:/ptit-dashboard-next/data")
EXCEL_OUTPUT_DIR = REPO_ROOT / "output"

PRODUCTION_JSON = DATA_DIR / "production_master.json"
SALES_JSON = DATA_DIR / "sales_master.json"
MANIFEST_JSON = DATA_DIR / "sync_manifest.json"

EXCEL_PROD_OUTPUT = EXCEL_OUTPUT_DIR / "petroleum_production_flat_table.xlsx"
EXCEL_SALE_OUTPUT = EXCEL_OUTPUT_DIR / "petroleum_sale_flat_table.xlsx"

# Import live stream module if in path
sys.path.insert(0, str(REPO_ROOT))
try:
    import dmf_live_stream as dmf
except ImportError:
    dmf = None
try:
    import field_mapping
except ImportError:
    field_mapping = None

# Thai Month References
THAI_MONTHS = [
    'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
    'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
]
MONTH_ORDER = {m: i + 1 for i, m in enumerate(THAI_MONTHS)}
DAYS_IN_MONTH = {
    'มกราคม': 31, 'กุมภาพันธ์': 28, 'มีนาคม': 31, 'เมษายน': 30,
    'พฤษภาคม': 31, 'มิถุนายน': 30, 'กรกฎาคม': 31, 'สิงหาคม': 31,
    'กันยายน': 30, 'ตุลาคม': 31, 'พฤศจิกายน': 30, 'ธันวาคม': 31
}

def get_days_in_month(month_name, year_val=2569):
    """Accurate days count with leap-year (29 Feb) handling."""
    try:
        y_int = int(year_val)
        y_ce = y_int - 543 if y_int > 2400 else y_int
    except Exception:
        y_ce = 2026
    m_clean = str(month_name).strip()
    if m_clean == 'กุมภาพันธ์':
        if (y_ce % 4 == 0 and y_ce % 100 != 0) or (y_ce % 400 == 0):
            return 29
        return 28
    return DAYS_IN_MONTH.get(m_clean, 30)

def clean_number(val):
    if val is None or val == '':
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        clean_str = re.sub(r'[, \t\n]', '', val)
        try:
            return float(clean_str)
        except ValueError:
            return 0.0
    return 0.0

def normalize_text(text):
    if not text:
        return ''
    return re.sub(r'\s+', ' ', str(text)).strip()

def get_merged_cell_value(ws, row, col):
    for rng in ws.merged_cells.ranges:
        if row >= rng.min_row and row <= rng.max_row and col >= rng.min_col and col <= rng.max_col:
            return ws.cell(rng.min_row, rng.min_col).value
    return ws.cell(row, col).value

def load_master_mapping():
    if os.path.exists(MASTER_MAPPING_FILE):
        return pd.read_excel(MASTER_MAPPING_FILE)
    cols = [
        "Lookup_Key", "พื้นที่", "แปลง_ไฟล์ดิบ", "แหล่ง_ไฟล์ดิบ",
        "PTIT_Region", "PTIT_Operator_Field", "PTIT_Order",
        "ผู้ดำเนินการ", "แอ่งปิโตรเลียม", "ประเภทสัญญา"
    ]
    return pd.DataFrame(columns=cols)

def load_sale_master_mapping():
    if os.path.exists(SALE_MAPPING_FILE):
        return pd.read_excel(SALE_MAPPING_FILE)
    cols = ["แหล่ง_ไฟล์ดิบ", "พื้นที่", "ผู้ดำเนินการ", "แอ่งปิโตรเลียม", "ประเภทสัญญา", "หมายเหตุ"]
    return pd.DataFrame(columns=cols)

def load_fang_master():
    default_data = {
        "2569": {
            "มกราคม": 0.0, "กุมภาพันธ์": 0.0, "มีนาคม": 0.0, "เมษายน": 0.0,
            "พฤษภาคม": 0.0, "มิถุนายน": 610.4, "กรกฎาคม": 0.0, "สิงหาคม": 0.0,
            "กันยายน": 0.0, "ตุลาคม": 0.0, "พฤศจิกายน": 0.0, "ธันวาคม": 0.0
        }
    }
    if os.path.exists(FANG_MASTER_XLSX):
        try:
            wb = openpyxl.load_workbook(FANG_MASTER_XLSX, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if len(rows) > 1:
                res = {}
                hdr = [str(c or '').strip() for c in rows[0]]
                idx_y = hdr.index("ปี") if "ปี" in hdr else 0
                idx_m = hdr.index("เดือน") if "เดือน" in hdr else 2
                idx_val = len(hdr) - 1
                for i, h in enumerate(hdr):
                    if "ค่าน้ำมันดิบ" in h or "BPD" in h:
                        idx_val = i
                        break
                for r in rows[1:]:
                    if r[idx_y] is not None and r[idx_m] is not None:
                        y = str(r[idx_y]).strip()
                        m = str(r[idx_m]).strip()
                        v = float(r[idx_val]) if r[idx_val] is not None and str(r[idx_val]).replace('.', '', 1).isdigit() else 0.0
                        if y not in res:
                            res[y] = {}
                        res[y][m] = v
                if res:
                    return res
        except Exception:
            pass

    if os.path.exists(FANG_MASTER_JSON):
        try:
            with open(FANG_MASTER_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_data

def inject_fang_to_dataframe(df_source):
    if df_source is None or df_source.empty:
        return df_source
    df_clean = df_source[df_source.get('ผู้ดำเนินการ', '') != 'Defence Energy Department'].copy()
    fang_data = load_fang_master()
    fang_rows = []
    years_in_data = [str(y) for y in df_clean['ปี'].dropna().unique().tolist()] if 'ปี' in df_clean.columns else ['2569']

    for y_str in years_in_data:
        y_fang = fang_data.get(y_str, {})
        for m_name, m_ord in MONTH_ORDER.items():
            val = float(y_fang.get(m_name, 0.0))
            if val > 0:
                y_val = int(y_str) if y_str.isdigit() else y_str
                days_cnt = get_days_in_month(m_name, y_val)
                fang_rows.append({
                    'ปี': y_val,
                    'เดือน': m_name,
                    'ลำดับเดือน': m_ord,
                    'พื้นที่': 'บนบก',
                    'PTIT_Region': 'Onshore',
                    'PTIT_Operator_Field': 'Defence Energy Department / Fang',
                    'PTIT_Order': 13,
                    'ผู้ดำเนินการ': 'Defence Energy Department',
                    'แอ่งปิโตรเลียม': 'Fang Basin',
                    'ประเภทสัญญา': 'DEDP',
                    'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': 0.0,
                    'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 0.0,
                    'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': 0.0,
                    'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 0.0,
                    'น้ำมันดิบ (บาร์เรล/วัน)': val,
                    'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': val,
                    'จำนวนวันที่ผลิต': days_cnt,
                    'หมายเหตุ': 'ข้อมูลจากกรมการพลังงานทหาร (DEDP)',
                    'แปลง_ไฟล์ดิบ': 'Fang',
                    'แหล่ง_ไฟล์ดิบ': 'Fang',
                    'Lookup_Key': 'บนบก_Fang_Fang',
                    'ไฟล์ที่มา': 'DEDP_Fang_Verified'
                })

    if fang_rows:
        df_fang = pd.DataFrame(fang_rows)
        for col in df_clean.columns:
            if col not in df_fang.columns:
                df_fang[col] = None
        return pd.concat([df_clean, df_fang], ignore_index=True)
    return df_clean

def parse_excel_file(file_input, filename_label):
    wb = openpyxl.load_workbook(file_input, data_only=True)
    ws = wb.active

    header_row_idx = None
    for r in range(1, min(30, ws.max_row + 1)):
        row_values = [normalize_text(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
        if any('พื้นที่' in v for v in row_values) and any('แปลง' in v for v in row_values):
            header_row_idx = r
            break

    if header_row_idx is None:
        raise ValueError(f"ไม่พบหัวตารางในไฟล์ {filename_label}")

    month_name, year_val = '', '2569'
    for r in range(1, header_row_idx):
        for c in range(1, ws.max_column + 1):
            val = str(ws.cell(r, c).value or '')
            match = re.search(r'เดือน\s*([^\s]+)\s*ปี\s*(\d+)', val)
            if match:
                month_name, year_val = match.group(1), match.group(2)
                break
        if month_name:
            break

    col_map = {}
    for c in range(1, ws.max_column + 1):
        top = get_merged_cell_value(ws, header_row_idx - 1, c)
        top = normalize_text(top)
        sub = normalize_text(ws.cell(header_row_idx, c).value)
        full = f"{top} {sub}".strip()

        if 'พื้นที่' in sub:
            col_map['area'] = c
        elif 'แปลง' in sub:
            col_map['block'] = c
        elif 'แหล่ง' in sub:
            col_map['field'] = c
        elif 'จำนวนวัน' in sub or 'วันผลิต' in sub or 'days' in sub.lower():
            col_map['days'] = c
        elif 'หมายเหตุ' in sub:
            col_map['notes'] = c
        elif 'เทียบเท่า' in full or 'เทียบเท่า' in sub:
            if 'เหลว' in full or 'คอนเดนเสท' in full:
                col_map['cond_boed'] = c
            elif 'ก๊าซ' in full:
                col_map['gas_boed'] = c
        elif 'น้ำมันดิบ' in full and 'เทียบเท่า' not in full:
            col_map['crude_bpd'] = c
        elif 'ก๊าซ' in full and any(u in full for u in ['ล้านลบ', 'mmscfd']):
            col_map['gas_mmscfd'] = c
        elif ('เหลว' in full or 'คอนเดนเสท' in full) and 'เทียบเท่า' not in full:
            col_map['cond_bpd'] = c

    area_col = col_map.get('area', 1)
    block_col = col_map.get('block', 2)
    field_col = col_map.get('field', 3)

    records = []
    for r in range(header_row_idx + 1, ws.max_row + 1):
        area_val = normalize_text(ws.cell(r, area_col).value)
        if not area_val or any(k in area_val for k in ['รวมอัตรา', 'รายงานปริมาณ', 'หมายเหตุ']):
            continue

        raw_block = normalize_text(ws.cell(r, block_col).value)
        raw_field = normalize_text(ws.cell(r, field_col).value)

        gas_mmscfd = clean_number(ws.cell(r, col_map.get('gas_mmscfd')).value) if 'gas_mmscfd' in col_map else 0.0
        gas_boed = clean_number(ws.cell(r, col_map.get('gas_boed')).value) if 'gas_boed' in col_map else 0.0
        cond_bpd = clean_number(ws.cell(r, col_map.get('cond_bpd')).value) if 'cond_bpd' in col_map else 0.0
        cond_boed = clean_number(ws.cell(r, col_map.get('cond_boed')).value) if 'cond_boed' in col_map else 0.0
        crude_bpd = clean_number(ws.cell(r, col_map.get('crude_bpd')).value) if 'crude_bpd' in col_map else 0.0
        total_boed = gas_boed + cond_boed + crude_bpd

        days = clean_number(ws.cell(r, col_map.get('days')).value) if 'days' in col_map else 0.0
        notes = normalize_text(ws.cell(r, col_map.get('notes')).value) if 'notes' in col_map else ''

        records.append({
            'Lookup_Key': f"{area_val}_{raw_block}_{raw_field}",
            'ปี': int(year_val) if year_val.isdigit() else year_val,
            'เดือน': month_name,
            'ลำดับเดือน': MONTH_ORDER.get(month_name, 99),
            'พื้นที่': area_val,
            'แปลง_ไฟล์ดิบ': raw_block,
            'แหล่ง_ไฟล์ดิบ': raw_field,
            'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': gas_mmscfd,
            'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': gas_boed,
            'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': cond_bpd,
            'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': cond_boed,
            'น้ำมันดิบ (บาร์เรล/วัน)': crude_bpd,
            'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': total_boed,
            'จำนวนวันที่ผลิต': int(days) if days else 0,
            'หมายเหตุ': notes,
            'ไฟล์ที่มา': filename_label
        })

    return pd.DataFrame(records)

def parse_sales_file(file_input, filename_label):
    wb = openpyxl.load_workbook(file_input, data_only=True)
    ws = wb.active

    row2_val = str(ws.cell(2, 1).value or '')
    month_name, year_val = '', '2569'
    for m in THAI_MONTHS:
        if m in row2_val:
            month_name = m
            break
    ymatch = re.search(r'(\d{4})', row2_val)
    if ymatch:
        year_val = ymatch.group(1)

    days_cnt = get_days_in_month(month_name, year_val)
    current_product = None
    records = []

    for r in range(4, ws.max_row + 1):
        c1 = str(ws.cell(r, 1).value or '').strip()
        c2 = ws.cell(r, 2).value
        c3 = ws.cell(r, 3).value
        c4 = ws.cell(r, 4).value
        c5 = ws.cell(r, 5).value

        if c1 in ['ก๊าซธรรมชาติ', 'ก๊าซธรรมชาติเหลว', 'น้ำมันดิบ']:
            current_product = c1
            continue

        if not c1 or c1 in ['แหล่ง', 'รวมทั้งหมด'] or 'ปริมาณ' in str(c2) or 'ล้าน' in str(c2) or 'บาร์เรล' in str(c2):
            continue

        prod_type = current_product
        if 'LPG' in c1:
            prod_type = 'ก๊าซปิโตรเลียมเหลว (LPG)'

        val = clean_number(c4)
        royalty = clean_number(c5)

        mmscf = None
        mmbtu = None
        bbl = None
        kg = None
        rate_daily_vol = None
        rate_daily_heat = None
        rate_daily_bpd = None
        wellhead_price = 0.0
        wellhead_unit = ''
        wellhead_gas_mmscf = None
        heating_val = None

        if prod_type == 'ก๊าซธรรมชาติ':
            mmscf = clean_number(c2)
            mmbtu = clean_number(c3)
            rate_daily_vol = mmscf / days_cnt if days_cnt > 0 else 0.0
            rate_daily_heat = mmbtu / days_cnt if days_cnt > 0 else 0.0
            wellhead_price = val / mmbtu if mmbtu > 0 else 0.0
            wellhead_unit = 'บาท/MMBTU'
            wellhead_gas_mmscf = val / mmscf if mmscf > 0 else 0.0
            heating_val = mmbtu / mmscf if mmscf > 0 else 0.0
            unit_str = 'ล้าน ลบ.ฟุต & ล้านบีทียู'
            v_main = mmscf

        elif prod_type == 'ก๊าซปิโตรเลียมเหลว (LPG)':
            c3_val = clean_number(c3)
            c2_val = clean_number(c2)
            kg = c3_val if c3_val > 0 else c2_val
            rate_daily_vol = kg / days_cnt if days_cnt > 0 else 0.0
            wellhead_price = val / kg if kg > 0 else 0.0
            wellhead_unit = 'บาท/กก.'
            unit_str = 'กิโลกรัม'
            v_main = kg

        elif prod_type in ['ก๊าซธรรมชาติเหลว', 'น้ำมันดิบ']:
            bbl = clean_number(c2)
            rate_daily_bpd = bbl / days_cnt if days_cnt > 0 else 0.0
            wellhead_price = val / bbl if bbl > 0 else 0.0
            wellhead_unit = 'บาท/บาร์เรล'
            unit_str = 'บาร์เรล'
            v_main = bbl

        royalty_pct = (royalty / val * 100) if val > 0 else 0.0

        rec = {
            'ปี': year_val,
            'เดือน': month_name,
            'ลำดับเดือน': MONTH_ORDER.get(month_name, 99),
            'ประเภทปิโตรเลียม': prod_type,
            'แหล่ง_ไฟล์ดิบ': c1,
            'หน่วยปริมาณ': unit_str,
            'ปริมาณการขาย_หน่วยหลัก': v_main,
            'ปริมาณการขาย_MMSCF': mmscf,
            'ปริมาณการขาย_MMBTU': mmbtu,
            'ปริมาณการขาย_บาร์เรล': bbl,
            'ปริมาณการขาย_กิโลกรัม': kg,
            'ปริมาณการขายเฉลี่ย_MMSCFD': rate_daily_vol if prod_type == 'ก๊าซธรรมชาติ' else None,
            'ปริมาณความร้อนเฉลี่ย_MMBTUD': rate_daily_heat if prod_type == 'ก๊าซธรรมชาติ' else None,
            'ปริมาณการขายเฉลี่ย_BPD': rate_daily_bpd if prod_type in ['ก๊าซธรรมชาติเหลว', 'น้ำมันดิบ'] else None,
            'ค่าความร้อน_Heating_Value_BTU_per_SCF': heating_val,
            'มูลค่าการขาย_บาท': val,
            'ค่าภาคหลวง_บาท': royalty,
            'ราคาปากหลุม_Wellhead_Price': wellhead_price,
            'หน่วยราคาปากหลุม': wellhead_unit,
            'ราคาปากหลุม_ก๊าซ_บาทต่อMMSCF': wellhead_gas_mmscf,
            'อัตราค่าภาคหลวงที่แท้จริง_Pct': royalty_pct,
            'ราคาเฉลี่ยต่อหน่วย_บาท': wellhead_price,
            'ไฟล์ที่มา': filename_label
        }
        records.append(rec)

    return pd.DataFrame(records)

def build_12month_matrix(df_wide, metric_col, days_dict):
    """
    Construct official PTIT 12-month matrix format with monthly columns,
    daily average, and cumulative total for a given metric.
    """
    active_months = [m for m in THAI_MONTHS if m in df_wide['เดือน'].unique()]
    
    # Pivot: Index = [PTIT_Region, PTIT_Operator_Field, PTIT_Order], Columns = เดือน
    pivot_df = df_wide.pivot_table(
        index=['PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'],
        columns='เดือน',
        values=metric_col,
        aggfunc='sum'
    ).reset_index()

    # Re-order columns
    col_order = ['PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'] + [m for m in THAI_MONTHS if m in pivot_df.columns]
    pivot_df = pivot_df[[c for c in col_order if c in pivot_df.columns]]
    
    # Calculate Year Average and Cumulative Total
    month_cols = [m for m in THAI_MONTHS if m in pivot_df.columns]
    total_active_days = sum(days_dict.get(m, 30) for m in month_cols)
    
    def calc_row_stats(row):
        total_vol = 0.0
        for m in month_cols:
            val = row.get(m, 0.0)
            if pd.notna(val):
                days = days_dict.get(m, 30)
                total_vol += float(val) * days
        avg_rate = total_vol / total_active_days if total_active_days > 0 else 0.0
        # For gas: BCF (Billion cubic feet) / For liquids: MMbbl (Million barrels)
        cum_metric = (total_vol / 1000.0) if 'ล้าน' in metric_col else (total_vol / 1_000_000.0)
        return pd.Series({'เฉลี่ยทั้งปี': avg_rate, 'สะสมทั้งปี': cum_metric})

    stats_df = pivot_df.apply(calc_row_stats, axis=1)
    pivot_df['เฉลี่ยทั้งปี'] = stats_df['เฉลี่ยทั้งปี']
    pivot_df['สะสมทั้งปี'] = stats_df['สะสมทั้งปี']

    # Sort by PTIT_Region (Onshore first), then PTIT_Order
    pivot_df['is_onshore'] = pivot_df['PTIT_Region'].apply(lambda x: 0 if str(x).strip().lower() == 'onshore' else 1)
    pivot_df = pivot_df.sort_values(by=['is_onshore', 'PTIT_Order']).drop(columns=['is_onshore'])
    pivot_df = pivot_df.fillna(0.0)
    
    return pivot_df


# ---------------------------------------------------------------------------
# Multi-year sync: per-year cache of parsed DMF files + per-year outputs
# ---------------------------------------------------------------------------
CACHE_DIR = DATA_DIR / "cache"
YEARS_INDEX_NAME = "years_index.json"
# DMF ปรับตัวเลขย้อนหลังได้ จึงดาวน์โหลดปีล่าสุดและปีก่อนหน้าใหม่ทุกครั้ง ส่วนปีเก่ากว่านั้นใช้แคช
RECENT_YEARS_REFRESH = 2
FULL_REFRESH = os.environ.get('FORCE_REFRESH', '').strip().lower() in ('1', 'true', 'yes')
DOWNLOAD_DELAY_SEC = float(os.environ.get('DMF_DOWNLOAD_DELAY', '0.5'))


def df_to_columnar(df):
    """Compact JSON layout {columns, rows} — avoids repeating Thai keys on every record."""
    clean = df.copy()
    for col in clean.select_dtypes(include=['float', 'int']).columns:
        clean[col] = clean[col].fillna(0.0)
    clean = clean.astype(object).where(pd.notna(clean), '')
    return clean_for_json({'columns': list(clean.columns), 'rows': clean.values.tolist()})


def columnar_to_df(payload):
    return pd.DataFrame(payload.get('rows', []), columns=payload.get('columns', []))


def write_json(path, payload, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        if compact:
            json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(payload, f, ensure_ascii=False, indent=2)


def load_year_cache(kind):
    """{year_be: DataFrame} of raw parsed records cached from previous runs."""
    out = {}
    for p in sorted((CACHE_DIR / kind).glob('*.json')):
        if p.stem.isdigit():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    out[int(p.stem)] = columnar_to_df(json.load(f))
            except Exception as ex:
                print(f"   [WARN] Corrupt cache {p.name}: {ex}")
    return out


def collect_monthly(kind, items, fetch_fn, parse_fn, year_is_str):
    """
    items: [(year_be, month, dmf_year_arg)]. Downloads months missing from the cache, plus every month of the
    most recent RECENT_YEARS_REFRESH years (or everything when FULL_REFRESH). Returns all raw records.
    """
    cache = load_year_cache(kind)
    if items:
        latest_year = max(y for y, _, _ in items)
        refresh_years = set(range(latest_year - RECENT_YEARS_REFRESH + 1, latest_year + 1))
    else:
        print(f"   [{kind}] No DMF inventory — using {len(cache)} cached years only")
        refresh_years = set()
    changed, failed, downloaded = set(), [], 0

    for y_be, m_num, dmf_year in sorted(items):
        cached = cache.get(y_be)
        has_month = cached is not None and not cached.empty and (cached['ลำดับเดือน'].astype(int) == m_num).any()
        if has_month and not FULL_REFRESH and y_be not in refresh_years:
            continue
        try:
            buf, fname = fetch_fn(dmf_year, m_num)
            df_m = parse_fn(buf, f"DMF_{fname}")
            downloaded += 1
        except Exception as ex:
            failed.append(f"{m_num}/{y_be}")
            print(f"   [WARN] {kind} {m_num}/{y_be}: {ex}")
            continue
        finally:
            time.sleep(DOWNLOAD_DELAY_SEC)
        if df_m.empty:
            failed.append(f"{m_num}/{y_be}")
            print(f"   [WARN] {kind} {m_num}/{y_be}: file parsed to 0 rows — keeping cached data")
            continue
        # Trust the DMF URL for the period; the sheet title is only a cross-check
        parsed_months = set(df_m['ลำดับเดือน'].astype(int))
        if parsed_months != {m_num}:
            print(f"   [WARN] {kind} {m_num}/{y_be}: sheet says month {sorted(parsed_months)} — using URL month")
        df_m['ลำดับเดือน'] = m_num
        df_m['เดือน'] = THAI_MONTHS[m_num - 1]
        df_m['ปี'] = str(y_be) if year_is_str else y_be
        base = cache.get(y_be)
        if base is not None and not base.empty:
            base = base[base['ลำดับเดือน'].astype(int) != m_num]
            df_m = pd.concat([base, df_m], ignore_index=True)
        cache[y_be] = df_m.sort_values('ลำดับเดือน', kind='stable').reset_index(drop=True)
        changed.add(y_be)
        # Persist after every month so an interrupted backfill resumes where it stopped
        write_json(CACHE_DIR / kind / f"{y_be}.json", df_to_columnar(cache[y_be]), compact=True)
        print(f"   [OK] {kind} {m_num}/{y_be}: {len(df_m) - (len(base) if base is not None else 0)} rows", flush=True)

    print(f"   [{kind}] {len(cache)} years in cache · downloaded {downloaded} files · "
          f"updated years {sorted(changed) or '-'} · failed {len(failed)}")
    if failed:
        print(f"   [{kind}] failed months: {', '.join(failed[:40])}{' ...' if len(failed) > 40 else ''}")

    frames = []
    for df in cache.values():
        if df.empty:
            continue
        df = df.copy()
        df['ปี'] = df['ปี'].astype(int).astype(str) if year_is_str else df['ปี'].astype(int)
        df['ลำดับเดือน'] = df['ลำดับเดือน'].astype(int)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def discover_inventory():
    """All-years DMF inventory -> ([(year_be, month, arg)], [(year_be, month, arg)], is_live)."""
    if dmf is None:
        return [], [], False
    print("[DMF] Discovering every year/month published on dmf.go.th ...")
    inv = dmf.get_dmf_all_years_inventory()
    for err in inv.get('errors', []):
        print(f"   [WARN] inventory: {err}")
    if not inv.get('production') and not inv.get('sales'):
        print("   [WARN] All-years discovery failed; falling back to current-year inventory")
        inv = dmf.get_dmf_online_inventory(timeout=10)
    prod = [(int(i['year_be']), int(i['month']), int(i['year_be'])) for i in inv.get('production', [])]
    sales = [(int(i['year_ce']) + 543, int(i['month']), int(i['year_ce'])) for i in inv.get('sales', [])]
    return prod, sales, bool(inv.get('is_live'))


def local_file_items():
    """Last-resort fallback when DMF is unreachable and no cache exists: files bundled in the repo."""
    prod, sales = [], []
    for pf in sorted(glob.glob(str(REPO_ROOT / "createpetroleum_*_*.xlsx"))):
        m = re.search(r'createpetroleum_(\d{4})_(\d+)\.xlsx', os.path.basename(pf))
        if m:
            prod.append((int(m.group(1)), int(m.group(2)), int(m.group(1))))
    for sf in sorted(glob.glob(str(REPO_ROOT / "Sale" / "salevalue_*_*.xlsx"))):
        m = re.search(r'salevalue_(\d{4})_(\d+)\.xlsx', os.path.basename(sf))
        if m:
            sales.append((int(m.group(1)) + 543, int(m.group(2)), int(m.group(1))))
    return prod, sales


def fetch_production(year_be, m_num):
    if dmf:
        return dmf.stream_dmf_production_bytes(year_be, m_num)
    loc = REPO_ROOT / f"createpetroleum_{year_be}_{m_num}.xlsx"
    with open(loc, 'rb') as f:
        return io.BytesIO(f.read()), loc.name


def fetch_sales(year_ce, m_num):
    if dmf:
        return dmf.stream_dmf_sales_bytes(year_ce, m_num)
    loc = REPO_ROOT / "Sale" / f"salevalue_{year_ce}_{m_num:02d}.xlsx"
    with open(loc, 'rb') as f:
        return io.BytesIO(f.read()), loc.name


def enrich_production(df_raw_prod, df_master):
    master_cols = ['Lookup_Key', 'PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order', 'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา']
    master_cols = [c for c in master_cols if c in df_master.columns]
    master = df_master[master_cols].drop_duplicates('Lookup_Key')
    df = pd.merge(df_raw_prod, master, on='Lookup_Key', how='left')

    unmapped = df.loc[df['PTIT_Region'].isna(), 'Lookup_Key'].nunique()
    if unmapped:
        print(f"   [INFO] {unmapped} field keys are not in master_mapping.xlsx (region inferred from พื้นที่)")
    # Older fields are often missing from master_mapping — infer region from DMF's own area column
    area_region = df['พื้นที่'].map(lambda a: 'Onshore' if 'บนบก' in str(a) else 'Offshore')
    df['PTIT_Region'] = df['PTIT_Region'].fillna(area_region)
    df['PTIT_Operator_Field'] = df['PTIT_Operator_Field'].fillna(df['แหล่ง_ไฟล์ดิบ'])
    for col in ['ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา']:
        df[col] = df[col].fillna('ยังไม่ระบุ')
    df['PTIT_Order'] = df['PTIT_Order'].fillna(99).astype(int)

    df = inject_fang_to_dataframe(df)

    # Tracking group across renames/splits — confirmed rows of field_group_mapping.xlsx only
    lookup = field_mapping.confirmed_group_lookup(field_mapping.load_mapping()) if field_mapping else {}
    names = df['แหล่ง_ไฟล์ดิบ'].fillna('').astype(str).str.strip()
    df['กลุ่มติดตาม'] = names.map(lambda n: lookup.get(n, n))
    return df.sort_values(
        by=['ปี', 'ลำดับเดือน', 'พื้นที่', 'PTIT_Order'],
        ascending=[True, True, False, True]
    ).reset_index(drop=True)


def frame_for_json(df):
    out = df.copy()
    for col in out.select_dtypes(include=['float', 'int']).columns:
        out[col] = out[col].fillna(0.0)
    return out.fillna('')


def build_production_payload(df_year):
    """Same schema as the original single-year production_master.json."""
    active_months = [m for m in THAI_MONTHS if m in df_year['เดือน'].unique()]
    year_be = int(df_year['ปี'].iloc[0])
    days_dict = {m: get_days_in_month(m, year_be) for m in active_months}

    metrics_map = {
        'gas_mmscfd': ('ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'MMSCFD'),
        'condensate_bpd': ('ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 'BPD'),
        'crude_bpd': ('น้ำมันดิบ (บาร์เรล/วัน)', 'BPD'),
        'total_boed': ('รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)', 'BOED')
    }
    matrices = {}
    for m_key, (col_name, unit_lbl) in metrics_map.items():
        if col_name in df_year.columns:
            mat_df = build_12month_matrix(df_year, col_name, days_dict)
            matrices[m_key] = {'column_name': col_name, 'unit': unit_lbl, 'rows': mat_df.to_dict(orient='records')}

    latest_month = active_months[-1]
    latest_df = df_year[df_year['เดือน'] == latest_month]
    kpis = {
        'latest_month': latest_month,
        'reporting_year_be': year_be,
        'reporting_year_ce': year_be - 543,
        'active_months': active_months,
        'latest_gas_mmscfd': round(float(latest_df['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)'].sum()), 2),
        'latest_cond_bpd': round(float(latest_df['ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)'].sum()), 2),
        'latest_crude_bpd': round(float(latest_df['น้ำมันดิบ (บาร์เรล/วัน)'].sum()), 2),
        'latest_boed': round(float(latest_df['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum()), 2),
        'total_active_fields': int(df_year['PTIT_Operator_Field'].nunique()),
        'total_concessions': int(df_year['แปลง_ไฟล์ดิบ'].nunique()),
        'total_operators': int(df_year['ผู้ดำเนินการ'].nunique())
    }

    return clean_for_json({
        'metadata': {
            'title': 'PTIT Focus Statistics - Domestic Petroleum Production',
            'source': 'Department of Mineral Fuels (DMF), Defence Energy Department (DEDP)',
            'publisher': 'Petroleum Institute of Thailand',
            'sync_timestamp': datetime.datetime.now().isoformat(),
            'record_count': len(df_year),
            'active_months': active_months
        },
        'kpis': kpis,
        'matrices': matrices,
        'flat_records': frame_for_json(df_year).to_dict(orient='records')
    })


def enrich_sales(df_raw_sales, df_sale_master):
    master = df_sale_master.drop_duplicates('แหล่ง_ไฟล์ดิบ') if 'แหล่ง_ไฟล์ดิบ' in df_sale_master.columns else df_sale_master
    df = pd.merge(df_raw_sales, master, on='แหล่ง_ไฟล์ดิบ', how='left')
    for col in ['พื้นที่', 'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา']:
        if col not in df.columns:
            df[col] = None
        df[col] = df[col].fillna('ไม่ระบุ')
    df['_y'] = df['ปี'].astype(int)
    df = df.sort_values(['_y', 'ลำดับเดือน', 'ประเภทปิโตรเลียม', 'แหล่ง_ไฟล์ดิบ']).drop(columns=['_y'])
    return df.reset_index(drop=True)


def build_sales_payload(df_year):
    total_val_thb = float(df_year['มูลค่าการขาย_บาท'].sum())
    total_royalty_thb = float(df_year['ค่าภาคหลวง_บาท'].sum())
    avg_royalty_pct = (total_royalty_thb / total_val_thb * 100) if total_val_thb > 0 else 0.0
    return clean_for_json({
        'metadata': {
            'title': 'PTIT Focus Statistics - Domestic Petroleum Sales & Royalty',
            'source': 'Department of Mineral Fuels (DMF)',
            'publisher': 'Petroleum Institute of Thailand',
            'sync_timestamp': datetime.datetime.now().isoformat(),
            'record_count': len(df_year)
        },
        'kpis': {
            'total_sales_value_thb': total_val_thb,
            'total_sales_value_million_thb': round(total_val_thb / 1_000_000.0, 2),
            'total_royalty_thb': total_royalty_thb,
            'total_royalty_million_thb': round(total_royalty_thb / 1_000_000.0, 2),
            'effective_royalty_rate_pct': round(avg_royalty_pct, 2)
        },
        'flat_records': frame_for_json(df_year).to_dict(orient='records')
    })


def months_by_year(df):
    if df is None or df.empty:
        return {}
    grp = df.groupby(df['ปี'].astype(int))['ลำดับเดือน'].apply(lambda s: sorted({int(v) for v in s}))
    return {str(y): months for y, months in grp.sort_index(ascending=False).items()}


def write_excel(path, sheets):
    try:
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=name, index=False)
        print(f"   [OK] Wrote Excel: {path}")
    except Exception as ex:
        print(f"   [WARN] Could not write Excel {path.name}: {ex}")


def run_etl():
    print("[START] PTIT Hydrocarbon ETL Pipeline (all DMF years)...")
    print(f"   Full refresh: {FULL_REFRESH}")
    t0 = time.time()

    for d in (DATA_DIR, FRONTEND_DATA_DIR, EXCEL_OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Discover what DMF has published (every year)
    prod_items, sale_items, is_live = discover_inventory()
    print(f"   DMF Status: {'ONLINE (Live Portal)' if is_live else 'OFFLINE / FALLBACK'}")
    print(f"   Production months on DMF: {len(prod_items)} · Sales months on DMF: {len(sale_items)}")
    if not prod_items and not (CACHE_DIR / 'production').exists():
        prod_items = local_file_items()[0]
    if not sale_items and not (CACHE_DIR / 'sales').exists():
        sale_items = local_file_items()[1]

    # 2. Extract (cached per year) & transform
    print("[PROD] Collecting production months...")
    df_raw_prod = collect_monthly('production', prod_items, fetch_production, parse_excel_file, year_is_str=False)
    print("[SALE] Collecting sales months...")
    df_raw_sales = collect_monthly('sales', sale_items, fetch_sales, parse_sales_file, year_is_str=True)

    target_dirs = [DATA_DIR, FRONTEND_DATA_DIR]
    public_dirs = [FRONTEND_DATA_DIR]
    skip_standalone = os.environ.get('PTIT_SKIP_STANDALONE', '').strip() == '1'
    if STANDALONE_PUBLIC_DATA_DIR.parent.parent.exists() and not skip_standalone:
        target_dirs.extend([STANDALONE_PUBLIC_DATA_DIR, STANDALONE_DATA_DIR])
        public_dirs.append(STANDALONE_PUBLIC_DATA_DIR)

    prod_result, sales_result = {}, {}
    df_prod, df_sales = pd.DataFrame(), pd.DataFrame()

    if not df_raw_prod.empty:
        df_master = load_master_mapping()
        df_prod = enrich_production(df_raw_prod, df_master)
        latest_prod_year = int(df_prod['ปี'].max())
        df_latest = df_prod[df_prod['ปี'] == latest_prod_year].reset_index(drop=True)
        prod_result = build_production_payload(df_latest)
        write_excel(EXCEL_PROD_OUTPUT, {'Flat_Wide': df_latest, 'Master_Mapping': df_master})
        write_excel(EXCEL_OUTPUT_DIR / "petroleum_production_flat_table_all_years.xlsx",
                    {'Flat_Wide_All_Years': df_prod, 'Master_Mapping': df_master})
        for pub in public_dirs:
            for y, df_y in df_prod.groupby('ปี'):
                write_json(pub / 'production' / f"{int(y)}.json", df_to_columnar(frame_for_json(df_y)), compact=True)

    if not df_raw_sales.empty:
        df_sale_master = load_sale_master_mapping()
        df_sales = enrich_sales(df_raw_sales, df_sale_master)
        sale_years = df_sales['ปี'].astype(int)
        latest_sale_year = int(sale_years.max())
        df_latest_s = df_sales[sale_years == latest_sale_year].reset_index(drop=True)
        sales_result = build_sales_payload(df_latest_s)
        write_excel(EXCEL_SALE_OUTPUT, {'Sale_Flat_Table': df_latest_s, 'Sale_Master_Mapping': df_sale_master})
        write_excel(EXCEL_OUTPUT_DIR / "petroleum_sale_flat_table_all_years.xlsx",
                    {'Sale_Flat_All_Years': df_sales, 'Sale_Master_Mapping': df_sale_master})
        for pub in public_dirs:
            for y, df_y in df_sales.groupby(sale_years):
                write_json(pub / 'sales' / f"{int(y)}.json", df_to_columnar(frame_for_json(df_y)), compact=True)

    # 3. Latest-year masters (same schema as before) + index of every available year
    years_index = {
        'generated': datetime.datetime.now().isoformat(),
        'production': months_by_year(df_prod),
        'sales': months_by_year(df_sales),
    }
    for target_dir in target_dirs:
        try:
            write_json(target_dir / "production_master.json", prod_result)
            write_json(target_dir / "sales_master.json", sales_result)
            write_json(target_dir / YEARS_INDEX_NAME, years_index)
            if field_mapping:
                df_map = field_mapping.merge_with_inventory(field_mapping.load_mapping(), field_mapping.field_inventory())
                write_json(target_dir / "field_groups.json", field_mapping.public_payload(df_map))
        except Exception as ex:
            print(f"   [WARN] Could not write JSON to {target_dir}: {ex}")

    manifest = {
        'timestamp': datetime.datetime.now().isoformat(),
        'execution_duration_sec': round(time.time() - t0, 2),
        'status': 'success',
        'is_live_dmf': is_live,
        'production_records': len(prod_result.get('flat_records', [])),
        'sales_records': len(sales_result.get('flat_records', [])),
        'production_years': len(years_index['production']),
        'sales_years': len(years_index['sales']),
        'production_records_all_years': len(df_prod),
        'sales_records_all_years': len(df_sales),
        'latest_production_month': prod_result.get('kpis', {}).get('latest_month', 'N/A'),
        'checksum_prod': hashlib.md5(json.dumps(prod_result).encode('utf-8')).hexdigest(),
        'checksum_sale': hashlib.md5(json.dumps(sales_result).encode('utf-8')).hexdigest()
    }
    for target_dir in target_dirs:
        try:
            write_json(target_dir / "sync_manifest.json", manifest)
        except Exception as ex:
            print(f"   [WARN] Could not write manifest to {target_dir}: {ex}")

    print(f"[SUCCESS] ETL Pipeline completed in {manifest['execution_duration_sec']}s!")
    print(f"   Production: {manifest['production_years']} years, {len(df_prod)} records")
    print(f"   Sales: {manifest['sales_years']} years, {len(df_sales)} records")


if __name__ == '__main__':
    run_etl()
