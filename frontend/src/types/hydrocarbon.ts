export interface ProductionRecord {
  ปี: number | string;
  เดือน: string;
  ลำดับเดือน: number;
  พื้นที่: string;
  PTIT_Region: string;
  PTIT_Operator_Field: string;
  PTIT_Order: number;
  ผู้ดำเนินการ: string;
  แอ่งปิโตรเลียม: string;
  ประเภทสัญญา: string;
  "ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)": number;
  "ก๊าซธรรมชาติ_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)": number;
  "ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)": number;
  "ก๊าซธรรมชาติเหลว_เทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)": number;
  "น้ำมันดิบ (บาร์เรล/วัน)": number;
  "รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)": number;
  จำนวนวันที่ผลิต: number;
  หมายเหตุ: string;
  แปลง_ไฟล์ดิบ: string;
  แหล่ง_ไฟล์ดิบ: string;
  Lookup_Key: string;
  ไฟล์ที่มา: string;
}

export interface MatrixRow {
  PTIT_Region: string;
  PTIT_Operator_Field: string;
  PTIT_Order: number;
  [monthOrStat: string]: any;
}

export interface ProductionMatrix {
  column_name: string;
  unit: string;
  rows: MatrixRow[];
}

export interface ProductionKPIs {
  latest_month: string;
  reporting_year_be: number;
  reporting_year_ce: number;
  active_months: string[];
  latest_gas_mmscfd: number;
  latest_cond_bpd: number;
  latest_crude_bpd: number;
  latest_boed: number;
  total_active_fields: number;
  total_concessions: number;
  total_operators: number;
}

export interface ProductionMasterData {
  metadata: {
    title: string;
    source: string;
    publisher: string;
    sync_timestamp: string;
    record_count: number;
    active_months: string[];
  };
  kpis: ProductionKPIs;
  matrices: {
    gas_mmscfd: ProductionMatrix;
    condensate_bpd: ProductionMatrix;
    crude_bpd: ProductionMatrix;
    total_boed: ProductionMatrix;
  };
  flat_records: ProductionRecord[];
}

export interface SalesRecord {
  ปี: string | number;
  เดือน: string;
  ลำดับเดือน: number;
  ประเภทปิโตรเลียม: string;
  แหล่ง_ไฟล์ดิบ: string;
  พื้นที่: string;
  ผู้ดำเนินการ: string;
  แอ่งปิโตรเลียม: string;
  ประเภทสัญญา: string;
  ปริมาณการขาย_หน่วยหลัก: number;
  หน่วยปริมาณ: string;
  ปริมาณการขาย_MMSCF?: number | null;
  ปริมาณการขาย_MMBTU?: number | null;
  ปริมาณการขาย_บาร์เรล?: number | null;
  ปริมาณการขาย_กิโลกรัม?: number | null;
  ปริมาณการขายเฉลี่ย_MMSCFD?: number | null;
  ปริมาณความร้อนเฉลี่ย_MMBTUD?: number | null;
  ปริมาณการขายเฉลี่ย_BPD?: number | null;
  ค่าความร้อน_Heating_Value_BTU_per_SCF?: number | null;
  มูลค่าการขาย_บาท: number;
  ค่าภาคหลวง_บาท: number;
  ราคาปากหลุม_Wellhead_Price: number;
  หน่วยราคาปากหลุม: string;
  ราคาปากหลุม_ก๊าซ_บาทต่อMMSCF?: number | null;
  อัตราค่าภาคหลวงที่แท้จริง_Pct: number;
  ราคาเฉลี่ยต่อหน่วย_บาท: number;
  ไฟล์ที่มา: string;
}

export interface SalesMasterData {
  metadata: {
    title: string;
    source: string;
    publisher: string;
    sync_timestamp: string;
    record_count: number;
  };
  kpis: {
    total_sales_value_thb: number;
    total_sales_value_million_thb: number;
    total_royalty_thb: number;
    total_royalty_million_thb: number;
    effective_royalty_rate_pct: number;
  };
  flat_records: SalesRecord[];
}

export interface SyncManifest {
  timestamp: string;
  execution_duration_sec: number;
  status: string;
  is_live_dmf: boolean;
  production_records: number;
  sales_records: number;
  latest_production_month: string;
  checksum_prod: string;
  checksum_sale: string;
}
