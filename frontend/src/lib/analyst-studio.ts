import { ProductionRecord } from "@/types/hydrocarbon";
import { daysInMonth } from "@/lib/reporting";
import {
  TRACKER_METRICS,
  TimelinePoint,
  TrackerMetric,
  annualSeries,
  fieldKey,
} from "@/lib/field-tracker";

/**
 * "ห้องวิเคราะห์" — analysts pick DMF field names, put them into groups they name themselves,
 * and get monthly / annual pivots. Everything here is plain functions over the flat records.
 */

export interface StudioField {
  name: string;
  region: "Onshore" | "Offshore" | string;
  blocks: string[];
  latestBlock: string;
  operators: string[];
  latestOperator: string;
  firstYear: number;
  lastYear: number;
  /** Total volume over the range in the chosen metric (rate × days), for ranking. */
  volume: number;
}

const clean = (value: unknown) => String(value ?? "").trim();
const UNKNOWN_OPERATOR = "ยังไม่ระบุ";

export function buildStudioCatalog(
  records: ProductionRecord[],
  fromYear: number,
  toYear: number,
  metric: TrackerMetric,
): StudioField[] {
  const column = TRACKER_METRICS[metric].column;
  type Acc = StudioField & { blockSet: Set<string>; operatorSet: Set<string>; latestStamp: number };
  const catalog = new Map<string, Acc>();
  records.forEach((record) => {
    const year = Number(record.ปี);
    if (year < fromYear || year > toYear) return;
    const name = fieldKey(record);
    if (!name) return;
    const month = Number(record.ลำดับเดือน);
    const stamp = year * 100 + month;
    let info = catalog.get(name);
    if (!info) {
      info = {
        name,
        region: record.PTIT_Region,
        blocks: [],
        latestBlock: "",
        operators: [],
        latestOperator: "",
        firstYear: year,
        lastYear: year,
        volume: 0,
        blockSet: new Set(),
        operatorSet: new Set(),
        latestStamp: -1,
      };
      catalog.set(name, info);
    }
    const block = clean(record.แปลง_ไฟล์ดิบ);
    const operator = clean(record.ผู้ดำเนินการ);
    if (block) info.blockSet.add(block);
    if (operator && operator !== UNKNOWN_OPERATOR) info.operatorSet.add(operator);
    if (stamp >= info.latestStamp) {
      info.latestStamp = stamp;
      info.region = record.PTIT_Region || info.region;
      if (block) info.latestBlock = block;
      if (operator && operator !== UNKNOWN_OPERATOR) info.latestOperator = operator;
    }
    info.firstYear = Math.min(info.firstYear, year);
    info.lastYear = Math.max(info.lastYear, year);
    info.volume += (Number(record[column]) || 0) * daysInMonth(month, year);
  });
  return Array.from(catalog.values())
    .map(({ blockSet, operatorSet, latestStamp, ...info }) => ({
      ...info,
      blocks: Array.from(blockSet),
      operators: Array.from(operatorSet),
      latestOperator: info.latestOperator || "ไม่ระบุผู้ดำเนินการ",
      latestBlock: info.latestBlock || "ไม่ระบุแปลง",
    }))
    .sort((a, b) => b.volume - a.volume);
}

export const regionLabel = (region: string) => (region === "Onshore" ? "บนบก" : "ในทะเล");

export type GroupPreset = "field" | "one" | "block" | "operator" | "region" | "mapping";

export const GROUP_PRESETS: { id: GroupPreset; label: string; hint: string }[] = [
  { id: "field", label: "แยกรายแหล่ง", hint: "1 แหล่ง = 1 กลุ่ม" },
  { id: "mapping", label: "ตาม Mapping ของ PTIT", hint: "รวมชื่อที่เปลี่ยน/แยก ตามที่ PTIT ยืนยันแล้ว" },
  { id: "block", label: "ตามแปลงสัมปทาน", hint: "ใช้แปลงล่าสุดที่ DMF รายงานแหล่งนั้น" },
  { id: "operator", label: "ตามผู้ดำเนินการ", hint: "ใช้ผู้ดำเนินการล่าสุดของแหล่งนั้น" },
  { id: "region", label: "บนบก / ในทะเล", hint: "" },
  { id: "one", label: "รวมทั้งหมดเป็นกลุ่มเดียว", hint: "" },
];

/** field name → group name for the chosen fields under a preset. */
export function presetAssignment(
  fields: StudioField[],
  preset: GroupPreset,
  mappingLookup: Map<string, string>,
): Record<string, string> {
  const assign: Record<string, string> = {};
  fields.forEach((f) => {
    switch (preset) {
      case "one":
        assign[f.name] = "รวมแหล่งที่เลือก";
        break;
      case "block":
        assign[f.name] = `แปลง ${f.latestBlock}`;
        break;
      case "operator":
        assign[f.name] = f.latestOperator;
        break;
      case "region":
        assign[f.name] = regionLabel(f.region);
        break;
      case "mapping":
        assign[f.name] = mappingLookup.get(f.name) || f.name;
        break;
      default:
        assign[f.name] = f.name;
    }
  });
  return assign;
}

/** Groups in display order: largest volume first. */
export function orderGroups(assign: Record<string, string>, fields: StudioField[]): string[] {
  const volume = new Map<string, number>();
  fields.forEach((f) => {
    const group = assign[f.name];
    if (group !== undefined) volume.set(group, (volume.get(group) || 0) + f.volume);
  });
  return Array.from(volume.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([group]) => group);
}

/** One pass over the records: monthly daily-rate per group (null where no member reported). */
export function groupMonthlySeries(
  records: ProductionRecord[],
  assign: Record<string, string>,
  timeline: TimelinePoint[],
  metric: TrackerMetric,
): Map<string, (number | null)[]> {
  const column = TRACKER_METRICS[metric].column;
  const position = new Map(timeline.map((p, index) => [p.year * 100 + p.month, index]));
  const series = new Map<string, (number | null)[]>();
  records.forEach((record) => {
    const group = assign[fieldKey(record)];
    if (group === undefined) return;
    const index = position.get(Number(record.ปี) * 100 + Number(record.ลำดับเดือน));
    if (index === undefined) return;
    let values = series.get(group);
    if (!values) {
      values = new Array(timeline.length).fill(null);
      series.set(group, values);
    }
    values[index] = (values[index] ?? 0) + (Number(record[column]) || 0);
  });
  return series;
}

export type Granularity = "monthly" | "annual";
export type ValueMode = "rate" | "volume";

export interface PivotPeriod {
  year: number;
  /** 1–12, or 0 for a whole year */
  month: number;
  label: string;
  /** false when the year is not fully published yet */
  complete: boolean;
}

const SHORT_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];

/**
 * Turns monthly rates into the values shown in the pivot / chart.
 * rate   → average barrels (or MMSCF) per day; annual = day-weighted average over published months
 * volume → total produced in the period, in the metric's volume unit (e.g. MMBOE)
 */
export function toPeriods(
  monthly: (number | null)[],
  timeline: TimelinePoint[],
  granularity: Granularity,
  mode: ValueMode,
  metric: TrackerMetric,
): { periods: PivotPeriod[]; values: (number | null)[] } {
  const divisor = TRACKER_METRICS[metric].volumeDivisor;
  if (granularity === "monthly") {
    return {
      periods: timeline.map((p) => ({ ...p, label: `${SHORT_MONTHS[p.month - 1]} ${p.year}`, complete: true })),
      values: monthly.map((value, index) =>
        value === null
          ? null
          : mode === "rate"
            ? value
            : (value * daysInMonth(timeline[index].month, timeline[index].year)) / divisor,
      ),
    };
  }
  const annual = annualSeries(monthly, timeline);
  return {
    periods: annual.map((a) => ({
      year: a.year,
      month: 0,
      label: a.isComplete ? `${a.year}` : `${a.year} (${a.months} ด.)`,
      complete: a.isComplete,
    })),
    values: annual.map((a) =>
      a.averageRate === null ? null : mode === "rate" ? a.averageRate : a.volume / divisor,
    ),
  };
}

/** Sum of several aligned series; null only where every series is null. */
export function sumSeries(all: (number | null)[][], length: number): (number | null)[] {
  return Array.from({ length }, (_, index) => {
    let total: number | null = null;
    all.forEach((values) => {
      const value = values[index];
      if (value !== null && value !== undefined) total = (total ?? 0) + value;
    });
    return total;
  });
}

/** Summary over the whole range for one group: average daily rate and total volume. */
export function rangeSummary(monthly: (number | null)[], timeline: TimelinePoint[], metric: TrackerMetric) {
  let volume = 0;
  let days = 0;
  monthly.forEach((value, index) => {
    const d = daysInMonth(timeline[index].month, timeline[index].year);
    days += d;
    if (value !== null) volume += value * d;
  });
  return { averageRate: days ? volume / days : 0, volume: volume / TRACKER_METRICS[metric].volumeDivisor };
}

// ---- Saved / shared analysis ----
export interface StudioState {
  from: number;
  to: number;
  metric: TrackerMetric;
  granularity: Granularity;
  mode: ValueMode;
  /** field → group */
  assign: Record<string, string>;
  /** groups drawn on the chart (max 8) */
  shown: string[];
}

export const STUDIO_STORAGE_KEY = "ptit.analystStudio.v1";
export const STUDIO_HASH_KEY = "studio";

export function isStudioState(value: unknown): value is StudioState {
  const s = value as StudioState;
  return (
    !!s &&
    Number.isFinite(s.from) &&
    Number.isFinite(s.to) &&
    typeof s.metric === "string" &&
    s.metric in TRACKER_METRICS &&
    (s.granularity === "monthly" || s.granularity === "annual") &&
    (s.mode === "rate" || s.mode === "volume") &&
    !!s.assign &&
    typeof s.assign === "object" &&
    Object.values(s.assign).every((g) => typeof g === "string") &&
    Array.isArray(s.shown)
  );
}
