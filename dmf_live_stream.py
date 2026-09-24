"""
dmf_live_stream.py - โมดูลเชื่อมต่อและสตรีมข้อมูลสดจากเว็บไซต์กรมเชื้อเพลิงธรรมชาติ (DMF)
ทำงานบนหน่วยความจำ (In-Memory / RAM) 100% ไม่ต้องบันทึกไฟล์ลงฮาร์ดดิสก์
"""
import io
import re
import ssl
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd

# สร้าง SSL Context แบบผ่อนปรนเพื่อรองรับ HTTPS ของหน่วยงานราชการ
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

THAI_MONTHS_MAP = {
    1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
    5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
    9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
}

def check_dmf_connection(timeout=8):
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
            'message': f"ไม่สามารถเชื่อมต่อได้: {str(e)}"
        }

def get_dmf_online_inventory(timeout=10):
    """
    ดึงรายการเดือนที่ DMF เผยแพร่แล้วบนเว็บ (ทั้ง Production และ Sales)
    """
    inventory = {'production': [], 'sales': []}
    
    # 1. รายการเดือนฝั่ง Production (เมนู 1114)
    try:
        prod_url = "https://dmf.go.th/public/createpetroleum/data/index/menu/1114/groupid/1"
        req = urllib.request.Request(prod_url, headers={'User-Agent': HEADERS['User-Agent']})
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
    except Exception as e:
        print(f"Error fetching prod inventory: {e}")

    # 2. รายการเดือนฝั่ง Sales & Royalty (เมนู 774)
    try:
        sale_url = "https://dmf.go.th/public/salevalue/data/index/menu/774/groupid/1"
        req = urllib.request.Request(sale_url, headers={'User-Agent': HEADERS['User-Agent']})
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
    except Exception as e:
        print(f"Error fetching sale inventory: {e}")

    inventory['production'].sort(key=lambda x: (x['year_be'], x['month']), reverse=True)
    inventory['sales'].sort(key=lambda x: (x['year_ce'], x['month']), reverse=True)
    return inventory

def stream_dmf_production_bytes(year_be, month_num, timeout=25):
    """
    ดึงไฟล์ Excel การผลิตจาก DMF เข้าสู่ io.BytesIO ใน RAM โดยตรง (ไม่เขียนไฟล์ลงดิสก์)
    """
    post_url = f"https://dmf.go.th/public/createpetroleum/data/excel/menu/1114/year/{year_be}/month/{month_num}"
    post_data = urllib.parse.urlencode({'source': '0', 'type': '0'}).encode('utf-8')
    req = urllib.request.Request(post_url, data=post_data, headers=HEADERS)

    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
        rs = resp.read().decode('utf-8', errors='ignore').strip()
        if 'createpetroleum' not in rs:
            raise ValueError(f"ไม่ได้รับชื่อไฟล์ Excel จาก DMF สำหรับปี {year_be} เดือน {month_num}: {rs[:100]}")
        fname = 'createpetroleum' + rs.split('createpetroleum')[-1].split()[0]
        dl_url = f"https://dmf.go.th/public/createpetroleum_upload/{fname}"
        
        dl_req = urllib.request.Request(dl_url, headers={'User-Agent': HEADERS['User-Agent']})
        with urllib.request.urlopen(dl_req, context=CTX, timeout=timeout) as dl_resp:
            content = dl_resp.read()
            return io.BytesIO(content), fname

def stream_dmf_sales_bytes(year_ce, month_num, timeout=25):
    """
    ดึงไฟล์ Excel ยอดขายและค่าภาคหลวงจาก DMF เข้าสู่ io.BytesIO ใน RAM โดยตรง (ไม่เขียนไฟล์ลงดิสก์)
    """
    month_str = f"{month_num:02d}"
    post_url = f"https://dmf.go.th/public/salevalue/data/excel/menu/774/year/{year_ce}/month/{month_str}"
    post_data = urllib.parse.urlencode({'source': '0', 'type': '0'}).encode('utf-8')
    req = urllib.request.Request(post_url, data=post_data, headers=HEADERS)

    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
        rs = resp.read().decode('utf-8', errors='ignore').strip()
        if 'salevalue' not in rs:
            raise ValueError(f"ไม่ได้รับชื่อไฟล์ Excel จาก DMF สำหรับปี {year_ce} เดือน {month_str}: {rs[:100]}")
        raw_tail = rs.split('salevalue')[-1].split()[0]
        fname = 'salevalue' + raw_tail
        fname = re.sub(r'[^\w\.-]', '', fname)
        dl_url = f"https://dmf.go.th/public/salevalue_upload/{fname}"
        
        dl_req = urllib.request.Request(dl_url, headers={'User-Agent': HEADERS['User-Agent']})
        with urllib.request.urlopen(dl_req, context=CTX, timeout=timeout) as dl_resp:
            content = dl_resp.read()
            return io.BytesIO(content), fname
