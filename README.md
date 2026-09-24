# PTIT Focus Statistics - ระบบแปลงข้อมูลและแดชบอร์ดสถิติปิโตรเลียม (DMF)

ระบบจัดการ แปลงข้อมูล และวิเคราะห์สถิติการผลิต การจำหน่าย และมูลค่าปิโตรเลียมของประเทศไทย จากรายงานประจำเดือนของ **กรมเชื้อเพลิงธรรมชาติ (DMF)** จัดทำโดย **สถาบันปิโตรเลียมแห่งประเทศไทย (PTIT)**

---

## 🌟 ฟีเจอร์หลัก (Key Features)

1. **Dashboard & Data Visualization:**
   - แดชบอร์ดสรุปสถิติปริมาณการผลิต (BOED, MMSCFD, BPD) และมูลค่าการจำหน่าย/ค่าภาคหลวง
   - กราฟแนวโน้มรายเดือน (Monthly Trends) และการเปรียบเทียบแยกตาม Operator / พื้นที่ (Onshore vs Offshore)
   - เจาะลึกสถิติประจำเดือน (Monthly Deep-Dive) และ Market Share
2. **ระบบแบ่งสิทธิ์ผู้ใช้งาน (Role-Based Access):**
   - **Viewer (ผู้ใช้งานทั่วไป):** เข้าถึงเฉพาะหน้าแดชบอร์ดสถิติและรายงานมาตรฐาน พร้อมปุ่มดาวน์โหลด Flat Table
   - **Admin (ผู้ดูแลระบบ):** ปลดล็อกฟังก์ชันการแปลงข้อมูล, จัดการ Master Data Model และระบบ 1-Click Auto Sync
3. **ระบบ 1-Click Auto Sync (In-Memory Stream):**
   - ตรวจจับเดือนใหม่และดึงข้อมูลสดจากเว็บไซต์กรมเชื้อเพลิงธรรมชาติ (dmf.go.th) เข้าสู่หน่วยความจำ RAM โดยตรง
   - คำนวณและปรับปรุงตัวเลขย้อนหลังอัตโนมัติ (Retroactive Adjustments)
4. **มาตรฐานรายงาน PTIT (Domestic Production Report):**
   - ส่งออกรายงานการผลิตในประเทศรูปแบบทางการตามมาตรฐานสิ่งพิมพ์ PTIT (.xlsx)

---

## 🚀 วิธีการติดตั้งและรันระบบ (Quick Start)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. รันแอปพลิเคชัน
```bash
streamlit run app.py
```
หรือดับเบิลคลิกไฟล์ **`เปิดระบบแปลงข้อมูล.bat`** บน Windows

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)
```text
├── app.py                      # สคริปต์หลักของ Web Application (Streamlit)
├── dmf_live_stream.py          # โมดูลเชื่อมต่อสตรีมข้อมูลสดจากเว็บ DMF
├── master_mapping.xlsx         # ตาราง Master Data Model การผลิต
├── sale_master_mapping.xlsx    # ตาราง Master Data Model ยอดขายและค่าภาคหลวง
├── requirements.txt            # รายการ Dependencies สำหรับรันระบบ
├── output/                     # โฟลเดอร์เก็บไฟล์ผลลัพธ์ Flat Table (.xlsx)
├── Sale/                       # โฟลเดอร์เก็บไฟล์รายงานยอดขาย DMF
└── คู่มือการใช้งาน.md          # คู่มือการใช้งานระบบฉบับละเอียด
```
