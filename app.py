import os
import re
import glob
import io
import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import dmf_live_stream as dmf

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="PTIT Focus - ระบบแปลงข้อมูลการผลิตปิโตรเลียม",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# Design System: Siam Hydrocarbon Intelligence (Crystal Aqua Glass)
# ----------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Hanken+Grotesk:wght@400;500;600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Manrope:wght@600;700;800&display=swap');

/* Global Font & Canvas Base Background */
html, body, [class*="css"], .stApp {
    font-family: 'Hanken Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: radial-gradient(135% 100% at 50% 0%, #E0F2FE 0%, #F0F9FF 35%, #F8FAFC 70%, #EFF6FF 100%) !important;
    background-attachment: fixed !important;
    color: #0F172A !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 700 !important;
    color: #0F172A !important;
    letter-spacing: -0.015em !important;
}

/* Glass Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.76) !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    border-right: 1px solid rgba(186, 230, 253, 0.5) !important;
    box-shadow: 4px 0 24px rgba(2, 62, 138, 0.04) !important;
}

/* Vitreous Glass Panels */
.glass-panel {
    background: rgba(255, 255, 255, 0.72) !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.85) !important;
    box-shadow: 
        0 8px 32px 0 rgba(31, 38, 135, 0.06),
        0 2px 6px 0 rgba(0, 0, 0, 0.02),
        inset 0 1px 1px 0 rgba(255, 255, 255, 0.9) !important;
    border-radius: 18px !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
}

/* Vitreous Metric Cards (st.metric) */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 20px rgba(2, 62, 138, 0.04), inset 0 1px 1px rgba(255, 255, 255, 0.95) !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Manrope', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #0F172A !important;
    font-variant-numeric: tabular-nums !important;
}

/* Glass Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(224, 242, 254, 0.45) !important;
    padding: 6px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(186, 230, 253, 0.6) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 18px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: #334155 !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: #0284C7 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
}

/* Primary Action Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Action Buttons */
.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    color: #0F172A !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* Live Pulse Animation */
@keyframes live-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.35; transform: scale(1.2); }
}

.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    margin-right: 6px;
    animation: live-pulse 1.8s infinite ease-in-out;
    box-shadow: 0 0 8px #10B981;
}

/* Crisp Clean DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(186, 230, 253, 0.6) !important;
    box-shadow: 0 4px 20px rgba(2, 62, 138, 0.03) !important;
}

/* Executive A4 Landscape Print Engine */
@media print {
    @page {
        size: A4 landscape;
        margin: 8mm 10mm 8mm 10mm;
    }
    header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], .stTabs [data-baseweb="tab-list"], .no-print {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        background: #FFFFFF !important;
    }
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    .ptit-letterhead {
        border-radius: 0 !important;
        box-shadow: none !important;
        border: 1px solid #CBD5E1 !important;
        page-break-inside: avoid;
    }
    .ptit-letterhead table {
        page-break-inside: auto;
    }
    .ptit-letterhead tr {
        page-break-inside: avoid;
        page-break-after: auto;
    }
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_FILE = os.path.join(BASE_DIR, "master_mapping.xlsx")
_local_sale = os.path.join(BASE_DIR, "Sale")
_parent_sale = os.path.normpath(os.path.join(BASE_DIR, "..", "Sale"))
SALE_DIR = _local_sale if os.path.exists(_local_sale) else _parent_sale
SALE_MASTER_FILE = os.path.join(BASE_DIR, "sale_master_mapping.xlsx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "petroleum_production_flat_table.xlsx")
DEFAULT_SALE_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "petroleum_sale_flat_table.xlsx")

THAI_MONTHS = [
    'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
    'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
]
MONTH_ORDER = {m: i+1 for i, m in enumerate(THAI_MONTHS)}
DAYS_IN_MONTH = {
    'มกราคม': 31, 'กุมภาพันธ์': 28, 'มีนาคม': 31, 'เมษายน': 30,
    'พฤษภาคม': 31, 'มิถุนายน': 30, 'กรกฎาคม': 31, 'สิงหาคม': 31,
    'กันยายน': 30, 'ตุลาคม': 31, 'พฤศจิกายน': 30, 'ธันวาคม': 31
}

def get_days_in_month(month_name, year_val=2569):
    """คำนวณจำนวนวันในเดือนอย่างถูกต้อง พร้อมตรวจเช็ครอบปีอธิกสุรทิน (Leap Year) 29 ก.พ."""
    try:
        y_int = int(year_val)
        y_ce = y_int - 543 if y_int > 2400 else y_int
    except Exception:
        y_ce = 2026
    if str(month_name).strip() == 'กุมภาพันธ์':
        if (y_ce % 4 == 0 and y_ce % 100 != 0) or (y_ce % 400 == 0):
            return 29
        return 28
    return DAYS_IN_MONTH.get(str(month_name).strip(), 30)


# ----------------------------------------------------
# Helper Functions & Crystal Aqua Plotly Theme
# ----------------------------------------------------
def apply_crystal_aqua_theme(fig):
    """ตกแต่งกราฟ Plotly ให้มีสไตล์โปร่งแสง คมชัด ตามแบบฉบับ Crystal Aqua Glass"""
    fig.update_layout(
        font=dict(family="Manrope, Inter, sans-serif", color="#0F172A"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=45, b=20),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(15, 23, 42, 0.05)",
            linecolor="rgba(15, 23, 42, 0.12)",
            tickfont=dict(family="Manrope, Inter, sans-serif", size=11, color="#475569")
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(15, 23, 42, 0.05)",
            linecolor="rgba(15, 23, 42, 0.12)",
            tickfont=dict(family="JetBrains Mono, monospace", size=11, color="#475569")
        )
    )
    return fig

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
    """ดึงค่าจากเซลล์ที่ถูก Merge ใน Excel ได้ถูกต้อง ไม่รั่วข้ามคอลัมน์"""
    for rng in ws.merged_cells.ranges:
        if row >= rng.min_row and row <= rng.max_row and col >= rng.min_col and col <= rng.max_col:
            return ws.cell(rng.min_row, rng.min_col).value
    return ws.cell(row, col).value

def load_master_mapping():
    if os.path.exists(MASTER_FILE):
        return pd.read_excel(MASTER_FILE)
    else:
        cols = [
            "Lookup_Key", "พื้นที่", "แปลง_ไฟล์ดิบ", "แหล่ง_ไฟล์ดิบ",
            "PTIT_Region", "PTIT_Operator_Field", "PTIT_Order",
            "ผู้ดำเนินการ", "แอ่งปิโตรเลียม", "ประเภทสัญญา"
        ]
        return pd.DataFrame(columns=cols)

def save_master_mapping(df):
    df['Lookup_Key'] = df['พื้นที่'].astype(str) + '_' + df['แปลง_ไฟล์ดิบ'].astype(str) + '_' + df['แหล่ง_ไฟล์ดิบ'].astype(str)
    df.to_excel(MASTER_FILE, index=False)

def load_sale_master_mapping():
    if os.path.exists(SALE_MASTER_FILE):
        return pd.read_excel(SALE_MASTER_FILE)
    else:
        cols = ["แหล่ง_ไฟล์ดิบ", "พื้นที่", "ผู้ดำเนินการ", "แอ่งปิโตรเลียม", "ประเภทสัญญา", "หมายเหตุ"]
        return pd.DataFrame(columns=cols)

def save_sale_master_mapping(df):
    df.to_excel(SALE_MASTER_FILE, index=False)

# ----------------------------------------------------
# DEDP Fang Crude Oil Master Storage & Functions
# ----------------------------------------------------
FANG_MASTER_FILE = os.path.join(BASE_DIR, "fang_production_master.json")
FANG_EXCEL_FILE = os.path.join(BASE_DIR, "fang_production_master.xlsx")

def save_fang_master(data):
    """บันทึกข้อมูลค่าน้ำมันดิบแหล่งฝางลงทั้ง JSON และ Excel (fang_production_master.xlsx) ในโฟลเดอร์เดียวกัน"""
    try:
        with open(FANG_MASTER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Fang_Production"
        ws.append(["ปี", "ลำดับเดือน", "เดือน", "ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)"])
        for y_str, m_dict in data.items():
            for m_name in THAI_MONTHS:
                ws.append([str(y_str), MONTH_ORDER.get(m_name, 99), m_name, float(m_dict.get(m_name, 0.0))])
        wb.save(FANG_EXCEL_FILE)
    except Exception as e:
        pass

def load_fang_master():
    """โหลดข้อมูลค่าน้ำมันดิบแหล่งฝางจาก Excel หรือ JSON ในโฟลเดอร์ หากไม่มีให้สร้างค่าเริ่มต้น"""
    default_data = {
        "2569": {
            "มกราคม": 0.0, "กุมภาพันธ์": 0.0, "มีนาคม": 0.0, "เมษายน": 0.0,
            "พฤษภาคม": 0.0, "มิถุนายน": 610.4, "กรกฎาคม": 0.0, "สิงหาคม": 0.0,
            "กันยายน": 0.0, "ตุลาคม": 0.0, "พฤศจิกายน": 0.0, "ธันวาคม": 0.0
        }
    }
    # 1. ลองโหลดจาก Excel ก่อน
    if os.path.exists(FANG_EXCEL_FILE):
        try:
            wb = openpyxl.load_workbook(FANG_EXCEL_FILE, data_only=True)
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

    # 2. ลองโหลดจาก JSON
    if os.path.exists(FANG_MASTER_FILE):
        try:
            with open(FANG_MASTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    save_fang_master(default_data)
    return default_data

def get_fang_value(year_str, month_str):
    """ดึงค่าน้ำมันดิบแหล่งฝางสำหรับปีและเดือนที่กำหนด"""
    data = load_fang_master()
    y_data = data.get(str(year_str), {})
    return float(y_data.get(str(month_str), 0.0))

def set_fang_value(year_str, month_str, val):
    """อัปเดตและบันทึกค่าน้ำมันดิบแหล่งฝางสำหรับปีและเดือนที่กำหนด"""
    data = load_fang_master()
    y_str = str(year_str)
    if y_str not in data:
        data[y_str] = {}
    data[y_str][str(month_str)] = float(val)
    save_fang_master(data)

def inject_fang_to_dataframe(df_source):
    """ผนวกข้อมูลค่าน้ำมันดิบแหล่งฝาง (DEDP) จากฐานข้อมูล Master เข้ากับ DataFrame เพื่อให้แสดงผลครบถ้วนทุกรายงานและแดชบอร์ด"""
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
                    'จำนวนวันที่ผลิต': 30,
                    'หมายเหตุ': 'ข้อมูลจากกรมการพลังงานทหาร (DEDP)',
                    'แปลง_ไฟล์ดิบ': 'Fang',
                    'แหล่ง_ไฟล์ดิบ': 'Fang',
                    'Lookup_Key': 'บนบก_Fang_Fang',
                    'ไฟล์ที่มา': 'DEDP_Fang_Manual_Entry'
                })

    if fang_rows:
        df_fang = pd.DataFrame(fang_rows)
        for col in df_clean.columns:
            if col not in df_fang.columns:
                df_fang[col] = None
        return pd.concat([df_clean, df_fang], ignore_index=True)
    return df_clean

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
            # LPG รายงานใน c3 หรือ c2 (หน่วย kgs)
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

def parse_excel_file(file_input, filename_label):
    wb = openpyxl.load_workbook(file_input, data_only=True)
    ws = wb.active

    # 1. Find Header Row using Anchor keywords
    header_row_idx = None
    for r in range(1, min(30, ws.max_row + 1)):
        row_values = [normalize_text(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
        if any('พื้นที่' in v for v in row_values) and any('แปลง' in v for v in row_values):
            header_row_idx = r
            break

    if header_row_idx is None:
        raise ValueError(f"ไม่พบหัวตารางในไฟล์ {filename_label}")

    # 2. Extract Month & Year from rows above header
    month_name, year_val = '', ''
    for r in range(1, header_row_idx):
        for c in range(1, ws.max_column + 1):
            val = str(ws.cell(r, c).value or '')
            match = re.search(r'เดือน\s*([^\s]+)\s*ปี\s*(\d+)', val)
            if match:
                month_name, year_val = match.group(1), match.group(2)
                break
        if month_name:
            break

    # 3. Dynamic & Precise Column Mapping
    col_map = {}
    for c in range(1, ws.max_column + 1):
        top = get_merged_cell_value(ws, header_row_idx - 1, c)
        top = normalize_text(top)
        sub = normalize_text(ws.cell(header_row_idx, c).value)
        full = f"{top} {sub}".strip()

        # Identifier columns
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

        # BOE Equivalent columns (Check 'เทียบเท่า' FIRST before checking 'น้ำมันดิบ')
        elif 'เทียบเท่า' in full or 'เทียบเท่า' in sub:
            if 'เหลว' in full or 'คอนเดนเสท' in full:
                col_map['cond_boed'] = c
            elif 'ก๊าซ' in full:
                col_map['gas_boed'] = c

        # Pure Crude Oil (Must NOT contain 'เทียบเท่า')
        elif 'น้ำมันดิบ' in full and 'เทียบเท่า' not in full:
            col_map['crude_bpd'] = c

        # Natural Gas (MMSCFD)
        elif 'ก๊าซ' in full and any(u in full for u in ['ล้านลบ', 'mmscfd']):
            col_map['gas_mmscfd'] = c

        # Condensate (BPD - Must NOT contain 'เทียบเท่า')
        elif ('เหลว' in full or 'คอนเดนเสท' in full) and 'เทียบเท่า' not in full:
            col_map['cond_bpd'] = c

    # 4. Extract Records
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

def export_ptit_styled_excel(month_name, year_val, onshore_rows, offshore_rows, onshore_sub, offshore_sub, grand_tot, theme="imperial"):
    """สร้างไฟล์ Excel พร้อมจัดฟอร์แมตสไตล์ Luxury Executive ตามมาตรฐาน PTIT Focus Statistics"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Domestic_Production_{month_name}"
    ws.views.sheetView[0].showGridLines = True

    # Theme definitions
    theme_palettes = {
        'imperial': {
            'title_bg': '1F1610', 'title_fg': 'FFFFFF',
            'sub_bg': '332216', 'sub_fg': 'E8D5B5',
            'hdr_bg': '24180E', 'hdr_fg': 'FFFFFF',
            'subhdr_bg': '2E2218', 'subhdr_fg': 'F5EBE1',
            'sec_bg': '7A5328', 'sec_fg': 'FFFFFF',
            'zebra_bg': 'FAF7F2',
            'total_bg': 'EFE5D5', 'total_fg': '1C1917',
            'border_color': 'E5DFD5',
            'tot_border_top': '7A5328', 'tot_border_bot': '451A03'
        },
        'navy': {
            'title_bg': '0A1128', 'title_fg': 'FFFFFF',
            'sub_bg': '14213D', 'sub_fg': 'E2BA55',
            'hdr_bg': '0F172A', 'hdr_fg': 'FFFFFF',
            'subhdr_bg': '162038', 'subhdr_fg': 'F1F5F9',
            'sec_bg': '1E3A8A', 'sec_fg': 'FFFFFF',
            'zebra_bg': 'F8FAFC',
            'total_bg': 'EFF6FF', 'total_fg': '0F172A',
            'border_color': 'E2E8F0',
            'tot_border_top': '1E3A8A', 'tot_border_bot': '0F172A'
        },
        'emerald': {
            'title_bg': '06281E', 'title_fg': 'FFFFFF',
            'sub_bg': '0B3B2D', 'sub_fg': '6EE7B7',
            'hdr_bg': '0F281E', 'hdr_fg': 'FFFFFF',
            'subhdr_bg': '132620', 'subhdr_fg': 'ECFDF5',
            'sec_bg': '047857', 'sec_fg': 'FFFFFF',
            'zebra_bg': 'F0FDF4',
            'total_bg': 'ECFDF5', 'total_fg': '064E3B',
            'border_color': 'D1FAE5',
            'tot_border_top': '047857', 'tot_border_bot': '064E3B'
        }
    }
    t = theme_palettes.get(theme, theme_palettes['imperial'])

    font_title = Font(name="Calibri", size=13, bold=True, color=t['title_fg'])
    font_sub_title = Font(name="Calibri", size=10, bold=True, color=t['sub_fg'])
    font_main = Font(name="Calibri", size=10, color="1C1917")
    font_header = Font(name="Calibri", size=10.5, bold=True, color=t['hdr_fg'])
    font_subhdr = Font(name="Calibri", size=10, bold=True, color=t['subhdr_fg'])
    font_sec = Font(name="Calibri", size=10, bold=True, color=t['sec_fg'])
    font_total = Font(name="Calibri", size=11, bold=True, color=t['total_fg'])
    font_notes = Font(name="Calibri", size=9, italic=True, color="64748B")

    fill_title = PatternFill(start_color=t['title_bg'], end_color=t['title_bg'], fill_type="solid")
    fill_sub_title = PatternFill(start_color=t['sub_bg'], end_color=t['sub_bg'], fill_type="solid")
    fill_header = PatternFill(start_color=t['hdr_bg'], end_color=t['hdr_bg'], fill_type="solid")
    fill_subhdr = PatternFill(start_color=t['subhdr_bg'], end_color=t['subhdr_bg'], fill_type="solid")
    fill_section = PatternFill(start_color=t['sec_bg'], end_color=t['sec_bg'], fill_type="solid")
    fill_zebra = PatternFill(start_color=t['zebra_bg'], end_color=t['zebra_bg'], fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_total = PatternFill(start_color=t['total_bg'], end_color=t['total_bg'], fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=t['border_color']),
        right=Side(style='thin', color=t['border_color']),
        top=Side(style='thin', color=t['border_color']),
        bottom=Side(style='thin', color=t['border_color'])
    )
    total_border = Border(
        top=Side(style='thin', color=t['tot_border_top']),
        bottom=Side(style='double', color=t['tot_border_bot']),
        left=Side(style='thin', color=t['border_color']),
        right=Side(style='thin', color=t['border_color'])
    )

    align_right = Alignment(horizontal='right', vertical='center')
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')

    num_fmt = '#,##0.0;(#,##0.0);"-";@'

    # Row 1: Official Masthead
    ws.merge_cells('A1:D1')
    ws['A1'] = "PETROLEUM INSTITUTE OF THAILAND (PTIT)"
    ws['A1'].font = font_title
    ws['A1'].fill = fill_title
    ws['A1'].alignment = align_center
    ws.row_dimensions[1].height = 25

    # Row 2: Subtitle
    ws.merge_cells('A2:D2')
    ws['A2'] = f"DOMESTIC PETROLEUM PRODUCTION REPORT - {str(month_name).upper()} {year_val}"
    ws['A2'].font = font_sub_title
    ws['A2'].fill = fill_sub_title
    ws['A2'].alignment = align_center
    ws.row_dimensions[2].height = 18

    # Row 3: Blank gap
    ws.row_dimensions[3].height = 7

    # Row 4: Header Row 1
    ws.merge_cells('B4:D4')
    ws['B4'] = "Domestic Production"
    ws['B4'].font = font_header
    ws['B4'].fill = fill_header
    ws['B4'].alignment = align_center

    ws['A4'] = f"Operator / Field ({month_name} {year_val})"
    ws['A4'].font = font_header
    ws['A4'].fill = fill_header
    ws['A4'].alignment = align_center
    ws.row_dimensions[4].height = 24

    # Row 5: Header Row 2
    headers = [
        ("A5", "Operator / Field"),
        ("B5", "Natural Gas\n(MMSCFD)"),
        ("C5", "Condensate\n(BPD)"),
        ("D5", "Crude\n(BPD)")
    ]
    for cell_ref, text in headers:
        ws[cell_ref] = text
        ws[cell_ref].font = font_subhdr
        ws[cell_ref].fill = fill_subhdr
        ws[cell_ref].alignment = align_center
        ws[cell_ref].border = thin_border
    ws.row_dimensions[5].height = 30

    current_row = 6

    def write_sec(sec_name, items, sub):
        nonlocal current_row
        # Section Header Row
        ws.cell(row=current_row, column=1, value=sec_name).font = font_sec
        ws.cell(row=current_row, column=1).fill = fill_section
        ws.cell(row=current_row, column=1).alignment = align_left
        ws.cell(row=current_row, column=1).border = thin_border

        for c_idx, val in enumerate(sub, start=2):
            cell = ws.cell(row=current_row, column=c_idx, value=val)
            cell.font = font_sec
            cell.fill = fill_section
            cell.alignment = align_right
            cell.number_format = num_fmt
            cell.border = thin_border
        ws.row_dimensions[current_row].height = 22
        current_row += 1

        # Data Rows with Zebra Striping
        for idx, item in enumerate(items):
            row_fill = fill_zebra if (idx % 2 == 1) else fill_white
            ws.cell(row=current_row, column=1, value="    " + str(item['Operator_Field'])).font = font_main
            ws.cell(row=current_row, column=1).fill = row_fill
            ws.cell(row=current_row, column=1).alignment = align_left
            ws.cell(row=current_row, column=1).border = thin_border

            for c_idx, val in enumerate([item['Gas'], item['Cond'], item['Crude']], start=2):
                cell = ws.cell(row=current_row, column=c_idx, value=val if val >= 0.05 else (0.0 if val > 0 else 0))
                cell.font = font_main
                cell.fill = row_fill
                cell.alignment = align_right
                cell.number_format = num_fmt
                cell.border = thin_border
            ws.row_dimensions[current_row].height = 20
            current_row += 1

    write_sec("Onshore", onshore_rows, onshore_sub)
    write_sec("Offshore", offshore_rows, offshore_sub)

    # Total Row
    ws.cell(row=current_row, column=1, value="Total").font = font_total
    ws.cell(row=current_row, column=1).fill = fill_total
    ws.cell(row=current_row, column=1).alignment = align_center
    ws.cell(row=current_row, column=1).border = total_border

    for c_idx, val in enumerate(grand_tot, start=2):
        cell = ws.cell(row=current_row, column=c_idx, value=val)
        cell.font = font_total
        cell.fill = fill_total
        cell.alignment = align_right
        cell.number_format = num_fmt
        cell.border = total_border
    ws.row_dimensions[current_row].height = 24
    current_row += 2

    # Notes & Source
    ws.cell(row=current_row, column=1, value='Note:   Data shown as "0.0" means figure less than 0.05.').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='Source: Department of Mineral Fuels (DMF),  Defence Energy Department (DEDP)').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='Official Publication: Petroleum Institute of Thailand (PTIT Focus Statistics)').font = font_notes

    ws.column_dimensions['A'].width = 56
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 18

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

# ----------------------------------------------------
# Annual Report Calculation & Excel Export Helpers
# ----------------------------------------------------



def export_annual_styled_excel(year_val, onshore_items, offshore_items, onshore_sub, offshore_sub, grand_tot, active_months, theme="imperial"):
    """สร้างไฟล์ Excel รายงานประจำปีสไตล์ Luxury Executive พร้อม Daily Avg และ Cumulative Total"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Annual_Production_{year_val}"
    ws.views.sheetView[0].showGridLines = True

    theme_palettes = {
        'imperial': {
            'title_bg': '1F1610', 'title_fg': 'FFFFFF', 'sub_bg': '332216', 'sub_fg': 'E8D5B5',
            'hdr_bg': '24180E', 'hdr_fg': 'FFFFFF', 'subhdr_bg': '2E2218', 'subhdr_fg': 'F5EBE1',
            'sec_bg': '7A5328', 'sec_fg': 'FFFFFF', 'zebra_bg': 'FAF7F2', 'total_bg': 'EFE5D5',
            'total_fg': '1C1917', 'border_color': 'E5DFD5', 'tot_border_top': '7A5328', 'tot_border_bot': '451A03'
        },
        'navy': {
            'title_bg': '0A1128', 'title_fg': 'FFFFFF', 'sub_bg': '14213D', 'sub_fg': 'E2BA55',
            'hdr_bg': '0F172A', 'hdr_fg': 'FFFFFF', 'subhdr_bg': '162038', 'subhdr_fg': 'F1F5F9',
            'sec_bg': '1E3A8A', 'sec_fg': 'FFFFFF', 'zebra_bg': 'F8FAFC', 'total_bg': 'EFF6FF',
            'total_fg': '0F172A', 'border_color': 'E2E8F0', 'tot_border_top': '1E3A8A', 'tot_border_bot': '0F172A'
        },
        'emerald': {
            'title_bg': '06281E', 'title_fg': 'FFFFFF', 'sub_bg': '0B3B2D', 'sub_fg': '6EE7B7',
            'hdr_bg': '0F281E', 'hdr_fg': 'FFFFFF', 'subhdr_bg': '132620', 'subhdr_fg': 'ECFDF5',
            'sec_bg': '047857', 'sec_fg': 'FFFFFF', 'zebra_bg': 'F0FDF4', 'total_bg': 'ECFDF5',
            'total_fg': '064E3B', 'border_color': 'D1FAE5', 'tot_border_top': '047857', 'tot_border_bot': '064E3B'
        }
    }
    t = theme_palettes.get(theme, theme_palettes['imperial'])

    font_title = Font(name="Calibri", size=13, bold=True, color=t['title_fg'])
    font_sub_title = Font(name="Calibri", size=10, bold=True, color=t['sub_fg'])
    font_main = Font(name="Calibri", size=10, color="1C1917")
    font_header = Font(name="Calibri", size=10, bold=True, color=t['hdr_fg'])
    font_subhdr = Font(name="Calibri", size=9.5, bold=True, color=t['subhdr_fg'])
    font_sec = Font(name="Calibri", size=10, bold=True, color=t['sec_fg'])
    font_total = Font(name="Calibri", size=10.5, bold=True, color=t['total_fg'])
    font_notes = Font(name="Calibri", size=9, italic=True, color="64748B")

    fill_title = PatternFill(start_color=t['title_bg'], end_color=t['title_bg'], fill_type="solid")
    fill_sub_title = PatternFill(start_color=t['sub_bg'], end_color=t['sub_bg'], fill_type="solid")
    fill_header = PatternFill(start_color=t['hdr_bg'], end_color=t['hdr_bg'], fill_type="solid")
    fill_subhdr = PatternFill(start_color=t['subhdr_bg'], end_color=t['subhdr_bg'], fill_type="solid")
    fill_section = PatternFill(start_color=t['sec_bg'], end_color=t['sec_bg'], fill_type="solid")
    fill_zebra = PatternFill(start_color=t['zebra_bg'], end_color=t['zebra_bg'], fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_total = PatternFill(start_color=t['total_bg'], end_color=t['total_bg'], fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=t['border_color']), right=Side(style='thin', color=t['border_color']),
        top=Side(style='thin', color=t['border_color']), bottom=Side(style='thin', color=t['border_color'])
    )
    total_border = Border(
        left=Side(style='thin', color=t['border_color']), right=Side(style='thin', color=t['border_color']),
        top=Side(style='medium', color=t['tot_border_top']), bottom=Side(style='double', color=t['tot_border_bot'])
    )

    # 1. Document Title
    ws.merge_cells('A1:J1')
    c1 = ws['A1']
    c1.value = "PETROLEUM INSTITUTE OF THAILAND"
    c1.font = font_title
    c1.fill = fill_title
    c1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24

    ws.merge_cells('A2:J2')
    c2 = ws['A2']
    c2.value = f"DOMESTIC PETROLEUM PRODUCTION ANNUAL REPORT ({year_val})"
    c2.font = font_sub_title
    c2.fill = fill_sub_title
    c2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

    # Period Info
    ws.merge_cells('A3:J3')
    c3 = ws['A3']
    period_txt = f"Annual Production Summary & Cumulative Output (YTD {len(active_months)} Months: {active_months[0]} - {active_months[-1]} {year_val})" if active_months else f"Annual Production Summary ({year_val})"
    c3.value = period_txt
    c3.font = Font(name="Calibri", size=9.5, italic=True, color="475569")
    c3.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 16

    # 2. Table Headers (Row 4 & 5)
    headers_top = [
        ('A4', 'A5', "Operator / Field"),
        ('B4', 'C4', "Natural Gas"),
        ('D4', 'E4', "Condensate"),
        ('F4', 'G4', "Crude Oil"),
        ('H4', 'I4', "Total Energy Equivalent"),
        ('J4', 'J5', "Share (%)")
    ]
    for start_col, end_col, title in headers_top:
        ws.merge_cells(f"{start_col}:{end_col}")
        cell = ws[start_col]
        cell.value = title
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    headers_sub = [
        ('B5', "Daily (MMSCFD)"), ('C5', "Total (BCF)"),
        ('D5', "Daily (BPD)"), ('E5', "Total (MMbbl)"),
        ('F5', "Daily (BPD)"), ('G5', "Total (MMbbl)"),
        ('H5', "Daily (BOED)"), ('I5', "Total (MMBOE)")
    ]
    for cell_ref, sub_title in headers_sub:
        cell = ws[cell_ref]
        cell.value = sub_title
        cell.font = font_subhdr
        cell.fill = fill_subhdr
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(4, 6):
        for col_idx in range(1, 11):
            ws.cell(row=r, column=col_idx).border = thin_border

    ws.row_dimensions[4].height = 20
    ws.row_dimensions[5].height = 20

    current_row = 6

    def write_section(sec_title, items, sub_vals):
        nonlocal current_row
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=10)
        sec_cell = ws.cell(row=current_row, column=1, value=sec_title)
        sec_cell.font = font_sec
        sec_cell.fill = fill_section
        sec_cell.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[current_row].height = 18
        current_row += 1

        for idx, item in enumerate(items):
            fill = fill_zebra if (idx % 2 == 1) else fill_white
            ws.row_dimensions[current_row].height = 17

            c_name = ws.cell(row=current_row, column=1, value=f"  {item['Operator_Field']}")
            c_name.font = font_main
            c_name.fill = fill
            c_name.border = thin_border

            num_cols = [
                (2, item.get('Gas_Avg', 0.0), '#,##0.0'),
                (3, item.get('Gas_Cum', 0.0), '#,##0.00'),
                (4, item.get('Cond_Avg', 0.0), '#,##0'),
                (5, item.get('Cond_Cum', 0.0), '#,##0.00'),
                (6, item.get('Crude_Avg', 0.0), '#,##0'),
                (7, item.get('Crude_Cum', 0.0), '#,##0.00'),
                (8, item.get('BOED_Avg', 0.0), '#,##0'),
                (9, item.get('BOED_Cum', 0.0), '#,##0.00'),
                (10, item.get('Share_Pct', 0.0) / 100.0, '0.0%')
            ]
            for col_idx, val, num_fmt in num_cols:
                cell = ws.cell(row=current_row, column=col_idx)
                if val is not None and val > 0.0001:
                    cell.value = val
                    cell.number_format = num_fmt
                else:
                    cell.value = "-"
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.font = font_main
                cell.fill = fill
                cell.border = thin_border
            current_row += 1

        # Subtotal
        ws.row_dimensions[current_row].height = 18
        c_sub_label = ws.cell(row=current_row, column=1, value=f"Total {sec_title.split('(')[0].strip()}")
        c_sub_label.font = font_total
        c_sub_label.fill = fill_total
        c_sub_label.border = thin_border

        sub_cols = [
            (2, sub_vals.get('Gas_Avg', 0.0), '#,##0.0'),
            (3, sub_vals.get('Gas_Cum', 0.0), '#,##0.00'),
            (4, sub_vals.get('Cond_Avg', 0.0), '#,##0'),
            (5, sub_vals.get('Cond_Cum', 0.0), '#,##0.00'),
            (6, sub_vals.get('Crude_Avg', 0.0), '#,##0'),
            (7, sub_vals.get('Crude_Cum', 0.0), '#,##0.00'),
            (8, sub_vals.get('BOED_Avg', 0.0), '#,##0'),
            (9, sub_vals.get('BOED_Cum', 0.0), '#,##0.00'),
            (10, sub_vals.get('Share_Pct', 0.0) / 100.0, '0.0%')
        ]
        for col_idx, val, num_fmt in sub_cols:
            cell = ws.cell(row=current_row, column=col_idx)
            if val is not None and val > 0.0001:
                cell.value = val
                cell.number_format = num_fmt
            else:
                cell.value = "-"
                cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = font_total
            cell.fill = fill_total
            cell.border = thin_border
        current_row += 1

    write_section("ONSHORE BASIN", onshore_items, onshore_sub)
    write_section("OFFSHORE GULF OF THAILAND", offshore_items, offshore_sub)

    # Grand Total
    ws.row_dimensions[current_row].height = 20
    c_tot_label = ws.cell(row=current_row, column=1, value="GRAND TOTAL")
    c_tot_label.font = Font(name="Calibri", size=11, bold=True, color=t['total_fg'])
    c_tot_label.fill = fill_total
    c_tot_label.border = total_border

    tot_cols = [
        (2, grand_tot.get('Gas_Avg', 0.0), '#,##0.0'),
        (3, grand_tot.get('Gas_Cum', 0.0), '#,##0.00'),
        (4, grand_tot.get('Cond_Avg', 0.0), '#,##0'),
        (5, grand_tot.get('Cond_Cum', 0.0), '#,##0.00'),
        (6, grand_tot.get('Crude_Avg', 0.0), '#,##0'),
        (7, grand_tot.get('Crude_Cum', 0.0), '#,##0.00'),
        (8, grand_tot.get('BOED_Avg', 0.0), '#,##0'),
        (9, grand_tot.get('BOED_Cum', 0.0), '#,##0.00'),
        (10, 1.0, '0.0%')
    ]
    for col_idx, val, num_fmt in tot_cols:
        cell = ws.cell(row=current_row, column=col_idx)
        cell.value = val
        cell.number_format = num_fmt
        cell.font = Font(name="Calibri", size=11, bold=True, color=t['total_fg'])
        cell.fill = fill_total
        cell.border = total_border
    current_row += 2

    # Footnotes
    ws.cell(row=current_row, column=1, value='Note:   1. Daily rates are weighted averages based on actual operating days in each active reporting month.').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='        2. Cumulative volumes: Natural Gas in BCF (Billion Cubic Feet), Liquids in MMbbl (Million Barrels), Energy in MMBOE.').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='        3. Crude oil includes Sirikit, Offshore fields, and Defence Energy Department (DEDP Fang).').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='Source: Department of Mineral Fuels (DMF), Defence Energy Department (DEDP)').font = font_notes
    current_row += 1
    ws.cell(row=current_row, column=1, value='Official Publication: Petroleum Institute of Thailand (PTIT Focus Statistics)').font = font_notes

    ws.column_dimensions['A'].width = 44
    for c_letter in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        ws.column_dimensions[c_letter].width = 15

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

def export_12month_matrix_excel(year_val, df_matrix, metric_name, unit_label, theme="imperial"):
    """สร้างไฟล์ Excel ตารางเมทริกซ์ 12 เดือน (Jan - Dec) พร้อมค่าเฉลี่ยและยอดสะสมทั้งปี"""
    wb = openpyxl.Workbook()
    ws = wb.active
    clean_title = re.sub(r'[\\/*?:\[\]]', '_', str(metric_name))[:28]
    ws.title = clean_title
    ws.views.sheetView[0].showGridLines = True

    theme_palettes = {
        'imperial': {'hdr_bg': '24180E', 'hdr_fg': 'FFFFFF', 'sec_bg': '7A5328', 'sec_fg': 'FFFFFF', 'total_bg': 'EFE5D5', 'total_fg': '1C1917', 'zebra_bg': 'FAF7F2'},
        'navy': {'hdr_bg': '0F172A', 'hdr_fg': 'FFFFFF', 'sec_bg': '1E3A8A', 'sec_fg': 'FFFFFF', 'total_bg': 'EFF6FF', 'total_fg': '0F172A', 'zebra_bg': 'F8FAFC'},
        'emerald': {'hdr_bg': '0F281E', 'hdr_fg': 'FFFFFF', 'sec_bg': '047857', 'sec_fg': 'FFFFFF', 'total_bg': 'ECFDF5', 'total_fg': '064E3B', 'zebra_bg': 'F0FDF4'}
    }
    t = theme_palettes.get(theme, theme_palettes['imperial'])

    ws.merge_cells('A1:O1')
    ws['A1'].value = "PETROLEUM INSTITUTE OF THAILAND"
    ws['A1'].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color=t['hdr_bg'], end_color=t['hdr_bg'], fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24

    ws.merge_cells('A2:O2')
    ws['A2'].value = f"12-MONTH DOMESTIC PETROLEUM PRODUCTION MATRIX ({year_val}) - {metric_name}"
    ws['A2'].font = Font(name="Calibri", size=10.5, bold=True, color="FFFFFF")
    ws['A2'].fill = PatternFill(start_color=t['sec_bg'], end_color=t['sec_bg'], fill_type="solid")
    ws['A2'].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

    ws.merge_cells('A3:O3')
    ws['A3'].value = f"Primary Rate Unit: {unit_label}"
    ws['A3'].font = Font(name="Calibri", size=9.5, italic=True, color="475569")
    ws['A3'].alignment = Alignment(horizontal="center", vertical="center")

    headers = ['Operator / Field', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.', 'เฉลี่ยทั้งปี', 'สะสมทั้งปี']
    for col_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h_text)
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=t['hdr_bg'], end_color=t['hdr_bg'], fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'), top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1'))
    ws.row_dimensions[4].height = 22

    cur_r = 5
    for idx, r_data in df_matrix.iterrows():
        name_str = str(r_data.get('Operator_Field', ''))
        is_sub = 'Subtotal' in name_str or 'รวม' in name_str
        is_grand = 'GRAND' in name_str.upper() or 'ยอดรวมทั้งประเทศ' in name_str
        fill = PatternFill(start_color=t['total_bg'], end_color=t['total_bg'], fill_type="solid") if (is_sub or is_grand) else (PatternFill(start_color=t['zebra_bg'], end_color=t['zebra_bg'], fill_type="solid") if (idx % 2 == 1) else PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid"))
        font = Font(name="Calibri", size=10, bold=(is_sub or is_grand))

        for col_idx, h_text in enumerate(headers, 1):
            val = r_data.get(h_text, None)
            cell = ws.cell(row=cur_r, column=col_idx)
            cell.font = font
            cell.fill = fill
            cell.border = Border(left=Side(style='thin', color='E2E8F0'), right=Side(style='thin', color='E2E8F0'), top=Side(style='thin', color='E2E8F0'), bottom=Side(style='thin', color='E2E8F0'))
            if col_idx == 1:
                cell.value = str(val) if val is not None else ""
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                if isinstance(val, (int, float)) and val > 0.0001:
                    cell.value = float(val)
                    cell.number_format = '#,##0.0' if 'MMSCF' in unit_label or 'BCF' in str(h_text) else '#,##0'
                else:
                    cell.value = "-"
                    cell.alignment = Alignment(horizontal="center", vertical="center")
        cur_r += 1

    ws.column_dimensions['A'].width = 38
    for c_idx in range(2, 16):
        col_letter = openpyxl.utils.get_column_letter(c_idx)
        ws.column_dimensions[col_letter].width = 13

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

def export_custom_pivot_excel(df_pivot, title="Custom_Pivot_Analysis"):
    """ส่งออกตาราง Pivot Table ที่ User ปรับแต่งเองเป็น Excel สะอาดตา"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as wr:
        df_pivot.to_excel(wr, sheet_name='Pivot_Summary')
        ws = wr.sheets['Pivot_Summary']
        ws.views.sheetView[0].showGridLines = True
        hdr_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        hdr_font = Font(name="Calibri", size=10.5, bold=True, color="FFFFFF")
        for col in ws.iter_cols(min_row=1, max_row=1):
            for cell in col:
                cell.fill = hdr_fill
                cell.font = hdr_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    buf.seek(0)
    return buf

# ----------------------------------------------------
# DMF Live Stream Helpers & Data Processors
# ----------------------------------------------------
@st.cache_data(ttl=120)
def cached_dmf_status():
    return dmf.check_dmf_connection()

@st.cache_data(ttl=300)
def cached_dmf_inventory():
    return dmf.get_dmf_online_inventory()

def process_production_dfs(dfs, save_to_disk=False):
    """รัน ETL แปลง DataFrames การผลิต เข้า Master Model และสร้าง Flat Tables"""
    if not dfs:
        return None
    df_raw_combined = pd.concat(dfs, ignore_index=True)
    df_master = load_master_mapping()

    master_cols_to_join = [
        'Lookup_Key', 'PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order',
        'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา'
    ]
    master_cols_to_join = [c for c in master_cols_to_join if c in df_master.columns]

    df_merged = pd.merge(
        df_raw_combined,
        df_master[master_cols_to_join],
        on='Lookup_Key',
        how='left'
    )
    df_merged['PTIT_Operator_Field'] = df_merged['PTIT_Operator_Field'].fillna(df_merged['แหล่ง_ไฟล์ดิบ'])
    df_merged['ผู้ดำเนินการ'] = df_merged['ผู้ดำเนินการ'].fillna('ยังไม่ระบุ')
    df_merged['แอ่งปิโตรเลียม'] = df_merged['แอ่งปิโตรเลียม'].fillna('ยังไม่ระบุ')
    df_merged['ประเภทสัญญา'] = df_merged['ประเภทสัญญา'].fillna('ยังไม่ระบุ')

    df_merged = df_merged.sort_values(
        by=['ปี', 'ลำดับเดือน', 'พื้นที่', 'PTIT_Order'],
        ascending=[True, True, False, True]
    ).reset_index(drop=True)

    ordered_cols = [
        'ปี', 'เดือน', 'ลำดับเดือน', 'พื้นที่', 'PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order',
        'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา',
        'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
        'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
        'น้ำมันดิบ (บาร์เรล/วัน)', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
        'จำนวนวันที่ผลิต', 'หมายเหตุ', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ', 'Lookup_Key', 'ไฟล์ที่มา'
    ]
    final_cols = [c for c in ordered_cols if c in df_merged.columns]
    df_flat_wide = df_merged[final_cols]

    metric_vars = [
        'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)',
        'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
        'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
        'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
        'น้ำมันดิบ (บาร์เรล/วัน)',
        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
    ]
    id_vars = [c for c in final_cols if c not in metric_vars]
    df_flat_long = pd.melt(
        df_flat_wide,
        id_vars=id_vars,
        value_vars=[c for c in metric_vars if c in df_flat_wide.columns],
        var_name='ประเภทตัวชี้วัด',
        value_name='ปริมาณ'
    )

    df_flat_wide = inject_fang_to_dataframe(df_flat_wide)
    st.session_state['df_flat_wide'] = df_flat_wide
    st.session_state['df_flat_long'] = df_flat_long

    unmapped = df_merged[df_merged['ผู้ดำเนินการ'] == 'ยังไม่ระบุ'][['พื้นที่', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ']].drop_duplicates()
    st.session_state['unmapped'] = unmapped

    if save_to_disk:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        try:
            with pd.ExcelWriter(DEFAULT_OUTPUT_FILE, engine='openpyxl') as writer:
                df_flat_wide.to_excel(writer, sheet_name='Flat_Wide', index=False)
                df_flat_long.to_excel(writer, sheet_name='Flat_Long_Unpivoted', index=False)
                df_master.to_excel(writer, sheet_name='Master_Mapping', index=False)
        except Exception:
            pass

    return df_flat_wide, df_flat_long, unmapped

def process_sales_dfs(parsed_list, save_to_disk=False):
    """รัน ETL แปลง DataFrames ยอดขาย เข้า Sale Master Model และสร้าง Flat Table"""
    if not parsed_list:
        return None
    df_all_sales = pd.concat(parsed_list, ignore_index=True)
    df_sale_master = load_sale_master_mapping()

    df_sales_merged = pd.merge(df_all_sales, df_sale_master, on='แหล่ง_ไฟล์ดิบ', how='left')
    df_sales_merged['พื้นที่'] = df_sales_merged['พื้นที่'].fillna('ไม่ระบุ')
    df_sales_merged['ผู้ดำเนินการ'] = df_sales_merged['ผู้ดำเนินการ'].fillna('ไม่ระบุ')
    df_sales_merged['แอ่งปิโตรเลียม'] = df_sales_merged['แอ่งปิโตรเลียม'].fillna('ไม่ระบุ')
    df_sales_merged['ประเภทสัญญา'] = df_sales_merged['ประเภทสัญญา'].fillna('ไม่ระบุ')

    if 'ราคาปากหลุม_Wellhead_Price' not in df_sales_merged.columns:
        df_sales_merged['ราคาปากหลุม_Wellhead_Price'] = 0.0
        mask_gas = (df_sales_merged['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติ') & (df_sales_merged.get('ปริมาณการขาย_MMBTU', 0) > 0)
        df_sales_merged.loc[mask_gas, 'ราคาปากหลุม_Wellhead_Price'] = df_sales_merged.loc[mask_gas, 'มูลค่าการขาย_บาท'] / df_sales_merged.loc[mask_gas, 'ปริมาณการขาย_MMBTU']
        mask_oil = (df_sales_merged['ประเภทปิโตรเลียม'].isin(['ก๊าซธรรมชาติเหลว', 'น้ำมันดิบ'])) & (df_sales_merged.get('ปริมาณการขาย_บาร์เรล', 0) > 0)
        df_sales_merged.loc[mask_oil, 'ราคาปากหลุม_Wellhead_Price'] = df_sales_merged.loc[mask_oil, 'มูลค่าการขาย_บาท'] / df_sales_merged.loc[mask_oil, 'ปริมาณการขาย_บาร์เรล']

    df_sales_merged['ราคาเฉลี่ยต่อหน่วย_บาท'] = df_sales_merged.get('ราคาปากหลุม_Wellhead_Price', 0.0)

    ordered_sale_cols = [
        'ปี', 'เดือน', 'ลำดับเดือน', 'ประเภทปิโตรเลียม', 'แหล่ง_ไฟล์ดิบ',
        'พื้นที่', 'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา',
        'ปริมาณการขาย_หน่วยหลัก', 'หน่วยปริมาณ',
        'ปริมาณการขาย_MMSCF', 'ปริมาณการขาย_MMBTU',
        'ปริมาณการขาย_บาร์เรล', 'ปริมาณการขาย_กิโลกรัม',
        'ปริมาณการขายเฉลี่ย_MMSCFD', 'ปริมาณความร้อนเฉลี่ย_MMBTUD',
        'ปริมาณการขายเฉลี่ย_BPD',
        'ค่าความร้อน_Heating_Value_BTU_per_SCF',
        'มูลค่าการขาย_บาท', 'ค่าภาคหลวง_บาท',
        'ราคาปากหลุม_Wellhead_Price', 'หน่วยราคาปากหลุม',
        'ราคาปากหลุม_ก๊าซ_บาทต่อMMSCF',
        'อัตราค่าภาคหลวงที่แท้จริง_Pct',
        'ราคาเฉลี่ยต่อหน่วย_บาท',
        'หมายเหตุ', 'ไฟล์ที่มา'
    ]
    final_sale_cols = [c for c in ordered_sale_cols if c in df_sales_merged.columns]
    df_sales_flat = df_sales_merged[final_sale_cols].sort_values(['ลำดับเดือน', 'ประเภทปิโตรเลียม', 'แหล่ง_ไฟล์ดิบ']).reset_index(drop=True)

    st.session_state['df_sale_flat'] = df_sales_flat

    if save_to_disk:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        try:
            with pd.ExcelWriter(DEFAULT_SALE_OUTPUT_FILE, engine='openpyxl') as writer:
                df_sales_flat.to_excel(writer, sheet_name='Sale_Flat_Table', index=False)
                df_sale_master.to_excel(writer, sheet_name='Sale_Master_Mapping', index=False)
        except Exception:
            pass

    return df_sales_flat

# ----------------------------------------------------
# Auto-load existing output data if available & Auth setup
# ----------------------------------------------------
ADMIN_PASSWORD = "ptit2026"
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'viewer'

def run_auto_sync_production(online_items):
    progress_bar = st.sidebar.progress(0, text="กำลังเตรียมการดึงข้อมูลการผลิตสด...")
    items_sorted = sorted(online_items, key=lambda x: (x.get('year_be', 2569), x.get('month', 1)))
    parsed_list = []
    total = len(items_sorted)
    
    for idx, it in enumerate(items_sorted):
        progress_bar.progress(idx / total, text=f"📥 สตรีม {it['label']} ({idx+1}/{total})...")
        try:
            buf, fname = dmf.stream_dmf_production_bytes(it['year_be'], it['month'])
            df_parsed = parse_excel_file(buf, f"DMF_Online_{fname}")
            parsed_list.append(df_parsed)
        except Exception as ex:
            st.sidebar.error(f"เกิดข้อผิดพลาดเดือน {it['label']}: {ex}")
            
    if parsed_list:
        progress_bar.progress(1.0, text="🏷️ กำลังประมวลผล Flat Table...")
        df_wide, df_long, unmapped = process_production_dfs(parsed_list, save_to_disk=True)
        st.session_state['df_flat_wide'] = df_wide
        st.session_state['df_flat_long'] = df_long
        st.session_state['unmapped'] = unmapped
        progress_bar.empty()
        st.toast(f"🎉 อัปเดตข้อมูลการผลิต {total} เดือน ({len(df_wide):,} แถว) บันทึก Flat Table สำเร็จ!", icon="🚀")
        st.rerun()

def run_auto_sync_sales(online_items):
    progress_bar = st.sidebar.progress(0, text="กำลังเตรียมการดึงข้อมูลยอดขายสด...")
    items_sorted = sorted(online_items, key=lambda x: (x.get('year_ce', 2026), x.get('month', 1)))
    parsed_list = []
    total = len(items_sorted)
    
    for idx, it in enumerate(items_sorted):
        progress_bar.progress(idx / total, text=f"📥 สตรีมยอดขาย {it['label']} ({idx+1}/{total})...")
        try:
            buf, fname = dmf.stream_dmf_sales_bytes(it['year_ce'], it['month'])
            df_parsed = parse_sales_file(buf, f"DMF_Online_{fname}")
            parsed_list.append(df_parsed)
        except Exception as ex:
            st.sidebar.error(f"เกิดข้อผิดพลาดเดือน {it['label']}: {ex}")
            
    if parsed_list:
        progress_bar.progress(1.0, text="🏷️ กำลังประมวลผล Flat Table ยอดขาย...")
        df_sales_flat = process_sales_dfs(parsed_list, save_to_disk=True)
        st.session_state['df_sale_flat'] = df_sales_flat
        progress_bar.empty()
        st.toast(f"🎉 อัปเดตข้อมูลยอดขาย {total} เดือน ({len(df_sales_flat):,} แถว) บันทึก Flat Table สำเร็จ!", icon="🚀")
        st.rerun()

if 'df_flat_wide' not in st.session_state and os.path.exists(DEFAULT_OUTPUT_FILE):
    try:
        df_loaded_prod = pd.read_excel(DEFAULT_OUTPUT_FILE, sheet_name='Flat_Wide')
        st.session_state['df_flat_wide'] = inject_fang_to_dataframe(df_loaded_prod)
    except Exception:
        pass

    try:
        st.session_state['df_flat_long'] = pd.read_excel(DEFAULT_OUTPUT_FILE, sheet_name='Flat_Long_Unpivoted')
    except Exception:
        if 'df_flat_wide' in st.session_state:
            df_w = st.session_state['df_flat_wide']
            id_cols = [c for c in ['พื้นที่', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ', 'ปี', 'เดือน', 'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา', 'PTIT_Region', 'PTIT_Operator_Field'] if c in df_w.columns]
            val_cols = [c for c in ['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 'น้ำมันดิบ (บาร์เรล/วัน)', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'] if c in df_w.columns]
            st.session_state['df_flat_long'] = pd.melt(df_w, id_vars=id_cols, value_vars=val_cols, var_name='ผลิตภัณฑ์ปิโตรเลียม', value_name='ปริมาณการผลิตต่อวัน')

if 'df_sale_flat' not in st.session_state and os.path.exists(DEFAULT_SALE_OUTPUT_FILE):
    try:
        st.session_state['df_sale_flat'] = pd.read_excel(DEFAULT_SALE_OUTPUT_FILE, sheet_name='Sale_Flat_Table')
    except Exception:
        pass

# ----------------------------------------------------
# Sidebar Navigation Menu & Domain Router
# ----------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 12px 0;">
    <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: linear-gradient(135deg, #0284C7 0%, #023E8A 100%); border-radius: 12px; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25); margin-bottom: 10px;">
        <span style="font-family: 'Manrope', sans-serif; font-size: 15px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.04em;">PTIT</span>
    </div>
    <h2 style="margin:0; color:#0F172A; font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: -0.01em;">Siam Hydrocarbon</h2>
    <div style="display: inline-block; font-size: 10.5px; font-weight: 700; color: #0284C7; letter-spacing: 0.08em; text-transform: uppercase;">Statistics Intelligence</div>
    <p style="margin:4px 0 0 0; font-size: 12px; color: #475569; font-weight: 500;">สถาบันปิโตรเลียมแห่งประเทศไทย</p>
    <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(186, 230, 253, 0.8), transparent); margin-top: 14px;"></div>
</div>
""", unsafe_allow_html=True)

# Role Switcher Widget
user_role = st.session_state.get('user_role', 'viewer')
if user_role == 'admin':
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, rgba(254, 243, 199, 0.9) 0%, rgba(253, 230, 138, 0.8) 100%); border: 1px solid #F59E0B; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.12);">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 700; color: #92400E; font-size: 13px;">🔑 สิทธิ์ผู้ดูแลระบบ (Admin)</span>
            <span style="background: #F59E0B; color: white; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 6px;">UNLOCKED</span>
        </div>
        <div style="font-size: 11px; color: #78350F; margin-top: 3px;">เข้าถึงฟังก์ชัน Auto Sync, แปลงข้อมูล และ Master Model</div>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("🚪 สลับกลับเป็นโหมด Viewer", use_container_width=True, key="btn_logout_admin"):
        st.session_state['user_role'] = 'viewer'
        st.toast("สลับเป็นโหมด Viewer เรียบร้อย", icon="👥")
        st.rerun()
else:
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, rgba(240, 249, 255, 0.9) 0%, rgba(224, 242, 254, 0.8) 100%); border: 1px solid #BAE6FD; border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 700; color: #0369A1; font-size: 13px;">👥 ผู้ใช้งานทั่วไป (Viewer)</span>
            <span style="background: #0284C7; color: white; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 6px;">VIEW ONLY</span>
        </div>
        <div style="font-size: 11px; color: #475569; margin-top: 3px;">แดชบอร์ดสรุปสถิติ & รายงานทางการ PTIT</div>
    </div>
    """, unsafe_allow_html=True)
    with st.sidebar.expander("🔑 ปลดล็อก Admin (ใส่รหัสผ่าน)", expanded=False):
        pwd_val = st.text_input("รหัสผ่าน:", type="password", key="inp_admin_pwd")
        if st.button("เข้าสู่โหมด Admin", key="btn_login_admin", use_container_width=True):
            if pwd_val == ADMIN_PASSWORD:
                st.session_state['user_role'] = 'admin'
                st.toast("ปลดล็อกโหมด Admin เรียบร้อย!", icon="🎉")
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")

st.sidebar.markdown("### หมวดหมู่สถิติ")

base_options = [
    "การผลิตปิโตรเลียม (DMF Production)",
    "การจำหน่ายและมูลค่า (DMF Sales & Royalty)",
    "การนำเข้า-ส่งออก (Import / Export)",
    "การจัดหาและการใช้พลังงาน (Supply & Demand)"
]
if st.session_state.get('user_role', 'viewer') == 'admin':
    base_options.append("จัดการ Master Data Model รวม")
base_options.append("คู่มือการใช้งาน & เกี่ยวกับระบบ")

data_domain = st.sidebar.radio(
    "เลือกโมดูลที่ต้องการใช้งาน:",
    options=base_options,
    index=0
)

# ----------------------------------------------------
# TIER 3: Petroleum Units & Conversion Toolkit (Killer Feature)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("##### 📐 เครื่องมือ & ตัวแปลงหน่วยปิโตรเลียม")

with st.sidebar.expander("🔄 ตัวแปลงหน่วยปิโตรเลียมทันใจ", expanded=False):
    c_mode = st.selectbox(
        "เลือกประเภทผลิตภัณฑ์ / หน่วย:",
        [
            "ก๊าซธรรมชาติ (MMSCFD)",
            "น้ำมันดิบ & คอนเดนเสท (BPD)",
            "พลังงานรวมเทียบเท่า (BOED)",
            "ก๊าซปริมาณรวม (MMSCF/เดือน)",
            "น้ำมันปริมาณรวม (Barrels/เดือน)"
        ],
        key="sb_calc_mode"
    )
    def_val = 1000.0 if "ก๊าซ" in c_mode or "BOED" in c_mode else 500.0
    c_val = st.number_input(
        "ใส่ตัวเลขที่ต้องการคำนวณ:",
        min_value=0.0,
        value=def_val,
        step=50.0,
        key="sb_calc_val"
    )
    c_days = st.selectbox(
        "จำนวนวันในเดือนที่คำนวณ:",
        [30, 31, 28, 29],
        index=0,
        key="sb_calc_days"
    )

    st.markdown("<div style='height: 1px; background: #E2E8F0; margin: 8px 0 6px 0;'></div>", unsafe_allow_html=True)
    st.caption("📊 **ผลการคำนวณเทียบเท่ามาตรฐาน:**")

    if c_mode == "ก๊าซธรรมชาติ (MMSCFD)":
        boed_val = (c_val * 1_000_000) / 5800.0
        month_mmscf = c_val * c_days
        mmbtu_day = c_val * 1000.0
        st.markdown(f"""
        <div style="background: rgba(2, 132, 199, 0.08); border-radius: 8px; padding: 7px 10px; font-size: 11.5px; border-left: 3px solid #0284C7; line-height: 1.6;">
            • <b>เทียบเท่าน้ำมันดิบ:</b> <span style="font-weight:700; color:#0369A1;">{boed_val:,.1f}</span> BOED<br/>
            • <b>ปริมาณรวมเดือน ({c_days} วัน):</b> <span style="font-weight:700; color:#0F172A;">{month_mmscf:,.1f}</span> MMSCF<br/>
            • <b>ค่าความร้อนโดยประมาณ:</b> <span style="font-weight:700; color:#047857;">{mmbtu_day:,.0f}</span> MMBTU/วัน
        </div>
        """, unsafe_allow_html=True)

    elif c_mode == "น้ำมันดิบ & คอนเดนเสท (BPD)":
        month_bbl = c_val * c_days
        litres_day = c_val * 158.9873
        tonnes_day = c_val / 7.33
        st.markdown(f"""
        <div style="background: rgba(234, 88, 12, 0.08); border-radius: 8px; padding: 7px 10px; font-size: 11.5px; border-left: 3px solid #EA580C; line-height: 1.6;">
            • <b>ปริมาณรวมเดือน ({c_days} วัน):</b> <span style="font-weight:700; color:#C2410C;">{month_bbl:,.0f}</span> Barrels<br/>
            • <b>เทียบเท่าปริมาตร:</b> <span style="font-weight:700; color:#0F172A;">{litres_day:,.0f}</span> ลิตร/วัน<br/>
            • <b>เทียบเท่าน้ำหนัก:</b> <span style="font-weight:700; color:#334155;">{tonnes_day:,.1f}</span> ตัน/วัน (~7.33 bbl/t)
        </div>
        """, unsafe_allow_html=True)

    elif c_mode == "พลังงานรวมเทียบเท่า (BOED)":
        equiv_gas = (c_val * 5800.0) / 1_000_000.0
        month_boe = c_val * c_days
        st.markdown(f"""
        <div style="background: rgba(147, 51, 234, 0.08); border-radius: 8px; padding: 7px 10px; font-size: 11.5px; border-left: 3px solid #9333EA; line-height: 1.6;">
            • <b>หากเป็นก๊าซธรรมชาติ:</b> <span style="font-weight:700; color:#7E22CE;">{equiv_gas:,.2f}</span> MMSCFD<br/>
            • <b>หากเป็นน้ำมันดิบ:</b> <span style="font-weight:700; color:#7E22CE;">{c_val:,.1f}</span> BPD<br/>
            • <b>พลังงานรวมเดือน ({c_days} วัน):</b> <span style="font-weight:700; color:#0F172A;">{month_boe:,.0f}</span> BOE
        </div>
        """, unsafe_allow_html=True)

    elif c_mode == "ก๊าซปริมาณรวม (MMSCF/เดือน)":
        daily_rate = c_val / c_days if c_days > 0 else 0
        boed_val = (daily_rate * 1_000_000) / 5800.0
        st.markdown(f"""
        <div style="background: rgba(2, 132, 199, 0.08); border-radius: 8px; padding: 7px 10px; font-size: 11.5px; border-left: 3px solid #0284C7; line-height: 1.6;">
            • <b>อัตราเฉลี่ยต่อวัน:</b> <span style="font-weight:700; color:#0369A1;">{daily_rate:,.2f}</span> MMSCFD ({c_days} วัน)<br/>
            • <b>เทียบเท่าน้ำมันดิบ:</b> <span style="font-weight:700; color:#0F172A;">{boed_val:,.1f}</span> BOED
        </div>
        """, unsafe_allow_html=True)

    elif c_mode == "น้ำมันปริมาณรวม (Barrels/เดือน)":
        daily_bpd = c_val / c_days if c_days > 0 else 0
        st.markdown(f"""
        <div style="background: rgba(234, 88, 12, 0.08); border-radius: 8px; padding: 7px 10px; font-size: 11.5px; border-left: 3px solid #EA580C; line-height: 1.6;">
            • <b>อัตราเฉลี่ยต่อวัน:</b> <span style="font-weight:700; color:#C2410C;">{daily_bpd:,.1f}</span> BPD ({c_days} วัน)
        </div>
        """, unsafe_allow_html=True)

with st.sidebar.expander("📚 ค่าคงที่ & ตัวคูณอ้างอิง PTIT", expanded=False):
    st.markdown("""
    <div style="font-size: 11px; color: #334155; line-height: 1.7;">
        <b>มาตรฐานสถิติพลังงานสากล & กรมเชื้อเพลิงฯ:</b><br/>
        • <b>1 BOE</b> = 5,800 ลูกบาศก์ฟุต (ก๊าซธรรมชาติ)<br/>
        • <b>1 MMSCFD</b> ≈ 172.41 BOED<br/>
        • <b>1 Barrel (น้ำมัน)</b> = 42 US Gal ≈ 158.987 ลิตร<br/>
        • <b>1 Metric Ton</b> ≈ 7.33 บาร์เรล (API ~34°)<br/>
        • <b>ก๊าซธรรมชาติไทย</b> ≈ 1,000 BTU/scf (~980–1,050)<br/>
        • <b>1 BOE</b> ≈ 5.8 MMBTU
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# TIER 4: System Status & DMF Auto-Sync Panel (Collapsed by default for Viewers)
# ----------------------------------------------------
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ สถานะระบบ & DMF Live Sync", expanded=(user_role == 'admin')):
    # Production & Sales Loaded Telemetry
    if 'df_flat_wide' in st.session_state and not st.session_state['df_flat_wide'].empty:
        df_sb = st.session_state['df_flat_wide']
        loaded_months = len(df_sb['เดือน'].dropna().unique())
        total_rows = len(df_sb)
        st.success(f"**การผลิต:** {loaded_months} เดือน ({total_rows:,} แถว)")
    else:
        st.info("**การผลิต:** ยังไม่พบข้อมูลในระบบ")

    if 'df_sale_flat' in st.session_state and not st.session_state['df_sale_flat'].empty:
        df_s_sb = st.session_state['df_sale_flat']
        l_s_m = len(df_s_sb['เดือน'].dropna().unique())
        t_s_r = len(df_s_sb)
        st.success(f"**การจำหน่าย:** {l_s_m} เดือน ({t_s_r:,} แถว)")
    else:
        st.info("**การจำหน่าย:** ยังไม่พบข้อมูลในระบบ")

    try:
        dmf_stat = cached_dmf_status()
        is_dmf_online = (dmf_stat.get('status') == 'online')
        if is_dmf_online:
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 10px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 8px; font-size: 11.5px; margin-bottom: 8px;">
                <span style="color: #065F46; font-weight: 600;"><span class="live-dot" style="width: 6px; height: 6px; margin-right: 6px;"></span>ระบบ DMF ออนไลน์</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #047857; font-size: 10.5px;">{dmf_stat['elapsed_sec']}s</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"DMF Portal: {dmf_stat.get('message', 'ออฟไลน์')}")
    except Exception:
        is_dmf_online = False
        st.info("ตรวจสอบการเชื่อมต่อ DMF")

    try:
        dmf_inv = cached_dmf_inventory()
    except Exception:
        dmf_inv = {'production': [], 'sales': []}

    # Auto-Detect and 1-Click Sync based on current module
    if is_dmf_online:
        if "การผลิต" in data_domain:
            prod_online_items = dmf_inv.get('production', [])
            if prod_online_items:
                latest_online_prod = prod_online_items[0]
                df_cur_p = st.session_state.get('df_flat_wide')
                p_sys_months = df_cur_p['เดือน'].dropna().unique().tolist() if df_cur_p is not None and not df_cur_p.empty else []
                num_online_p = len(prod_online_items)
                num_sys_p = len(p_sys_months)
                
                if num_online_p > num_sys_p:
                    st.markdown(f"""
                    <div style="background: rgba(254, 243, 199, 0.9); border: 1px solid #F59E0B; border-radius: 10px; padding: 10px; margin-bottom: 8px; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="color: #92400E; font-weight: 700; font-size: 12px;">🔔 ตรวจพบเดือนใหม่บน DMF!</span>
                            <span style="background: #F59E0B; color: white; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 5px;">NEW</span>
                        </div>
                        <div style="font-size: 11px; color: #475569; margin-top: 4px; line-height: 1.5;">
                            • <b>เว็บ DMF มี:</b> {latest_online_prod['label']} ({num_online_p} เดือน)<br/>
                            • <b>ในระบบมี:</b> {num_sys_p} เดือน
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.get('user_role', 'viewer') == 'admin':
                        if st.button("⚡ 1-Click Auto Sync การผลิต (RAM)", type="primary", use_container_width=True, key="btn_sync_prod_sidebar"):
                            run_auto_sync_production(prod_online_items)
                        st.caption("💡 ดึงสดทุกเดือนเข้า RAM + อัปเดตย้อนหลังและบันทึก Flat Table ทันที")
                    else:
                        st.info("⏳ ตรวจพบข้อมูลเดือนใหม่ (รอผู้ดูแลระบบกด Sync)")
                else:
                    st.markdown(f"""
                    <div style="background: rgba(209, 250, 229, 0.7); border: 1px solid #10B981; border-radius: 10px; padding: 8px 10px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="color: #065F46; font-weight: 700; font-size: 11.5px;">✅ ข้อมูลการผลิตเป็นปัจจุบัน</span>
                            <span style="background: #10B981; color: white; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 5px;">{num_sys_p} เดือน</span>
                        </div>
                        <div style="font-size: 10.5px; color: #047857; margin-top: 3px;">
                            ครบถ้วน (ม.ค. - {latest_online_prod['month_name']} {latest_online_prod['year_be']})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.session_state.get('user_role', 'viewer') == 'admin':
                        if st.button("🔄 รีเฟรชการผลิต (อัปเดตย้อนหลัง)", use_container_width=True, key="btn_refresh_prod_sidebar"):
                            run_auto_sync_production(prod_online_items)
                        st.caption("💡 ดึงใหม่ทุกเดือนเพื่ออัปเดตกรณี DMF แก้ไขตัวเลขย้อนหลัง")

        elif "การจำหน่าย" in data_domain:
            sale_online_items = dmf_inv.get('sales', [])
            if sale_online_items:
                latest_online_sale = sale_online_items[0]
                df_cur_s = st.session_state.get('df_sale_flat')
                s_sys_months = df_cur_s['เดือน'].dropna().unique().tolist() if df_cur_s is not None and not df_cur_s.empty else []
                num_online_s = len(sale_online_items)
                num_sys_s = len(s_sys_months)
                
                if num_online_s > num_sys_s:
                    st.markdown(f"""
                    <div style="background: rgba(254, 243, 199, 0.9); border: 1px solid #F59E0B; border-radius: 10px; padding: 10px; margin-bottom: 8px; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="color: #92400E; font-weight: 700; font-size: 12px;">🔔 ตรวจพบเดือนใหม่บน DMF!</span>
                            <span style="background: #F59E0B; color: white; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 5px;">NEW</span>
                        </div>
                        <div style="font-size: 11px; color: #475569; margin-top: 4px; line-height: 1.5;">
                            • <b>เว็บ DMF มี:</b> {latest_online_sale['label']} ({num_online_s} เดือน)<br/>
                            • <b>ในระบบมี:</b> {num_sys_s} เดือน
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.get('user_role', 'viewer') == 'admin':
                        if st.button("⚡ 1-Click Auto Sync ยอดขาย (RAM)", type="primary", use_container_width=True, key="btn_sync_sale_sidebar"):
                            run_auto_sync_sales(sale_online_items)
                        st.caption("💡 ดึงสดทุกเดือนเข้า RAM + อัปเดตย้อนหลังและบันทึก Flat Table ทันที")
                    else:
                        st.info("⏳ ตรวจพบข้อมูลเดือนใหม่ (รอผู้ดูแลระบบกด Sync)")
                else:
                    st.markdown(f"""
                    <div style="background: rgba(209, 250, 229, 0.7); border: 1px solid #10B981; border-radius: 10px; padding: 8px 10px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="color: #065F46; font-weight: 700; font-size: 11.5px;">✅ ข้อมูลยอดขายเป็นปัจจุบัน</span>
                            <span style="background: #10B981; color: white; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 5px;">{num_sys_s} เดือน</span>
                        </div>
                        <div style="font-size: 10.5px; color: #047857; margin-top: 3px;">
                            ครบถ้วน (ม.ค. - {latest_online_sale['month_name']} {latest_online_sale['year_ce']})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.session_state.get('user_role', 'viewer') == 'admin':
                        if st.button("🔄 รีเฟรชยอดขาย (อัปเดตย้อนหลัง)", use_container_width=True, key="btn_refresh_sale_sidebar"):
                            run_auto_sync_sales(sale_online_items)
                        st.caption("💡 ดึงใหม่ทุกเดือนเพื่ออัปเดตกรณี DMF แก้ไขตัวเลขย้อนหลัง")

    st.markdown("""
    <div style="font-size: 10.5px; line-height: 1.8; color: #64748B; padding-top: 6px; border-top: 1px dashed #E2E8F0; margin-top: 8px;">
        • <a href="https://dmf.go.th/public/epsummary/data/index/menu/1100" target="_blank" style="color: #0284C7; text-decoration: none;">DMF E&P Summary</a><br/>
        • <a href="https://dmf.go.th/public/createpetroleum/data/index/menu/1114/groupid/1" target="_blank" style="color: #0284C7; text-decoration: none;">DMF ผลิต (1114)</a><br/>
        • <a href="https://dmf.go.th/public/salevalue/data/index/menu/774/groupid/1" target="_blank" style="color: #0284C7; text-decoration: none;">DMF จำหน่าย (774)</a>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# Page Views for Non-Production Domains
# ----------------------------------------------------
if data_domain == "การจำหน่ายและมูลค่า (DMF Sales & Royalty)":
    st.markdown("""
    <div class="glass-panel" style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(254, 243, 199, 0.55) 100%); border: 1px solid rgba(255, 255, 255, 0.95);">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: linear-gradient(135deg, #EA580C 0%, #D97706 100%); border-radius: 10px; color: white; font-size: 18px; box-shadow: 0 4px 10px rgba(234, 88, 12, 0.3);">💰</span>
                <h1 style="margin:0; font-size: 22px; color: #0F172A; font-weight: 800;">Siam Hydrocarbon Intelligence</h1>
                <span style="background: rgba(234, 88, 12, 0.1); color: #C2410C; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(234, 88, 12, 0.25);">SALES & ROYALTY</span>
            </div>
            <p style="margin:0; font-size: 13px; color: #475569;">วิเคราะห์สถิติมูลค่าการจำหน่ายและค่าภาคหลวงปิโตรเลียมรายเดือน (Petroleum Sales, Valuation & Royalty Telemetry)</p>
        </div>
        <div style="text-align: right; background: rgba(255, 255, 255, 0.85); padding: 8px 16px; border-radius: 12px; border: 1px solid rgba(254, 215, 170, 0.8); box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; font-weight: 700; color: #EA580C; letter-spacing: 0.06em;"><span class="live-dot"></span>FISCAL TELEMETRY</div>
            <div style="font-size: 12px; font-weight: 600; color: #0F172A; font-family: 'JetBrains Mono', monospace;">OFFTAKE & VALUE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    is_admin = (st.session_state.get('user_role', 'viewer') == 'admin')
    if is_admin:
        tab_s_convert, tab_s_master, tab_s_charts, tab_s_report = st.tabs([
            "⚡ 1. แปลงข้อมูลยอดขายเป็น Flat Table",
            "🏷️ 2. จัดการ Sale Master Mapping",
            "📊 3. กราฟวิเคราะห์มูลค่าและค่าภาคหลวง",
            "📑 4. รายงานสรุปยอดจำหน่ายและค่าภาคหลวง"
        ])
    else:
        tab_s_charts, tab_s_report = st.tabs([
            "📊 แดชบอร์ดวิเคราะห์มูลค่าและค่าภาคหลวง (Sales Analytics)",
            "📑 รายงานสรุปยอดจำหน่ายและค่าภาคหลวง (Fiscal Report)"
        ])
        tab_s_convert = None
        tab_s_master = None

    # ====================================================
    # SALES TAB 1: CONVERTER (ADMIN ONLY)
    # ====================================================
    def render_sales_converter():
        st.subheader("📁 เลือกไฟล์รายงานการจำหน่ายและค่าภาคหลวง")

        c_s_mode, c_s_blank = st.columns([2.5, 1])
        with c_s_mode:
            sale_source_mode = st.radio(
                "แหล่งที่มาของไฟล์รายงานยอดขาย:",
                [
                    "🌐 สตรีมข้อมูลสดจากเว็บ DMF โดยตรง (In-Memory Live Stream - ไม่บันทึกลงเครื่อง)",
                    f"สแกนไฟล์ทั้งหมดในโฟลเดอร์ `Sale` อัตโนมัติ (`salevalue_*.xlsx`)",
                    "อัปโหลดไฟล์ใหม่ (Drag & Drop)"
                ],
                horizontal=False,
                key="sale_source_mode"
            )

        sale_files_to_process = []

        if "สตรีมข้อมูลสด" in sale_source_mode:
            st.markdown("""
            <div style="background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <b style="color: #166534;">🌐 โหมด In-Memory Live Stream:</b> สตรีมข้อมูลยอดขายและค่าภาคหลวงส่งตรงจากเว็บ DMF เข้าสู่ RAM และแมพปิ้งขึ้นแดชบอร์ดทันที <b>โดยไม่มีการบันทึกไฟล์ลงฮาร์ดดิสก์</b> (Zero Disk Footprint)
            </div>
            """, unsafe_allow_html=True)

            dmf_inv = cached_dmf_inventory()
            sale_online_list = dmf_inv.get('sales', [])
            is_live_s = dmf_inv.get('is_live', True)

            if sale_online_list:
                if not is_live_s:
                    st.info("💡 **โหมดคลังข้อมูลสำรอง (Cloud Fallback Mode):** เนื่องจากเซิร์ฟเวอร์ Streamlit Cloud อยู่ต่างประเทศและไฟร์วอลล์ของ DMF ปฏิเสธการเข้าถึง ระบบได้ดึงรายการเดือนจากแคชและไฟล์ในระบบมาให้คุณสามารถกดสตรีมข้อมูลขึ้น Dashboard ได้ตามปกติ")
                col_sel_s1, col_sel_s2 = st.columns([3, 1.2])
                with col_sel_s1:
                    opts_sale = [f"{item['label']} (ปี {item['year_ce']} เดือน {item['month']})" for item in sale_online_list]
                    selected_sale_labels = st.multiselect(
                        "เลือกเดือนที่ต้องการสตรีมสดจากเว็บ DMF:",
                        options=opts_sale,
                        default=opts_sale,
                        key="selected_sale_stream_months"
                    )
                with col_sel_s2:
                    save_backup_sales = st.checkbox("💾 บันทึกสำเนาลงโฟลเดอร์ `Sale` ด้วย", value=False, key="cb_save_backup_sales")
                    if st.button("🔄 รีเฟรชรายการเว็บ", key="btn_ref_sales_inv"):
                        st.cache_data.clear()
                        st.rerun()

                st.markdown("---")
                btn_stream_sales = st.button("🚀 เริ่มสตรีมข้อมูลยอดขายสดจากเว็บ DMF ขึ้น Dashboard (In-Memory)", type="primary", use_container_width=True, key="btn_stream_sales")

                if btn_stream_sales and selected_sale_labels:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    streamed_parsed_list = []

                    items_to_fetch = [item for item in sale_online_list if f"{item['label']} (ปี {item['year_ce']} เดือน {item['month']})" in selected_sale_labels]

                    for idx, item in enumerate(items_to_fetch):
                        status_text.write(f"📥 กำลังสตรีมข้อมูลเดือน **{item['label']}** จาก dmf.go.th เข้าสู่ RAM...")
                        try:
                            buf, fname = dmf.stream_dmf_sales_bytes(item['year_ce'], item['month'])
                            if save_backup_sales:
                                os.makedirs(SALE_DIR, exist_ok=True)
                                with open(os.path.join(SALE_DIR, fname), 'wb') as f_out:
                                    f_out.write(buf.getvalue())

                            df_single = parse_sales_file(buf, f"DMF_Online_{fname}")
                            streamed_parsed_list.append(df_single)
                        except Exception as err:
                            st.error(f"เกิดข้อผิดพลาดในการสตรีม {item['label']}: {err}")
                        progress_bar.progress((idx + 1) / len(items_to_fetch))

                    if streamed_parsed_list:
                        status_text.write("🏷️ กำลังแมพปิ้ง Master Model และคำนวณราคาเฉลี่ย...")
                        df_res = process_sales_dfs(streamed_parsed_list, save_to_disk=save_backup_sales)
                        status_text.empty()
                        progress_bar.empty()
                        st.success(f"🎉 สตรีมข้อมูลสดสำเร็จ {len(items_to_fetch)} เดือน ({len(df_res):,} แถว) ขึ้นแดชบอร์ดเรียบร้อย!")
                        st.rerun()
            else:
                st.warning("ไม่พบรายการเดือนออนไลน์บนเว็บ DMF หรือการเชื่อมต่อขัดข้อง")

        elif "สแกนไฟล์" in sale_source_mode:
            if os.path.exists(SALE_DIR):
                all_sale_files = sorted([f for f in os.listdir(SALE_DIR) if f.endswith('.xlsx') and not f.startswith('~$')])
                final_sale_files = []
                for f in all_sale_files:
                    if f == "salevalue_2026_02.xlsx" and "salevalue_2026_02 asof 7aug.xlsx" in all_sale_files:
                        continue
                    final_sale_files.append(f)

                if final_sale_files:
                    st.success(f"พบ **{len(final_sale_files)} ไฟล์** ในโฟลเดอร์ `Sale` พร้อมประมวลผล:")
                    st.caption(" • " + ", ".join(final_sale_files))
                    if "salevalue_2026_02 asof 7aug.xlsx" in final_sale_files:
                        st.info("💡 **ระบบเลือกใช้อัตโนมัติ:** `salevalue_2026_02 asof 7aug.xlsx` (ฉบับปรับปรุงล่าสุด 7 ส.ค. สำหรับเดือน ก.พ.)")
                    sale_files_to_process = [(os.path.join(SALE_DIR, f), f) for f in final_sale_files]
                else:
                    st.warning("ไม่พบไฟล์ Excel ในโฟลเดอร์ `Sale`")
            else:
                st.warning(f"ไม่พบโฟลเดอร์: `{SALE_DIR}`")
        else:
            uploaded_sales = st.file_uploader(
                "ลากไฟล์รายงานยอดขาย Excel มาวางที่นี่ (เลือกได้หลายไฟล์พร้อมกัน):",
                type=['xlsx', 'xls'],
                accept_multiple_files=True,
                key="sales_uploader_widget"
            )
            if uploaded_sales:
                sale_files_to_process = [(io.BytesIO(f.read()), f.name) for f in uploaded_sales]
                st.success(f"อัปโหลดเรียบร้อย {len(uploaded_sales)} ไฟล์")

        if "สตรีมข้อมูลสด" not in sale_source_mode:
            st.markdown("---")
            btn_run_sale = st.button("🚀 เริ่มการแปลงข้อมูลยอดขายเป็น Flat Table", type="primary", use_container_width=True, key="btn_run_sales")

            if btn_run_sale and sale_files_to_process:
                with st.spinner("กำลังอ่านและสกัดข้อมูลจากไฟล์รายงานยอดขาย..."):
                    parsed_list = []
                    for f_src, f_label in sale_files_to_process:
                        try:
                            df_single = parse_sales_file(f_src, f_label)
                            parsed_list.append(df_single)
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการประมวลผลไฟล์ `{f_label}`: {e}")

                    if parsed_list:
                        df_sales_flat = process_sales_dfs(parsed_list, save_to_disk=True)
                        st.toast(f"บันทึกไฟล์อัตโนมัติแล้วที่: {DEFAULT_SALE_OUTPUT_FILE}", icon="✅")
                        st.rerun()

        if 'df_sale_flat' in st.session_state and not st.session_state['df_sale_flat'].empty:
            df_s_show = st.session_state['df_sale_flat']
            st.success(f"🎉 ตรวจจับและจับคู่กับ Master Data Model ครบสมบูรณ์! (ทั้งหมด {len(df_s_show)} แถว จาก {len(df_s_show['เดือน'].unique())} เดือน)")

            buf_s = io.BytesIO()
            with pd.ExcelWriter(buf_s, engine='openpyxl') as wr:
                df_s_show.to_excel(wr, sheet_name='Sale_Flat_Table', index=False)
            buf_s.seek(0)

            st.download_button(
                label="📥 ดาวน์โหลดตาราง Flat Table ยอดขาย (Excel .xlsx)",
                data=buf_s,
                file_name=f"petroleum_sale_flat_table_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

            st.dataframe(df_s_show, use_container_width=True, height=450)
        else:
            st.info("💡 กรุณากดปุ่ม '🚀 เริ่มการแปลงข้อมูลยอดขายเป็น Flat Table' ด้านบนเพื่อเริ่มประมวลผลครับ")

    if is_admin and tab_s_convert is not None:
        with tab_s_convert:
            render_sales_converter()

    # ====================================================
    # SALES TAB 2: MASTER LIST MANAGEMENT (ADMIN ONLY)
    # ====================================================
    def render_sales_master():
        st.subheader("🏷️ จัดการตาราง Sale Master Data Model & Mapping")
        st.caption("สามารถแก้ไข Operator, แอ่งปิโตรเลียม หรือหมายเหตุของแต่ละจุดจำหน่ายในตารางนี้ได้โดยตรง เมื่อแก้ไขเสร็จแล้วให้กดปุ่ม 'บันทึก Master List'")

        df_sale_master_curr = load_sale_master_mapping()

        edited_sale_master = st.data_editor(
            df_sale_master_curr,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            key="sale_master_editor"
        )

        col_btn_sm, col_info_sm = st.columns([1, 3])
        with col_btn_sm:
            if st.button("💾 บันทึก Sale Master List", type="primary", use_container_width=True, key="btn_save_sale_master"):
                save_sale_master_mapping(edited_sale_master)
                st.success("บันทึกข้อมูล Sale Master Data Model เรียบร้อยแล้ว!")
                st.rerun()
        with col_info_sm:
            st.caption(f"📁 ไฟล์จัดเก็บอยู่ที่: `{os.path.basename(SALE_MASTER_FILE)}`")

    if is_admin and tab_s_master is not None:
        with tab_s_master:
            render_sales_master()

    # ====================================================
    # SALES TAB 3: CHARTS & ANALYTICS
    # ====================================================
    with tab_s_charts:
        st.subheader("📊 สรุปสถิติมูลค่าการจำหน่ายและค่าภาคหลวง (Sales & Royalty Analytics)")

        if 'df_sale_flat' in st.session_state and not st.session_state['df_sale_flat'].empty:
            df_s_data = st.session_state['df_sale_flat'].copy()

            # Executive Summary & Quick Download Bar
            s_months = df_s_data['เดือน'].dropna().unique().tolist()
            tot_annual_val = df_s_data['มูลค่าการขาย_บาท'].sum()
            tot_annual_roy = df_s_data['ค่าภาคหลวง_บาท'].sum()
            
            # Executive Summary Bar (Clean, Focused on Sales Metrics)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(254, 243, 199, 0.5) 0%, rgba(255, 251, 235, 0.8) 100%); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 14px; padding: 14px 20px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(217, 119, 6, 0.05); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <span style="font-size: 14.5px; font-weight: 800; color: #92400E;">
                            📊 สรุปข้อมูลยอดขายสะสม {len(s_months)} เดือน (มกราคม - {s_months[-1] if s_months else ''})
                        </span>
                        <span style="background: #D97706; color: white; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 12px; letter-spacing: 0.04em;">
                            FISCAL TELEMETRY
                        </span>
                    </div>
                    <div style="font-size: 12.5px; color: #78350F; line-height: 1.6;">
                        • มูลค่าการจำหน่ายสะสม: <b>{tot_annual_val/1e9:,.2f} พันล้านบาท</b> &nbsp;|&nbsp; 
                        • ค่าภาคหลวงจัดเก็บสะสม: <b>{tot_annual_roy/1e9:,.2f} พันล้านบาท</b> &nbsp;|&nbsp; 
                        • สัดส่วนค่าภาคหลวงเฉลี่ย: <b>{(tot_annual_roy/tot_annual_val*100) if tot_annual_val else 0:.2f}%</b>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(245, 158, 11, 0.4); font-size: 11.5px; font-weight: 600; color: #92400E; padding: 6px 14px; border-radius: 20px;">
                        💰 ฐานข้อมูลยอดขาย {len(df_s_data):,} แถว ({len(s_months)} เดือน)
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔍 กรองข้อมูลสถิติยอดขาย (Filters)", expanded=False):
                c_sf1, c_sf2, c_sf3 = st.columns(3)
                with c_sf1:
                    all_s_areas = sorted(df_s_data['พื้นที่'].dropna().unique())
                    sel_s_area = st.multiselect("กรองตามพื้นที่:", options=all_s_areas, default=all_s_areas, key="sel_s_area")
                with c_sf2:
                    all_s_ops = sorted(df_s_data['ผู้ดำเนินการ'].dropna().unique())
                    sel_s_op = st.multiselect("กรองตาม Operator:", options=all_s_ops, default=all_s_ops, key="sel_s_op")
                with c_sf3:
                    all_s_prods = sorted(df_s_data['ประเภทปิโตรเลียม'].dropna().unique())
                    sel_s_prod = st.multiselect("กรองตามประเภทเชื้อเพลิง:", options=all_s_prods, default=all_s_prods, key="sel_s_prod")

            df_s_filt = df_s_data[
                (df_s_data['พื้นที่'].isin(sel_s_area)) &
                (df_s_data['ผู้ดำเนินการ'].isin(sel_s_op)) &
                (df_s_data['ประเภทปิโตรเลียม'].isin(sel_s_prod))
            ].copy()

            if df_s_filt.empty:
                st.warning("⚠️ ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาเลือกตัวกรองใหม่อีกครั้ง")
            else:
                df_s_monthly = df_s_filt.groupby(['เดือน', 'ลำดับเดือน'], as_index=False).agg({
                    'มูลค่าการขาย_บาท': 'sum',
                    'ค่าภาคหลวง_บาท': 'sum'
                }).sort_values('ลำดับเดือน').reset_index(drop=True)

                df_s_monthly['Royalty_pct'] = (df_s_monthly['ค่าภาคหลวง_บาท'] / df_s_monthly['มูลค่าการขาย_บาท']) * 100
                df_s_monthly['Value_MoM_diff'] = df_s_monthly['มูลค่าการขาย_บาท'].diff()
                df_s_monthly['Value_MoM_pct'] = (df_s_monthly['Value_MoM_diff'] / df_s_monthly['มูลค่าการขาย_บาท'].shift(1)) * 100
                df_s_monthly['Royalty_MoM_diff'] = df_s_monthly['ค่าภาคหลวง_บาท'].diff()
                df_s_monthly['Royalty_MoM_pct'] = (df_s_monthly['Royalty_MoM_diff'] / df_s_monthly['ค่าภาคหลวง_บาท'].shift(1)) * 100

                latest_s = df_s_monthly.iloc[-1]
                # KPI Summary Bar for Latest Month (Including Wellhead Prices!)
                df_latest_month = df_s_filt[df_s_filt['เดือน'] == latest_s['เดือน']]

                gas_lat = df_latest_month[df_latest_month['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติ']
                gas_mmbtu_sum = gas_lat['ปริมาณการขาย_MMBTU'].sum() if 'ปริมาณการขาย_MMBTU' in gas_lat.columns else 0
                gas_val_sum = gas_lat['มูลค่าการขาย_บาท'].sum()
                avg_wp_gas = (gas_val_sum / gas_mmbtu_sum) if gas_mmbtu_sum > 0 else 0.0

                oil_lat = df_latest_month[df_latest_month['ประเภทปิโตรเลียม'] == 'น้ำมันดิบ']
                oil_bbl_sum = oil_lat['ปริมาณการขาย_บาร์เรล'].sum() if 'ปริมาณการขาย_บาร์เรล' in oil_lat.columns else oil_lat['ปริมาณการขาย_หน่วยหลัก'].sum()
                oil_val_sum = oil_lat['มูลค่าการขาย_บาท'].sum()
                avg_wp_oil = (oil_val_sum / oil_bbl_sum) if oil_bbl_sum > 0 else 0.0

                cond_lat = df_latest_month[df_latest_month['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติเหลว']
                cond_bbl_sum = cond_lat['ปริมาณการขาย_บาร์เรล'].sum() if 'ปริมาณการขาย_บาร์เรล' in cond_lat.columns else cond_lat['ปริมาณการขาย_หน่วยหลัก'].sum()
                cond_val_sum = cond_lat['มูลค่าการขาย_บาท'].sum()
                avg_wp_cond = (cond_val_sum / cond_bbl_sum) if cond_bbl_sum > 0 else 0.0

                st.markdown(f"##### 📌 สถิติประจำเดือนล่าสุด: **{latest_s['เดือน']}**")

                k_s1, k_s2, k_s3, k_s4 = st.columns(4)
                with k_s1:
                    v_val = latest_s['มูลค่าการขาย_บาท']
                    p_val = latest_s['Value_MoM_pct']
                    st.metric("💰 มูลค่าการขายรวม", f"{v_val/1e9:,.2f} พันล้านบาท", f"{p_val:+.1f}% MoM" if pd.notna(p_val) else None)
                with k_s2:
                    v_roy = latest_s['ค่าภาคหลวง_บาท']
                    p_roy = latest_s['Royalty_MoM_pct']
                    st.metric("🏛️ ค่าภาคหลวงรวม", f"{v_roy/1e9:,.2f} พันล้านบาท", f"{p_roy:+.1f}% MoM" if pd.notna(p_roy) else None)
                with k_s3:
                    r_pct = latest_s['Royalty_pct']
                    st.metric("📈 สัดส่วนค่าภาคหลวง", f"{r_pct:.1f}% ต่อยอดขาย")
                with k_s4:
                    ytd_val = df_s_monthly['มูลค่าการขาย_บาท'].sum()
                    st.metric("📅 มูลค่าขายสะสม (YTD)", f"{ytd_val/1e9:,.2f} พันล้านบาท")

                # Wellhead Price KPI Strip (Bento Style)
                st.markdown(f"""
                <div style="background: rgba(240, 249, 255, 0.7); border: 1px solid rgba(186, 230, 253, 0.8); border-radius: 12px; padding: 10px 16px; margin: 10px 0 16px 0; display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <span style="font-size: 11px; font-weight: 700; color: #0284C7;">💨 ราคาปากหลุม ก๊าซธรรมชาติ ({latest_s['เดือน']})</span><br/>
                        <span style="font-size: 17px; font-weight: 700; color: #0F172A; font-family: 'JetBrains Mono', monospace;">{avg_wp_gas:,.2f}</span> <span style="font-size: 12px; color: #475569;">บาท/MMBTU</span>
                    </div>
                    <div style="border-left: 1px solid rgba(186, 230, 253, 0.8); padding-left: 16px;">
                        <span style="font-size: 11px; font-weight: 700; color: #EA580C;">🛢️ ราคาปากหลุม น้ำมันดิบ ({latest_s['เดือน']})</span><br/>
                        <span style="font-size: 17px; font-weight: 700; color: #0F172A; font-family: 'JetBrains Mono', monospace;">{avg_wp_oil:,.2f}</span> <span style="font-size: 12px; color: #475569;">บาท/บาร์เรล</span>
                    </div>
                    <div style="border-left: 1px solid rgba(186, 230, 253, 0.8); padding-left: 16px;">
                        <span style="font-size: 11px; font-weight: 700; color: #7C3AED;">💧 ราคาปากหลุม คอนเดนเสท ({latest_s['เดือน']})</span><br/>
                        <span style="font-size: 17px; font-weight: 700; color: #0F172A; font-family: 'JetBrains Mono', monospace;">{avg_wp_cond:,.2f}</span> <span style="font-size: 12px; color: #475569;">บาท/บาร์เรล</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                subtab_s1, subtab_s2, subtab_s3, subtab_s4 = st.tabs([
                    "💰 1. มูลค่าและค่าภาคหลวง (Revenue & Royalties)",
                    "🎯 2. ราคา ณ ปากหลุม (Wellhead Price Telemetry)",
                    "⚖️ 3. ปริมาณการขาย 2 รูปแบบ & ค่าความร้อน (Sales Volume & Energy Units)",
                    "🏢 4. สัดส่วนตลาดตามผู้ดำเนินการและแอ่ง (Market Share)"
                ])

                # ----------------------------------------------------
                # SUBTAB 1: REVENUE & ROYALTIES
                # ----------------------------------------------------
                with subtab_s1:
                    ch_s1, ch_s2 = st.columns(2)
                    with ch_s1:
                        st.markdown("#### 1.1 มูลค่าการจำหน่ายรวมรายเดือน (บาท)")
                        df_prod_m = df_s_filt.groupby(['เดือน', 'ลำดับเดือน', 'ประเภทปิโตรเลียม'], as_index=False)['มูลค่าการขาย_บาท'].sum().sort_values('ลำดับเดือน')
                        fig_s_val = px.bar(
                            df_prod_m,
                            x='เดือน',
                            y='มูลค่าการขาย_บาท',
                            color='ประเภทปิโตรเลียม',
                            barmode='stack',
                            title="มูลค่าการจำหน่ายปิโตรเลียมรายเดือนแยกตามประเภท (บาท)",
                            labels={'มูลค่าการขาย_บาท': 'มูลค่า (บาท)', 'เดือน': 'เดือน'},
                            color_discrete_map={
                                'ก๊าซธรรมชาติ': '#0284C7',
                                'ก๊าซธรรมชาติเหลว': '#7C3AED',
                                'น้ำมันดิบ': '#EA580C',
                                'ก๊าซปิโตรเลียมเหลว (LPG)': '#0096C7'
                            }
                        )
                        fig_s_val.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        apply_crystal_aqua_theme(fig_s_val)
                        st.plotly_chart(fig_s_val, use_container_width=True)

                    with ch_s2:
                        st.markdown("#### 1.2 ค่าภาคหลวงที่จัดเก็บได้รายเดือน (บาท)")
                        fig_s_roy = px.bar(
                            df_s_monthly,
                            x='เดือน',
                            y='ค่าภาคหลวง_บาท',
                            text_auto='.2s',
                            title="ค่าภาคหลวงปิโตรเลียมรายเดือน (บาท)",
                            labels={'ค่าภาคหลวง_บาท': 'ค่าภาคหลวง (บาท)', 'เดือน': 'เดือน'},
                            color_discrete_sequence=['#F77F00']
                        )
                        fig_s_roy.update_traces(textposition='outside')
                        apply_crystal_aqua_theme(fig_s_roy)
                        st.plotly_chart(fig_s_roy, use_container_width=True)

                    st.markdown("#### 1.3 ตารางสรุปตัวเลขสถิติรายเดือน")
                    df_s_tbl = df_s_monthly[['เดือน', 'มูลค่าการขาย_บาท', 'ค่าภาคหลวง_บาท', 'Royalty_pct', 'Value_MoM_diff', 'Value_MoM_pct']].copy()
                    df_s_tbl.rename(columns={
                        'มูลค่าการขาย_บาท': 'มูลค่าการขาย (บาท)',
                        'ค่าภาคหลวง_บาท': 'ค่าภาคหลวง (บาท)',
                        'Royalty_pct': 'สัดส่วนค่าภาคหลวง (%)',
                        'Value_MoM_diff': 'เปลี่ยนแปลง MoM (บาท)',
                        'Value_MoM_pct': 'MoM (%)'
                    }, inplace=True)
                    st.dataframe(
                        df_s_tbl.style.format({
                            'มูลค่าการขาย (บาท)': '{:,.0f}',
                            'ค่าภาคหลวง (บาท)': '{:,.0f}',
                            'สัดส่วนค่าภาคหลวง (%)': '{:.2f}%',
                            'เปลี่ยนแปลง MoM (บาท)': lambda x: f"{x:+,.0f}" if pd.notna(x) else "-",
                            'MoM (%)': lambda x: f"{x:+.2f}%" if pd.notna(x) else "-"
                        }),
                        use_container_width=True
                    )

                # ----------------------------------------------------
                # SUBTAB 2: WELLHEAD PRICE TELEMETRY
                # ----------------------------------------------------
                with subtab_s2:
                    st.markdown("#### 🎯 2. ข้อมูลและการวิเคราะห์ราคา ณ ปากหลุม (Wellhead Price)")
                    st.caption("Wellhead Price คือราคาขายปิโตรเลียม ณ จุดส่งมอบหน้าปากหลุมผลิต ใช้เป็นเกณฑ์ในการคำนวณมูลค่าและจัดเก็บค่าภาคหลวงปิโตรเลียมของประเทศ")

                    wp_col1, wp_col2 = st.columns(2)
                    with wp_col1:
                        # Monthly trend for Natural Gas (THB/MMBTU)
                        df_gas_trend = df_s_filt[df_s_filt['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติ'].groupby(['เดือน', 'ลำดับเดือน'], as_index=False).apply(
                            lambda g: pd.Series({
                                'ราคาปากหลุมก๊าซฯ (บาท/MMBTU)': g['มูลค่าการขาย_บาท'].sum() / g['ปริมาณการขาย_MMBTU'].sum() if g['ปริมาณการขาย_MMBTU'].sum() > 0 else 0
                            }), include_groups=False
                        ).reset_index().sort_values('ลำดับเดือน')

                        fig_wp_gas = px.line(
                            df_gas_trend,
                            x='เดือน',
                            y='ราคาปากหลุมก๊าซฯ (บาท/MMBTU)',
                            markers=True,
                            title="💨 แนวโน้มราคาปากหลุม ก๊าซธรรมชาติ (บาท/MMBTU)",
                            color_discrete_sequence=['#0284C7']
                        )
                        fig_wp_gas.update_traces(text=df_gas_trend['ราคาปากหลุมก๊าซฯ (บาท/MMBTU)'].apply(lambda x: f"{x:.1f}"), textposition="top center")
                        apply_crystal_aqua_theme(fig_wp_gas)
                        st.plotly_chart(fig_wp_gas, use_container_width=True)

                    with wp_col2:
                        # Monthly trend for Liquids (THB/BBL)
                        df_oil_trend = df_s_filt[df_s_filt['ประเภทปิโตรเลียม'] == 'น้ำมันดิบ'].groupby(['เดือน', 'ลำดับเดือน'], as_index=False).apply(
                            lambda g: pd.Series({
                                'น้ำมันดิบ (บาท/บาร์เรล)': g['มูลค่าการขาย_บาท'].sum() / g['ปริมาณการขาย_บาร์เรล'].sum() if g['ปริมาณการขาย_บาร์เรล'].sum() > 0 else (g['มูลค่าการขาย_บาท'].sum() / g['ปริมาณการขาย_หน่วยหลัก'].sum() if g['ปริมาณการขาย_หน่วยหลัก'].sum() > 0 else 0)
                            }), include_groups=False
                        ).reset_index().sort_values('ลำดับเดือน')

                        df_cond_trend = df_s_filt[df_s_filt['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติเหลว'].groupby(['เดือน', 'ลำดับเดือน'], as_index=False).apply(
                            lambda g: pd.Series({
                                'คอนเดนเสท (บาท/บาร์เรล)': g['มูลค่าการขาย_บาท'].sum() / g['ปริมาณการขาย_บาร์เรล'].sum() if g['ปริมาณการขาย_บาร์เรล'].sum() > 0 else (g['มูลค่าการขาย_บาท'].sum() / g['ปริมาณการขาย_หน่วยหลัก'].sum() if g['ปริมาณการขาย_หน่วยหลัก'].sum() > 0 else 0)
                            }), include_groups=False
                        ).reset_index().sort_values('ลำดับเดือน')

                        df_liq_trend = pd.merge(df_oil_trend[['เดือน', 'ลำดับเดือน', 'น้ำมันดิบ (บาท/บาร์เรล)']], df_cond_trend[['เดือน', 'คอนเดนเสท (บาท/บาร์เรล)']], on='เดือน', how='outer').sort_values('ลำดับเดือน')

                        fig_wp_liq = px.line(
                            df_liq_trend,
                            x='เดือน',
                            y=['น้ำมันดิบ (บาท/บาร์เรล)', 'คอนเดนเสท (บาท/บาร์เรล)'],
                            markers=True,
                            title="🛢️ แนวโน้มราคาปากหลุม น้ำมันดิบและคอนเดนเสท (บาท/บาร์เรล)",
                            color_discrete_map={
                                'น้ำมันดิบ (บาท/บาร์เรล)': '#EA580C',
                                'คอนเดนเสท (บาท/บาร์เรล)': '#7C3AED'
                            }
                        )
                        fig_wp_liq.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        apply_crystal_aqua_theme(fig_wp_liq)
                        st.plotly_chart(fig_wp_liq, use_container_width=True)

                    st.markdown("---")
                    st.markdown("##### 🔍 เปรียบเทียบราคา ณ ปากหลุม แยกตามรายแหล่ง (Field Benchmark)")
                    c_f_sel1, c_f_sel2 = st.columns(2)
                    with c_f_sel1:
                        sel_wp_prod = st.selectbox("เลือกประเภทปิโตรเลียม:", ['ก๊าซธรรมชาติ', 'น้ำมันดิบ', 'ก๊าซธรรมชาติเหลว'], key="sel_wp_prod")
                    with c_f_sel2:
                        sel_wp_month = st.selectbox("เลือกเดือนที่ต้องการเปรียบเทียบ:", s_months, index=len(s_months)-1, key="sel_wp_month")

                    df_wp_bench = df_s_filt[(df_s_filt['ประเภทปิโตรเลียม'] == sel_wp_prod) & (df_s_filt['เดือน'] == sel_wp_month) & (df_s_filt['ราคาปากหลุม_Wellhead_Price'] > 0)].sort_values('ราคาปากหลุม_Wellhead_Price', ascending=True)

                    if not df_wp_bench.empty:
                        u_label = df_wp_bench['หน่วยราคาปากหลุม'].iloc[0] if 'หน่วยราคาปากหลุม' in df_wp_bench.columns else 'บาท/หน่วย'
                        fig_bench = px.bar(
                            df_wp_bench,
                            x='ราคาปากหลุม_Wellhead_Price',
                            y='แหล่ง_ไฟล์ดิบ',
                            orientation='h',
                            text_auto='.1f',
                            title=f"ราคา ณ ปากหลุม รายแหล่ง: {sel_wp_prod} ({sel_wp_month}) [{u_label}]",
                            labels={'ราคาปากหลุม_Wellhead_Price': f'ราคาปากหลุม ({u_label})', 'แหล่ง_ไฟล์ดิบ': 'ชื่อแหล่ง'},
                            color='ราคาปากหลุม_Wellhead_Price',
                            color_continuous_scale=['#BAE6FD', '#0284C7', '#023E8A'] if sel_wp_prod == 'ก๊าซธรรมชาติ' else ['#FED7AA', '#EA580C', '#9A3412']
                        )
                        fig_bench.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
                        apply_crystal_aqua_theme(fig_bench)
                        st.plotly_chart(fig_bench, use_container_width=True)
                    else:
                        st.info(f"ไม่พบข้อมูลราคาปากหลุมสำหรับ {sel_wp_prod} ในเดือน {sel_wp_month}")

                # ----------------------------------------------------
                # SUBTAB 3: VOLUMES & HEATING VALUE
                # ----------------------------------------------------
                with subtab_s3:
                    st.markdown("#### ⚖️ 3. ปริมาณการจำหน่ายก๊าซธรรมชาติ 2 รูปแบบ และการวิเคราะห์ค่าความร้อน (Heating Value)")
                    st.markdown("""
                    <div style="background: rgba(240, 253, 250, 0.8); border: 1px solid rgba(153, 246, 228, 0.8); border-radius: 10px; padding: 10px 16px; margin-bottom: 14px;">
                        <span style="color: #0F766E; font-weight: 700; font-size: 13px;">💡 การจัดรูปแบบหน่วยของก๊าซธรรมชาติในสัญญาซื้อขาย (Gas Contracts):</span><br/>
                        <span style="font-size: 12px; color: #334155; line-height: 1.5;">
                        • <b>ปริมาณเชิงปริมาตร (Volume):</b> วัดเป็น <b>ล้านลูกบาศก์ฟุต (MMSCF)</b> หรือเฉลี่ยรายวันคือ <b>MMSCFD</b> ซึ่งเป็นปริมาตรทางกายภาพ<br/>
                        • <b>ปริมาณเชิงพลังงาน (Energy Content):</b> วัดเป็น <b>ล้านบีทียู (MMBTU)</b> ซึ่งเป็นตัวเลขที่ใช้ในการคิดเงินตามสัญญา (Billing)<br/>
                        • <b>ค่าความร้อน (Heating Value):</b> อัตราส่วน <b>BTU/scf (หรือ MMBTU/MMSCF)</b> สะท้อนคุณภาพของก๊าซธรรมชาติในแต่ละแหล่ง
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        df_gas_vol = df_s_filt[df_s_filt['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติ'].groupby(['เดือน', 'ลำดับเดือน'], as_index=False).agg({
                            'ปริมาณการขาย_MMSCF': 'sum',
                            'ปริมาณการขาย_MMBTU': 'sum'
                        }).sort_values('ลำดับเดือน')

                        fig_g_vol = px.bar(
                            df_gas_vol,
                            x='เดือน',
                            y='ปริมาณการขาย_MMSCF',
                            text_auto=',.0f',
                            title="💨 ปริมาณการขายก๊าซธรรมชาติเชิงปริมาตรรายเดือน (ล้าน ลบ.ฟุต - MMSCF)",
                            labels={'ปริมาณการขาย_MMSCF': 'ปริมาณ (MMSCF)', 'เดือน': 'เดือน'},
                            color_discrete_sequence=['#0284C7']
                        )
                        fig_g_vol.update_traces(textposition='outside')
                        apply_crystal_aqua_theme(fig_g_vol)
                        st.plotly_chart(fig_g_vol, use_container_width=True)

                    with c_v2:
                        fig_g_heat = px.bar(
                            df_gas_vol,
                            x='เดือน',
                            y='ปริมาณการขาย_MMBTU',
                            text_auto='.2s',
                            title="🔥 ปริมาณความร้อนก๊าซธรรมชาติรายเดือน (ล้านบีทียู - MMBTU)",
                            labels={'ปริมาณการขาย_MMBTU': 'ความร้อน (MMBTU)', 'เดือน': 'เดือน'},
                            color_discrete_sequence=['#F59E0B']
                        )
                        fig_g_heat.update_traces(textposition='outside')
                        apply_crystal_aqua_theme(fig_g_heat)
                        st.plotly_chart(fig_g_heat, use_container_width=True)

                    # Heating value per field
                    st.markdown("##### 🔬 ค่าความร้อนก๊าซธรรมชาติเฉลี่ยแยกตามรายแหล่ง (Heating Value: BTU/scf)")
                    if 'ค่าความร้อน_Heating_Value_BTU_per_SCF' in df_s_filt.columns:
                        df_gas_hv = df_s_filt[(df_s_filt['ประเภทปิโตรเลียม'] == 'ก๊าซธรรมชาติ') & (df_s_filt['ค่าความร้อน_Heating_Value_BTU_per_SCF'] > 0)].groupby('แหล่ง_ไฟล์ดิบ', as_index=False)['ค่าความร้อน_Heating_Value_BTU_per_SCF'].mean().sort_values('ค่าความร้อน_Heating_Value_BTU_per_SCF', ascending=True)

                        if not df_gas_hv.empty:
                            fig_hv = px.bar(
                                df_gas_hv,
                                x='ค่าความร้อน_Heating_Value_BTU_per_SCF',
                                y='แหล่ง_ไฟล์ดิบ',
                                orientation='h',
                                text_auto=',.1f',
                                title="ค่าความร้อนของก๊าซธรรมชาติเฉลี่ยรายแหล่ง (BTU/scf) - ค่าเฉลี่ยมาตรฐานอ่าวไทย ~950-1,050",
                                labels={'ค่าความร้อน_Heating_Value_BTU_per_SCF': 'Heating Value (BTU/scf)', 'แหล่ง_ไฟล์ดิบ': 'ชื่อแหล่ง'},
                                color='ค่าความร้อน_Heating_Value_BTU_per_SCF',
                                color_continuous_scale=['#CCFBF1', '#0D9488', '#115E59']
                            )
                            fig_hv.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
                            apply_crystal_aqua_theme(fig_hv)
                            st.plotly_chart(fig_hv, use_container_width=True)

                # ----------------------------------------------------
                # SUBTAB 4: MARKET SHARE
                # ----------------------------------------------------
                with subtab_s4:
                    ch_s3, ch_s4 = st.columns(2)
                    with ch_s3:
                        st.markdown("#### 4.1 สัดส่วนมูลค่าการจำหน่ายตาม Operator")
                        df_s_op = df_s_filt.groupby('ผู้ดำเนินการ', as_index=False)['มูลค่าการขาย_บาท'].sum()
                        fig_s_op = px.pie(
                            df_s_op,
                            names='ผู้ดำเนินการ',
                            values='มูลค่าการขาย_บาท',
                            hole=0.45,
                            title="Market Share มูลค่ายอดขายตาม Operator รวม",
                            color_discrete_sequence=['#0284C7', '#023E8A', '#EA580C', '#7C3AED', '#0096C7', '#F77F00', '#10B981', '#64748B']
                        )
                        apply_crystal_aqua_theme(fig_s_op)
                        st.plotly_chart(fig_s_op, use_container_width=True)

                    with ch_s4:
                        st.markdown("#### 4.2 สัดส่วนมูลค่าตามแอ่งปิโตรเลียม (Basin)")
                        df_s_basin = df_s_filt.groupby('แอ่งปิโตรเลียม', as_index=False)['มูลค่าการขาย_บาท'].sum()
                        fig_s_basin = px.pie(
                            df_s_basin,
                            names='แอ่งปิโตรเลียม',
                            values='มูลค่าการขาย_บาท',
                            hole=0.45,
                            title="สัดส่วนมูลค่ายอดขายตามแอ่งปิโตรเลียม (Basin)",
                            color_discrete_sequence=['#023E8A', '#0284C7', '#48CAE4', '#90E0EF']
                        )
                        apply_crystal_aqua_theme(fig_s_basin)
                        st.plotly_chart(fig_s_basin, use_container_width=True)
        else:
            if st.session_state.get('user_role', 'viewer') == 'admin':
                st.info("💡 ยังไม่มีข้อมูลยอดขายในระบบ สามารถกดปุ่ม '⚡ 1-Click Auto Sync ยอดขาย' ในแถบเมนูด้านซ้ายเพื่อดึงข้อมูลสดจาก DMF ได้ทันทีครับ")
            else:
                st.info("💡 ขณะนี้ยังไม่มีข้อมูลยอดขายในระบบ กรุณาติดต่อผู้ดูแลระบบ (Admin) เพื่อรัน Auto Sync ข้อมูลล่าสุดครับ")

    # ====================================================
    # SALES TAB 4: SUMMARY REPORT
    # ====================================================
    with tab_s_report:
        st.subheader("📑 รายงานสรุปยอดจำหน่ายและค่าภาคหลวงรายเดือน (Fiscal Report)")
        st.caption("รายงานจำแนกประเภทปิโตรเลียม แหล่งผลิต ปริมาณการจำหน่ายในหน่วยเฉพาะ มูลค่า ค่าภาคหลวง และราคา ณ ปากหลุม (Wellhead Price)")

        if 'df_sale_flat' in st.session_state and not st.session_state['df_sale_flat'].empty:
            df_s_rep = st.session_state['df_sale_flat'].copy()
            months_avail = df_s_rep[['เดือน', 'ลำดับเดือน']].drop_duplicates().sort_values('ลำดับเดือน', ascending=False)['เดือน'].tolist()

            sel_s_month = st.selectbox("📅 เลือกเดือนที่ต้องการดูรายงาน:", options=months_avail, index=0, key="sel_s_month")
            df_s_month_data = df_s_rep[df_s_rep['เดือน'] == sel_s_month].copy()

            tot_val = df_s_month_data['มูลค่าการขาย_บาท'].sum()
            tot_roy = df_s_month_data['ค่าภาคหลวง_บาท'].sum()
            st.info(f"📊 สรุปยอดเดือน **{sel_s_month}**: มูลค่าการขายรวม **{tot_val:,.2f} บาท** | ค่าภาคหลวงรวม **{tot_roy:,.2f} บาท**")

            report_cols = [
                'ประเภทปิโตรเลียม', 'แหล่ง_ไฟล์ดิบ', 'ผู้ดำเนินการ', 'พื้นที่',
                'ปริมาณการขาย_MMSCF', 'ปริมาณการขาย_MMBTU',
                'ปริมาณการขาย_บาร์เรล', 'ปริมาณการขาย_กิโลกรัม',
                'มูลค่าการขาย_บาท', 'ค่าภาคหลวง_บาท',
                'ราคาปากหลุม_Wellhead_Price', 'หน่วยราคาปากหลุม',
                'ค่าความร้อน_Heating_Value_BTU_per_SCF', 'อัตราค่าภาคหลวงที่แท้จริง_Pct'
            ]
            df_rep_show = df_s_month_data[[c for c in report_cols if c in df_s_month_data.columns]].copy()
            rename_rep_map = {
                'ปริมาณการขาย_MMSCF': 'ปริมาณก๊าซ (MMSCF)',
                'ปริมาณการขาย_MMBTU': 'ปริมาณความร้อน (MMBTU)',
                'ปริมาณการขาย_บาร์เรล': 'ปริมาณ (บาร์เรล)',
                'ปริมาณการขาย_กิโลกรัม': 'ปริมาณ (กก.)',
                'มูลค่าการขาย_บาท': 'มูลค่าการขาย (บาท)',
                'ค่าภาคหลวง_บาท': 'ค่าภาคหลวง (บาท)',
                'ราคาปากหลุม_Wellhead_Price': 'ราคาปากหลุม (Wellhead Price)',
                'หน่วยราคาปากหลุม': 'หน่วยราคา',
                'ค่าความร้อน_Heating_Value_BTU_per_SCF': 'Heating Value (BTU/scf)',
                'อัตราค่าภาคหลวงที่แท้จริง_Pct': 'Royalty (%)'
            }
            df_rep_show.rename(columns=rename_rep_map, inplace=True)

            st.dataframe(
                df_rep_show.style.format({
                    'ปริมาณก๊าซ (MMSCF)': lambda x: f"{x:,.2f}" if pd.notna(x) and x > 0 else "-",
                    'ปริมาณความร้อน (MMBTU)': lambda x: f"{x:,.0f}" if pd.notna(x) and x > 0 else "-",
                    'ปริมาณ (บาร์เรล)': lambda x: f"{x:,.0f}" if pd.notna(x) and x > 0 else "-",
                    'ปริมาณ (กก.)': lambda x: f"{x:,.0f}" if pd.notna(x) and x > 0 else "-",
                    'มูลค่าการขาย (บาท)': '{:,.2f}',
                    'ค่าภาคหลวง (บาท)': '{:,.2f}',
                    'ราคาปากหลุม (Wellhead Price)': lambda x: f"{x:,.2f}" if pd.notna(x) and x > 0 else "-",
                    'Heating Value (BTU/scf)': lambda x: f"{x:,.1f}" if pd.notna(x) and x > 0 else "-",
                    'Royalty (%)': lambda x: f"{x:.2f}%" if pd.notna(x) and x > 0 else "-"
                }),
                use_container_width=True,
                height=500
            )

            # Action Toolbar: UI/UX Pro Max Dual Export Hub (Sales)
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin: 18px 0 12px 0;">
                <span style="font-size: 16px;">📦</span>
                <span style="font-weight: 800; font-size: 14.5px; color: #0F172A;">ศูนย์ดาวน์โหลดข้อมูลและรายงานยอดขาย (Sales Export Center)</span>
                <span style="background: rgba(217, 119, 6, 0.12); color: #B45309; font-size: 10.5px; font-weight: 700; padding: 2px 9px; border-radius: 12px; margin-left: 4px;">
                    DUAL FORMAT
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_sx1, col_sx2 = st.columns(2, gap="medium")
            with col_sx1:
                st.markdown(f"""
                <div style="background: white; border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 14px; padding: 16px 18px 14px 18px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); min-height: 142px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 13.5px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px;">
                                📑 รายงานยอดขายประจำเดือน ({sel_s_month})
                            </span>
                            <span style="background: rgba(217, 119, 6, 0.12); color: #B45309; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">
                                MONTHLY FISCAL
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #64748B; line-height: 1.5; margin-bottom: 8px;">
                            ตารางสรุปปริมาณและมูลค่าการจำหน่าย ค่าภาคหลวง และราคาปากหลุม (Wellhead Price) ประจำเดือน <b>{sel_s_month} 2569</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                buf_rep = io.BytesIO()
                with pd.ExcelWriter(buf_rep, engine='openpyxl') as w_rep:
                    df_rep_show.to_excel(w_rep, sheet_name=f'Sale_{sel_s_month}', index=False)
                buf_rep.seek(0)
                st.download_button(
                    label=f"📥 ดาวน์โหลดรายงานประจำเดือน {sel_s_month} (.xlsx)",
                    data=buf_rep,
                    file_name=f"DMF_Petroleum_Sale_{sel_s_month}_2569.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    key="btn_dl_s_report"
                )

            with col_sx2:
                num_s_months = len(df_s_rep['เดือน'].dropna().unique())
                total_s_rows = len(df_s_rep)
                st.markdown(f"""
                <div style="background: white; border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 14px; padding: 16px 18px 14px 18px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); min-height: 142px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 13.5px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px;">
                                📊 ฐานข้อมูลยอดขาย Flat Table สะสมทั้งปี
                            </span>
                            <span style="background: rgba(16, 185, 129, 0.12); color: #059669; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">
                                BI & PIVOT READY
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #64748B; line-height: 1.5; margin-bottom: 8px;">
                            ฐานข้อมูลการจำหน่ายสะสม <b>{num_s_months} เดือน</b> ({total_s_rows:,} แถว) คอลัมน์ครบถ้วน พร้อมนำเข้า Power BI, Tableau หรือ Excel Data Model
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                buf_s_all = io.BytesIO()
                with pd.ExcelWriter(buf_s_all, engine='openpyxl') as w_all:
                    df_s_rep.to_excel(w_all, sheet_name='Sale_Flat_Table', index=False)
                buf_s_all.seek(0)
                st.download_button(
                    label=f"📊 ดาวน์โหลดฐานข้อมูล Flat Table ยอดขายทั้งปี (.xlsx)",
                    data=buf_s_all,
                    file_name=f"petroleum_sale_flat_table_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    use_container_width=True,
                    key="btn_dl_s_flat_tab4"
                )
        else:
            if st.session_state.get('user_role', 'viewer') == 'admin':
                st.info("💡 ยังไม่มีข้อมูลยอดขายในระบบ สามารถกดปุ่ม '⚡ 1-Click Auto Sync ยอดขาย' ในแถบเมนูด้านซ้ายเพื่อดึงข้อมูลสดจาก DMF ได้ทันทีครับ")
            else:
                st.info("💡 ขณะนี้ยังไม่มีข้อมูลยอดขายในระบบ กรุณาติดต่อผู้ดูแลระบบ (Admin) เพื่อรัน Auto Sync ข้อมูลล่าสุดครับ")

    st.stop()

if data_domain == "การนำเข้า-ส่งออก (Import / Export)":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0b486b 0%, #3b8d99 100%); padding: 22px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <h1 style="margin:0; font-size: 26px; color: white;">PTIT Focus Statistics - โมดูลการนำเข้าและส่งออกปิโตรเลียม (Import & Export Data Hub)</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9; font-size: 14px;">ศูนย์กลางการจัดการและแปลงข้อมูลสถิติการนำเข้าน้ำมันดิบ น้ำมันสำเร็จรูป ก๊าซธรรมชาติ (LNG) และการส่งออก</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("โครงสร้างโมดูลพร้อมเชื่อมต่อ (Ready for Future Integration): เมื่อมีไฟล์ข้อมูลจากกรมศุลกากร / กรมธุรกิจพลังงาน (DOEB) สามารถนำมาวางเพื่อเขียน Script สกัดเป็น Flat Table ได้ทันที")

    col_ie1, col_ie2 = st.columns([3, 2])
    with col_ie1:
        st.subheader("อัปโหลดไฟล์รายงานการนำเข้า-ส่งออก")
        uploaded_ie = st.file_uploader(
            "ลากไฟล์รายงานการนำเข้า/ส่งออก (Excel หรือ CSV) มาวางที่นี่:",
            type=['xlsx', 'xls', 'csv'],
            key="ie_uploader"
        )
        if uploaded_ie:
            st.success(f"ตรวจพบไฟล์: `{uploaded_ie.name}` พร้อมสำหรับการประมวลผลเมื่อเชื่อมต่อสคริปต์สกัดข้อมูล")
        else:
            st.caption("ตัวอย่างไฟล์ที่รองรับในอนาคต: รายงานการนำเข้าน้ำมันดิบรายประเทศ, การส่งออกน้ำมันสำเร็จรูปรายผลิตภัณฑ์ ฯลฯ")

    with col_ie2:
        st.subheader("แผนผังชุดข้อมูลเป้าหมาย")
        st.markdown("""
        - **การนำเข้าน้ำมันดิบ (Crude Oil Imports):** ปริมาณ (BPD, Liters), มูลค่า C.I.F., จำแนกตามแหล่งกำเนิด (Middle East, Far East, อื่นๆ)
        - **การนำเข้า-ส่งออกผลิตภัณฑ์ปิโตรเลียมสำเร็จรูป:** เบนซิน, ดีเซล, น้ำมันอากาศยาน (Jet Fuel), น้ำมันเตา, LPG
        - **การนำเข้าก๊าซธรรมชาติเหลว (LNG):** สัญญาระยะยาว & ตลาดจร (Spot)
        """)
    st.stop()

elif data_domain == "การจัดหาและการใช้พลังงาน (Supply & Demand)":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #d35400 0%, #e67e22 100%); padding: 22px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <h1 style="margin:0; font-size: 26px; color: white;">PTIT Focus Statistics - โมดูลการจัดหาและการใช้น้ำมัน (Supply & Demand Hub)</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9; font-size: 14px;">สถิติการจำหน่ายและการใช้น้ำมันเชื้อเพลิงสำเร็จรูปรายผลิตภัณฑ์และรายภาคเศรษฐกิจ</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("โครงสร้างโมดูลพร้อมเชื่อมต่อ (Ready for Future Integration): รองรับไฟล์สถิติจากกรมธุรกิจพลังงาน (DOEB) หรือสำนักงานนโยบายและแผนพลังงาน (EPPO)")

    col_sd1, col_sd2 = st.columns([3, 2])
    with col_sd1:
        st.subheader("อัปโหลดไฟล์รายงานยอดจำหน่าย / การใช้น้ำมัน")
        uploaded_sd = st.file_uploader(
            "ลากไฟล์รายงานการใช้น้ำมัน (Excel หรือ CSV) มาวางที่นี่:",
            type=['xlsx', 'xls', 'csv'],
            key="sd_uploader"
        )
        if uploaded_sd:
            st.success(f"ตรวจพบไฟล์: `{uploaded_sd.name}` พร้อมสำหรับการประมวลผล")

    with col_sd2:
        st.subheader("แผนผังชุดข้อมูลเป้าหมาย")
        st.markdown("""
        - **ภาคขนส่ง (Transportation):** แก๊สโซฮอล์ 95, 91, E20, E85, ดีเซล B7, B10, B20, NGV
        - **ภาคอุตสาหกรรม (Industry):** น้ำมันเตา, ก๊าซปิโตรเลียมเหลว (LPG)
        - **การบิน (Aviation):** น้ำมันอากาศยาน Jet A-1
        - **การผลิตไฟฟ้า (Power Generation):** ก๊าซธรรมชาติ, ดีเซล, น้ำมันเตา
        """)
    st.stop()

elif data_domain == "จัดการ Master Data Model รวม":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); padding: 22px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <h1 style="margin:0; font-size: 26px; color: white;">PTIT Master Data Management Hub</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9; font-size: 14px;">ตารางฐานข้อมูลหลักสำหรับควบคุมมาตรฐานรหัส, ชื่อ Operator, แอ่งปิโตรเลียม, แปลงสัมปทาน และการเชื่อมโยงระบบ</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("ตาราง Master Data Model & Mapping กลาง")
    st.caption("สามารถดับเบิลคลิกแก้ไขข้อมูลในตารางด้านล่างนี้ได้โดยตรง เมื่อแก้ไขเสร็จแล้วให้กดปุ่ม 'บันทึก Master Data Model'")

    df_master_current = load_master_mapping()
    st.markdown(f"**จำนวนข้อมูล Master Mapping ในระบบ:** `{len(df_master_current)} รายการ`")

    edited_master_global = st.data_editor(
        df_master_current,
        num_rows="dynamic",
        use_container_width=True,
        height=550,
        key="global_master_editor"
    )

    col_btn_m, col_info_m = st.columns([1, 3])
    with col_btn_m:
        if st.button("💾 บันทึก Master Data Model", type="primary", use_container_width=True, key="btn_save_global_master"):
            save_master_mapping(edited_master_global)
            st.success("บันทึกข้อมูล Master Data Model เรียบร้อยแล้ว!")
            st.rerun()

    with col_info_m:
        st.caption(f"📁 บันทึกลงไฟล์: `{os.path.basename(MASTER_FILE)}` (ใช้ร่วมกันทุกโมดูลในระบบ)")
    st.stop()

elif data_domain == "คู่มือการใช้งาน & เกี่ยวกับระบบ":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #373b44 0%, #4286f4 100%); padding: 22px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <h1 style="margin:0; font-size: 26px; color: white;">📖 คู่มือการใช้งาน & รายละเอียดระบบ (System Documentation)</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9; font-size: 14px;">คู่มือขั้นตอนการดำเนินงานประจำเดือน คำอธิบาย Data Model และโครงสร้างของระบบ PTIT Focus Statistics</p>
    </div>
    """, unsafe_allow_html=True)

    manual_path = os.path.join(BASE_DIR, "คู่มือการใช้งาน.md")
    if os.path.exists(manual_path):
        with open(manual_path, "r", encoding="utf-8") as f:
            manual_text = f.read()
        st.markdown(manual_text)
    else:
        st.info("ไม่พบไฟล์คู่มือการใช้งาน.md")
    st.stop()

# ----------------------------------------------------
# Production Domain Main View
# ----------------------------------------------------
st.markdown("""
<div class="glass-panel" style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(224, 242, 254, 0.65) 100%); border: 1px solid rgba(255, 255, 255, 0.95);">
    <div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%); border-radius: 10px; color: white; font-size: 18px; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);">🛢️</span>
            <h1 style="margin:0; font-size: 22px; color: #0F172A; font-weight: 800;">Siam Hydrocarbon Intelligence</h1>
            <span style="background: rgba(2, 132, 199, 0.1); color: #0284C7; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(2, 132, 199, 0.25);">PRODUCTION TELEMETRY</span>
        </div>
        <p style="margin:0; font-size: 13px; color: #475569;">ระบบสถิติและการผลิตปิโตรเลียมประเทศไทย (Thailand Petroleum Telemetry & Analytics Platform) • สถาบันปิโตรเลียมแห่งประเทศไทย (PTIT)</p>
    </div>
    <div style="text-align: right; background: rgba(255, 255, 255, 0.85); padding: 8px 16px; border-radius: 12px; border: 1px solid rgba(186, 230, 253, 0.8); box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-size: 11px; font-weight: 700; color: #0284C7; letter-spacing: 0.06em;"><span class="live-dot"></span>LIVE TELEMETRY</div>
        <div style="font-size: 12px; font-weight: 600; color: #0F172A; font-family: 'JetBrains Mono', monospace;">CRYSTAL AQUA GLASS</div>
    </div>
</div>
""", unsafe_allow_html=True)

is_admin = (st.session_state.get('user_role', 'viewer') == 'admin')
if is_admin:
    tab_convert, tab_master, tab_charts, tab_ptit_report = st.tabs([
        "⚡ 1. แปลงข้อมูลเป็น Flat Table",
        "🏷️ 2. จัดการ Master List & Data Model",
        "📊 3. แดชบอร์ดสรุปสถิติ & กราฟแนวโน้ม (Production Analytics)",
        "📑 4. รายงานมาตรฐาน PTIT (Domestic Production)"
    ])
else:
    tab_charts, tab_ptit_report = st.tabs([
        "📊 แดชบอร์ดสรุปสถิติ & กราฟแนวโน้ม (Production Analytics)",
        "📑 รายงานมาตรฐาน PTIT (Domestic Production Report)"
    ])
    tab_convert = None
    tab_master = None

# ====================================================
# TAB 1: CONVERTER (ADMIN ONLY)
# ====================================================
def render_production_converter():
    st.subheader("📁 เลือกไฟล์ที่ต้องการแปลง")

    col_src, col_opt = st.columns([2.5, 1])
    with col_src:
        source_mode = st.radio(
            "แหล่งที่มาของไฟล์การผลิต:",
            [
                "🌐 สตรีมข้อมูลสดจากเว็บ DMF โดยตรง (In-Memory Live Stream - ไม่บันทึกลงเครื่อง)",
                "สแกนไฟล์ทั้งหมดในโฟลเดอร์นี้อัตโนมัติ (`createpetroleum_*.xlsx`)",
                "อัปโหลดไฟล์ใหม่ (Drag & Drop)"
            ],
            horizontal=False,
            key="prod_source_mode"
        )

    files_to_process = []

    if "สตรีมข้อมูลสด" in source_mode:
        st.markdown("""
        <div style="background-color: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <b style="color: #1e40af;">🌐 โหมด In-Memory Live Stream:</b> สตรีมข้อมูลรายงานการผลิตปิโตรเลียมส่งตรงจากเว็บ DMF เข้าสู่ RAM และแมพปิ้งขึ้นแดชบอร์ดทันที <b>โดยไม่มีการบันทึกไฟล์ลงฮาร์ดดิสก์</b> (Zero Disk Footprint)
        </div>
        """, unsafe_allow_html=True)

        dmf_inv = cached_dmf_inventory()
        prod_online_list = dmf_inv.get('production', [])
        is_live_p = dmf_inv.get('is_live', True)

        if prod_online_list:
            if not is_live_p:
                st.info("💡 **โหมดคลังข้อมูลสำรอง (Cloud Fallback Mode):** เนื่องจากเซิร์ฟเวอร์ Streamlit Cloud อยู่ต่างประเทศและไฟร์วอลล์ของ DMF ปฏิเสธการเข้าถึง ระบบได้ดึงรายการเดือนจากแคชและไฟล์ในระบบมาให้คุณสามารถกดสตรีมข้อมูลขึ้น Dashboard ได้ตามปกติ")
            col_sel_p1, col_sel_p2 = st.columns([3, 1.2])
            with col_sel_p1:
                opts_prod = [f"{item['label']} (เดือน {item['month']})" for item in prod_online_list]
                selected_prod_labels = st.multiselect(
                    "เลือกเดือนที่ต้องการสตรีมสดจากเว็บ DMF:",
                    options=opts_prod,
                    default=opts_prod,
                    key="selected_prod_stream_months"
                )
            with col_sel_p2:
                save_backup_prod = st.checkbox("💾 บันทึกสำเนาลงโฟลเดอร์ Production ด้วย", value=False, key="cb_save_backup_prod")
                if st.button("🔄 รีเฟรชรายการเว็บ", key="btn_ref_prod_inv"):
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("---")
            btn_stream_prod = st.button("🚀 เริ่มสตรีมข้อมูลการผลิตสดจากเว็บ DMF ขึ้น Dashboard (In-Memory)", type="primary", use_container_width=True, key="btn_stream_prod")

            if btn_stream_prod and selected_prod_labels:
                progress_bar = st.progress(0)
                status_text = st.empty()
                streamed_parsed_list = []

                items_to_fetch = [item for item in prod_online_list if f"{item['label']} (เดือน {item['month']})" in selected_prod_labels]

                for idx, item in enumerate(items_to_fetch):
                    status_text.write(f"📥 กำลังสตรีมข้อมูลเดือน **{item['label']}** จาก dmf.go.th เข้าสู่ RAM...")
                    try:
                        buf, fname = dmf.stream_dmf_production_bytes(item['year_be'], item['month'])
                        if save_backup_prod:
                            os.makedirs(BASE_DIR, exist_ok=True)
                            with open(os.path.join(BASE_DIR, fname), 'wb') as f_out:
                                f_out.write(buf.getvalue())

                        df_sub = parse_excel_file(buf, f"DMF_Online_{fname}")
                        streamed_parsed_list.append(df_sub)
                    except Exception as err:
                        st.error(f"เกิดข้อผิดพลาดในการสตรีม {item['label']}: {err}")
                    progress_bar.progress((idx + 1) / len(items_to_fetch))

                if streamed_parsed_list:
                    status_text.write("🏷️ กำลังแมพปิ้ง Master Model และจัดทำ Flat Tables...")
                    df_wide, df_long, unmapped = process_production_dfs(streamed_parsed_list, save_to_disk=save_backup_prod)
                    status_text.empty()
                    progress_bar.empty()
                    st.success(f"🎉 สตรีมข้อมูลสดสำเร็จ {len(items_to_fetch)} เดือน ({len(df_wide):,} แถว) ขึ้นแดชบอร์ดเรียบร้อย!")
                    st.rerun()
        else:
            st.warning("ไม่พบรายการเดือนออนไลน์บนเว็บ DMF หรือการเชื่อมต่อขัดข้อง")

    elif "สแกนไฟล์" in source_mode:
        local_files = sorted(glob.glob(os.path.join(BASE_DIR, "createpetroleum_2569_*.xlsx")))
        if local_files:
            st.success(f"พบ {len(local_files)} ไฟล์ในโฟลเดอร์ปัจจุบันพร้อมแปลง:")
            file_names = [os.path.basename(f) for f in local_files]
            st.caption(" • " + ", ".join(file_names))
            files_to_process = [(f, os.path.basename(f)) for f in local_files]
        else:
            st.warning("ไม่พบไฟล์ชื่อ `createpetroleum_*.xlsx` ในโฟลเดอร์นี้")
    else:
        uploaded_files = st.file_uploader(
            "ลากไฟล์ Excel รายเดือนมาวางที่นี่ (เลือกได้หลายไฟล์พร้อมกัน):",
            type=['xlsx', 'xls'],
            accept_multiple_files=True
        )
        if uploaded_files:
            files_to_process = [(io.BytesIO(f.read()), f.name) for f in uploaded_files]
            st.success(f"อัปโหลดเรียบร้อย {len(uploaded_files)} ไฟล์")

    if "สตรีมข้อมูลสด" not in source_mode:
        st.markdown("---")
        btn_run = st.button("🚀 เริ่มการแปลงข้อมูลเป็น Flat Table", type="primary", use_container_width=True)

        if btn_run and files_to_process:
            with st.spinner("กำลังอ่านไฟล์และปรับปรุงข้อมูลเข้า Data Model..."):
                dfs = []
                for file_input, name in files_to_process:
                    try:
                        df_sub = parse_excel_file(file_input, name)
                        dfs.append(df_sub)
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์ {name}: {e}")

                if dfs:
                    process_production_dfs(dfs, save_to_disk=True)
                    st.toast(f"บันทึกไฟล์อัตโนมัติแล้วที่: {DEFAULT_OUTPUT_FILE}", icon="✅")
                    st.rerun()

    # Display Results if Available
    if 'df_flat_wide' in st.session_state:
        df_wide = st.session_state['df_flat_wide']
        if 'df_flat_long' in st.session_state:
            df_long = st.session_state['df_flat_long']
        else:
            id_cols = [c for c in ['พื้นที่', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ', 'ปี', 'เดือน', 'ผู้ดำเนินการ', 'แอ่งปิโตรเลียม', 'ประเภทสัญญา', 'PTIT_Region', 'PTIT_Operator_Field'] if c in df_wide.columns]
            val_cols = [c for c in ['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 'น้ำมันดิบ (บาร์เรล/วัน)', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'] if c in df_wide.columns]
            df_long = pd.melt(df_wide, id_vars=id_cols, value_vars=val_cols, var_name='ผลิตภัณฑ์ปิโตรเลียม', value_name='ปริมาณการผลิตต่อวัน')
            st.session_state['df_flat_long'] = df_long
        unmapped = st.session_state.get('unmapped', pd.DataFrame())

        if len(unmapped) > 0:
            st.warning(f"⚠️ พบ **{len(unmapped)} แหล่งใหม่** ที่ยังไม่มีข้อมูลใน Master List (ระบบใส่ชื่อตั้งต้นให้แล้ว คุณสามารถไประบุ Operator/Basin ได้ที่แท็บ 'จัดการ Master List')")
            with st.expander("ดูรายชื่อแหล่งที่ยังไม่ได้ระบุ Master:"):
                st.dataframe(unmapped, use_container_width=True)
        else:
            st.success(f"🎉 ตรวจจับและจับคู่กับ Master Data Model ครบสมบูรณ์ 100%! (ทั้งหมด {len(df_wide)} แถว)")

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("จำนวนรายการทั้งหมด", f"{len(df_wide):,} แถว")
        kpi2.metric("เดือนที่ครอบคลุม", f"{df_wide['เดือน'].nunique()} เดือน")
        if 'น้ำมันดิบ (บาร์เรล/วัน)' in df_wide.columns:
            kpi3.metric("ปริมาณน้ำมันดิบรวมเฉลี่ย", f"{df_wide['น้ำมันดิบ (บาร์เรล/วัน)'].mean():,.1f} BPD")
        else:
            kpi3.metric("ผู้ดำเนินการ (Operators)", f"{df_wide['ผู้ดำเนินการ'].nunique()} ราย")
        kpi4.metric("ผู้ดำเนินการ (Operators)", f"{df_wide['ผู้ดำเนินการ'].nunique()} ราย")

        st.markdown("---")

        d_col1, d_col2, d_col3 = st.columns([1.5, 1.5, 3])
        with d_col1:
            buf_excel = io.BytesIO()
            with pd.ExcelWriter(buf_excel, engine='openpyxl') as wr:
                df_wide.to_excel(wr, sheet_name='Flat_Wide', index=False)
                df_long.to_excel(wr, sheet_name='Flat_Long_Unpivoted', index=False)
            buf_excel.seek(0)
            st.download_button(
                label="📥 ดาวน์โหลด Excel (.xlsx มี 2 ชีท)",
                data=buf_excel,
                file_name="DMF_Petroleum_Production_Flat_Table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with d_col2:
            st.download_button(
                label="📥 ดาวน์โหลด CSV (UTF-8)",
                data=df_wide.to_csv(index=False).encode('utf-8-sig'),
                file_name="DMF_Petroleum_Production_Flat_Wide.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d_col3:
            st.info(f"💾 **บันทึกอัตโนมัติแล้ว:** `{os.path.relpath(DEFAULT_OUTPUT_FILE, BASE_DIR)}`")

        st.write("### 👀 พรีวิวตารางข้อมูลผลลัพธ์")
        sub_tab_wide, sub_tab_long = st.tabs(["ตาราง Flat แบบ Wide (คอลัมน์กว้าง)", "ตาราง Flat แบบ Long (สำหรับ Power BI / SQL)"])

        with sub_tab_wide:
            st.dataframe(df_wide, use_container_width=True, height=450)

        with sub_tab_long:
            st.dataframe(df_long, use_container_width=True, height=450)

if is_admin and tab_convert is not None:
    with tab_convert:
        render_production_converter()

# ====================================================
# TAB 2: MASTER LIST MANAGEMENT (ADMIN ONLY)
# ====================================================
def render_production_master():
    st.subheader("🏷️ จัดการ Master Data Model & ฐานข้อมูลแหล่งฝาง (Admin)")
    st.caption("จัดการโครงสร้างข้อมูล Master Mapping สำหรับ DMF และบันทึกค่าน้ำมันดิบแหล่งฝาง (DEDP) ประจำแต่ละเดือน")

    subtab_dmf_m, subtab_fang_m = st.tabs([
        "📑 1. Master Mapping กรมเชื้อเพลิงฯ (DMF)",
        "🛢️ 2. ค่าน้ำมันดิบ แหล่งฝาง รายเดือน (Fang - DEDP)"
    ])

    with subtab_dmf_m:
        st.markdown("##### 📋 ตาราง Master Mapping สำหรับเชื่อมโยงข้อมูล DMF")
        st.caption("คุณสามารถดับเบิลคลิกแก้ไขข้อมูลในตารางด้านล่างนี้ได้โดยตรงเหมือนใช้ Excel เมื่อแก้ไขเสร็จแล้วให้กดปุ่ม 'บันทึก Master List'")

        df_master_current = load_master_mapping()

        edited_master = st.data_editor(
            df_master_current,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            key="master_editor"
        )

        col_btn_save, col_info = st.columns([1, 3])
        with col_btn_save:
            if st.button("💾 บันทึก Master List", type="primary", use_container_width=True):
                save_master_mapping(edited_master)
                st.success("บันทึกข้อมูล Master Data Model เรียบร้อยแล้ว!")
                st.rerun()

        with col_info:
            st.caption(f"📁 ไฟล์ Master ถูกจัดเก็บไว้ที่: `{os.path.basename(MASTER_FILE)}` (เปิดแก้ไขด้วย Excel ได้เช่นกัน)")

    with subtab_fang_m:
        st.markdown("##### 🛢️ กรอกและจัดการค่าน้ำมันดิบ แหล่งฝาง (Fang - DEDP) รายเดือน")
        st.markdown("""
        <div style="background: rgba(224, 242, 254, 0.6); border: 1px solid rgba(186, 230, 253, 0.9); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;">
            <b style="color: #0369A1; font-size: 13.5px;">💡 คำชี้แจงสำหรับผู้ดูแลระบบ (Admin):</b><br/>
            <span style="font-size: 12.5px; color: #334155; line-height: 1.6;">
            • ข้อมูลการผลิตน้ำมันดิบของ <b>แหล่งฝาง (สังกัดกรมการพลังงานทหาร - DEDP)</b> ไม่ได้อยู่ในรายงานของกรมเชื้อเพลิงธรรมชาติ (DMF)<br/>
            • คุณสามารถกรอกค่าน้ำมันดิบ (บาร์เรล/วัน - BPD) ของแต่ละเดือนในตารางด้านล่างนี้ และกดปุ่ม <b>"💾 บันทึกตารางค่าน้ำมันดิบแหล่งฝาง"</b><br/>
            • ข้อมูลที่บันทึกจะถูกนำไปแสดงใน <b>รายงานรายเดือนของแต่ละเดือน (PTIT Domestic Production Report)</b> และรวมในแดชบอร์ดโดยอัตโนมัติ
            </span>
        </div>
        """, unsafe_allow_html=True)

        fang_all = load_fang_master()
        avail_years = sorted(list(fang_all.keys()))
        if not avail_years:
            avail_years = ["2569"]

        col_fy, col_fblank = st.columns([1.5, 3])
        with col_fy:
            sel_f_year = st.selectbox("เลือกปี พ.ศ.:", avail_years, index=0, key="sel_fang_year_master")

        y_dict = fang_all.get(sel_f_year, {})

        fang_records = []
        for m in THAI_MONTHS:
            val = float(y_dict.get(m, 0.0))
            status_txt = "✅ มีข้อมูลแล้ว" if val > 0 else "⏳ ยังไม่มีข้อมูล (0.0)"
            fang_records.append({
                "ลำดับ": MONTH_ORDER.get(m, 99),
                "เดือน": m,
                "ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)": val,
                "สถานะ": status_txt
            })
        df_fang_edit = pd.DataFrame(fang_records)

        edited_fang = st.data_editor(
            df_fang_edit,
            column_config={
                "ลำดับ": st.column_config.NumberColumn("ลำดับ", disabled=True, width="small"),
                "เดือน": st.column_config.TextColumn("เดือน", disabled=True, width="medium"),
                "ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)": st.column_config.NumberColumn(
                    "ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)",
                    min_value=0.0,
                    step=10.0,
                    format="%.1f"
                ),
                "สถานะ": st.column_config.TextColumn("สถานะ", disabled=True, width="medium")
            },
            use_container_width=True,
            hide_index=True,
            key="fang_data_editor"
        )

        col_f_btn, col_f_dl_xl, col_f_dl_js = st.columns([1.5, 1.4, 1.4])
        with col_f_btn:
            if st.button("💾 บันทึกตารางค่าน้ำมันดิบแหล่งฝาง", type="primary", use_container_width=True, key="btn_save_fang_table"):
                updated_dict = {}
                for _, r in edited_fang.iterrows():
                    updated_dict[r["เดือน"]] = float(r["ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)"])
                fang_all[sel_f_year] = updated_dict
                save_fang_master(fang_all)
                if 'df_flat_wide' in st.session_state:
                    st.session_state['df_flat_wide'] = inject_fang_to_dataframe(st.session_state['df_flat_wide'])
                    try:
                        with pd.ExcelWriter(DEFAULT_OUTPUT_FILE, engine='openpyxl') as writer:
                            st.session_state['df_flat_wide'].to_excel(writer, sheet_name='Flat_Wide', index=False)
                            if 'df_flat_long' in st.session_state:
                                st.session_state['df_flat_long'].to_excel(writer, sheet_name='Flat_Long_Unpivoted', index=False)
                    except Exception:
                        pass
                st.success(f"🎉 บันทึกค่าน้ำมันดิบแหล่งฝางประจำปี {sel_f_year} เรียบร้อยแล้ว! (บันทึกทั้งไฟล์ Excel และ JSON ในโฟลเดอร์)")
                st.rerun()

        with col_f_dl_xl:
            buf_fang_xl = io.BytesIO()
            wb_exp = openpyxl.Workbook()
            ws_exp = wb_exp.active
            ws_exp.title = "Fang_Production"
            ws_exp.append(["ปี", "ลำดับเดือน", "เดือน", "ค่าน้ำมันดิบ (บาร์เรล/วัน - BPD)"])
            for y_s, m_d in fang_all.items():
                for m_n in THAI_MONTHS:
                    ws_exp.append([str(y_s), MONTH_ORDER.get(m_n, 99), m_n, float(m_d.get(m_n, 0.0))])
            wb_exp.save(buf_fang_xl)
            st.download_button(
                label="📥 ดาวน์โหลด Excel (Fang.xlsx)",
                data=buf_fang_xl.getvalue(),
                file_name="fang_production_master.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_fang_excel"
            )

        with col_f_dl_js:
            fang_backup_json = json.dumps(fang_all, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์สำรอง (JSON)",
                data=fang_backup_json,
                file_name="fang_production_master.json",
                mime="application/json",
                use_container_width=True,
                key="btn_dl_fang_backup"
            )

        st.caption("📁 บันทึกข้อมูลที่: `fang_production_master.xlsx` และ `fang_production_master.json` ในโฟลเดอร์โปรเจกต์โดยอัตโนมัติ")

        with st.expander("📤 กู้คืน / นำเข้าไฟล์ค่าน้ำมันดิบแหล่งฝาง (Import from Excel or JSON)", expanded=False):
            st.caption("คุณสามารถเปิดไฟล์ `fang_production_master.xlsx` แก้ไขตัวเลขใน Excel ในคอมพิวเตอร์ของคุณ แล้วนำไฟล์มาอัปโหลดที่นี่เพื่ออัปเดตระบบได้ทันที")
            uploaded_fang = st.file_uploader("เลือกไฟล์ Excel (.xlsx) หรือ JSON (.json):", type=["xlsx", "xls", "json"], key="upload_fang_restore")
            if uploaded_fang is not None:
                try:
                    if uploaded_fang.name.endswith(".json"):
                        restored_data = json.load(uploaded_fang)
                    else:
                        wb_imp = openpyxl.load_workbook(uploaded_fang, data_only=True)
                        ws_imp = wb_imp.active
                        r_list = list(ws_imp.iter_rows(values_only=True))
                        restored_data = {}
                        if len(r_list) > 1:
                            hdr = [str(c or '').strip() for c in r_list[0]]
                            i_y = hdr.index("ปี") if "ปี" in hdr else 0
                            i_m = hdr.index("เดือน") if "เดือน" in hdr else 2
                            i_v = len(hdr) - 1
                            for idx, h in enumerate(hdr):
                                if "ค่าน้ำมันดิบ" in h or "BPD" in h:
                                    i_v = idx
                                    break
                            for r in r_list[1:]:
                                if r[i_y] is not None and r[i_m] is not None:
                                    y_str = str(r[i_y]).strip()
                                    m_str = str(r[i_m]).strip()
                                    v_num = float(r[i_v]) if r[i_v] is not None and str(r[i_v]).replace('.', '', 1).isdigit() else 0.0
                                    if y_str not in restored_data:
                                        restored_data[y_str] = {}
                                    restored_data[y_str][m_str] = v_num

                    if st.button("⚡ ยืนยันการนำเข้าข้อมูลแหล่งฝาง", type="primary", key="btn_confirm_fang_restore"):
                        save_fang_master(restored_data)
                        if 'df_flat_wide' in st.session_state:
                            st.session_state['df_flat_wide'] = inject_fang_to_dataframe(st.session_state['df_flat_wide'])
                        st.success("✅ นำเข้าข้อมูลค่าน้ำมันดิบแหล่งฝางสำเร็จเรียบร้อยแล้ว!")
                        st.rerun()
                except Exception as err:
                    st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {err}")

if is_admin and tab_master is not None:
    with tab_master:
        render_production_master()

# ====================================================
# TAB 3: CHARTS & VISUALIZATIONS
# ====================================================
with tab_charts:
    st.subheader("📊 สรุปสถิติและแนวโน้มการผลิต (Monthly Production Statistics & Trends)")

    if 'df_flat_wide' in st.session_state and not st.session_state['df_flat_wide'].empty:
        df_data = st.session_state['df_flat_wide'].copy()

        if 'ลำดับเดือน' not in df_data.columns:
            df_data['ลำดับเดือน'] = df_data['เดือน'].map(MONTH_ORDER).fillna(99)

        # Executive Summary & Quick Download Bar (UI Pro Max Bento Style)
        p_months = df_data[['เดือน', 'ลำดับเดือน']].drop_duplicates().sort_values('ลำดับเดือน')['เดือน'].tolist()
        num_m = len(p_months)
        latest_m = p_months[-1] if p_months else "ล่าสุด"
        
        tot_gas_daily = df_data.groupby('เดือน')['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)'].sum().mean() if 'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)' in df_data.columns else 0
        tot_oil_daily = df_data.groupby('เดือน')['น้ำมันดิบ (บาร์เรล/วัน)'].sum().mean() if 'น้ำมันดิบ (บาร์เรล/วัน)' in df_data.columns else 0
        tot_cnd_daily = df_data.groupby('เดือน')['ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)'].sum().mean() if 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)' in df_data.columns else 0
        tot_boed_daily = df_data.groupby('เดือน')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().mean() if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_data.columns else 0
        
        # Executive Telemetry Hero Banner (Clean, Focused on Metrics)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(224, 242, 254, 0.7) 0%, rgba(240, 249, 255, 0.9) 100%); border: 1px solid rgba(186, 230, 253, 0.85); border-radius: 14px; padding: 14px 20px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(2, 132, 199, 0.05); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                    <span style="font-size: 14.5px; font-weight: 800; color: #0369A1;">
                        🛢️ ภาพรวมการผลิตปิโตรเลียมเฉลี่ย {num_m} เดือน (มกราคม - {latest_m} 2569)
                    </span>
                    <span style="background: #0284C7; color: white; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 12px; letter-spacing: 0.04em;">
                        LIVE TELEMETRY
                    </span>
                </div>
                <div style="font-size: 12.5px; color: #334155; line-height: 1.6;">
                    • <b>การผลิตรวมเฉลี่ย:</b> <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #0284C7;">{tot_boed_daily:,.0f} BOED</span> &nbsp;|&nbsp; 
                    • <b>ก๊าซธรรมชาติเฉลี่ย:</b> <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">{tot_gas_daily:,.1f} MMSCFD</span><br/>
                    • <b>น้ำมันดิบเฉลี่ย:</b> <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">{tot_oil_daily:,.0f} BPD</span> &nbsp;|&nbsp; 
                    • <b>คอนเดนเสทเฉลี่ย:</b> <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">{tot_cnd_daily:,.0f} BPD</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(186, 230, 253, 0.9); font-size: 11.5px; font-weight: 600; color: #0369A1; padding: 6px 14px; border-radius: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    📊 สถิติสะสม {len(df_data):,} แถว ({num_m} เดือน)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 กรองข้อมูลภาพรวม (Area & Operator Filter)", expanded=False):
            c_filter1, c_filter2 = st.columns(2)
            with c_filter1:
                all_areas = sorted(df_data['พื้นที่'].dropna().unique())
                sel_area = st.multiselect("กรองตามพื้นที่ (Area):", options=all_areas, default=all_areas)
        with c_filter2:
            all_ops = sorted(df_data['ผู้ดำเนินการ'].dropna().unique())
            sel_op = st.multiselect("กรองตามผู้ดำเนินการ (Operator):", options=all_ops, default=all_ops)

        df_filtered = df_data[(df_data['พื้นที่'].isin(sel_area)) & (df_data['ผู้ดำเนินการ'].isin(sel_op))].copy()

        if df_filtered.empty:
            st.warning("⚠️ ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาเลือกพื้นที่หรือผู้ดำเนินการอย่างน้อย 1 รายการ")
        else:
            subtab_trend, subtab_op, subtab_spotlight, subtab_overall = st.tabs([
                "📅 1. แนวโน้มรายเดือน (Monthly Trends)",
                "🏢 2. แนวโน้มแยกตาม Operator & พื้นที่",
                "🔍 3. เจาะลึกสถิติประจำเดือน (Monthly Deep-Dive)",
                "🥧 4. ภาพรวมสัดส่วนสะสม (Market Share & Basins)"
            ])

            # ----------------------------------------------------
            # Subtab 1: Monthly Trends & Native Units
            # ----------------------------------------------------
            with subtab_trend:
                cols_to_sum = {
                    'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': 'sum',
                    'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': 'sum',
                    'น้ำมันดิบ (บาร์เรล/วัน)': 'sum',
                    'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'sum',
                    'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'sum',
                    'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'sum'
                }
                avail_cols = {k: v for k, v in cols_to_sum.items() if k in df_filtered.columns}
                df_monthly = df_filtered.groupby(['เดือน', 'ลำดับเดือน'], as_index=False).agg(avail_cols).sort_values('ลำดับเดือน').reset_index(drop=True)

                # MoM calculation
                for col in ['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 'น้ำมันดิบ (บาร์เรล/วัน)', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)']:
                    if col in df_monthly.columns:
                        df_monthly[f'{col}_MoM_diff'] = df_monthly[col].diff()
                        df_monthly[f'{col}_MoM_pct'] = (df_monthly[f'{col}_MoM_diff'] / df_monthly[col].shift(1)) * 100

                if not df_monthly.empty:
                    latest_row = df_monthly.iloc[-1]
                    st.markdown(f"##### 📌 สถิติการผลิตประจำเดือนล่าสุด: **{latest_row['เดือน']}**")
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    with kpi1:
                        v = latest_row.get('ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 0)
                        p = latest_row.get('ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)_MoM_pct', None)
                        st.metric("💨 ก๊าซธรรมชาติ", f"{v:,.1f} MMSCFD", f"{p:+.1f}% MoM" if pd.notna(p) else None)
                    with kpi2:
                        v = latest_row.get('ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)', 0)
                        p = latest_row.get('ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)_MoM_pct', None)
                        st.metric("💧 ก๊าซธรรมชาติเหลว", f"{v:,.0f} BPD", f"{p:+.1f}% MoM" if pd.notna(p) else None)
                    with kpi3:
                        v = latest_row.get('น้ำมันดิบ (บาร์เรล/วัน)', 0)
                        p = latest_row.get('น้ำมันดิบ (บาร์เรล/วัน)_MoM_pct', None)
                        st.metric("🛢️ น้ำมันดิบ", f"{v:,.0f} BPD", f"{p:+.1f}% MoM" if pd.notna(p) else None)
                    with kpi4:
                        v = latest_row.get('รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)', 0)
                        p = latest_row.get('รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)_MoM_pct', None)
                        st.metric("⚡ รวมเทียบเท่าน้ำมันดิบ", f"{v:,.0f} BOED", f"{p:+.1f}% MoM" if pd.notna(p) else None)

                    st.markdown("---")

                    # 1. Total BOED Stacked Bar Chart
                    st.markdown("#### 1.1 แนวโน้มปริมาณการผลิตรวมเทียบเท่าน้ำมันดิบรายเดือน (BOED)")
                    boed_parts = [
                        'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                        'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                        'น้ำมันดิบ (บาร์เรล/วัน)'
                    ]
                    boed_avail = [c for c in boed_parts if c in df_monthly.columns]
                    if boed_avail:
                        fig_boed = px.bar(
                            df_monthly,
                            x='เดือน',
                            y=boed_avail,
                            barmode='stack',
                            title="ปริมาณการผลิตรวมเทียบเท่าน้ำมันดิบรายเดือน (BOED)",
                            labels={'value': 'ปริมาณ (BOED)', 'variable': 'ประเภทเชื้อเพลิง', 'เดือน': 'เดือน'},
                            color_discrete_map={
                                'ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': '#0284C7',
                                'ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': '#7C3AED',
                                'น้ำมันดิบ (บาร์เรล/วัน)': '#EA580C'
                            }
                        )
                        fig_boed.update_layout(
                            hovermode="x unified",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        apply_crystal_aqua_theme(fig_boed)
                        st.plotly_chart(fig_boed, use_container_width=True)

                    # 2. Native Units 3 Columns
                    st.markdown("#### 1.2 แนวโน้มรายเดือนแยกตาม 3 ผลิตภัณฑ์หลัก (หน่วยจริง)")
                    col_c1, col_c2, col_c3 = st.columns(3)
                    with col_c1:
                        if 'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)' in df_monthly.columns:
                            fig_gas = px.bar(
                                df_monthly, x='เดือน', y='ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)',
                                text_auto='.1f', title="💨 ก๊าซธรรมชาติ (MMSCFD)",
                                color_discrete_sequence=['#0284C7']
                            )
                            fig_gas.update_traces(textposition='outside')
                            fig_gas.update_layout(yaxis_title='MMSCFD', xaxis_title='')
                            apply_crystal_aqua_theme(fig_gas)
                            st.plotly_chart(fig_gas, use_container_width=True)

                    with col_c2:
                        if 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)' in df_monthly.columns:
                            fig_cond = px.bar(
                                df_monthly, x='เดือน', y='ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
                                text_auto=',.0f', title="💧 ก๊าซธรรมชาติเหลว (BPD)",
                                color_discrete_sequence=['#7C3AED']
                            )
                            fig_cond.update_traces(textposition='outside')
                            fig_cond.update_layout(yaxis_title='BPD', xaxis_title='')
                            apply_crystal_aqua_theme(fig_cond)
                            st.plotly_chart(fig_cond, use_container_width=True)

                    with col_c3:
                        if 'น้ำมันดิบ (บาร์เรล/วัน)' in df_monthly.columns:
                            fig_crude = px.bar(
                                df_monthly, x='เดือน', y='น้ำมันดิบ (บาร์เรล/วัน)',
                                text_auto=',.0f', title="🛢️ น้ำมันดิบ (BPD)",
                                color_discrete_sequence=['#EA580C']
                            )
                            fig_crude.update_traces(textposition='outside')
                            fig_crude.update_layout(yaxis_title='BPD', xaxis_title='')
                            apply_crystal_aqua_theme(fig_crude)
                            st.plotly_chart(fig_crude, use_container_width=True)

                    # 3. Monthly Summary Data Table
                    st.markdown("#### 1.3 ตารางสรุปตัวเลขสถิติรายเดือน")
                    display_cols = [
                        'เดือน',
                        'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)',
                        'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
                        'น้ำมันดิบ (บาร์เรล/วัน)',
                        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)_MoM_diff',
                        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)_MoM_pct'
                    ]
                    cols_in_table = [c for c in display_cols if c in df_monthly.columns]
                    df_table_show = df_monthly[cols_in_table].copy()
                    rename_map = {
                        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)_MoM_diff': 'เปลี่ยนแปลง MoM (BOED)',
                        'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)_MoM_pct': 'MoM (%)'
                    }
                    df_table_show.rename(columns=rename_map, inplace=True)
                    st.dataframe(
                        df_table_show.style.format({
                            'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': '{:,.1f}',
                            'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': '{:,.0f}',
                            'น้ำมันดิบ (บาร์เรล/วัน)': '{:,.0f}',
                            'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': '{:,.0f}',
                            'เปลี่ยนแปลง MoM (BOED)': lambda x: f"{x:+,.0f}" if pd.notna(x) else "-",
                            'MoM (%)': lambda x: f"{x:+.2f}%" if pd.notna(x) else "-"
                        }),
                        use_container_width=True
                    )

            # ----------------------------------------------------
            # Subtab 2: Monthly Operator & Region Breakdown
            # ----------------------------------------------------
            with subtab_op:
                st.markdown("#### 2.1 แนวโน้มปริมาณการผลิตรายเดือนตาม Operator (BOED)")
                if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_filtered.columns and 'ผู้ดำเนินการ' in df_filtered.columns:
                    df_op_m = df_filtered.groupby(['ผู้ดำเนินการ', 'เดือน', 'ลำดับเดือน'], as_index=False)['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().sort_values('ลำดับเดือน')
                    all_op_list = sorted(df_filtered['ผู้ดำเนินการ'].dropna().unique())
                    top_default = df_filtered.groupby('ผู้ดำเนินการ')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().nlargest(6).index.tolist()

                    sel_ops_chart = st.multiselect(
                        "เลือก Operator ที่ต้องการเปรียบเทียบในกราฟเส้น:",
                        options=all_op_list,
                        default=top_default
                    )

                    df_op_m_filtered = df_op_m[df_op_m['ผู้ดำเนินการ'].isin(sel_ops_chart)]
                    if not df_op_m_filtered.empty:
                        fig_op_line = px.line(
                            df_op_m_filtered,
                            x='เดือน',
                            y='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                            color='ผู้ดำเนินการ',
                            markers=True,
                            title="แนวโน้มการผลิตรายเดือนจำแนกตาม Operator (BOED)",
                            labels={'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'ปริมาณ (BOED)', 'เดือน': 'เดือน'},
                            color_discrete_sequence=['#0284C7', '#023E8A', '#EA580C', '#7C3AED', '#0096C7', '#F77F00', '#10B981', '#64748B']
                        )
                        fig_op_line.update_layout(hovermode="x unified")
                        apply_crystal_aqua_theme(fig_op_line)
                        st.plotly_chart(fig_op_line, use_container_width=True)

                st.markdown("#### 2.2 เปรียบเทียบการผลิต Onshore vs Offshore รายเดือน (BOED)")
                if 'พื้นที่' in df_filtered.columns and 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_filtered.columns:
                    df_reg_m = df_filtered.groupby(['พื้นที่', 'เดือน', 'ลำดับเดือน'], as_index=False)['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().sort_values('ลำดับเดือน')
                    fig_reg = px.bar(
                        df_reg_m,
                        x='เดือน',
                        y='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                        color='พื้นที่',
                        barmode='group',
                        title="ปริมาณการผลิต บนบก (Onshore) เทียบกับ ในทะเล (Offshore) แต่ละเดือน",
                        labels={'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'ปริมาณ (BOED)', 'เดือน': 'เดือน'},
                        color_discrete_map={'บนบก': '#EA580C', 'ในทะเล': '#0284C7'}
                    )
                    apply_crystal_aqua_theme(fig_reg)
                    st.plotly_chart(fig_reg, use_container_width=True)

            # ----------------------------------------------------
            # Subtab 3: Monthly Deep-Dive / Spotlight
            # ----------------------------------------------------
            with subtab_spotlight:
                st.markdown("#### 3. เจาะลึกสถิติประจำเดือน (Monthly Deep-Dive)")
                all_months_ordered = df_filtered[['เดือน', 'ลำดับเดือน']].drop_duplicates().sort_values('ลำดับเดือน', ascending=False)['เดือน'].tolist()
                
                sel_dive_month = st.selectbox(
                    "📅 เลือกเดือนที่ต้องการเจาะลึกข้อมูล:",
                    options=all_months_ordered,
                    index=0
                )

                df_spot = df_filtered[df_filtered['เดือน'] == sel_dive_month].copy()

                if not df_spot.empty:
                    # Metric row for selected month
                    m_gas = df_spot['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)'].sum() if 'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)' in df_spot.columns else 0
                    m_cond = df_spot['ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)'].sum() if 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)' in df_spot.columns else 0
                    m_crude = df_spot['น้ำมันดิบ (บาร์เรล/วัน)'].sum() if 'น้ำมันดิบ (บาร์เรล/วัน)' in df_spot.columns else 0
                    m_boed = df_spot['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum() if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_spot.columns else 0

                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric("💨 ก๊าซธรรมชาติ", f"{m_gas:,.1f} MMSCFD")
                    c_m2.metric("💧 ก๊าซธรรมชาติเหลว", f"{m_cond:,.0f} BPD")
                    c_m3.metric("🛢️ น้ำมันดิบ", f"{m_crude:,.0f} BPD")
                    c_m4.metric("⚡ รวมเทียบเท่า", f"{m_boed:,.0f} BOED")

                    st.markdown("---")

                    col_spot_left, col_spot_right = st.columns([3, 2])

                    with col_spot_left:
                        st.markdown(f"##### 🏆 Top 10 แหล่งผลิตสูงสุดในเดือน **{sel_dive_month}** (BOED)")
                        if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_spot.columns:
                            df_top10 = df_spot.nlargest(10, 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)').sort_values('รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)', ascending=True)
                            fig_top10 = px.bar(
                                df_top10,
                                x='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                                y='แหล่ง_ไฟล์ดิบ',
                                orientation='h',
                                text_auto=',.0f',
                                title=f"Top 10 แหล่งผลิตสูงสุด ({sel_dive_month})",
                                labels={'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': 'ปริมาณเทียบเท่าน้ำมันดิบ (BOED)', 'แหล่ง_ไฟล์ดิบ': 'ชื่อแหล่ง'},
                                color='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                                color_continuous_scale=['#BAE6FD', '#0284C7', '#023E8A']
                            )
                            fig_top10.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
                            apply_crystal_aqua_theme(fig_top10)
                            st.plotly_chart(fig_top10, use_container_width=True)

                    with col_spot_right:
                        st.markdown(f"##### 🏢 สัดส่วน Operator เดือน **{sel_dive_month}**")
                        if 'ผู้ดำเนินการ' in df_spot.columns and 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_spot.columns:
                            df_spot_op = df_spot.groupby('ผู้ดำเนินการ')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().reset_index()
                            fig_spot_op = px.pie(
                                df_spot_op,
                                names='ผู้ดำเนินการ',
                                values='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                                hole=0.45,
                                title=f"สัดส่วน Operator ({sel_dive_month})",
                                color_discrete_sequence=['#0284C7', '#023E8A', '#EA580C', '#7C3AED', '#0096C7', '#F77F00', '#10B981', '#64748B']
                            )
                            apply_crystal_aqua_theme(fig_spot_op)
                            st.plotly_chart(fig_spot_op, use_container_width=True)

                    # Table of all fields in selected month
                    with st.expander(f"📋 ดูตารางแสดงข้อมูลทุกแหล่งในเดือน {sel_dive_month} (ทั้งหมด {len(df_spot)} แหล่ง)"):
                        show_cols_spot = [
                            'พื้นที่', 'ผู้ดำเนินการ', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ',
                            'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)', 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
                            'น้ำมันดิบ (บาร์เรล/วัน)', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
                        ]
                        cols_available_spot = [c for c in show_cols_spot if c in df_spot.columns]
                        st.dataframe(
                            df_spot[cols_available_spot].sort_values('รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)', ascending=False).style.format({
                                'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': '{:,.2f}',
                                'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': '{:,.1f}',
                                'น้ำมันดิบ (บาร์เรล/วัน)': '{:,.1f}',
                                'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)': '{:,.1f}'
                            }),
                            use_container_width=True
                        )

            # ----------------------------------------------------
            # Subtab 4: Overall Market Share & Basins
            # ----------------------------------------------------
            with subtab_overall:
                st.markdown("#### 4. ภาพรวมสัดส่วนสะสมทั้งปี (Overall Cumulative Share)")
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.markdown("##### 🏢 สัดส่วนการผลิตตาม Operator รวมสะสม (BOED)")
                    if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_filtered.columns:
                        df_op_total = df_filtered.groupby('ผู้ดำเนินการ')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().reset_index()
                        fig_op_total = px.pie(
                            df_op_total,
                            names='ผู้ดำเนินการ',
                            values='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                            hole=0.45,
                            color_discrete_sequence=['#0284C7', '#023E8A', '#EA580C', '#7C3AED', '#0096C7', '#F77F00', '#10B981', '#64748B']
                        )
                        apply_crystal_aqua_theme(fig_op_total)
                        st.plotly_chart(fig_op_total, use_container_width=True)

                with chart_col2:
                    st.markdown("##### 🌊 สัดส่วนการผลิตตามแอ่งปิโตรเลียม (Basin) รวมสะสม")
                    if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_filtered.columns and 'แอ่งปิโตรเลียม' in df_filtered.columns:
                        df_basin_total = df_filtered.groupby('แอ่งปิโตรเลียม')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().reset_index()
                        fig_basin_total = px.pie(
                            df_basin_total,
                            names='แอ่งปิโตรเลียม',
                            values='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                            hole=0.45,
                            color_discrete_sequence=['#0284C7', '#0096C7', '#023E8A', '#48CAE4', '#90E0EF', '#ADE8F4']
                        )
                        apply_crystal_aqua_theme(fig_basin_total)
                        st.plotly_chart(fig_basin_total, use_container_width=True)

                if 'ประเภทสัญญา' in df_filtered.columns and 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_filtered.columns:
                    st.markdown("##### 📜 สัดส่วนการผลิตตามประเภทสัญญา (Concession vs PSC)")
                    df_contract_total = df_filtered.groupby('ประเภทสัญญา')['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum().reset_index()
                    fig_contract = px.pie(
                        df_contract_total,
                        names='ประเภทสัญญา',
                        values='รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                        hole=0.45,
                        color_discrete_sequence=['#023E8A', '#0284C7', '#7C3AED']
                    )
                    apply_crystal_aqua_theme(fig_contract)
                    st.plotly_chart(fig_contract, use_container_width=True)
    else:
        if st.session_state.get('user_role', 'viewer') == 'admin':
            st.info("💡 ยังไม่มีข้อมูลการผลิตในระบบ สามารถกดปุ่ม '⚡ 1-Click Auto Sync การผลิต' ในแถบเมนูด้านซ้ายเพื่อดึงข้อมูลสดจาก DMF ได้ทันทีครับ")
        else:
            st.info("💡 ขณะนี้ยังไม่มีข้อมูลการผลิตในระบบ กรุณาติดต่อผู้ดูแลระบบ (Admin) เพื่อรัน Auto Sync ข้อมูลล่าสุดครับ")


import os, sys, json, io, re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Theme Design Tokens for Annual Letterhead Table
ANNUAL_THEME_TOKENS = {
    'imperial': {
        'card_bg': '#FFFFFF',
        'card_border': 'rgba(197, 160, 89, 0.45)',
        'card_shadow': '0 20px 48px -12px rgba(44, 30, 18, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
        'masthead_bg': 'linear-gradient(135deg, #1C1917 0%, #2A2118 60%, #38271A 100%)',
        'masthead_accent': '#C5A059',
        'masthead_org': '#D4AF37',
        'badge_bg': 'rgba(212, 175, 55, 0.18)',
        'badge_fg': '#E5C378',
        'badge_border': 'rgba(212, 175, 55, 0.4)',
        'th_main_bg': 'linear-gradient(135deg, #24180E 0%, #332216 100%)',
        'th_sub_bg': '#2E2218',
        'th_sub_color': '#FAF6F0',
        'unit_chip_bg': 'rgba(197, 160, 89, 0.22)',
        'unit_chip_color': '#F5D899',
        'unit_chip_border': 'rgba(197, 160, 89, 0.45)',
        'sec_bg': 'linear-gradient(90deg, #784E20 0%, #966734 50%, #7D5325 100%)',
        'sec_color': '#FFFFFF',
        'sec_badge_bg': 'rgba(0, 0, 0, 0.2)',
        'sec_badge_color': '#FFFFFF',
        'zebra_bg': '#FAF7F2',
        'hover_bg': '#F5EFE6',
        'hover_border': '#C5A059',
        'tot_bg': 'linear-gradient(90deg, #EFE5D5 0%, #E3D3BE 100%)',
        'tot_color': '#1C1917',
        'tot_border_top': '#784E20',
        'tot_border_bot': '#3D240E',
        'grid_border': '#E8E2D8'
    },
    'navy': {
        'card_bg': '#FFFFFF',
        'card_border': 'rgba(30, 58, 138, 0.35)',
        'card_shadow': '0 20px 48px -12px rgba(15, 23, 42, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
        'masthead_bg': 'linear-gradient(135deg, #0A1128 0%, #0F172A 60%, #1E293B 100%)',
        'masthead_accent': '#38BDF8',
        'masthead_org': '#93C5FD',
        'badge_bg': 'rgba(56, 189, 248, 0.18)',
        'badge_fg': '#38BDF8',
        'badge_border': 'rgba(56, 189, 248, 0.4)',
        'th_main_bg': 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
        'th_sub_bg': '#162038',
        'th_sub_color': '#F1F5F9',
        'unit_chip_bg': 'rgba(56, 189, 248, 0.18)',
        'unit_chip_color': '#38BDF8',
        'unit_chip_border': 'rgba(56, 189, 248, 0.4)',
        'sec_bg': 'linear-gradient(90deg, #1E3A8A 0%, #2563EB 50%, #1E40AF 100%)',
        'sec_color': '#FFFFFF',
        'sec_badge_bg': 'rgba(0, 0, 0, 0.25)',
        'sec_badge_color': '#FFFFFF',
        'zebra_bg': '#F8FAFC',
        'hover_bg': '#EFF6FF',
        'hover_border': '#38BDF8',
        'tot_bg': 'linear-gradient(90deg, #EFF6FF 0%, #DBEAFE 100%)',
        'tot_color': '#0F172A',
        'tot_border_top': '#1E3A8A',
        'tot_border_bot': '#0F172A',
        'grid_border': '#E2E8F0'
    },
    'emerald': {
        'card_bg': '#FFFFFF',
        'card_border': 'rgba(4, 120, 87, 0.35)',
        'card_shadow': '0 20px 48px -12px rgba(6, 78, 59, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
        'masthead_bg': 'linear-gradient(135deg, #091310 0%, #0F201B 60%, #162F27 100%)',
        'masthead_accent': '#10B981',
        'masthead_org': '#6EE7B7',
        'badge_bg': 'rgba(16, 185, 129, 0.18)',
        'badge_fg': '#34D399',
        'badge_border': 'rgba(16, 185, 129, 0.4)',
        'th_main_bg': 'linear-gradient(135deg, #0F281E 0%, #132620 100%)',
        'th_sub_bg': '#132620',
        'th_sub_color': '#ECFDF5',
        'unit_chip_bg': 'rgba(16, 185, 129, 0.18)',
        'unit_chip_color': '#34D399',
        'unit_chip_border': 'rgba(16, 185, 129, 0.4)',
        'sec_bg': 'linear-gradient(90deg, #065F46 0%, #047857 50%, #064E3B 100%)',
        'sec_color': '#FFFFFF',
        'sec_badge_bg': 'rgba(0, 0, 0, 0.25)',
        'sec_badge_color': '#FFFFFF',
        'zebra_bg': '#F0FDF4',
        'hover_bg': '#ECFDF5',
        'hover_border': '#10B981',
        'tot_bg': 'linear-gradient(90deg, #ECFDF5 0%, #D1FAE5 100%)',
        'tot_color': '#064E3B',
        'tot_border_top': '#065F46',
        'tot_border_bot': '#064E3B',
        'grid_border': '#D1FAE5'
    }
}

def render_ptit_annual_report(df_all_data, is_admin=False):
    """ฟังก์ชันแสดงผลรายงานการผลิตประจำปี (Annual Production Report) และเครื่องมือสร้าง Pivot Table ตามมาตรฐาน PTIT"""
    # 1. Selection & Configuration Bar
    avail_years = sorted(df_all_data['ปี'].astype(str).unique(), reverse=True)
    
    sel_col1, sel_col2, sel_col3 = st.columns([1.5, 2.2, 1.3])
    with sel_col1:
        sel_year = st.selectbox("📅 เลือกปีรายงาน (Reporting Year):", avail_years, index=0, key="annual_sel_year")
    with sel_col2:
        selected_theme_label = st.selectbox(
            "🎨 สไตล์เทมเพลต (Luxury Theme):",
            [
                "👑 Imperial Bronze & Champagne Gold (Signature Luxury)",
                "💎 Royal Navy & Platinum (Sovereign Executive)",
                "🏛️ Obsidian Platinum & Emerald (Energy Terminal)"
            ],
            index=0,
            key="annual_theme_sel"
        )
        if "Royal Navy" in selected_theme_label:
            report_theme_key = "navy"
        elif "Emerald" in selected_theme_label:
            report_theme_key = "emerald"
        else:
            report_theme_key = "imperial"
    with sel_col3:
        st.write("")
        st.write("")
        show_zero_fields = st.checkbox("แสดงแหล่งยอด 0", value=False, key="annual_show_zero", help="หากเลือก จะแสดงทุกแหล่งสัมปทานแม้ว่าทั้งปีจะไม่มีปริมาณการผลิต")

    # Filter year data
    df_year_data = df_all_data[df_all_data['ปี'].astype(str) == sel_year].copy()
    if 'ลำดับเดือน' not in df_year_data.columns:
        df_year_data['ลำดับเดือน'] = df_year_data['เดือน'].map(MONTH_ORDER).fillna(99)

    avail_months_df = df_year_data[['เดือน', 'ลำดับเดือน']].drop_duplicates().sort_values('ลำดับเดือน')
    active_months = avail_months_df['เดือน'].tolist()
    total_active_days = sum(get_days_in_month(m, sel_year) for m in active_months)
    is_full_year = (len(active_months) == 12)

    # Self-healing Master Mapping lookup for fields
    if 'PTIT_Region' not in df_year_data.columns:
        if 'Lookup_Key' not in df_year_data.columns and 'แปลง_ไฟล์ดิบ' in df_year_data.columns:
            df_year_data['Lookup_Key'] = df_year_data['พื้นที่'].astype(str) + '_' + df_year_data['แปลง_ไฟล์ดิบ'].astype(str) + '_' + df_year_data['แหล่ง_ไฟล์ดิบ'].astype(str)
        df_m = load_master_mapping()
        cols_to_add = [c for c in ['Lookup_Key', 'PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'] if c in df_m.columns]
        if 'Lookup_Key' in df_year_data.columns:
            df_year_data = pd.merge(df_year_data, df_m[cols_to_add], on='Lookup_Key', how='left')

    # Status & YTD Indicator Banner with Fang DEDP Provenance Badge
    period_status_html = f"""
    <div style="background: rgba(248, 250, 252, 0.95); border: 1px solid #CBD5E1; border-radius: 12px; padding: 12px 18px; margin: 12px 0 16px 0; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 18px;">{'🟢' if is_full_year else '🟡'}</span>
                <div>
                    <span style="font-size: 13px; font-weight: 700; color: #0F172A;">สถานะรอบรายงานประจำปี {sel_year}:</span>
                    <span style="font-size: 12.5px; color: #334155; margin-left: 6px;">
                        {'ข้อมูลครบถ้วนเต็มปี (12 เดือน / 365 วัน)' if is_full_year else f'ข้อมูลสะสมระหว่างปี (YTD {len(active_months)} เดือน: {active_months[0]} – {active_months[-1]} {sel_year} | รวม {total_active_days} วันทำการผลิตสะสม)'}
                    </span>
                </div>
            </div>
            <div>
                <span style="background: {'rgba(16, 185, 129, 0.15)' if is_full_year else 'rgba(245, 158, 11, 0.15)'}; color: {'#065F46' if is_full_year else '#92400E'}; border: 1px solid {'rgba(16, 185, 129, 0.35)' if is_full_year else 'rgba(245, 158, 11, 0.35)'}; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase;">
                    {'Full Year Official' if is_full_year else 'YTD Verified Telemetry'}
                </span>
            </div>
        </div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #E2E8F0; display: flex; align-items: center; gap: 8px; font-size: 11.5px; color: #0369A1;">
            <span style="background: #E0F2FE; color: #0284C7; font-weight: 700; font-size: 10px; padding: 2px 6px; border-radius: 4px; border: 1px solid #BAE6FD;">DEDP INTEGRATED</span>
            <span>🛡️ <b>การบูรณาการข้อมูลแหล่งฝาง:</b> สถิติน้ำมันดิบแหล่งฝางนำเข้าและตรวจสอบตรงตามสถิติทางการของกรมการพลังงานทหาร (DEDP) บูรณาการร่วมกับฐานข้อมูลสัมปทานและสัญญาแบ่งปันผลผลิต (DMF) ครบถ้วน</span>
        </div>
    </div>
    """
    st.markdown(period_status_html, unsafe_allow_html=True)

    # 3 Sub-tabs
    ann_subtab1, ann_subtab2, ann_subtab3 = st.tabs([
        "📑 1. สรุปภาพรวมรายแหล่งทั้งปี (Annual Field Summary)",
        "📅 2. ตารางกระจาย 12 เดือน (12-Month Matrix)",
        "🎛️ 3. เครื่องมือจัดตารางกำหนดเอง (Dynamic Pivot Table Builder)"
    ])

    # ----------------------------------------------------
    # SUBTAB 1: ANNUAL FIELD SUMMARY
    # ----------------------------------------------------
    with ann_subtab1:
        # Calculate monthly production volumes
        df_year_data['Month_Days'] = df_year_data['เดือน'].apply(lambda m: get_days_in_month(m, sel_year))
        df_year_data['Gas_MMSCF'] = df_year_data['ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)'] * df_year_data['Month_Days']
        df_year_data['Cond_Bbl'] = df_year_data['ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)'] * df_year_data['Month_Days']
        df_year_data['Crude_Bbl'] = df_year_data['น้ำมันดิบ (บาร์เรล/วัน)'] * df_year_data['Month_Days']
        df_year_data['BOED_Bbl'] = df_year_data['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'] * df_year_data['Month_Days']

        df_agg = df_year_data.groupby(['PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'], as_index=False).agg({
            'Gas_MMSCF': 'sum',
            'Cond_Bbl': 'sum',
            'Crude_Bbl': 'sum',
            'BOED_Bbl': 'sum'
        }).rename(columns={'PTIT_Region': 'Region', 'PTIT_Operator_Field': 'Operator_Field', 'PTIT_Order': 'Order'})

        # Daily weighted averages and Cumulative volumes
        df_agg['Gas_Avg'] = df_agg['Gas_MMSCF'] / total_active_days if total_active_days > 0 else 0.0
        df_agg['Gas_Cum'] = df_agg['Gas_MMSCF'] / 1000.0  # BCF
        df_agg['Cond_Avg'] = df_agg['Cond_Bbl'] / total_active_days if total_active_days > 0 else 0.0
        df_agg['Cond_Cum'] = df_agg['Cond_Bbl'] / 1_000_000.0  # MMbbl
        df_agg['Crude_Avg'] = df_agg['Crude_Bbl'] / total_active_days if total_active_days > 0 else 0.0
        df_agg['Crude_Cum'] = df_agg['Crude_Bbl'] / 1_000_000.0  # MMbbl
        df_agg['BOED_Avg'] = df_agg['BOED_Bbl'] / total_active_days if total_active_days > 0 else 0.0
        df_agg['BOED_Cum'] = df_agg['BOED_Bbl'] / 1_000_000.0  # MMBOE

        # DEDP Fang Crude Oil Integration
        fang_cum_bbl = sum(get_fang_value(sel_year, m) * get_days_in_month(m, sel_year) for m in active_months)
        fang_avg_bpd = fang_cum_bbl / total_active_days if total_active_days > 0 else 0.0

        fang_idx = df_agg[df_agg['Operator_Field'] == 'Defence Energy Department / Fang'].index
        if len(fang_idx) > 0:
            df_agg.loc[fang_idx, 'Crude_Avg'] = fang_avg_bpd
            df_agg.loc[fang_idx, 'Crude_Cum'] = fang_cum_bbl / 1_000_000.0
            df_agg.loc[fang_idx, 'BOED_Avg'] = fang_avg_bpd
            df_agg.loc[fang_idx, 'BOED_Cum'] = fang_cum_bbl / 1_000_000.0
        else:
            if fang_cum_bbl > 0 or show_zero_fields:
                df_fang = pd.DataFrame([{
                    'Region': 'Onshore',
                    'Operator_Field': 'Defence Energy Department / Fang',
                    'Order': 13,
                    'Gas_MMSCF': 0.0, 'Cond_Bbl': 0.0, 'Crude_Bbl': fang_cum_bbl, 'BOED_Bbl': fang_cum_bbl,
                    'Gas_Avg': 0.0, 'Gas_Cum': 0.0, 'Cond_Avg': 0.0, 'Cond_Cum': 0.0,
                    'Crude_Avg': fang_avg_bpd, 'Crude_Cum': fang_cum_bbl / 1_000_000.0,
                    'BOED_Avg': fang_avg_bpd, 'BOED_Cum': fang_cum_bbl / 1_000_000.0
                }])
                df_agg = pd.concat([df_agg, df_fang], ignore_index=True)

        # Filter out zeroes if requested
        if not show_zero_fields:
            df_agg = df_agg[(df_agg['BOED_Avg'] >= 0.05) | (df_agg['Gas_Avg'] >= 0.05) | (df_agg['Cond_Avg'] >= 0.05) | (df_agg['Crude_Avg'] >= 0.05)].reset_index(drop=True)

        df_agg = df_agg.sort_values(['Region', 'Order']).reset_index(drop=True)

        # Total Cumulative BOED for % Share
        tot_boed_cum = df_agg['BOED_Cum'].sum()
        df_agg['Share_Pct'] = (df_agg['BOED_Cum'] / tot_boed_cum * 100.0).fillna(0.0) if tot_boed_cum > 0 else 0.0

        # Subtotals
        onshore_items = df_agg[df_agg['Region'] == 'Onshore'].to_dict('records')
        offshore_items = df_agg[df_agg['Region'] == 'Offshore'].to_dict('records')

        def calc_sub(items):
            return {
                'Gas_Avg': sum(x.get('Gas_Avg', 0.0) for x in items),
                'Gas_Cum': sum(x.get('Gas_Cum', 0.0) for x in items),
                'Cond_Avg': sum(x.get('Cond_Avg', 0.0) for x in items),
                'Cond_Cum': sum(x.get('Cond_Cum', 0.0) for x in items),
                'Crude_Avg': sum(x.get('Crude_Avg', 0.0) for x in items),
                'Crude_Cum': sum(x.get('Crude_Cum', 0.0) for x in items),
                'BOED_Avg': sum(x.get('BOED_Avg', 0.0) for x in items),
                'BOED_Cum': sum(x.get('BOED_Cum', 0.0) for x in items),
                'Share_Pct': sum(x.get('Share_Pct', 0.0) for x in items)
            }

        onshore_sub = calc_sub(onshore_items)
        offshore_sub = calc_sub(offshore_items)
        grand_tot = {k: onshore_sub[k] + offshore_sub[k] for k in onshore_sub}

        # Bento Metric Ribbon (Annual Totals)
        bk = ANNUAL_THEME_TOKENS[report_theme_key]
        bento_cols = st.columns(4)
        
        with bento_cols[0]:
            st.markdown(f"""
            <div style="background: {bk['card_bg']}; border: 1px solid {bk['card_border']}; border-radius: 14px; padding: 14px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 700; color: #0284C7; text-transform: uppercase; letter-spacing: 0.05em;">⛽ ก๊าซธรรมชาติ (Natural Gas)</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">{grand_tot['Gas_Avg']:,.1f} <span style="font-size: 12px; font-weight: 600; color: #64748B;">MMSCFD</span></div>
                <div style="font-size: 11.5px; color: #475569;">สะสมทั้งปี: <b style="color: #0284C7; font-family: 'JetBrains Mono', monospace;">{grand_tot['Gas_Cum']:,.2f}</b> BCF</div>
            </div>
            """, unsafe_allow_html=True)

        with bento_cols[1]:
            st.markdown(f"""
            <div style="background: {bk['card_bg']}; border: 1px solid {bk['card_border']}; border-radius: 14px; padding: 14px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 700; color: #D97706; text-transform: uppercase; letter-spacing: 0.05em;">💧 ก๊าซธรรมชาติเหลว (Condensate)</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">{grand_tot['Cond_Avg']:,.0f} <span style="font-size: 12px; font-weight: 600; color: #64748B;">BPD</span></div>
                <div style="font-size: 11.5px; color: #475569;">สะสมทั้งปี: <b style="color: #D97706; font-family: 'JetBrains Mono', monospace;">{grand_tot['Cond_Cum']:,.2f}</b> MMbbl</div>
            </div>
            """, unsafe_allow_html=True)

        with bento_cols[2]:
            st.markdown(f"""
            <div style="background: {bk['card_bg']}; border: 1px solid {bk['card_border']}; border-radius: 14px; padding: 14px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">🛢️ น้ำมันดิบ (Crude Oil - รวมฝาง)</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">{grand_tot['Crude_Avg']:,.0f} <span style="font-size: 12px; font-weight: 600; color: #64748B;">BPD</span></div>
                <div style="font-size: 11.5px; color: #475569;">สะสมทั้งปี: <b style="color: #475569; font-family: 'JetBrains Mono', monospace;">{grand_tot['Crude_Cum']:,.2f}</b> MMbbl</div>
            </div>
            """, unsafe_allow_html=True)

        with bento_cols[3]:
            st.markdown(f"""
            <div style="background: {bk['card_bg']}; border: 1.5px solid {bk['masthead_accent']}; border-radius: 14px; padding: 14px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 700; color: #7C3AED; text-transform: uppercase; letter-spacing: 0.05em;">⚡ รวมเทียบเท่าน้ำมันดิบ (Total BOED)</div>
                <div style="font-size: 24px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">{grand_tot['BOED_Avg']:,.0f} <span style="font-size: 12px; font-weight: 600; color: #64748B;">BOED</span></div>
                <div style="font-size: 11.5px; color: #475569;">สะสมทั้งปี: <b style="color: #7C3AED; font-family: 'JetBrains Mono', monospace;">{grand_tot['BOED_Cum']:,.2f}</b> MMBOE</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Context-Aware Download Row
        dl_col1, dl_col2 = st.columns([2.5, 1.5])
        with dl_col1:
            st.markdown("""
            <div style="padding: 7px 12px; background: rgba(248, 250, 252, 0.85); border: 1px dashed #CBD5E1; border-radius: 8px; font-size: 12px; color: #475569;">
                ✨ <b>คำแนะนำ:</b> สามารถพิมพ์รายงานสรุปประจำปีสไตล์ Executive Letterhead ทางการได้ทันทีโดยกด <kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Ctrl + P</kbd>
            </div>
            """, unsafe_allow_html=True)
        with dl_col2:
            excel_annual_buf = export_annual_styled_excel(
                sel_year, onshore_items, offshore_items,
                onshore_sub, offshore_sub, grand_tot,
                active_months, report_theme_key
            )
            st.download_button(
                label=f"📥 ดาวน์โหลดรายงานประจำปี ({sel_year}.xlsx)",
                data=excel_annual_buf.getvalue(),
                file_name=f"PTIT_Annual_Production_Summary_{sel_year}_{report_theme_key}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=f"btn_dl_annual_summary_{sel_year}_{report_theme_key}"
            )

        # HTML Table Helper
        def fmt_cell(val, decimals=1, is_int_comma=False):
            if val is None or val == 0:
                return "&nbsp;"
            if val < 0.005:
                return "0.0"
            if is_int_comma:
                return f"{val:,.0f}"
            return f"{val:,.{decimals}f}"

        # HTML Letterhead Table Rendering
        tk = ANNUAL_THEME_TOKENS[report_theme_key]
        html_annual = f"""
        <style>
            .ann-luxury-wrapper {{
                background: {tk['card_bg']};
                border: 1px solid {tk['card_border']};
                box-shadow: {tk['card_shadow']};
                border-radius: 18px;
                overflow: hidden;
                margin-top: 14px;
                font-family: 'Hanken Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .ann-masthead {{
                background: {tk['masthead_bg']};
                border-top: 4px solid {tk['masthead_accent']};
                padding: 22px 28px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 14px;
            }}
            .ann-masthead-org {{
                font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
                font-size: 12.5px;
                font-weight: 700;
                color: {tk['masthead_org']};
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}
            .ann-masthead-title {{
                font-family: 'Manrope', 'Hanken Grotesk', sans-serif;
                font-size: 21px;
                font-weight: 800;
                color: #FFFFFF;
                letter-spacing: -0.015em;
                line-height: 1.25;
            }}
            .ann-masthead-sub {{
                font-size: 13px;
                color: #E2E8F0;
                margin-top: 3px;
                opacity: 0.92;
            }}
            .ann-badge {{
                font-size: 10px;
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 6px;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                display: inline-block;
                background: {tk['badge_bg']};
                color: {tk['badge_fg']};
                border: 1px solid {tk['badge_border']};
            }}
            .ann-table-responsive {{
                overflow-x: auto;
                width: 100%;
            }}
            .ann-luxury-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12.5px;
                color: #1E293B;
            }}
            .ann-luxury-table th, .ann-luxury-table td {{
                border: 1px solid {tk['grid_border']};
                padding: 6px 10px;
                line-height: 1.35;
            }}
            .ann-th-main {{
                background: {tk['th_main_bg']};
                color: #FFFFFF;
                text-align: center;
                font-weight: 700;
                font-size: 12.5px;
                padding: 9px 10px !important;
            }}
            .ann-th-sub {{
                background: {tk['th_sub_bg']};
                color: {tk['th_sub_color']};
                text-align: center;
                font-weight: 700;
                font-size: 11.5px;
                padding: 7px 8px !important;
            }}
            .ann-tr-sec {{
                background: {tk['sec_bg']};
                color: {tk['sec_color']};
                font-weight: 800;
                font-size: 12.5px;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            .ann-tr-item-even {{ background: {tk['zebra_bg']}; }}
            .ann-tr-item-odd {{ background: #FFFFFF; }}
            .ann-num-cell {{
                text-align: right;
                font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
                font-size: 12px;
                font-weight: 500;
            }}
            .ann-tr-subtotal {{
                background: {tk['hover_bg']};
                font-weight: 700;
                color: #0F172A;
                border-top: 1.5px solid {tk['card_border']};
                border-bottom: 1.5px solid {tk['card_border']};
            }}
            .ann-tr-total {{
                background: {tk['tot_bg']};
                font-weight: 800;
                font-size: 13.5px;
                color: {tk['tot_color']};
                border-top: 2.5px solid {tk['tot_border_top']};
                border-bottom: 3.5px double {tk['tot_border_bot']};
            }}
            .ann-footnote-box {{
                background: #F8FAFC;
                border-top: 1px solid {tk['card_border']};
                padding: 12px 24px;
                font-size: 11px;
                color: #64748B;
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                gap: 12px;
            }}
        </style>

        <div class="ann-luxury-wrapper">
            <div class="ann-masthead">
                <div>
                    <div class="ann-masthead-org">PETROLEUM INSTITUTE OF THAILAND</div>
                    <div class="ann-masthead-title">DOMESTIC PETROLEUM PRODUCTION ANNUAL REPORT ({sel_year})</div>
                    <div class="ann-masthead-sub">Annual Production Summary & Cumulative Hydrocarbon Output ({'Full Year' if is_full_year else f'YTD {len(active_months)} Months: {active_months[0]} – {active_months[-1]} {sel_year} | {total_active_days} Operating Days'})</div>
                </div>
                <div style="text-align: right;">
                    <div class="ann-badge">PTIT FOCUS STATISTICS</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 5px; font-family: 'JetBrains Mono', monospace;">OFFICIAL STATISTICAL RELEASE</div>
                </div>
            </div>

            <div class="ann-table-responsive">
                <table class="ann-luxury-table">
                    <thead>
                        <tr>
                            <th class="ann-th-main" rowspan="2" style="width: 26%; text-align: left; padding-left: 20px !important;">Field / Concession</th>
                            <th class="ann-th-main" colspan="4">อัตราการผลิตเฉลี่ยต่อวัน (Daily Average Rate)</th>
                            <th class="ann-th-main" colspan="4">ปริมาณการผลิตสะสมตลอดปี (Cumulative Annual Volume)</th>
                            <th class="ann-th-main" rowspan="2" style="width: 7%;">สัดส่วน<br>(% Share)</th>
                        </tr>
                        <tr>
                            <th class="ann-th-sub">ก๊าซธรรมชาติ<br><span style="font-size: 10px; opacity: 0.85;">(MMSCFD)</span></th>
                            <th class="ann-th-sub">ก๊าซธรรมชาติเหลว<br><span style="font-size: 10px; opacity: 0.85;">(BPD)</span></th>
                            <th class="ann-th-sub">น้ำมันดิบ<br><span style="font-size: 10px; opacity: 0.85;">(BPD)</span></th>
                            <th class="ann-th-sub">รวมเทียบเท่า<br><span style="font-size: 10px; opacity: 0.85;">(BOED)</span></th>
                            <th class="ann-th-sub">ก๊าซธรรมชาติ<br><span style="font-size: 10px; opacity: 0.85;">(BCF)</span></th>
                            <th class="ann-th-sub">ก๊าซธรรมชาติเหลว<br><span style="font-size: 10px; opacity: 0.85;">(MMbbl)</span></th>
                            <th class="ann-th-sub">น้ำมันดิบ<br><span style="font-size: 10px; opacity: 0.85;">(MMbbl)</span></th>
                            <th class="ann-th-sub">รวมเทียบเท่า<br><span style="font-size: 10px; opacity: 0.85;">(MMBOE)</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="ann-tr-sec">
                            <td colspan="10" style="padding-left: 20px;">ONSHORE BASIN</td>
                        </tr>
        """

        for idx, it in enumerate(onshore_items):
            row_cls = "ann-tr-item-even" if (idx % 2 == 1) else "ann-tr-item-odd"
            html_annual += f"""
                        <tr class="{row_cls}">
                            <td style="padding-left: 26px;">{it['Operator_Field']}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Gas_Avg'], 1)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Cond_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Crude_Avg'], 0, True)}</td>
                            <td class="ann-num-cell" style="font-weight: 700;">{fmt_cell(it['BOED_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Gas_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Cond_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Crude_Cum'], 2)}</td>
                            <td class="ann-num-cell" style="font-weight: 700;">{fmt_cell(it['BOED_Cum'], 2)}</td>
                            <td class="ann-num-cell" style="color: #64748B;">{it['Share_Pct']:.1f}%</td>
                        </tr>
            """

        html_annual += f"""
                        <tr class="ann-tr-subtotal">
                            <td style="padding-left: 20px;">Total Onshore Basin</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Gas_Avg'], 1)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Cond_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Crude_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['BOED_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Gas_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Cond_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['Crude_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(onshore_sub['BOED_Cum'], 2)}</td>
                            <td class="ann-num-cell">{onshore_sub['Share_Pct']:.1f}%</td>
                        </tr>
                        <tr class="ann-tr-sec">
                            <td colspan="10" style="padding-left: 20px;">OFFSHORE GULF OF THAILAND</td>
                        </tr>
        """

        for idx, it in enumerate(offshore_items):
            row_cls = "ann-tr-item-even" if (idx % 2 == 1) else "ann-tr-item-odd"
            html_annual += f"""
                        <tr class="{row_cls}">
                            <td style="padding-left: 26px;">{it['Operator_Field']}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Gas_Avg'], 1)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Cond_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Crude_Avg'], 0, True)}</td>
                            <td class="ann-num-cell" style="font-weight: 700;">{fmt_cell(it['BOED_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Gas_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Cond_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(it['Crude_Cum'], 2)}</td>
                            <td class="ann-num-cell" style="font-weight: 700;">{fmt_cell(it['BOED_Cum'], 2)}</td>
                            <td class="ann-num-cell" style="color: #64748B;">{it['Share_Pct']:.1f}%</td>
                        </tr>
            """

        html_annual += f"""
                        <tr class="ann-tr-subtotal">
                            <td style="padding-left: 20px;">Total Offshore Gulf of Thailand</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Gas_Avg'], 1)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Cond_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Crude_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['BOED_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Gas_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Cond_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['Crude_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(offshore_sub['BOED_Cum'], 2)}</td>
                            <td class="ann-num-cell">{offshore_sub['Share_Pct']:.1f}%</td>
                        </tr>
                        <tr class="ann-tr-total">
                            <td style="text-align: center; font-family: 'Manrope', sans-serif;">Total Domestic Production</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Gas_Avg'], 1)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Cond_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Crude_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['BOED_Avg'], 0, True)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Gas_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Cond_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['Crude_Cum'], 2)}</td>
                            <td class="ann-num-cell">{fmt_cell(grand_tot['BOED_Cum'], 2)}</td>
                            <td class="ann-num-cell">100.0%</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="ann-footnote-box">
                <div>
                    <div><b>Note:</b> &nbsp; 1. Daily rates are weighted averages based on actual operating days in active reporting months ({total_active_days} days).</div>
                    <div style="margin-top: 2px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Cumulative volumes: Natural Gas in BCF, Hydrocarbon Liquids in MMbbl, Total Energy Equivalent in MMBOE.</div>
                    <div style="margin-top: 2px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Crude oil includes Sirikit, Offshore fields, and Defence Energy Department (DEDP Fang).</div>
                    <div style="margin-top: 2px;"><b>Source:</b> Department of Mineral Fuels (DMF), Defence Energy Department (DEDP)</div>
                </div>
                <div style="text-align: right;">
                    <div><b>Official Publication:</b> Petroleum Institute of Thailand (PTIT Focus Statistics)</div>
                    <div style="margin-top: 2px; color: #94A3B8;">National Hydrocarbon Telemetry Data Hub</div>
                </div>
            </div>
        </div>
        """

        clean_html_ann = re.sub(r'<!--.*?-->', '', html_annual, flags=re.DOTALL)
        clean_html_ann = "\n".join(line.strip() for line in clean_html_ann.splitlines() if line.strip())
        if hasattr(st, 'html'):
            st.html(clean_html_ann)
        else:
            st.markdown(clean_html_ann, unsafe_allow_html=True)

    # ----------------------------------------------------
    # SUBTAB 2: 12-MONTH MATRIX
    # ----------------------------------------------------
    with ann_subtab2:
        prod_opt = st.radio(
            "เลือกผลิตภัณฑ์สำหรับแสดงตารางเมทริกซ์ 12 เดือน (Select Hydrocarbon Stream):",
            [
                "⚡ รวมเทียบเท่าน้ำมันดิบ (Total BOED)",
                "⛽ ก๊าซธรรมชาติ (Natural Gas - MMSCFD)",
                "💧 ก๊าซธรรมชาติเหลว (Condensate - BPD)",
                "🛢️ น้ำมันดิบ (Crude Oil - BPD)"
            ],
            horizontal=True,
            key="annual_matrix_prod_opt"
        )

        matrix_meta = {
            "⚡ รวมเทียบเท่าน้ำมันดิบ (Total BOED)": {
                'col': 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                'slug': 'BOED', 'unit_d': 'BOED', 'unit_c': 'MMBOE', 'divisor': 1_000_000.0, 'dec': 0
            },
            "⛽ ก๊าซธรรมชาติ (Natural Gas - MMSCFD)": {
                'col': 'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)',
                'slug': 'Gas', 'unit_d': 'MMSCFD', 'unit_c': 'BCF', 'divisor': 1000.0, 'dec': 1
            },
            "💧 ก๊าซธรรมชาติเหลว (Condensate - BPD)": {
                'col': 'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
                'slug': 'Cond', 'unit_d': 'BPD', 'unit_c': 'MMbbl', 'divisor': 1_000_000.0, 'dec': 0
            },
            "🛢️ น้ำมันดิบ (Crude Oil - BPD)": {
                'col': 'น้ำมันดิบ (บาร์เรล/วัน)',
                'slug': 'Crude', 'unit_d': 'BPD', 'unit_c': 'MMbbl', 'divisor': 1_000_000.0, 'dec': 0
            }
        }
        meta = matrix_meta[prod_opt]

        MONTH_NAMES = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
        MONTH_SHORT = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']

        df_matrix_pivot = df_year_data.pivot_table(
            index=['PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'],
            columns='เดือน',
            values=meta['col'],
            aggfunc='sum'
        ).fillna(0.0).reset_index()

        # Handle Fang for Crude or BOED
        if meta['slug'] in ['Crude', 'BOED']:
            fang_piv_idx = df_matrix_pivot[df_matrix_pivot['PTIT_Operator_Field'] == 'Defence Energy Department / Fang'].index
            if len(fang_piv_idx) == 0:
                fang_dict = {'PTIT_Region': 'Onshore', 'PTIT_Operator_Field': 'Defence Energy Department / Fang', 'PTIT_Order': 13}
                for m in MONTH_NAMES:
                    fang_dict[m] = get_fang_value(sel_year, m) if m in active_months else 0.0
                df_matrix_pivot = pd.concat([df_matrix_pivot, pd.DataFrame([fang_dict])], ignore_index=True)
            else:
                for m in MONTH_NAMES:
                    df_matrix_pivot.loc[fang_piv_idx, m] = get_fang_value(sel_year, m) if m in active_months else 0.0

        df_matrix_pivot = df_matrix_pivot.sort_values(['PTIT_Region', 'PTIT_Order']).reset_index(drop=True)

        # Build clean export dataframe
        rows_matrix_export = []
        for _, r in df_matrix_pivot.iterrows():
            f_name = r['PTIT_Operator_Field']
            row_dict = {'Operator_Field': f_name, 'PTIT_Region': r['PTIT_Region']}
            r_sum_days = 0.0
            r_sum_vol = 0.0
            for full_m, short_m in zip(MONTH_NAMES, MONTH_SHORT):
                val = r.get(full_m, 0.0)
                row_dict[short_m] = val if val > 0 else 0.0
                if full_m in active_months and val > 0:
                    d = get_days_in_month(full_m, sel_year)
                    r_sum_days += d
                    r_sum_vol += val * d
            row_dict['เฉลี่ยทั้งปี'] = r_sum_vol / total_active_days if total_active_days > 0 else 0.0
            row_dict['สะสมทั้งปี'] = r_sum_vol / meta['divisor']
            rows_matrix_export.append(row_dict)

        df_matrix_export = pd.DataFrame(rows_matrix_export)

        # Download button for 12-Month Matrix
        m_dl1, m_dl2 = st.columns([2.5, 1.5])
        with m_dl1:
            st.caption(f"📊 ตารางแสดงอัตราการผลิตรายเดือน ม.ค. – ธ.ค. พร้อมค่าเฉลี่ยถ่วงน้ำหนักและผลผลิตสะสมทั้งปี หน่วย: {meta['unit_d']} / {meta['unit_c']}")
        with m_dl2:
            excel_matrix_buf = export_12month_matrix_excel(
                sel_year, df_matrix_export,
                meta['slug'], f"{meta['unit_d']} / {meta['unit_c']}", report_theme_key
            )
            st.download_button(
                label=f"📥 ดาวน์โหลด Excel เมทริกซ์ ({meta['slug']} {sel_year})",
                data=excel_matrix_buf.getvalue(),
                file_name=f"PTIT_12Month_Matrix_{sel_year}_{meta['slug']}_{report_theme_key}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=f"btn_dl_matrix_{sel_year}_{meta['slug']}"
            )

        # Display Dataframe
        display_df = df_matrix_export.drop(columns=['PTIT_Region']).copy()
        format_dict = {m: "{:,.1f}" if meta['dec'] == 1 else "{:,.0f}" for m in MONTH_SHORT}
        format_dict['เฉลี่ยทั้งปี'] = "{:,.1f}" if meta['dec'] == 1 else "{:,.0f}"
        format_dict['สะสมทั้งปี'] = "{:,.2f}"

        st.dataframe(
            display_df.style.format(format_dict, na_rep="-"),
            use_container_width=True,
            height=420
        )

        # Plotly Monthly Trend for Top 5 Fields
        st.markdown("##### 📈 แนวโน้มการผลิตรายเดือนของแหล่งหลัก (Monthly Trend - Top 5 Fields)")
        top_fields = df_matrix_export.nlargest(5, 'เฉลี่ยทั้งปี')['Operator_Field'].tolist()
        chart_records = []
        for _, r in df_matrix_export[df_matrix_export['Operator_Field'].isin(top_fields)].iterrows():
            for short_m in MONTH_SHORT:
                chart_records.append({
                    'Field': r['Operator_Field'],
                    'Month': short_m,
                    'Value': r[short_m]
                })
        df_chart_m = pd.DataFrame(chart_records)
        fig_trend = px.line(
            df_chart_m, x='Month', y='Value', color='Field',
            markers=True,
            title=f"แนวโน้มการผลิตรายเดือน Top 5 Fields ({meta['unit_d']}) - ปี {sel_year}",
            color_discrete_sequence=['#0284C7', '#C5A059', '#10B981', '#7C3AED', '#EF4444']
        )
        fig_trend.update_layout(
            xaxis_title="เดือน", yaxis_title=meta['unit_d'],
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # ----------------------------------------------------
    # SUBTAB 3: DYNAMIC PIVOT TABLE BUILDER
    # ----------------------------------------------------
    with ann_subtab3:
        st.markdown("#### ⚡ ทางลัดแม่แบบ Pivot ด่วน (1-Click Bento Presets)")
        p_c1, p_c2, p_c3, p_c4 = st.columns(4)
        with p_c1:
            if st.button("🏢 รายผู้ดำเนินการ", use_container_width=True, help="จัดกลุ่มตาม Operator และประเภทสัญญา"):
                st.session_state['pv_row'] = ['ผู้ดำเนินการ']
                st.session_state['pv_col'] = 'ประเภทสัญญา'
                st.session_state['pv_metric'] = 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
                st.session_state['pv_agg'] = 'เฉลี่ยต่อวัน (Mean Daily Rate)'
                st.rerun()
        with p_c2:
            if st.button("📜 รายประเภทสัญญา", use_container_width=True, help="จัดกลุ่มตามสัมปทาน Concession / PSC"):
                st.session_state['pv_row'] = ['ประเภทสัญญา']
                st.session_state['pv_col'] = 'พื้นที่'
                st.session_state['pv_metric'] = 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
                st.session_state['pv_agg'] = 'เฉลี่ยต่อวัน (Mean Daily Rate)'
                st.rerun()
        with p_c3:
            if st.button("🗺️ รายแอ่งปิโตรเลียม", use_container_width=True, help="จัดกลุ่มตามแอ่งปิโตรเลียม เช่น Pattani, Phitsanulok"):
                st.session_state['pv_row'] = ['แอ่งปิโตรเลียม']
                st.session_state['pv_col'] = 'พื้นที่'
                st.session_state['pv_metric'] = 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
                st.session_state['pv_agg'] = 'เฉลี่ยต่อวัน (Mean Daily Rate)'
                st.rerun()
        with p_c4:
            if st.button("📅 รายเดือน x มิติ", use_container_width=True, help="สรุปรายเดือนเทียบกับประเภทสัญญา"):
                st.session_state['pv_row'] = ['เดือน']
                st.session_state['pv_col'] = 'ประเภทสัญญา'
                st.session_state['pv_metric'] = 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'
                st.session_state['pv_agg'] = 'เฉลี่ยต่อวัน (Mean Daily Rate)'
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🎛️ ปรับแต่งมิติและตัวชี้วัด (Custom Pivot Dimension Selectors)")

        bento_dim1, bento_dim2, bento_dim3, bento_dim4 = st.columns(4)
        dim_options = [c for c in ['ผู้ดำเนินการ', 'ประเภทสัญญา', 'แอ่งปิโตรเลียม', 'พื้นที่', 'เดือน', 'แปลง_ไฟล์ดิบ', 'แหล่ง_ไฟล์ดิบ'] if c in df_year_data.columns]
        
        default_rows = st.session_state.get('pv_row', ['ผู้ดำเนินการ'])
        default_rows = [r for r in default_rows if r in dim_options] or ['ผู้ดำเนินการ']
        default_col = st.session_state.get('pv_col', 'ประเภทสัญญา')
        default_metric = st.session_state.get('pv_metric', 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)')
        default_agg = st.session_state.get('pv_agg', 'เฉลี่ยต่อวัน (Mean Daily Rate)')

        with bento_dim1:
            sel_rows = st.multiselect("แถว (Rows):", dim_options, default=default_rows, key="pivot_sel_rows")
            if not sel_rows:
                sel_rows = ['ผู้ดำเนินการ']
        with bento_dim2:
            col_opts = ['(ไม่มี - มิติเดียว)'] + [c for c in dim_options if c not in sel_rows]
            sel_col_idx = col_opts.index(default_col) if default_col in col_opts else 0
            sel_col = st.selectbox("คอลัมน์ (Columns):", col_opts, index=sel_col_idx, key="pivot_sel_cols")
        with bento_dim3:
            metric_candidates = [
                'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)',
                'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)',
                'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)',
                'น้ำมันดิบ (บาร์เรล/วัน)'
            ]
            metric_opts = [c for c in metric_candidates if c in df_year_data.columns]
            sel_metric_idx = metric_opts.index(default_metric) if default_metric in metric_opts else 0
            sel_metric = st.selectbox("ตัวชี้วัด (Metric):", metric_opts, index=sel_metric_idx, key="pivot_sel_metric")
        with bento_dim4:
            agg_opts = [
                'เฉลี่ยต่อวัน (Mean Daily Rate)',
                'ผลรวมสะสม (Sum Total)',
                'สัดส่วนร้อยละ (% Share of Total)'
            ]
            sel_agg_idx = agg_opts.index(default_agg) if default_agg in agg_opts else 0
            sel_agg = st.selectbox("การคำนวณ (Aggregation):", agg_opts, index=sel_agg_idx, key="pivot_sel_agg")

        # Perform Pivot Table calculation
        col_param = None if sel_col == '(ไม่มี - มิติเดียว)' else sel_col
        aggfunc_to_use = 'mean' if 'เฉลี่ย' in sel_agg else 'sum'

        try:
            df_pv = pd.pivot_table(
                df_year_data,
                index=sel_rows,
                columns=col_param,
                values=sel_metric,
                aggfunc=aggfunc_to_use,
                margins=True,
                margins_name='รวมทั้งหมด (Total)'
            ).fillna(0.0)

            # Reorder columns chronologically if column is 'เดือน'
            if col_param == 'เดือน':
                cols = [c for c in df_pv.columns if c != 'รวมทั้งหมด (Total)']
                sorted_cols = sorted(cols, key=lambda m: MONTH_ORDER.get(str(m).strip(), 99))
                if 'รวมทั้งหมด (Total)' in df_pv.columns:
                    sorted_cols.append('รวมทั้งหมด (Total)')
                df_pv = df_pv.reindex(columns=sorted_cols)

            # Reorder rows chronologically if 'เดือน' is in sel_rows
            if 'เดือน' in sel_rows:
                if len(sel_rows) == 1:
                    idx_rows = [i for i in df_pv.index if i != 'รวมทั้งหมด (Total)']
                    sorted_idx = sorted(idx_rows, key=lambda m: MONTH_ORDER.get(str(m).strip(), 99))
                    if 'รวมทั้งหมด (Total)' in df_pv.index:
                        sorted_idx.append('รวมทั้งหมด (Total)')
                    df_pv = df_pv.reindex(index=sorted_idx)
                else:
                    m_pos = sel_rows.index('เดือน')
                    idx_rows = [i for i in df_pv.index if i != 'รวมทั้งหมด (Total)' and i != ('รวมทั้งหมด (Total)',) * len(sel_rows)]
                    sorted_idx = sorted(idx_rows, key=lambda tup: (
                        tup[:m_pos] if isinstance(tup, tuple) else (),
                        MONTH_ORDER.get(str(tup[m_pos] if isinstance(tup, tuple) else tup).strip(), 99),
                        tup[m_pos+1:] if isinstance(tup, tuple) else ()
                    ))
                    margin_rows = [i for i in df_pv.index if i not in idx_rows]
                    df_pv = df_pv.reindex(index=sorted_idx + margin_rows)

            if 'สัดส่วน' in sel_agg:
                total_val = df_pv.iloc[-1, -1] if col_param else df_pv.iloc[-1]
                if total_val > 0:
                    df_pv = (df_pv / total_val) * 100.0

            # Download Row
            p_dl1, p_dl2 = st.columns([2.5, 1.5])
            with p_dl1:
                st.caption(f"📋 สรุปตาราง Pivot ตามมิติ: {' + '.join(sel_rows)} | คอลัมน์: {sel_col} | คำนวณ: {sel_agg}")
            with p_dl2:
                pivot_excel_buf = export_custom_pivot_excel(df_pv, title=f"PTIT_Pivot_{sel_year}")
                st.download_button(
                    label="📥 ดาวน์โหลด Pivot Table (Excel)",
                    data=pivot_excel_buf.getvalue(),
                    file_name=f"PTIT_Custom_Pivot_{sel_year}_{sel_metric}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"btn_dl_pivot_custom_{sel_year}"
                )

            # Display formatted dataframe
            if 'สัดส่วน' in sel_agg:
                st.dataframe(df_pv.map(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) and x > 0 else "-"), use_container_width=True)
            else:
                st.dataframe(df_pv.map(lambda x: f"{x:,.1f}" if isinstance(x, (int, float)) and x > 0 else "-"), use_container_width=True)

            # Dynamic Visualization
            st.markdown("##### 📊 แผนภูมิแสดงผลตามมิติที่เลือก (Interactive Visualization)")
            # Exclude Total margin row for chart
            df_plot_source = df_pv.drop(index='รวมทั้งหมด (Total)', errors='ignore')
            if col_param and 'รวมทั้งหมด (Total)' in df_plot_source.columns:
                df_plot_source = df_plot_source.drop(columns='รวมทั้งหมด (Total)')

            df_reset = df_plot_source.reset_index()
            # Category orders dict to ensure Plotly honors chronological order
            cat_orders = {}
            if col_param == 'เดือน':
                cat_orders['เดือน'] = [c for c in df_pv.columns if c != 'รวมทั้งหมด (Total)']
            if 'เดือน' in sel_rows:
                if len(sel_rows) == 1:
                    cat_orders['เดือน'] = [i for i in df_pv.index if i != 'รวมทั้งหมด (Total)']

            if col_param:
                df_melt = pd.melt(df_reset, id_vars=sel_rows, value_name=sel_metric, var_name=col_param)
                fig_pv = px.bar(
                    df_melt, x=sel_rows[0], y=sel_metric, color=col_param,
                    barmode='group',
                    title=f"{sel_metric} ({sel_agg}) ตาม {sel_rows[0]} และ {col_param}",
                    color_discrete_sequence=['#0284C7', '#C5A059', '#10B981', '#7C3AED', '#EF4444', '#F59E0B'],
                    category_orders=cat_orders
                )
            else:
                fig_pv = px.bar(
                    df_reset, x=sel_rows[0], y=sel_metric,
                    title=f"{sel_metric} ({sel_agg}) ตาม {sel_rows[0]}",
                    color_discrete_sequence=['#0284C7'],
                    category_orders=cat_orders
                )

            fig_pv.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_pv, use_container_width=True)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผล Pivot Table: {e}")


def render_ptit_monthly_report(df_all_data, is_admin=False):
    """ฟังก์ชันแสดงผลรายงานประจำเดือนสไตล์ Executive Letterhead ทางการ"""
    # Month Selector
    if 'ลำดับเดือน' not in df_all_data.columns:
        df_all_data['ลำดับเดือน'] = df_all_data['เดือน'].map(MONTH_ORDER).fillna(99)

    avail_months = df_all_data[['ปี', 'เดือน', 'ลำดับเดือน']].drop_duplicates().sort_values('ลำดับเดือน')
    month_options = [f"{r['เดือน']} ปี {r['ปี']}" for _, r in avail_months.iterrows()]

    # Month, Fang Input, Luxury Theme, and Filter Selector
    sel_col1, sel_col2, sel_col3, sel_col4 = st.columns([1.4, 1.8, 1.6, 1.1])
    with sel_col1:
        selected_month_label = st.selectbox("📅 เลือกเดือนรายงาน:", month_options, index=len(month_options)-1)

    # Parse selected month and year
    sel_month = selected_month_label.split()[0]
    sel_year = selected_month_label.split()[-1]

    # Ensure PTIT columns exist (Self-healing from Master)
    if 'PTIT_Region' not in df_all_data.columns:
        if 'Lookup_Key' not in df_all_data.columns and 'แปลง_ไฟล์ดิบ' in df_all_data.columns:
            df_all_data['Lookup_Key'] = df_all_data['พื้นที่'].astype(str) + '_' + df_all_data['แปลง_ไฟล์ดิบ'].astype(str) + '_' + df_all_data['แหล่ง_ไฟล์ดิบ'].astype(str)
        df_m = load_master_mapping()
        cols_to_add = [c for c in ['Lookup_Key', 'PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'] if c in df_m.columns]
        if 'Lookup_Key' in df_all_data.columns:
            df_all_data = pd.merge(df_all_data, df_m[cols_to_add], on='Lookup_Key', how='left')
            st.session_state['df_flat_wide'] = df_all_data

    # Filter data for chosen month
    df_month_data = df_all_data[(df_all_data['เดือน'] == sel_month) & (df_all_data['ปี'].astype(str) == sel_year)].copy()

    # DEDP Fang Value Retrieval & Role-based UI
    saved_fang_val = get_fang_value(sel_year, sel_month)

    with sel_col2:
        if is_admin:
            cf_in, cf_save = st.columns([2.2, 1.2])
            with cf_in:
                fang_val = st.number_input(
                    f"🛢️ ค่าน้ำมันดิบ แหล่งฝาง ({sel_month}) [BPD]:",
                    min_value=0.0,
                    value=float(saved_fang_val),
                    step=10.0,
                    key=f"input_fang_{sel_month}_{sel_year}",
                    help="ข้อมูลแหล่งฝางสังกัดกรมการพลังงานทหาร (DEDP) ผู้ดูแลระบบสามารถกรอกและกดบันทึกได้ทันที"
                )
            with cf_save:
                st.write("")
                st.write("")
                if st.button("💾 บันทึก", key=f"btn_save_fang_single_{sel_month}_{sel_year}", help="บันทึกค่าน้ำมันดิบแหล่งฝางสำหรับเดือนนี้"):
                    set_fang_value(sel_year, sel_month, fang_val)
                    if 'df_flat_wide' in st.session_state:
                        st.session_state['df_flat_wide'] = inject_fang_to_dataframe(st.session_state['df_flat_wide'])
                    st.toast(f"✅ บันทึกค่าน้ำมันดิบแหล่งฝาง ({sel_month} {sel_year}): {fang_val:,.1f} BPD เรียบร้อยแล้ว")
                    st.rerun()
        else:
            fang_val = saved_fang_val
            if fang_val > 0:
                st.markdown(f"""
                <div style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(186, 230, 253, 0.9); border-radius: 10px; padding: 7px 12px; margin-top: 14px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-size: 11px; font-weight: 700; color: #0284C7; text-transform: uppercase;">🛢️ แหล่งฝาง (DEDP):</span>
                        <span style="font-size: 15px; font-weight: 700; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin-left: 6px;">{fang_val:,.1f} BPD</span>
                    </div>
                    <span style="background: #0284C7; color: white; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">DEDP VERIFIED</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(148, 163, 184, 0.08); border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 10px; padding: 7px 12px; margin-top: 14px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-size: 11px; font-weight: 600; color: #64748B;">🛢️ แหล่งฝาง (DEDP):</span>
                        <span style="font-size: 13px; font-weight: 600; color: #94A3B8; margin-left: 6px;">0.0 BPD (ไม่มีการผลิต)</span>
                    </div>
                    <span style="background: #94A3B8; color: white; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">DEDP DATA</span>
                </div>
                """, unsafe_allow_html=True)

    with sel_col3:
        selected_theme_label = st.selectbox(
            "🎨 สไตล์เทมเพลต (Luxury Theme):",
            [
                "👑 Imperial Bronze & Champagne Gold (Signature Luxury)",
                "💎 Royal Navy & Platinum (Sovereign Executive)",
                "🏛️ Obsidian Platinum & Emerald (Energy Terminal)"
            ],
            index=0
        )
        if "Royal Navy" in selected_theme_label:
            report_theme_key = "navy"
        elif "Emerald" in selected_theme_label:
            report_theme_key = "emerald"
        else:
            report_theme_key = "imperial"

    with sel_col4:
        st.write("")
        st.write("")
        show_zero_fields = st.checkbox("แสดงแหล่งยอด 0", value=False, help="หากติ๊กเลือก จะแสดงแหล่งที่ไม่มีการผลิตในเดือนนั้น เช่น PTTEPI / G8/50")

    # Group and Aggregate by PTIT Operator / Field
    # Group keys: PTIT_Region, PTIT_Operator_Field, PTIT_Order
    df_agg = df_month_data.groupby(['PTIT_Region', 'PTIT_Operator_Field', 'PTIT_Order'], as_index=False).agg({
        'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': 'sum',
        'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': 'sum',
        'น้ำมันดิบ (บาร์เรล/วัน)': 'sum'
    }).rename(columns={
        'ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)': 'Gas',
        'ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)': 'Cond',
        'น้ำมันดิบ (บาร์เรล/วัน)': 'Crude',
        'PTIT_Region': 'Region',
        'PTIT_Operator_Field': 'Operator_Field',
        'PTIT_Order': 'Order'
    })

    # Append or update Fang in df_agg
    has_fang_row = ('Operator_Field' in df_agg.columns and (df_agg['Operator_Field'] == 'Defence Energy Department / Fang').any())
    if fang_val > 0:
        if not has_fang_row:
            df_fang_row = pd.DataFrame([{
                'Region': 'Onshore',
                'Operator_Field': 'Defence Energy Department / Fang',
                'Order': 13,
                'Gas': 0.0,
                'Cond': 0.0,
                'Crude': float(fang_val)
            }])
            df_agg = pd.concat([df_agg, df_fang_row], ignore_index=True)
        else:
            df_agg.loc[df_agg['Operator_Field'] == 'Defence Energy Department / Fang', 'Crude'] = float(fang_val)
    else:
        if has_fang_row:
            df_agg.loc[df_agg['Operator_Field'] == 'Defence Energy Department / Fang', 'Crude'] = 0.0
        elif show_zero_fields:
            df_fang_row = pd.DataFrame([{
                'Region': 'Onshore',
                'Operator_Field': 'Defence Energy Department / Fang',
                'Order': 13,
                'Gas': 0.0,
                'Cond': 0.0,
                'Crude': 0.0
            }])
            df_agg = pd.concat([df_agg, df_fang_row], ignore_index=True)

    if not show_zero_fields:
        df_agg = df_agg[(df_agg['Gas'] >= 0.001) | (df_agg['Cond'] >= 0.001) | (df_agg['Crude'] >= 0.001)].reset_index(drop=True)

    df_agg = df_agg.sort_values('Order').reset_index(drop=True)

    # Calculate Subtotals
    onshore_items = df_agg[df_agg['Region'] == 'Onshore'].to_dict('records')
    offshore_items = df_agg[df_agg['Region'] == 'Offshore'].to_dict('records')

    onshore_sub = (
        sum(x['Gas'] for x in onshore_items),
        sum(x['Cond'] for x in onshore_items),
        sum(x['Crude'] for x in onshore_items)
    )
    offshore_sub = (
        sum(x['Gas'] for x in offshore_items),
        sum(x['Cond'] for x in offshore_items),
        sum(x['Crude'] for x in offshore_items)
    )
    grand_total = (
        onshore_sub[0] + offshore_sub[0],
        onshore_sub[1] + offshore_sub[1],
        onshore_sub[2] + offshore_sub[2]
    )

    total_gas = grand_total[0]
    total_cond = grand_total[1]
    total_crude = grand_total[2]
    
    # Calculate official BOED from DMF data if present, otherwise standard conversion
    if 'รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)' in df_month_data.columns:
        total_boed = float(df_month_data['รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)'].sum()) + float(fang_val if fang_val > 0 else 0)
    else:
        total_boed = (total_gas * 1000 / 5.615) + total_cond + total_crude

    # ----------------------------------------------------
    # Executive Bento Metric Ribbon (Key Production Highlights)
    # ----------------------------------------------------
    bento_themes = {
        'imperial': {
            'card_bg': '#FFFFFF',
            'border': 'rgba(197, 160, 89, 0.45)',
            'halo_border': '1.5px solid #C5A059',
            'halo_shadow': '0 8px 24px rgba(197, 160, 89, 0.22)',
            'tag_bg': 'rgba(197, 160, 89, 0.15)',
            'tag_fg': '#8A6239',
            'accent_num': '#1C1917',
            'boed_bg': 'linear-gradient(135deg, #FFFDF9 0%, #FBF6EE 100%)'
        },
        'navy': {
            'card_bg': '#FFFFFF',
            'border': 'rgba(30, 58, 138, 0.35)',
            'halo_border': '1.5px solid #38BDF8',
            'halo_shadow': '0 8px 24px rgba(56, 189, 248, 0.22)',
            'tag_bg': 'rgba(56, 189, 248, 0.15)',
            'tag_fg': '#0284C7',
            'accent_num': '#0F172A',
            'boed_bg': 'linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)'
        },
        'emerald': {
            'card_bg': '#FFFFFF',
            'border': 'rgba(4, 120, 87, 0.35)',
            'halo_border': '1.5px solid #10B981',
            'halo_shadow': '0 8px 24px rgba(16, 185, 129, 0.22)',
            'tag_bg': 'rgba(16, 185, 129, 0.15)',
            'tag_fg': '#047857',
            'accent_num': '#064E3B',
            'boed_bg': 'linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%)'
        }
    }
    bt = bento_themes[report_theme_key]

    html_bento = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 15px 0 20px 0;">
        <div style="background: {bt['card_bg']}; border: 1px solid {bt['border']}; border-radius: 14px; padding: 14px 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #0284C7; letter-spacing: 0.05em; text-transform: uppercase;">🔵 ก๊าซธรรมชาติ (Gas)</span>
                <span style="background: rgba(2, 132, 199, 0.12); color: #0284C7; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">MMSCFD</span>
            </div>
            <div style="font-size: 24px; font-weight: 800; color: {bt['accent_num']}; font-family: 'JetBrains Mono', monospace; line-height: 1.2;">
                {total_gas:,.1f}
            </div>
            <div style="font-size: 11px; color: #64748B; margin-top: 5px;">
                Onshore: <b>{onshore_sub[0]:,.1f}</b> • Offshore: <b>{offshore_sub[0]:,.1f}</b>
            </div>
        </div>
        <div style="background: {bt['card_bg']}; border: 1px solid {bt['border']}; border-radius: 14px; padding: 14px 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #D97706; letter-spacing: 0.05em; text-transform: uppercase;">🟠 ก๊าซธรรมชาติเหลว (Cond)</span>
                <span style="background: rgba(217, 119, 6, 0.12); color: #D97706; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">BPD</span>
            </div>
            <div style="font-size: 24px; font-weight: 800; color: {bt['accent_num']}; font-family: 'JetBrains Mono', monospace; line-height: 1.2;">
                {total_cond:,.1f}
            </div>
            <div style="font-size: 11px; color: #64748B; margin-top: 5px;">
                อ่าวไทย (Offshore Gulf of Thailand 100%)
            </div>
        </div>
        <div style="background: {bt['card_bg']}; border: 1px solid {bt['border']}; border-radius: 14px; padding: 14px 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #475569; letter-spacing: 0.05em; text-transform: uppercase;">🛢️ น้ำมันดิบ (Crude Oil)</span>
                <span style="background: rgba(71, 85, 105, 0.12); color: #475569; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">BPD</span>
            </div>
            <div style="font-size: 24px; font-weight: 800; color: {bt['accent_num']}; font-family: 'JetBrains Mono', monospace; line-height: 1.2;">
                {total_crude:,.1f}
            </div>
            <div style="font-size: 11px; color: #64748B; margin-top: 5px;">
                Onshore: <b>{onshore_sub[2]:,.1f}</b> • Offshore: <b>{offshore_sub[2]:,.1f}</b>
            </div>
        </div>
        <div style="background: {bt['boed_bg']}; border: {bt['halo_border']}; border-radius: 14px; padding: 14px 18px; box-shadow: {bt['halo_shadow']};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 800; color: {bt['tag_fg']}; letter-spacing: 0.06em; text-transform: uppercase;">⚡ รวมเทียบเท่าน้ำมันดิบ</span>
                <span style="background: {bt['tag_bg']}; color: {bt['tag_fg']}; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 6px;">BOED</span>
            </div>
            <div style="font-size: 24px; font-weight: 900; color: {bt['accent_num']}; font-family: 'JetBrains Mono', monospace; line-height: 1.2;">
                {total_boed:,.1f}
            </div>
            <div style="font-size: 11px; color: #78716C; margin-top: 5px;">
                รวมเทียบเท่าตามค่าความร้อนจริง (DMF Standard)
            </div>
        </div>
    </div>
    """
    clean_bento = re.sub(r'<!--.*?-->', '', html_bento, flags=re.DOTALL)
    clean_bento = "\n".join(line.strip() for line in clean_bento.splitlines() if line.strip())
    if hasattr(st, 'html'):
        st.html(clean_bento)
    else:
        st.markdown(clean_bento, unsafe_allow_html=True)

    # ----------------------------------------------------
    # UI/UX Pro Max: Dual Export & Distribution Center
    # ----------------------------------------------------
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin: 18px 0 12px 0;">
        <span style="font-size: 16px;">📦</span>
        <span style="font-weight: 800; font-size: 14.5px; color: #0F172A;">ศูนย์ดาวน์โหลดข้อมูลและรายงาน (Export & Distribution Center)</span>
        <span style="background: rgba(2, 132, 199, 0.1); color: #0284C7; font-size: 10.5px; font-weight: 700; padding: 2px 9px; border-radius: 12px; margin-left: 4px;">
            DUAL FORMAT
        </span>
    </div>
    """, unsafe_allow_html=True)

    exp_c1, exp_c2 = st.columns(2, gap="medium")
    with exp_c1:
        st.markdown(f"""
        <div style="background: white; border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 14px; padding: 16px 18px 14px 18px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); min-height: 142px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px;">
                        📑 รายงานทางการ PTIT (Formatted Report)
                    </span>
                    <span style="background: rgba(2, 132, 199, 0.12); color: #0284C7; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">
                        EXECUTIVE READY
                    </span>
                </div>
                <div style="font-size: 12px; color: #64748B; line-height: 1.5; margin-bottom: 8px;">
                    จัดรูปแบบทางการสไตล์ PTIT Focus ประจำเดือน <b>{sel_month} {sel_year}</b> ในธีม <b>{selected_theme_label.split('(')[0].strip()}</b> พร้อมผลรวม Onshore / Offshore สำหรับเสนอผู้บริหารหรือพิมพ์รายงาน
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        excel_buf = export_ptit_styled_excel(
            sel_month, sel_year, onshore_items, offshore_items, onshore_sub, offshore_sub, grand_total, theme=report_theme_key
        )
        st.download_button(
            label=f"📥 ดาวน์โหลดตารางรายงาน PTIT ({sel_month} {sel_year})",
            data=excel_buf,
            file_name=f"PTIT_Domestic_Production_{sel_month}_{sel_year}_{report_theme_key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
            key="btn_dl_ptit_official_report"
        )

    with exp_c2:
        st.markdown(f"""
        <div style="background: white; border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 14px; padding: 16px 18px 14px 18px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03); min-height: 142px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 6px;">
                        📊 ฐานข้อมูลดิบรวมทั้งปี (Flat Table Database)
                    </span>
                    <span style="background: rgba(16, 185, 129, 0.12); color: #059669; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px;">
                        POWER BI & PIVOT
                    </span>
                </div>
                <div style="font-size: 12px; color: #64748B; line-height: 1.5; margin-bottom: 8px;">
                    ฐานข้อมูล Flat Matrix รวมทั้งปี <b>{len(avail_months)} เดือน</b> ({len(df_all_data):,} แถว) โครงสร้าง 2D สะอาด ไม่มีเซลล์ผสาน เหมาะสำหรับวิเคราะห์ต่อด้วย Power BI, Tableau หรือ Excel Pivot
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        buf_flat = io.BytesIO()
        with pd.ExcelWriter(buf_flat, engine='openpyxl') as wr_flat:
            df_all_data.to_excel(wr_flat, sheet_name='Flat_Wide', index=False)
            if 'df_flat_long' in st.session_state and not st.session_state['df_flat_long'].empty:
                st.session_state['df_flat_long'].to_excel(wr_flat, sheet_name='Flat_Long_Unpivoted', index=False)
        buf_flat.seek(0)
        st.download_button(
            label=f"📊 ดาวน์โหลดฐานข้อมูล Flat Table รวมทั้งปี (.xlsx)",
            data=buf_flat,
            file_name=f"petroleum_production_flat_table_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
            key="btn_dl_flat_table_tab4"
        )

    st.markdown("""
    <div style="margin: 10px 0 18px 0; padding: 9px 16px; background: rgba(248, 250, 252, 0.85); border: 1px dashed #CBD5E1; border-radius: 10px; font-size: 12px; color: #475569; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span>✨</span>
            <span><b>คำแนะนำการพิมพ์ / บันทึก PDF:</b> ตารางด้านล่างแสดงผลสไตล์ Executive Letterhead สามารถกด <kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Ctrl + P</kbd> บนคีย์บอร์ดเพื่อสั่งพิมพ์หรือบันทึกเป็น PDF ได้ทันที</span>
        </div>
        <span style="font-size: 11px; color: #94A3B8;">PTIT Focus Statistics Hub</span>
    </div>
    """, unsafe_allow_html=True)

    # Units Reference and Verification Expander
    with st.expander("📐 ตารางทบทวนและตรวจสอบหน่วยวัดปิโตรเลียม (Petroleum Units Audit Reference)", expanded=False):
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(203, 213, 225, 0.8); border-radius: 12px; padding: 14px; font-size: 13px; overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-family: 'Hanken Grotesk', sans-serif;">
                <thead>
                    <tr style="background: #F8FAFC; border-bottom: 2px solid #CBD5E1; color: #0F172A; font-size: 12.5px;">
                        <th style="padding: 8px 12px; text-align: left;">หมวดรายงาน</th>
                        <th style="padding: 8px 12px; text-align: left;">ผลิตภัณฑ์</th>
                        <th style="padding: 8px 12px; text-align: left;">หน่วยหลัก (Primary Unit)</th>
                        <th style="padding: 8px 12px; text-align: left;">หน่วยเทียบเท่า / หน่วยราคา</th>
                        <th style="padding: 8px 12px; text-align: left;">คำอธิบายและนิยามทางสถิติ</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 12px; font-weight: 700; color: #0284C7;" rowspan="3">🏭 การผลิตปิโตรเลียม<br><span style="font-size: 11px; font-weight: normal; color: #64748B;">(Production Report)</span></td>
                        <td style="padding: 8px 12px;"><b>ก๊าซธรรมชาติ</b> (Natural Gas)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(2, 132, 199, 0.12); color: #0284C7; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">MMSCFD</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-weight: 600;">BOED</td>
                        <td style="padding: 8px 12px; color: #475569;">ล้านลูกบาศก์ฟุตต่อวัน (วัดทางกายภาพ) เทียบเท่าบาร์เรล/วันตามค่าความร้อนเฉพาะของแต่ละแหล่ง</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 12px;"><b>ก๊าซธรรมชาติเหลว</b> (Condensate)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(217, 119, 6, 0.12); color: #D97706; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">BPD</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-weight: 600;">BOED</td>
                        <td style="padding: 8px 12px; color: #475569;">บาร์เรลต่อวัน (ไฮโดรคาร์บอนเหลวเบาที่แยกได้จากก๊าซธรรมชาติในอ่าวไทย)</td>
                    </tr>
                    <tr style="border-bottom: 2px solid #CBD5E1;">
                        <td style="padding: 8px 12px;"><b>น้ำมันดิบ</b> (Crude Oil)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(71, 85, 105, 0.12); color: #475569; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">BPD</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-weight: 600;">BOED</td>
                        <td style="padding: 8px 12px; color: #475569;">บาร์เรลต่อวัน (รวมแหล่งสิริกิติ์, อ่าวไทย, และแหล่งฝาง กรมการพลังงานทหาร DEDP)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 12px; font-weight: 700; color: #D97706;" rowspan="4">💰 การจำหน่ายปิโตรเลียม<br><span style="font-size: 11px; font-weight: normal; color: #64748B;">(Sales & Fiscal Report)</span></td>
                        <td style="padding: 8px 12px;"><b>ก๊าซธรรมชาติ</b> (2 รูปแบบ)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(16, 185, 129, 0.12); color: #047857; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">MMSCF</span> (ปริมาตร)<br><span style="background: rgba(16, 185, 129, 0.12); color: #047857; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-top: 3px; display: inline-block;">MMBTU</span> (ความร้อน)</td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace;"><b>บาท/MMBTU</b><br>(BTU/scf)</td>
                        <td style="padding: 8px 12px; color: #475569;">ปริมาตรใช้วัดทางวิศวกรรม ส่วนความร้อนใช้คิดเงินตามสัญญา GSA และคิดราคาปากหลุม</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 12px;"><b>คอนเดนเสท</b> (Condensate)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(217, 119, 6, 0.12); color: #D97706; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">บาร์เรล (BBL)</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace;"><b>บาท/บาร์เรล</b></td>
                        <td style="padding: 8px 12px; color: #475569;">ปริมาณจำหน่ายจริงรายเดือน และราคาเฉลี่ย ณ ปากหลุม (Wellhead Price)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 12px;"><b>น้ำมันดิบ</b> (Crude Oil)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(71, 85, 105, 0.12); color: #475569; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">บาร์เรล (BBL)</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace;"><b>บาท/บาร์เรล</b></td>
                        <td style="padding: 8px 12px; color: #475569;">ปริมาณจำหน่ายจริงรายเดือน และราคาเฉลี่ย ณ ปากหลุม (Wellhead Price)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px;"><b>ก๊าซปิโตรเลียมเหลว</b> (LPG)</td>
                        <td style="padding: 8px 12px;"><span style="background: rgba(147, 51, 234, 0.12); color: #7E22CE; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 2px 7px; border-radius: 4px;">กิโลกรัม (kg)</span></td>
                        <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace;"><b>บาท/กิโลกรัม</b></td>
                        <td style="padding: 8px 12px; color: #475569;">กิโลกรัมที่จำหน่ายจากแหล่งสิริกิติ์ และราคาเฉลี่ยต่อกิโลกรัม</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # HTML Table Generator
    def fmt(val, is_bpd=False):
        if val is None or val == 0:
            return "&nbsp;"
        if val < 0.05:
            return "0.0"
        if is_bpd:
            return f"{val:,.1f}"
        return f"{val:.1f}"

    # Theme Design Tokens for Table
    theme_table_tokens = {
        'imperial': {
            'card_bg': '#FFFFFF',
            'card_border': 'rgba(197, 160, 89, 0.45)',
            'card_shadow': '0 20px 48px -12px rgba(44, 30, 18, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
            'masthead_bg': 'linear-gradient(135deg, #1C1917 0%, #2A2118 60%, #38271A 100%)',
            'masthead_accent': '#C5A059',
            'masthead_org': '#D4AF37',
            'badge_bg': 'rgba(212, 175, 55, 0.18)',
            'badge_fg': '#E5C378',
            'badge_border': 'rgba(212, 175, 55, 0.4)',
            'th_main_bg': 'linear-gradient(135deg, #24180E 0%, #332216 100%)',
            'th_sub_bg': '#2E2218',
            'th_sub_color': '#FAF6F0',
            'unit_chip_bg': 'rgba(197, 160, 89, 0.22)',
            'unit_chip_color': '#F5D899',
            'unit_chip_border': 'rgba(197, 160, 89, 0.45)',
            'sec_bg': 'linear-gradient(90deg, #784E20 0%, #966734 50%, #7D5325 100%)',
            'sec_color': '#FFFFFF',
            'sec_badge_bg': 'rgba(0, 0, 0, 0.2)',
            'sec_badge_color': '#FFFFFF',
            'zebra_bg': '#FAF7F2',
            'hover_bg': '#F5EFE6',
            'hover_border': '#C5A059',
            'tot_bg': 'linear-gradient(90deg, #EFE5D5 0%, #E3D3BE 100%)',
            'tot_color': '#1C1917',
            'tot_border_top': '#784E20',
            'tot_border_bot': '#3D240E',
            'grid_border': '#E8E2D8'
        },
        'navy': {
            'card_bg': '#FFFFFF',
            'card_border': 'rgba(30, 58, 138, 0.35)',
            'card_shadow': '0 20px 48px -12px rgba(15, 23, 42, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
            'masthead_bg': 'linear-gradient(135deg, #0A1128 0%, #0F172A 60%, #1E293B 100%)',
            'masthead_accent': '#38BDF8',
            'masthead_org': '#93C5FD',
            'badge_bg': 'rgba(56, 189, 248, 0.18)',
            'badge_fg': '#38BDF8',
            'badge_border': 'rgba(56, 189, 248, 0.4)',
            'th_main_bg': 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
            'th_sub_bg': '#162038',
            'th_sub_color': '#F1F5F9',
            'unit_chip_bg': 'rgba(56, 189, 248, 0.18)',
            'unit_chip_color': '#38BDF8',
            'unit_chip_border': 'rgba(56, 189, 248, 0.4)',
            'sec_bg': 'linear-gradient(90deg, #1E3A8A 0%, #2563EB 50%, #1E40AF 100%)',
            'sec_color': '#FFFFFF',
            'sec_badge_bg': 'rgba(0, 0, 0, 0.25)',
            'sec_badge_color': '#FFFFFF',
            'zebra_bg': '#F8FAFC',
            'hover_bg': '#EFF6FF',
            'hover_border': '#38BDF8',
            'tot_bg': 'linear-gradient(90deg, #EFF6FF 0%, #DBEAFE 100%)',
            'tot_color': '#0F172A',
            'tot_border_top': '#1E3A8A',
            'tot_border_bot': '#0F172A',
            'grid_border': '#E2E8F0'
        },
        'emerald': {
            'card_bg': '#FFFFFF',
            'card_border': 'rgba(4, 120, 87, 0.35)',
            'card_shadow': '0 20px 48px -12px rgba(6, 78, 59, 0.14), 0 3px 10px rgba(0, 0, 0, 0.04)',
            'masthead_bg': 'linear-gradient(135deg, #091310 0%, #0F201B 60%, #162F27 100%)',
            'masthead_accent': '#10B981',
            'masthead_org': '#6EE7B7',
            'badge_bg': 'rgba(16, 185, 129, 0.18)',
            'badge_fg': '#34D399',
            'badge_border': 'rgba(16, 185, 129, 0.4)',
            'th_main_bg': 'linear-gradient(135deg, #0F281E 0%, #132620 100%)',
            'th_sub_bg': '#132620',
            'th_sub_color': '#ECFDF5',
            'unit_chip_bg': 'rgba(16, 185, 129, 0.18)',
            'unit_chip_color': '#34D399',
            'unit_chip_border': 'rgba(16, 185, 129, 0.4)',
            'sec_bg': 'linear-gradient(90deg, #065F46 0%, #047857 50%, #064E3B 100%)',
            'sec_color': '#FFFFFF',
            'sec_badge_bg': 'rgba(0, 0, 0, 0.25)',
            'sec_badge_color': '#FFFFFF',
            'zebra_bg': '#F0FDF4',
            'hover_bg': '#ECFDF5',
            'hover_border': '#10B981',
            'tot_bg': 'linear-gradient(90deg, #ECFDF5 0%, #D1FAE5 100%)',
            'tot_color': '#064E3B',
            'tot_border_top': '#065F46',
            'tot_border_bot': '#064E3B',
            'grid_border': '#D1FAE5'
        }
    }
    tk = theme_table_tokens[report_theme_key]

    html_table = f"""
    <style>
        .ptit-luxury-wrapper {{
            background: {tk['card_bg']};
            border: 1px solid {tk['card_border']};
            box-shadow: {tk['card_shadow']};
            border-radius: 18px;
            overflow: hidden;
            margin-top: 20px;
            font-family: 'Hanken Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .ptit-masthead {{
            background: {tk['masthead_bg']};
            border-top: 4px solid {tk['masthead_accent']};
            padding: 22px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }}
        .ptit-masthead-org {{
            font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
            font-size: 12px;
            font-weight: 700;
            color: {tk['masthead_org']};
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .ptit-masthead-title {{
            font-family: 'Manrope', 'Hanken Grotesk', sans-serif;
            font-size: 21px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.015em;
            line-height: 1.25;
        }}
        .ptit-masthead-sub {{
            font-size: 13px;
            color: #E2E8F0;
            margin-top: 3px;
            opacity: 0.92;
        }}
        .ptit-masthead-badges {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
        }}
        .ptit-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            display: inline-block;
        }}
        .ptit-badge-gold {{
            background: {tk['badge_bg']};
            color: {tk['badge_fg']};
            border: 1px solid {tk['badge_border']};
        }}
        .ptit-table-responsive {{
            overflow-x: auto;
            width: 100%;
        }}
        .ptit-luxury-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            color: #1E293B;
        }}
        .ptit-luxury-table th, .ptit-luxury-table td {{
            border: 1px solid {tk['grid_border']};
            padding: 7px 14px;
            line-height: 1.4;
        }}
        .th-main {{
            background: {tk['th_main_bg']};
            color: #FFFFFF;
            text-align: center;
            font-weight: 700;
            font-size: 13.5px;
            letter-spacing: 0.02em;
            padding: 10px 14px !important;
        }}
        .th-col {{
            background: {tk['th_sub_bg']};
            color: {tk['th_sub_color']};
            text-align: center;
            font-weight: 700;
            font-size: 13px;
            padding: 9px 12px !important;
        }}
        .unit-pill {{
            display: inline-block;
            background: {tk['unit_chip_bg']};
            color: {tk['unit_chip_color']};
            border: 1px solid {tk['unit_chip_border']};
            font-size: 10.5px;
            font-weight: 700;
            padding: 1px 7px;
            border-radius: 5px;
            margin-top: 3px;
        }}
        .tr-section {{
            background: {tk['sec_bg']};
            color: {tk['sec_color']};
            font-weight: 700;
            font-size: 13.5px;
        }}
        .tr-section td {{
            border-color: rgba(0, 0, 0, 0.15) !important;
            padding: 8px 14px !important;
        }}
        .sec-badge {{
            display: inline-block;
            background: {tk['sec_badge_bg']};
            color: {tk['sec_badge_color']};
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.03em;
        }}
        .tr-item-even {{
            background: {tk['zebra_bg']};
            transition: background-color 150ms ease, border-left 150ms ease;
        }}
        .tr-item-odd {{
            background: #FFFFFF;
            transition: background-color 150ms ease, border-left 150ms ease;
        }}
        .tr-item-even:hover, .tr-item-odd:hover {{
            background: {tk['hover_bg']} !important;
        }}
        .tr-item-even:hover td:first-child, .tr-item-odd:hover td:first-child {{
            border-left: 3px solid {tk['hover_border']} !important;
            padding-left: 25px !important;
        }}
        .tr-total {{
            background: {tk['tot_bg']};
            color: {tk['tot_color']};
            font-weight: 800;
            border-top: 2px solid {tk['tot_border_top']} !important;
            border-bottom: 3px double {tk['tot_border_bot']} !important;
            font-size: 14px;
        }}
        .tr-total td {{
            padding: 11px 14px !important;
            border-top: 2px solid {tk['tot_border_top']} !important;
            border-bottom: 3px double {tk['tot_border_bot']} !important;
        }}
        .num-cell {{
            text-align: right;
            font-family: 'JetBrains Mono', 'SF Mono', monospace;
            font-size: 13px;
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.01em;
        }}
        .tot-num {{
            font-size: 14.5px !important;
            font-weight: 800 !important;
        }}
        .ptit-footnote-box {{
            background: #FAFAF9;
            border-top: 1px solid {tk['grid_border']};
            padding: 14px 24px;
            font-size: 11.5px;
            color: #64748B;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }}
        @media print {{
            body * {{
                visibility: hidden !important;
            }}
            .ptit-luxury-wrapper, .ptit-luxury-wrapper * {{
                visibility: visible !important;
            }}
            .ptit-luxury-wrapper {{
                position: absolute !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
                border: 1px solid #777 !important;
                box-shadow: none !important;
            }}
        }}
    </style>

    <div class="ptit-luxury-wrapper">
        <div class="ptit-masthead">
            <div>
                <div class="ptit-masthead-org">PETROLEUM INSTITUTE OF THAILAND</div>
                <div class="ptit-masthead-title">DOMESTIC PETROLEUM PRODUCTION REPORT</div>
                <div class="ptit-masthead-sub">รายงานสถิติปริมาณการผลิตปิโตรเลียมในประเทศ ประจำเดือน {sel_month} {sel_year}</div>
            </div>
            <div class="ptit-masthead-badges">
                <span class="ptit-badge ptit-badge-gold">🔒 OFFICIAL AUDITED RECORD</span>
                <span class="ptit-badge ptit-badge-gold">📅 PTIT FOCUS RELEASE</span>
            </div>
        </div>

        <div class="ptit-table-responsive">
            <table class="ptit-luxury-table">
                <thead>
                    <tr>
                        <th rowspan="2" class="th-main" style="width: 46%; text-align: left; padding-left: 20px !important;">
                            Operator / Field <span style="font-size: 12px; font-weight: normal; opacity: 0.85;">({sel_month} {sel_year})</span>
                        </th>
                        <th colspan="3" class="th-main">
                            Domestic Production
                        </th>
                    </tr>
                    <tr>
                        <th class="th-col" style="width: 18%;">
                            Natural Gas<br><span class="unit-pill">MMSCFD</span>
                        </th>
                        <th class="th-col" style="width: 18%;">
                            Condensate<br><span class="unit-pill">BPD</span>
                        </th>
                        <th class="th-col" style="width: 18%;">
                            Crude<br><span class="unit-pill">BPD</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="tr-section">
                        <td style="padding-left: 18px !important;">
                            <span class="sec-badge">🏞️ ONSHORE BASIN</span>
                        </td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(onshore_sub[0])}</td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(onshore_sub[1], True)}</td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(onshore_sub[2], True)}</td>
                    </tr>
    """

    for idx, it in enumerate(onshore_items):
        row_cls = "tr-item-even" if (idx % 2 == 1) else "tr-item-odd"
        html_table += f"""
                    <tr class="{row_cls}">
                        <td style="padding-left: 28px;">{it['Operator_Field']}</td>
                        <td class="num-cell">{fmt(it['Gas'])}</td>
                        <td class="num-cell">{fmt(it['Cond'], True)}</td>
                        <td class="num-cell">{fmt(it['Crude'], True)}</td>
                    </tr>
        """

    html_table += f"""
                    <tr class="tr-section">
                        <td style="padding-left: 18px !important;">
                            <span class="sec-badge">🌊 OFFSHORE GULF OF THAILAND</span>
                        </td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(offshore_sub[0])}</td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(offshore_sub[1], True)}</td>
                        <td class="num-cell" style="font-weight: 700;">{fmt(offshore_sub[2], True)}</td>
                    </tr>
    """

    for idx, it in enumerate(offshore_items):
        row_cls = "tr-item-even" if (idx % 2 == 1) else "tr-item-odd"
        html_table += f"""
                    <tr class="{row_cls}">
                        <td style="padding-left: 28px;">{it['Operator_Field']}</td>
                        <td class="num-cell">{fmt(it['Gas'])}</td>
                        <td class="num-cell">{fmt(it['Cond'], True)}</td>
                        <td class="num-cell">{fmt(it['Crude'], True)}</td>
                    </tr>
        """

    html_table += f"""
                    <tr class="tr-total">
                        <td style="text-align: center; font-family: 'Manrope', sans-serif;">Total Domestic Production</td>
                        <td class="num-cell tot-num">{fmt(grand_total[0])}</td>
                        <td class="num-cell tot-num">{fmt(grand_total[1], True)}</td>
                        <td class="num-cell tot-num">{fmt(grand_total[2], True)}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="ptit-footnote-box">
            <div>
                <div><b>Note:</b> &nbsp; Data shown as "0.0" indicates production figure less than 0.05.</div>
                <div style="margin-top: 3px;"><b>Source:</b> Department of Mineral Fuels (DMF), &nbsp;Defence Energy Department (DEDP)</div>
            </div>
            <div style="text-align: right;">
                <div><b>Official Publication:</b> Petroleum Institute of Thailand (PTIT Focus Statistics)</div>
                <div style="margin-top: 3px; color: #94A3B8;">Verified National Hydrocarbon Production Telemetry</div>
            </div>
        </div>
    </div>
    """

    clean_html = re.sub(r'<!--.*?-->', '', html_table, flags=re.DOTALL)
    clean_html = "\n".join(line.strip() for line in clean_html.splitlines() if line.strip())
    if hasattr(st, 'html'):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)



# ====================================================
# TAB 4: PTIT DOMESTIC PRODUCTION REPORT
# ====================================================
with tab_ptit_report:
    st.subheader("📑 รายงานปริมาณการผลิตปิโตรเลียมในประเทศ (PTIT Domestic Production Report)")
    st.caption("ตารางรายงานสรุปรายเดือนและรายงานประจำปีตามมาตรฐานของ สถาบันปิโตรเลียมแห่งประเทศไทย (PTIT Focus Statistics)")

    if 'df_flat_wide' in st.session_state:
        df_all_data = st.session_state['df_flat_wide']

        report_period_mode = st.radio(
            "เลือกระดับรายงานการผลิต (Reporting Period & Analytical Mode):",
            ["📅 รายงานประจำเดือน (Monthly Report)", "👑 รายงานประจำปี & Pivot Builder (Annual Report & Custom Matrix)"],
            horizontal=True,
            key="ptit_report_period_mode"
        )

        if report_period_mode == "👑 รายงานประจำปี & Pivot Builder (Annual Report & Custom Matrix)":
            render_ptit_annual_report(df_all_data, is_admin)
        else:
            render_ptit_monthly_report(df_all_data, is_admin)
    else:
        if st.session_state.get('user_role', 'viewer') == 'admin':
            st.info("💡 ยังไม่มีข้อมูลการผลิตในระบบ สามารถกดปุ่ม '⚡ 1-Click Auto Sync การผลิต' ในแถบเมนูด้านซ้ายเพื่อดึงข้อมูลสดจาก DMF ได้ทันทีครับ")
        else:
            st.info("💡 ขณะนี้ยังไม่มีข้อมูลการผลิตในระบบ กรุณาติดต่อผู้ดูแลระบบ (Admin) เพื่อรัน Auto Sync ข้อมูลล่าสุดครับ")
