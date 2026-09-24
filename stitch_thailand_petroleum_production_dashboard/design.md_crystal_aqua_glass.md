# Design System: Siam Hydrocarbon Intelligence (Crystal Aqua Glass)

สเปกการออกแบบ (Design Specification) สไตล์ **Light Glassmorphism / Crystal Aqua Glass** สำหรับแอปพลิเคชันวิเคราะห์ข้อมูลการผลิตปิโตรเลียม (Petroleum Telemetry & Analytics) อ้างอิงตามหน้าจอ "เปรียบเทียบการผลิต - Crystal Aqua Glass"

---

## 1. Brand Identity & Design Philosophy
- **Name:** Siam Hydrocarbon Intelligence (Crystal Aqua Glass Edition)
- **Concept:** โมเดิร์นระดับ Enterprise Telemetry ที่ผสานความโปร่งใสแบบกระจกคริสตัล (Crystal Glass) สะท้อนภาพลักษณ์พลังงานอ่าวไทยและความสะอาด โปร่งใส น่าเชื่อถือ
- **Visual Personality:** Tech-forward, Analytical, High-transparency, Airy & Clean, High-contrast Legibility

---

## 2. Color Palette & Tokens

### Background & Surface Hierarchy
- **Canvas Base Background:** `radial-gradient(135% 100% at 50% 0%, #E0F2FE 0%, #F0F9FF 35%, #F8FAFC 70%, #EFF6FF 100%)`
  - พื้นผิวหลักเป็นสีฟ้าอ่อนพาสเทลไอซ์บลู มีความละมุน ไม่สะท้อนแสงจ้า
- **Glass Card Surface (Default):** `rgba(255, 255, 255, 0.72)` with `backdrop-filter: blur(16px) saturate(180%)`
- **Glass Card Surface (Elevated / Highlight):** `rgba(255, 255, 255, 0.88)` with `backdrop-filter: blur(20px)`
- **Glass Card Surface (Secondary / Recessed):** `rgba(240, 249, 255, 0.55)`

### Borders & Glowing Edges
- **Glass Border Light:** `1px solid rgba(255, 255, 255, 0.85)` (ขอบสะท้อนแสงด้านบน/ซ้าย)
- **Glass Border Subtle:** `1px solid rgba(186, 230, 253, 0.45)` (Sky-200 tint)
- **Glass Inner Glow:** `inset 0 1px 1px 0 rgba(255, 255, 255, 0.9)`

### Brand & Functional Colors
- **Primary / Brand Accent:** `#0284C7` (Sky Blue - ก๊าซธรรมชาติและการเชื่อมต่อดาต้า)
- **Primary Gradient:** `linear-gradient(135deg, #0284C7 0%, #0369A1 100%)`
- **Secondary Accent (Hydrocarbon Flame / Crude Oil):** `#EA580C` (Warm Amber / Energy Orange)
- **Secondary Flame Gradient:** `linear-gradient(135deg, #F97316 0%, #DC2626 100%)`
- **Condensate Accent (Purple):** `#7C3AED` / `#9333EA` (ก๊าซธรรมชาติเหลว)
- **Success / Positive Trend (+MoM / YoY):** `#16A34A` / Soft Badge `#DCFCE7` (Text `#15803D`)
- **Danger / Negative Trend (-MoM / YoY):** `#DC2626` / Soft Badge `#FEE2E2` (Text `#B91C1C`)

### Typography & Content Colors
- **Text Primary (Headings, Core KPIs):** `#0F172A` (Slate 900 - คมชัดสูง อ่านง่ายบนกระจกฝ้า)
- **Text Secondary (Subtitles, Units, Table Headers):** `#334155` (Slate 700)
- **Text Muted (Captions, Timestamps, Legends):** `#64748B` (Slate 500)
- **Text Inverted (On Active Buttons / Chips):** `#FFFFFF`

---

## 3. Typography Hierarchy
- **Font Family:** `'Manrope'`, `'Inter'`, system-ui, -apple-system, sans-serif
- **Scale:**
  - **Screen / Page Title:** 20px / 1.25rem, Font-weight: 800, Tracking: tight (`#0F172A`)
  - **KPI Hero Numbers:** 28px - 32px / 1.75rem - 2.0rem, Font-weight: 800, Monospace numbers (`tabular-nums`)
  - **Section Headers:** 14px - 15px, Font-weight: 700, Uppercase tracking (`tracking-wide`)
  - **Card Title / Metric Labels:** 13px - 14px, Font-weight: 600
  - **Body Text:** 12px - 13px, Font-weight: 400 - 500
  - **Badges / Micro Tags:** 10px - 11px, Font-weight: 700

---

## 4. Elevation, Blur & Glassmorphism Specs

```css
/* Glass Card Base Style */
.glass-card {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 
    0 8px 32px 0 rgba(31, 38, 135, 0.07),
    0 2px 6px 0 rgba(0, 0, 0, 0.02),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.9);
  border-radius: 20px;
}

/* Glass Interactive (Hover / Active State) */
.glass-card-interactive:active {
  transform: scale(0.985);
  background: rgba(255, 255, 255, 0.85);
}

/* Glass Pill / Filter Chip (Inactive) */
.glass-pill {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(224, 242, 254, 0.8);
  color: #334155;
}

/* Glass Pill (Active) */
.glass-pill-active {
  background: #0284C7;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}
```

---

## 5. UI Components & Patterns

### 1. Header & Live Indicator
- Sticky Top App Bar พร้อม Glass background (`rgba(255, 255, 255, 0.85)` + `blur(12px)`)
- DMF Logo เปลวไฟปิโตรเลียม ทรงมน Squircle (`rx=24`)
- Live Status Chip: จุดเขียวไฟกระพริบ `bg-emerald-500` พร้อมข้อความ "FIREBASE SYNCED" / "LIVE CLUSTER" บนแถบกระจกสีฟ้าอ่อน

### 2. Segmented Time Range Selector
- แคปซูลพื้นหลังสีฟ้าพาสเทลใส `rgba(224, 242, 254, 0.5)`
- สวิตช์ 3 ตัวเลือก: "เทียบรายเดือน (MoM)", "เทียบปีก่อน (YoY)", "สะสมรายปี (YTD)"
- รายการที่ถูกเลือกจะใช้สไตล์นูนสีเข้มเด่นชัดเพื่อความรวดเร็วในการสังเกต

### 3. Metric & Trend Stream Cards
- แยกแถบสีกำกับตามชนิดผลิตภัณฑ์:
  - **ฟ้า:** ก๊าซธรรมชาติ (Natural Gas)
  - **ส้ม:** น้ำมันดิบ (Crude Oil)
  - **ม่วง:** ก๊าซธรรมชาติเหลว (Condensate)
- ข้อมูลสัดส่วนเปอร์เซ็นต์ (เช่น สัดส่วน 68%) อยู่ใน Badge สีนุ่มนวล
- มี Sparkline SVG ขวามือแสดงแนวโน้ม 6 จุดข้อมูลล่าสุด

### 4. Comparison Bar Chart Styling
- **ปีปัจจุบัน (2567):** แท่งทึบสี `#0284C7` (Sky Blue) พร้อมมิติ Inner Glow
- **ปีฐาน (2566):** แท่งโปร่งแสงสีฟ้าขุ่น `rgba(186, 230, 253, 0.6)`
- **Peak Month Column:** ไฮไลท์พิเศษด้วยสีส้มเปลวไฟ `#F97316` พร้อม Pin Badge และตัวเลขชัดเจน
- **Target Line:** เส้นประสีทองอำพัน `#D97706` แสดงเป้าหมายสัมปทาน DMF

### 5. Historical Data Table
- ตารางสไตล์ Compact Clean มีแถบไฮไลท์เดือนล่าสุดด้วยจุด Accent Blue
- แถวตารางสลับสีอ่อนบางเบา (`rgba(248, 250, 252, 0.6)`)
- ตัวเลขสถิติจัดชิดขวา ใช้ฟอนต์แบบ Monospace (`tabular-nums`) พร้อมปุ่ม Export CSV สะดวกต่อการนำไปใช้งานต่อ

### 6. Bottom Navigation Bar
- Fixed Bottom Bar สไตล์ Floating Frosted Glass (`rgba(255, 255, 255, 0.9)` + `blur(16px)`)
- 4 แท็บหลัก:
  1. ภาพรวม (Overview)
  2. เปรียบเทียบรายเดือน (Monthly Comparison - Active)
  3. แหล่งสัมปทาน (Concessions)
  4. ยอดจำหน่าย (Sales & Offtake)
- แท็บที่ Active จะใช้สี Accent Cyan-Blue `#0284C7` พร้อมไอคอนเรืองแสงเล็กน้อย
