"use client";

import React, { useEffect, useMemo, useState } from "react";
import { Download, Loader2, Plus, Search, X } from "lucide-react";
import * as XLSX from "xlsx";
import { ProductionRecord } from "@/types/hydrocarbon";
import {
  FieldGroupRow,
  TRACKER_METRICS,
  TrackerMetric,
  annualSeries,
  buildFieldCatalog,
  buildTimeline,
  confirmedGroupLookup,
  fieldKey,
  groupedKeyFn,
  monthlySeries,
} from "@/lib/field-tracker";
import { FieldTrendChart, TrendPoint } from "@/components/FieldTrendChart";
import { FieldMappingReference } from "@/components/FieldMappingReference";
import { formatInteger, formatNumber } from "@/lib/utils";

// Categorical slots 1–4 (validated light/dark steps); color follows the field, never its rank
const SERIES_COLORS = {
  light: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"],
  dark: ["#3987e5", "#d95926", "#199e70", "#c98500"],
};
const MAX_FIELDS = 4;
const DEFAULT_SPAN = 10;

interface FieldTrackerViewProps {
  records: ProductionRecord[];
  monthsIndex: Record<string, number[]>;
  ensureYears: (years: number[]) => Promise<void>;
  loadedYears: Set<number>;
  pendingCount: number;
  theme: "light" | "dark";
  mappingRows: FieldGroupRow[];
  mappingGenerated?: string;
}

export function FieldTrackerView({
  records,
  monthsIndex,
  ensureYears,
  loadedYears,
  pendingCount,
  theme,
  mappingRows,
  mappingGenerated,
}: FieldTrackerViewProps) {
  const years = useMemo(
    () => Object.keys(monthsIndex).map(Number).filter(Number.isFinite).sort((a, b) => a - b),
    [monthsIndex],
  );
  const latestYear = years[years.length - 1];
  const [fromYear, setFromYear] = useState(Math.max(years[0], latestYear - DEFAULT_SPAN + 1));
  const [toYear, setToYear] = useState(latestYear);
  const [metric, setMetric] = useState<TrackerMetric>("boed");
  const [granularity, setGranularity] = useState<"monthly" | "annual">("monthly");
  const [selected, setSelected] = useState<string[]>([]);
  // Slot per field, kept for as long as the field stays selected
  const [slots, setSlots] = useState<Record<string, number>>({});
  const [query, setQuery] = useState("");
  const [useGroups, setUseGroups] = useState(true);
  const [needsDefault, setNeedsDefault] = useState(true);

  const groupLookup = useMemo(() => confirmedGroupLookup(mappingRows), [mappingRows]);
  const keyOf = useMemo(() => (useGroups ? groupedKeyFn(groupLookup) : fieldKey), [useGroups, groupLookup]);
  // Members of each confirmed multi-name group, for chip tooltips and labels
  const groupMembers = useMemo(() => {
    const members = new Map<string, string[]>();
    groupLookup.forEach((group, name) => members.set(group, [...(members.get(group) || []), name]));
    return members;
  }, [groupLookup]);
  const isMergedGroup = (name: string) => useGroups && (groupMembers.get(name)?.length || 0) > 1;

  const toggleGroups = (value: boolean) => {
    setUseGroups(value);
    setSelected([]);
    setNeedsDefault(true);
  };

  const rangeYears = useMemo(() => years.filter((y) => y >= fromYear && y <= toYear), [years, fromYear, toYear]);
  useEffect(() => {
    ensureYears(rangeYears);
  }, [ensureYears, rangeYears]);
  const rangeLoaded = rangeYears.every((y) => loadedYears.has(y));

  const catalog = useMemo(
    () => (rangeLoaded ? buildFieldCatalog(records, fromYear, toYear, metric, keyOf) : []),
    [records, fromYear, toYear, metric, rangeLoaded, keyOf],
  );

  const addField = (name: string) => {
    if (selected.includes(name) || selected.length >= MAX_FIELDS) return;
    const used = new Set(selected.map((f) => slots[f]));
    const slot = [0, 1, 2, 3].find((s) => !used.has(s)) ?? 0;
    setSlots((current) => ({ ...current, [name]: slot }));
    setSelected((current) => [...current, name]);
    setQuery("");
  };
  const removeField = (name: string) => setSelected((current) => current.filter((f) => f !== name));

  // Start with the three largest fields of the range so the page is never empty
  useEffect(() => {
    if (needsDefault && catalog.length > 0) {
      const initial = catalog.slice(0, 3).map((f) => f.name);
      setSlots(Object.fromEntries(initial.map((name, index) => [name, index])));
      setSelected(initial);
      setNeedsDefault(false);
    }
  }, [needsDefault, catalog]);

  const suggestions = useMemo(() => {
    const q = query.trim().toLowerCase();
    return catalog
      .filter((f) => !selected.includes(f.name))
      .filter((f) => !q || f.name.toLowerCase().includes(q) || f.operators.some((o) => o.toLowerCase().includes(q)))
      .slice(0, 12);
  }, [catalog, query, selected]);

  const cfg = TRACKER_METRICS[metric];
  const decimals = metric === "gas" ? 1 : 0;
  const timeline = useMemo(() => buildTimeline(monthsIndex, fromYear, toYear), [monthsIndex, fromYear, toYear]);
  const palette = SERIES_COLORS[theme];

  const fieldSeries = useMemo(
    () =>
      selected.map((name) => {
        const monthly = monthlySeries(records, name, timeline, metric, keyOf);
        return { name, color: palette[slots[name] ?? 0], monthly, annual: annualSeries(monthly, timeline) };
      }),
    [selected, records, timeline, metric, palette, slots, keyOf],
  );

  const chartPoints: TrendPoint[] =
    granularity === "monthly"
      ? timeline.map((p) => ({ year: p.year, month: p.month }))
      : rangeYears.map((year) => ({ year, month: 0 }));
  const chartSeries = fieldSeries.map((s) => ({
    name: s.name,
    color: s.color,
    values: granularity === "monthly" ? s.monthly : s.annual.map((a) => a.averageRate),
  }));

  const fmt = (v: number | null) => (v === null ? "-" : decimals ? formatNumber(v, decimals) : formatInteger(v));
  const latestPartial = monthsIndex[String(toYear)]?.length !== 12;

  const exportExcel = () => {
    const wb = XLSX.utils.book_new();
    const annualRows = fieldSeries.flatMap((s) =>
      s.annual.map((a) => ({
        แหล่งผลิต: s.name,
        ปี: a.year,
        จำนวนเดือนที่มีข้อมูล: a.months,
        [`อัตราเฉลี่ย (${cfg.unit})`]: a.averageRate ?? "",
        [`ปริมาณสะสม (${cfg.volumeUnit})`]: a.volume / cfg.volumeDivisor,
      })),
    );
    const monthlyRows = timeline.map((p, index) => {
      const row: Record<string, string | number> = { ปี: p.year, เดือน: p.month };
      fieldSeries.forEach((s) => {
        row[`${s.name} (${cfg.unit})`] = s.monthly[index] ?? "";
      });
      return row;
    });
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(annualRows), "รายปี");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(monthlyRows), "รายเดือน");
    XLSX.writeFile(wb, `PTIT_Field_Tracker_${metric}_${fromYear}-${toYear}.xlsx`);
  };

  const selectClass =
    "min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100";
  const segmentClass = (active: boolean) =>
    `min-h-11 rounded-lg px-3 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-600 ${
      active
        ? "bg-white text-sky-800 shadow-sm dark:bg-slate-800 dark:text-sky-300"
        : "text-slate-600 hover:text-slate-950 dark:text-slate-400 dark:hover:text-white"
    }`;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">
          PTIT FOCUS STATISTICS · FIELD TRACKER
        </p>
        <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">
          ติดตามการผลิตรายแหล่ง ต่อเนื่องหลายปี
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          เลือกแหล่งผลิตได้สูงสุด {MAX_FIELDS} แหล่ง เพื่อดูแนวโน้มรายเดือนหรือรายปีตั้งแต่ปี {years[0]} · ข้อมูลจาก DMF / DEDP
        </p>
      </div>

      {/* Filters: one row above everything they scope */}
      <section aria-label="ตัวเลือกการติดตาม" className="glass-panel flex flex-wrap items-center gap-3 p-4">
        <label className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
          ตั้งแต่ปี
          <select className={selectClass} value={fromYear} onChange={(e) => setFromYear(Math.min(Number(e.target.value), toYear))}>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
          ถึงปี
          <select className={selectClass} value={toYear} onChange={(e) => setToYear(Math.max(Number(e.target.value), fromYear))}>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>
        <div role="group" aria-label="ตัวชี้วัด" className="inline-flex flex-wrap rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900">
          {(Object.keys(TRACKER_METRICS) as TrackerMetric[]).map((key) => (
            <button key={key} type="button" aria-pressed={metric === key} onClick={() => setMetric(key)} className={segmentClass(metric === key)}>
              {TRACKER_METRICS[key].label}
            </button>
          ))}
        </div>
        <div role="group" aria-label="ความละเอียด" className="inline-flex rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900">
          <button type="button" aria-pressed={granularity === "monthly"} onClick={() => setGranularity("monthly")} className={segmentClass(granularity === "monthly")}>
            รายเดือน
          </button>
          <button type="button" aria-pressed={granularity === "annual"} onClick={() => setGranularity("annual")} className={segmentClass(granularity === "annual")}>
            เฉลี่ยรายปี
          </button>
        </div>
        <div role="group" aria-label="การรวมชื่อแหล่ง" className="inline-flex rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900">
          <button type="button" aria-pressed={useGroups} onClick={() => toggleGroups(true)} className={segmentClass(useGroups)}>
            รวมตาม Mapping
          </button>
          <button type="button" aria-pressed={!useGroups} onClick={() => toggleGroups(false)} className={segmentClass(!useGroups)}>
            ชื่อตาม DMF
          </button>
        </div>
      </section>

      {/* Field picker */}
      <section aria-label="เลือกแหล่งผลิต" className="glass-panel space-y-3 p-4">
        <div className="flex flex-wrap items-center gap-2">
          {fieldSeries.map((s) => (
            <span
              key={s.name}
              title={isMergedGroup(s.name) ? `รวม: ${groupMembers.get(s.name)?.join(", ")}` : undefined}
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-slate-200 bg-white pl-3 pr-1 text-sm font-semibold text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            >
              <span aria-hidden="true" className="inline-block h-0.5 w-4 rounded" style={{ background: s.color }} />
              {s.name}
              {isMergedGroup(s.name) && (
                <span className="text-xs font-normal text-slate-500 dark:text-slate-400">({groupMembers.get(s.name)?.length} ชื่อ)</span>
              )}
              <button
                type="button"
                onClick={() => removeField(s.name)}
                aria-label={`เอา ${s.name} ออก`}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
            </span>
          ))}
          {selected.length === 0 && rangeLoaded && (
            <span className="text-sm text-slate-500 dark:text-slate-400">ยังไม่ได้เลือกแหล่งผลิต</span>
          )}
        </div>

        <div className="relative max-w-md">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={selected.length >= MAX_FIELDS || !rangeLoaded}
            placeholder={selected.length >= MAX_FIELDS ? `เลือกครบ ${MAX_FIELDS} แหล่งแล้ว` : "ค้นหาชื่อแหล่งหรือผู้ดำเนินการ…"}
            aria-label="ค้นหาแหล่งผลิต"
            className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>

        <p className="text-xs text-slate-500 dark:text-slate-400">
          {useGroups
            ? "รวมตาม Mapping: ชื่อแหล่งที่ทีม PTIT ยืนยันว่าเป็นกลุ่มเดียวกัน (เปลี่ยนชื่อ/สะกดต่าง/รวม/แยกเมื่อเปลี่ยนสัมปทาน) จะแสดงเป็นเส้นเดียว · ดูรายละเอียดในตาราง Mapping ด้านล่าง"
            : "ชื่อตาม DMF: แสดงตามชื่อที่ DMF รายงานในแต่ละปี — บางแหล่งเปลี่ยนชื่อหรือแยกย่อยเมื่อเปลี่ยนสัมปทาน (เช่น ปี 2559 และ 2565–2566) เส้นจึงอาจขาดช่วง"}
        </p>

        {selected.length < MAX_FIELDS && rangeLoaded && (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((f) => (
              <button
                key={f.name}
                type="button"
                onClick={() => addField(f.name)}
                title={`${isMergedGroup(f.name) ? `รวม: ${groupMembers.get(f.name)?.join(", ")} · ` : ""}${f.operators.join(", ") || "ยังไม่ระบุผู้ดำเนินการ"} · มีข้อมูลปี ${f.firstYear}–${f.lastYear}`}
                className="inline-flex min-h-11 items-center gap-1.5 rounded-full border border-dashed border-slate-300 px-3 text-sm text-slate-700 hover:border-sky-500 hover:text-sky-800 dark:border-slate-700 dark:text-slate-300 dark:hover:text-sky-300"
              >
                <Plus aria-hidden="true" className="h-3.5 w-3.5" />
                {f.name}
                <span className="text-xs text-slate-400">{f.region === "Onshore" ? "บนบก" : "ในทะเล"}</span>
              </button>
            ))}
            {suggestions.length === 0 && (
              <span className="text-sm text-slate-500 dark:text-slate-400">ไม่พบแหล่งที่ตรงกับคำค้น</span>
            )}
          </div>
        )}
      </section>

      {!rangeLoaded && pendingCount === 0 ? (
        <div role="alert" className="glass-panel flex flex-wrap items-center gap-3 p-6 text-sm font-semibold text-amber-900 dark:text-amber-300">
          โหลดข้อมูลบางปีไม่สำเร็จ
          <button
            type="button"
            onClick={() => ensureYears(rangeYears)}
            className="min-h-11 rounded-lg border border-amber-300 px-3 hover:bg-amber-50 dark:border-amber-700 dark:hover:bg-amber-950/50"
          >
            ลองใหม่
          </button>
        </div>
      ) : !rangeLoaded || pendingCount > 0 ? (
        <div role="status" className="glass-panel flex items-center gap-3 p-6 text-sm font-semibold text-sky-800 dark:text-sky-300">
          <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          กำลังโหลดข้อมูลปี {fromYear}–{toYear} ({rangeYears.filter((y) => loadedYears.has(y)).length}/{rangeYears.length} ปี)…
        </div>
      ) : (
        <>
          <section className="glass-panel p-5">
            <div className="mb-3 flex flex-col gap-1 border-b border-slate-200/80 pb-3 dark:border-slate-800">
              <h3 className="text-sm font-extrabold text-slate-900 dark:text-white">
                {cfg.label} {granularity === "monthly" ? "รายเดือน" : "เฉลี่ยรายปี"} · {cfg.unit} · ปี {fromYear}–{toYear}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {granularity === "monthly"
                  ? "เส้นขาดช่วง = เดือนที่แหล่งนั้นไม่มีในรายงาน DMF"
                  : `ค่าเฉลี่ยถ่วงตามจำนวนวัน (เดือนที่ไม่มีรายงานนับเป็น 0)${latestPartial ? ` · ปี ${toYear} เป็นค่าสะสมถึงเดือนล่าสุด` : ""}`}
              </p>
            </div>
            {fieldSeries.length > 0 ? (
              <FieldTrendChart points={chartPoints} series={chartSeries} unit={cfg.unit} decimals={decimals} />
            ) : (
              <p className="py-16 text-center text-sm text-slate-500">เลือกแหล่งผลิตด้านบนเพื่อแสดงกราฟ</p>
            )}
          </section>

          {fieldSeries.length > 0 && (
            <section className="glass-panel p-5">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-sm font-extrabold text-slate-900 dark:text-white">ตารางเฉลี่ยรายปี · {cfg.unit}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    ปริมาณสะสมทั้งช่วงหน่วย {cfg.volumeUnit}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={exportExcel}
                  className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-sky-700 px-4 text-sm font-semibold text-white hover:bg-sky-800"
                >
                  <Download aria-hidden="true" className="h-4 w-4" />
                  ส่งออก Excel
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-right text-sm tabular-nums">
                  <thead>
                    <tr className="border-b border-slate-200 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
                      <th scope="col" className="sticky left-0 bg-white px-3 py-2 text-left dark:bg-slate-950">แหล่งผลิต</th>
                      {rangeYears.map((y) => (
                        <th key={y} scope="col" className="px-3 py-2">
                          {y}
                          {monthsIndex[String(y)]?.length !== 12 && <span className="block text-[10px] font-normal">YTD</span>}
                        </th>
                      ))}
                      <th scope="col" className="px-3 py-2">สะสม ({cfg.volumeUnit})</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fieldSeries.map((s) => (
                      <tr key={s.name} className="border-b border-slate-100 dark:border-slate-800/70">
                        <th scope="row" className="sticky left-0 bg-white px-3 py-2 text-left font-semibold text-slate-800 dark:bg-slate-950 dark:text-slate-100">
                          <span className="flex items-center gap-2 whitespace-nowrap">
                            <span aria-hidden="true" className="inline-block h-0.5 w-3 rounded" style={{ background: s.color }} />
                            {s.name}
                          </span>
                        </th>
                        {s.annual.map((a) => (
                          <td key={a.year} className="px-3 py-2 text-slate-700 dark:text-slate-300">{fmt(a.averageRate)}</td>
                        ))}
                        <td className="px-3 py-2 font-bold text-slate-900 dark:text-white">
                          {formatNumber(s.annual.reduce((sum, a) => sum + a.volume, 0) / cfg.volumeDivisor, 2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}

      <FieldMappingReference rows={mappingRows} generated={mappingGenerated} />
    </div>
  );
}
