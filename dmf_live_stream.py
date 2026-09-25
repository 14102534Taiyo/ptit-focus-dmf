"""
dmf_live_stream.py - โมดูลเชื่อมต่อและสตรีมข้อมูลสดจากเว็บไซต์กรมเชื้อเพลิงธรรมชาติ (DMF)
ทำงานบนหน่วยความจำ (In-Memory / RAM) 100% พร้อมระบบ Fallback รองรับคลาวด์ต่างประเทศ (Streamlit Cloud)
"""
import io
import re
import ssl
import time
import os
import json
import glob
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_CACHE_FILE = os.path.join(BASE_DIR, "dmf_inventory_cache.json")

# สร้าง SSL Context แบบผ่อนปรนเพื่อรองรับ HTTPS ของหน่วยงานราชการ
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
    'X-Requested-With': 'XMLHttpRequest'
}

THAI_MONTHS_MAP = {
    1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
    5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
    9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
}

def check_dmf_connection(timeout=6):
    """ทดสอบการเชื่อมต่อไปยังเว็บไซต์ DMF"""
    url = "https://dmf.go.th/public/epsummary/data/index/menu/1100"
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': HEADERS['User-Agent']})
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            elapsed = time.time() - t0
            return {
                'status': 'online',
                'code': resp.getcode(),
                'elapsed_sec': round(elapsed, 2),
                'message': f"เชื่อมต่อสำเร็จ ({elapsed:.2f} วินาที)"
            }
    except Exception as e:
        return {
            'status': 'offline',
            'code': None,
            'elapsed_sec': round(time.time() - t0, 2),
            'message': f"เซิร์ฟเวอร์ DMF ไม่ตอบสนอง (ใช้ระบบข้อมูลสำรองในระบบแทนอัตโนมัติ)"
        }

def get_dmf_online_inventory(timeout=8):
    """
    ดึงรายการเดือนที่ DMF เผยแพร่แล้วบนเว็บ (ทั้ง Production และ Sales)
    พร้อมระบบ Local Cache Fallback รองรับกรณีเซิร์ฟเวอร์ Cloud ต่างประเทศถูกไฟร์วอลล์บล็อก
    """
    inventory = {'production': [], 'sales': [], 'is_live': True}
    fetch_success = False

    # 1. รายการเดือนฝั่ง Production (เมนู 1114)
    try:
        prod_url = "https://dmf.go.th/public/createpetroleum/data/index/menu/1114/groupid/1"
        req = urllib.request.Request(prod_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            soup = BeautifulSoup(resp.read().decode('utf-8', errors='ignore'), 'html.parser')
            for a in soup.find_all('a', href=True):
                m = re.search(r'/createpetroleum/data/report/menu/1114/year/(\d+)/month/(\d+)', a['href'])
                if m:
                    year_be = int(m.group(1))
                    month_num = int(m.group(2))
                    month_name = a.get_text(strip=True) or THAI_MONTHS_MAP.get(month_num, f"เดือน {month_num}")
                    if not any(item['year_be'] == year_be and item['month'] == month_num for item in inventory['production']):
                        inventory['production'].append({
                            'year_be': year_be,
                            'month': month_num,
                            'month_name': month_name,
                            'label': f"{month_name} {year_be}"
                        })
            if inventory['production']:
                fetch_success = True
    except Exception as e:
        print(f"Notice: DMF Prod live fetch error: {e}")

    # 2. รายการเดือนฝั่ง Sales & Royalty (เมนู 774)
    try:
        sale_url = "https://dmf.go.th/public/salevalue/data/index/menu/774/groupid/1"
        req = urllib.request.Request(sale_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            soup = BeautifulSoup(resp.read().decode('utf-8', errors='ignore'), 'html.parser')
            for a in soup.find_all('a', href=True):
                m = re.search(r'/salevalue/data/report/menu/774/year/(\d+)/month/(\d+)', a['href'])
                if m:
                    year_ce = int(m.group(1))
                    month_num = int(m.group(2))
                    month_name = a.get_text(strip=True) or THAI_MONTHS_MAP.get(month_num, f"เดือน {month_num}")
                    if not any(item['year_ce'] == year_ce and item['month'] == month_num for item in inventory['sales']):
                        inventory['sales'].append({
                            'year_ce': year_ce,
                            'month': month_num,
                            'month_name': month_name,
                            'label': f"{month_name} {year_ce}"
                        })
            if inventory['sales']:
                fetch_success = True
    except Exception as e:
        print(f"Notice: DMF Sale live fetch error: {e}")

    # หากดึงข้อมูลสดสำเร็จ ให้บันทึกแคช
    if fetch_success and inventory['production']:
        inventory['production'].sort(key=lambda x: (x['year_be'], x['month']), reverse=True)
        inventory['sales'].sort(key=lambda x: (x['year_ce'], x['month']), reverse=True)
        try:
            with open(INVENTORY_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return inventory

    # --- FALLBACK: โหลดจากไฟล์แคช หรือสร้างจากไฟล์ในระบบ ---
    inventory['is_live'] = False
    if os.path.exists(INVENTORY_CACHE_FILE):
        try:
            with open(INVENTORY_CACHE_FILE, 'r', encoding='utf-8') as f:
                cached_inv = json.load(f)
                cached_inv['is_live'] = False
                return cached_inv
        except Exception:
            pass

    # หากไม่มีไฟล์แคช สแกนจากไฟล์ดิบในโฟลเดอร์โดยตรง
    p_files = glob.glob(os.path.join(BASE_DIR, "createpetroleum_2569_*.xlsx"))
    for pf in p_files:
        m = re.search(r'createpetroleum_(\d{4})_(\d+)\.xlsx', os.path.basename(pf))
        if m:
            y_b = int(m.group(1))
            m_n = int(m.group(2))
            inventory['production'].append({
                'year_be': y_b,
                'month': m_n,
                'month_name': THAI_MONTHS_MAP.get(m_n, f"เดือน {m_n}"),
                'label': f"{THAI_MONTHS_MAP.get(m_n, f'เดือน {m_n}')} {y_b}"
            })

    s_dir = os.path.join(BASE_DIR, "Sale")
    if not os.path.exists(s_dir):
        s_dir = os.path.normpath(os.path.join(BASE_DIR, "..", "Sale"))
    s_files = glob.glob(os.path.join(s_dir, "salevalue_2026_*.xlsx"))
    for sf in s_files:
        m = re.search(r'salevalue_(\d{4})_(\d+)\.xlsx', os.path.basename(sf))
        if m:
            y_c = int(m.group(1))
            m_n = int(m.group(2))
            inventory['sales'].append({
                'year_ce': y_c,
                'month': m_n,
                'month_name': THAI_MONTHS_MAP.get(m_n, f"เดือน {m_n}"),
                'label': f"{THAI_MONTHS_MAP.get(m_n, f'เดือน {m_n}')} {y_c}"
            })

    inventory['production'].sort(key=lambda x: (x['year_be'], x['month']), reverse=True)
    inventory['sales'].sort(key=lambda x: (x['year_ce'], x['month']), reverse=True)
    return inventory

def stream_dmf_production_bytes(year_be, month_num, timeout=20):
    """
    ดึงไฟล์ Excel การผลิตจาก DMF เข้าสู่ io.BytesIO ใน RAM โดยตรง (ไม่เขียนไฟล์ลงดิสก์)
    พร้อมระบบ Fallback อ่านจากไฟล์สำรองในระบบหากเซิร์ฟเวอร์ DMF ปฏิเสธการเชื่อมต่อ (เช่น Cloud ต่างประเทศ)
    """
    try:
        post_url = f"https://dmf.go.th/public/createpetroleum/data/excel/menu/1114/year/{year_be}/month/{month_num}"
        post_data = urllib.parse.urlencode({'source': '0', 'type': '0'}).encode('utf-8')
        req = urllib.request.Request(post_url, data=post_data, headers=HEADERS)

        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            rs = resp.read().decode('utf-8', errors='ignore').strip()
            if 'createpetroleum' in rs:
                fname = 'createpetroleum' + rs.split('createpetroleum')[-1].split()[0]
                dl_url = f"https://dmf.go.th/public/createpetroleum_upload/{fname}"
                dl_req = urllib.request.Request(dl_url, headers={'User-Agent': HEADERS['User-Agent']})
                with urllib.request.urlopen(dl_req, context=CTX, timeout=timeout) as dl_resp:
                    content = dl_resp.read()
                    return io.BytesIO(content), fname
    except Exception as ex:
        # Fallback ไปยังไฟล์สำรองในระบบ
        local_candidate = os.path.join(BASE_DIR, f"createpetroleum_{year_be}_{month_num}.xlsx")
        if os.path.exists(local_candidate):
            with open(local_candidate, 'rb') as f:
                return io.BytesIO(f.read()), os.path.basename(local_candidate)
        raise ex

    # Fallback กรณีไม่ได้ชื่อไฟล์จาก response
    local_candidate = os.path.join(BASE_DIR, f"createpetroleum_{year_be}_{month_num}.xlsx")
    if os.path.exists(local_candidate):
        with open(local_candidate, 'rb') as f:
            return io.BytesIO(f.read()), os.path.basename(local_candidate)
    raise ValueError(f"ไม่สามารถสตรีมข้อมูลปี {year_be} เดือน {month_num} จากเว็บ DMF หรือไฟล์สำรองได้")

def stream_dmf_sales_bytes(year_ce, month_num, timeout=20):
    """
    ดึงไฟล์ Excel ยอดขายและค่าภาคหลวงจาก DMF เข้าสู่ io.BytesIO ใน RAM โดยตรง (ไม่เขียนไฟล์ลงดิสก์)
    พร้อมระบบ Fallback อ่านจากไฟล์สำรองในระบบหากเซิร์ฟเวอร์ DMF ปฏิเสธการเชื่อมต่อ (เช่น Cloud ต่างประเทศ)
    """
    try:
        month_str = f"{month_num:02d}"
        post_url = f"https://dmf.go.th/public/salevalue/data/excel/menu/774/year/{year_ce}/month/{month_str}"
        post_data = urllib.parse.urlencode({'source': '0', 'type': '0'}).encode('utf-8')
        req = urllib.request.Request(post_url, data=post_data, headers=HEADERS)

        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            rs = resp.read().decode('utf-8', errors='ignore').strip()
            if 'salevalue' in rs:
                raw_tail = rs.split('salevalue')[-1].split()[0]
                fname = re.sub(r'[^\w\.-]', '', 'salevalue' + raw_tail)
                dl_url = f"https://dmf.go.th/public/salevalue_upload/{fname}"
                dl_req = urllib.request.Request(dl_url, headers={'User-Agent': HEADERS['User-Agent']})
                with urllib.request.urlopen(dl_req, context=CTX, timeout=timeout) as dl_resp:
                    content = dl_resp.read()
                    return io.BytesIO(content), fname
    except Exception as ex:
        pass

    # Fallback ไปยังไฟล์สำรองยอดขายในโฟลเดอร์ Sale
    s_dirs = [os.path.join(BASE_DIR, "Sale"), os.path.normpath(os.path.join(BASE_DIR, "..", "Sale"))]
    for cand_dir in s_dirs:
        cand_file = os.path.join(cand_dir, f"salevalue_{year_ce}_{month_num:02d}.xlsx")
        if os.path.exists(cand_file):
            with open(cand_file, 'rb') as f:
                return io.BytesIO(f.read()), os.path.basename(cand_file)
    raise ValueError(f"ไม่สามารถสตรีมข้อมูลยอดขายปี {year_ce} เดือน {month_num} จากเว็บ DMF หรือไฟล์สำรองได้")

