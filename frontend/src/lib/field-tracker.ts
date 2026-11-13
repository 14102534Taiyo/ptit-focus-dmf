import { ProductionRecord } from "@/types/hydrocarbon";
import { daysInMonth } from "@/lib/reporting";

export type TrackerMetric = "boed" | "gas" | "condensate" | "crude";

export const TRACKER_METRICS: Record<
  TrackerMetric,
  { label: string; column: keyof ProductionRecord; unit: string; volumeUnit: string; volumeDivisor: number }
> = {
  boed: {
    label: "รวมเทียบเท่าน้ำมัน",
    column: "รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)",
    unit: "BOED",
    volumeUnit: "MMBOE",
    volumeDivisor: 1_000_000,
  },
  gas: {
    label: "ก๊าซธรรมชาติ",
    column: "ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)",
    unit: "MMSCFD",
    volumeUnit: "BCF",
    volumeDivisor: 1_000,
  },
  condensate: {
    label: "คอนเดนเสท",
    column: "ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)",
    unit: "BPD",
    volumeUnit: "MMbbl",
    volumeDivisor: 1_000_000,
  },
  crude: {
    label: "น้ำมันดิบ",
    column: "น้ำมันดิบ (บาร์เรล/วัน)",
    unit: "BPD",
    volumeUnit: "MMbbl",
    volumeDivisor: 1_000_000,
  },
};

/** A field is identified by DMF's own field name, which is stable across years. */
export function fieldKey(record: ProductionRecord): string {
  return String(record.แหล่ง_ไฟล์ดิบ || record.PTIT_Operator_Field || "").trim();
}

export interface FieldInfo {
  name: string;
  region: string;
  operators: string[];
  firstYear: number;
  lastYear: number;
  /** Total volume over the selected range in the chosen metric — used for ranking. */
  volume: number;
}

export interface TimelinePoint {
  year: number;
  month: number;
}

/** Every (year, month) DMF has published inside [fromYear, toYear], in order. */
export function buildTimeline(
  monthsIndex: Record<string, number[]>,
  fromYear: number,
  toYear: number,
): TimelinePoint[] {
  const points: TimelinePoint[] = [];
  for (let year = fromYear; year <= toYear; year++) {
    (monthsIndex[String(year)] || []).forEach((month) => points.push({ year, month }));
  }
  return points;
}

function inRange(record: ProductionRecord, fromYear: number, toYear: number) {
  const year = Number(record.ปี);
  return year >= fromYear && year <= toYear;
}

export function buildFieldCatalog(
  records: ProductionRecord[],
  fromYear: number,
  toYear: number,
  metric: TrackerMetric,
): FieldInfo[] {
  const column = TRACKER_METRICS[metric].column;
  const catalog = new Map<string, FieldInfo & { operatorSet: Set<string> }>();
  records.forEach((record) => {
    if (!inRange(record, fromYear, toYear)) return;
    const name = fieldKey(record);
    if (!name) return;
    const year = Number(record.ปี);
    let info = catalog.get(name);
    if (!info) {
      info = {
        name,
        region: record.PTIT_Region,
        operators: [],
        operatorSet: new Set(),
        firstYear: year,
        lastYear: year,
        volume: 0,
      };
      catalog.set(name, info);
    }
    info.firstYear = Math.min(info.firstYear, year);
    info.lastYear = Math.max(info.lastYear, year);
    const operator = String(record.ผู้ดำเนินการ || "").trim();
    if (operator && operator !== "ยังไม่ระบุ") info.operatorSet.add(operator);
    info.volume +=
      (Number(record[column]) || 0) * daysInMonth(Number(record.ลำดับเดือน), year);
  });
  return Array.from(catalog.values())
    .map(({ operatorSet, ...info }) => ({ ...info, operators: Array.from(operatorSet) }))
    .sort((a, b) => b.volume - a.volume);
}

/**
 * Monthly daily-rate series for one field. A month where the field has no DMF row is null
 * (the field was not producing or not yet / no longer reported) so the line shows a gap.
 */
export function monthlySeries(
  records: ProductionRecord[],
  field: string,
  timeline: TimelinePoint[],
  metric: TrackerMetric,
): (number | null)[] {
  const column = TRACKER_METRICS[metric].column;
  const sums = new Map<string, number>();
  records.forEach((record) => {
    if (fieldKey(record) !== field) return;
    const key = `${Number(record.ปี)}-${Number(record.ลำดับเดือน)}`;
    sums.set(key, (sums.get(key) || 0) + (Number(record[column]) || 0));
  });
  return timeline.map(({ year, month }) => {
    const value = sums.get(`${year}-${month}`);
    return value === undefined ? null : value;
  });
}

export interface AnnualPoint {
  year: number;
  /** Day-weighted average rate over the months DMF published that year (absent months = 0). */
  averageRate: number | null;
  volume: number;
  months: number;
  isComplete: boolean;
}

export function annualSeries(
  monthly: (number | null)[],
  timeline: TimelinePoint[],
): AnnualPoint[] {
  const byYear = new Map<number, { volume: number; days: number; months: number; reported: boolean }>();
  timeline.forEach(({ year, month }, index) => {
    const entry = byYear.get(year) || { volume: 0, days: 0, months: 0, reported: false };
    const days = daysInMonth(month, year);
    const value = monthly[index];
    entry.days += days;
    entry.months += 1;
    if (value !== null) {
      entry.volume += value * days;
      entry.reported = true;
    }
    byYear.set(year, entry);
  });
  return Array.from(byYear.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([year, entry]) => ({
      year,
      averageRate: entry.reported && entry.days > 0 ? entry.volume / entry.days : null,
      volume: entry.volume,
      months: entry.months,
      isComplete: entry.months === 12,
    }));
}
