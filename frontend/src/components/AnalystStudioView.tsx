"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  Check,
  Download,
  Link2,
  Loader2,
  Pencil,
  Search,
  Split,
  Star,
  X,
} from "lucide-react";
import * as XLSX from "xlsx";
import { ProductionRecord } from "@/types/hydrocarbon";
import {
  FieldGroupRow,
  TRACKER_METRICS,
  TrackerMetric,
  buildTimeline,
  confirmedGroupLookup,
  fieldKey,
} from "@/lib/field-tracker";
import {
  GROUP_PRESETS,
  GroupPreset,
  Granularity,
  STUDIO_HASH_KEY,
  STUDIO_STORAGE_KEY,
  StudioField,
  StudioState,
  ValueMode,
  buildStudioCatalog,
  groupMonthlySeries,
  isStudioState,
  orderGroups,
  presetAssignment,
  rangeSummary,
  regionLabel,
  sumSeries,
  toPeriods,
} from "@/lib/analyst-studio";
import { clearHash, fromBase64Url, loadCustomGroups, toBase64Url } from "@/lib/custom-groups";
import { FieldTrendChart } from "@/components/FieldTrendChart";
import { formatInteger, formatNumber } from "@/lib/utils";

// Categorical slots 1–8 (validated palette, adjacent pairs); a group keeps its slot while shown
const SERIES_COLORS = {
  light: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
  dark: ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
};
const MAX_SHOWN = SERIES_COLORS.light.length;
const DEFAULT_SPAN = 10;
const DEFAULT_FIELDS = 10;

const segBtn = (active: boolean) =>
  `min-h-11 rounded-lg px-3 text-sm font-semibold transition-colors ${
    active
      ? "bg-white text-sky-800 shadow-sm dark:bg-slate-800 dark:text-sky-300"
      : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
  }`;
const segWrap = "inline-flex flex-wrap rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900";
const selectCls =
  "min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100";
const btnSecondary =
  "inline-flex min-h-11 items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 hover:border-sky-500 hover:text-sky-800 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:text-sky-300";
const btnPrimary =
  "inline-flex min-h-11 items-center gap-1.5 rounded-xl bg-sky-700 px-4 text-sm font-bold text-white hover:bg-sky-800 disabled:opacity-50 dark:bg-sky-600 dark:hover:bg-sky-500";

interface AnalystStudioViewProps {
  records: ProductionRecord[];
  monthsIndex: Record<string, number[]>;
  ensureYears: (years: number[]) => Promise<void>;
  loadedYears: Set<number>;
  pendingCount: number;
  theme: "light" | "dark";
  mappingRows: FieldGroupRow[];
}

function StepHeading({ n, title, hint }: { n: number; title: string; hint?: string }) {
  return (
    <div className="flex items-start gap-3">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-700 text-sm font-black text-white dark:bg-sky-600">
        {n}
      </span>
      <div>
        <h3 className="text-lg font-extrabold text-slate-950 dark:text-white">{title}</h3>
        {hint && <p className="text-sm text-slate-600 dark:text-slate-400">{hint}</p>}
      </div>
    </div>
  );
}

function readInitialState(): { state: StudioState | null; fromLink: boolean } {
  try {
    const match = window.location.hash.match(new RegExp(`${STUDIO_HASH_KEY}=([^&]+)`));
    if (match) {
      const parsed = JSON.parse(fromBase64Url(match[1]));
      if (isStudioState(parsed)) return { state: parsed, fromLink: true };
    }
  } catch {
    // broken link: fall through to the saved state
  }
  try {
    const raw = window.localStorage.getItem(STUDIO_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : null;
    if (isStudioState(parsed)) return { state: parsed, fromLink: false };
  } catch {
    // storage blocked
  }
  return { state: null, fromLink: false };
}

export function AnalystStudioView({
  records,
  monthsIndex,
  ensureYears,
  loadedYears,
  pendingCount,
  theme,
  mappingRows,
}: AnalystStudioViewProps) {
  const years = useMemo(
    () => Object.keys(monthsIndex).map(Number).filter(Number.isFinite).sort((a, b) => a - b),
    [monthsIndex],
  );
  const firstYear = years[0];
  const latestYear = years[years.length - 1];

  const [fromYear, setFromYear] = useState(Math.max(firstYear, latestYear - DEFAULT_SPAN + 1));
  const [toYear, setToYear] = useState(latestYear);
  const [metric, setMetric] = useState<TrackerMetric>("boed");
  const [granularity, setGranularity] = useState<Granularity>("annual");
  const [mode, setMode] = useState<ValueMode>("rate");
  /** field → group; null until the defaults (or a saved analysis) are applied */
  const [assign, setAssign] = useState<Record<string, string> | null>(null);
  /** index = colour slot, "" = free slot */
  const [shown, setShown] = useState<string[]>([]);
  const [preset, setPreset] = useState<GroupPreset | "custom">("mapping");
  const [notice, setNotice] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Step 1 filters
  const [query, setQuery] = useState("");
  const [regionFilter, setRegionFilter] = useState("");
  const [blockFilter, setBlockFilter] = useState("");
  const [operatorFilter, setOperatorFilter] = useState("");

  // Step 2 grouping
  const [picked, setPicked] = useState<string[]>([]);
  const [newGroupName, setNewGroupName] = useState("");
  const [renaming, setRenaming] = useState<{ group: string; value: string } | null>(null);

  // Step 3
  const [transpose, setTranspose] = useState(false);

  const mappingLookup = useMemo(() => confirmedGroupLookup(mappingRows), [mappingRows]);
  const palette = SERIES_COLORS[theme];

  // ---- Restore a shared link or the last analysis in this browser ----
  useEffect(() => {
    const { state, fromLink } = readInitialState();
    if (state) {
      const clamp = (y: number) => Math.min(Math.max(y, firstYear), latestYear);
      setFromYear(clamp(Math.min(state.from, state.to)));
      setToYear(clamp(Math.max(state.from, state.to)));
      setMetric(state.metric);
      setGranularity(state.granularity);
      setMode(state.mode);
      setAssign(state.assign);
      setShown(state.shown.slice(0, MAX_SHOWN));
      setPreset("custom");
      if (fromLink) {
        clearHash();
        setNotice("เปิดการวิเคราะห์จากลิงก์ที่แชร์มาแล้ว — แก้ไขต่อได้เลย (ไม่กระทบของคนที่แชร์)");
      }
    }
    setHydrated(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Keep the current analysis in this browser
  useEffect(() => {
    if (!hydrated || assign === null) return;
    try {
      const state: StudioState = { from: fromYear, to: toYear, metric, granularity, mode, assign, shown };
      window.localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify(state));
    } catch {
      // ignore
    }
  }, [hydrated, fromYear, toYear, metric, granularity, mode, assign, shown]);

  // ---- Data for the year range ----
  const rangeYears = useMemo(() => years.filter((y) => y >= fromYear && y <= toYear), [years, fromYear, toYear]);
  useEffect(() => {
    ensureYears(rangeYears);
  }, [ensureYears, rangeYears]);
  const rangeLoaded = rangeYears.every((y) => loadedYears.has(y));

  const catalog = useMemo(
    () => (rangeLoaded ? buildStudioCatalog(records, fromYear, toYear, metric) : []),
    [records, fromYear, toYear, metric, rangeLoaded],
  );
  const timeline = useMemo(() => buildTimeline(monthsIndex, fromYear, toYear), [monthsIndex, fromYear, toYear]);

  const current = assign || {};
  const selectedFields = useMemo(() => catalog.filter((f) => current[f.name] !== undefined), [catalog, current]);
  const outOfRange = Object.keys(current).length - selectedFields.length;
  const groups = useMemo(() => orderGroups(current, selectedFields), [current, selectedFields]);
  const membersOf = useMemo(() => {
    const members = new Map<string, StudioField[]>();
    selectedFields.forEach((f) => members.set(current[f.name], [...(members.get(current[f.name]) || []), f]));
    return members;
  }, [selectedFields, current]);

  const topShown = (groupList: string[]) => groupList.slice(0, MAX_SHOWN);

  // First visit: the ten largest fields, grouped by PTIT's confirmed mapping
  useEffect(() => {
    if (hydrated && assign === null && catalog.length > 0) {
      const initial = catalog.slice(0, DEFAULT_FIELDS);
      const next = presetAssignment(initial, "mapping", mappingLookup);
      setAssign(next);
      setShown(topShown(orderGroups(next, initial)));
    }
  }, [hydrated, assign, catalog, mappingLookup]);

  // ---- Step 1: choosing fields ----
  const blockOptions = useMemo(
    () => Array.from(new Set(catalog.flatMap((f) => f.blocks))).sort((a, b) => a.localeCompare(b, "th")),
    [catalog],
  );
  const operatorOptions = useMemo(
    () => Array.from(new Set(catalog.flatMap((f) => f.operators))).sort((a, b) => a.localeCompare(b, "th")),
    [catalog],
  );
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return catalog.filter(
      (f) =>
        (!regionFilter || f.region === regionFilter) &&
        (!blockFilter || f.blocks.includes(blockFilter)) &&
        (!operatorFilter || f.operators.includes(operatorFilter)) &&
        (!q ||
          f.name.toLowerCase().includes(q) ||
          f.blocks.some((b) => b.toLowerCase().includes(q)) ||
          f.operators.some((o) => o.toLowerCase().includes(q))),
    );
  }, [catalog, query, regionFilter, blockFilter, operatorFilter]);
  const totalVolume = useMemo(() => catalog.reduce((sum, f) => sum + f.volume, 0), [catalog]);

  const groupForNewField = (f: StudioField) =>
    preset === "custom" ? f.name : presetAssignment([f], preset, mappingLookup)[f.name];

  const addFields = (fields: StudioField[]) => {
    const next = { ...current };
    fields.forEach((f) => {
      if (next[f.name] === undefined) next[f.name] = groupForNewField(f);
    });
    applyAssign(next);
  };
  const removeFields = (names: string[]) => {
    const next = { ...current };
    names.forEach((name) => delete next[name]);
    applyAssign(next);
    setPicked((p) => p.filter((n) => !names.includes(n)));
  };
  const toggleField = (f: StudioField) => (current[f.name] === undefined ? addFields([f]) : removeFields([f.name]));

  /** Set the assignment; groups that disappeared free their chart slot, new groups get one if free. */
  const applyAssign = (next: Record<string, string>, renamed?: [string, string]) => {
    const alive = new Set(Object.values(next));
    setAssign(next);
    setShown((slots) => {
      let updated = slots.map((g) => (renamed && g === renamed[0] ? renamed[1] : g));
      updated = updated.map((g, i) => (g && alive.has(g) && updated.indexOf(g) === i ? g : ""));
      const present = new Set(updated.filter(Boolean));
      Array.from(alive)
        .filter((g) => !present.has(g) && !Object.values(current).includes(g))
        .forEach((g) => {
          const free = updated.indexOf("");
          if (free >= 0) updated[free] = g;
          else if (updated.length < MAX_SHOWN) updated.push(g);
        });
      while (updated.length && updated[updated.length - 1] === "") updated.pop();
      return updated;
    });
  };

  // ---- Step 2: grouping ----
  const applyPreset = (p: GroupPreset) => {
    const next = presetAssignment(selectedFields, p, mappingLookup);
    setAssign(next);
    setShown(topShown(orderGroups(next, selectedFields)));
    setPreset(p);
    setPicked([]);
  };

  const customGroups = useMemo(() => (hydrated ? loadCustomGroups() : []), [hydrated]);
  const applyMyGroups = () => {
    const next = { ...current };
    const byName = new Map(catalog.map((f) => [f.name, f]));
    let added = 0;
    customGroups.forEach((g) =>
      g.members.forEach((member) => {
        if (byName.has(member)) {
          next[member] = g.name;
          added++;
        }
      }),
    );
    const fields = catalog.filter((f) => next[f.name] !== undefined);
    setAssign(next);
    setShown(topShown(orderGroups(next, fields)));
    setPreset("custom");
    setNotice(added ? `ใช้ "กลุ่มของฉัน" จากหน้าติดตามรายแหล่งแล้ว (${added} แหล่ง)` : "กลุ่มของฉันไม่มีแหล่งที่มีข้อมูลในช่วงปีนี้");
  };

  const togglePick = (name: string) =>
    setPicked((p) => (p.includes(name) ? p.filter((n) => n !== name) : [...p, name]));

  const moveTo = (names: string[], group: string) => {
    const target = group.trim();
    if (!target || names.length === 0) return;
    const next = { ...current };
    names.forEach((name) => (next[name] = target));
    applyAssign(next);
    setPreset("custom");
    setPicked([]);
    setNewGroupName("");
  };

  const splitPicked = () => {
    const next = { ...current };
    picked.forEach((name) => (next[name] = name));
    applyAssign(next);
    setPreset("custom");
    setPicked([]);
  };

  const splitGroup = (group: string) => {
    const next = { ...current };
    (membersOf.get(group) || []).forEach((f) => (next[f.name] = f.name));
    applyAssign(next);
    setPreset("custom");
  };

  const commitRename = () => {
    if (!renaming) return;
    const name = renaming.value.trim();
    setRenaming(null);
    if (!name || name === renaming.group) return;
    if (groups.includes(name) && !window.confirm(`มีกลุ่มชื่อ "${name}" อยู่แล้ว — รวมสองกลุ่มนี้เข้าด้วยกัน?`)) return;
    const next = { ...current };
    Object.keys(next).forEach((field) => {
      if (next[field] === renaming.group) next[field] = name;
    });
    applyAssign(next, groups.includes(name) ? undefined : [renaming.group, name]);
    setPreset("custom");
  };

  const toggleShown = (group: string) =>
    setShown((slots) => {
      const index = slots.indexOf(group);
      if (index >= 0) {
        const updated = [...slots];
        updated[index] = "";
        while (updated.length && updated[updated.length - 1] === "") updated.pop();
        return updated;
      }
      // A slot is free when empty or held by a group that no longer exists in this range
      const free = slots.findIndex((g) => !g || !groups.includes(g));
      if (free >= 0) return slots.map((g, i) => (i === free ? group : g));
      return slots.length < MAX_SHOWN ? [...slots, group] : slots;
    });
  const shownCount = shown.filter((g) => g && groups.includes(g)).length;
  const colorOf = (group: string) => {
    const slot = shown.indexOf(group);
    return slot >= 0 ? palette[slot] : null;
  };

  // ---- Step 3: results ----
  const monthlyByGroup = useMemo(
    () => (rangeLoaded && assign ? groupMonthlySeries(records, assign, timeline, metric) : new Map<string, (number | null)[]>()),
    [records, assign, timeline, metric, rangeLoaded],
  );
  const groupSummary = useMemo(() => {
    const summary = new Map<string, { averageRate: number; volume: number }>();
    monthlyByGroup.forEach((values, group) => summary.set(group, rangeSummary(values, timeline, metric)));
    return summary;
  }, [monthlyByGroup, timeline, metric]);

  const pivot = useMemo(() => {
    const empty = new Array(timeline.length).fill(null);
    const rows = groups.map((group) => {
      const result = toPeriods(monthlyByGroup.get(group) || empty, timeline, granularity, mode, metric);
      return { group, values: result.values, periods: result.periods };
    });
    const periods = rows[0]?.periods || toPeriods(empty, timeline, granularity, mode, metric).periods;
    const total = sumSeries(rows.map((r) => r.values), periods.length);
    return { rows, periods, total };
  }, [groups, monthlyByGroup, timeline, granularity, mode, metric]);

  const spec = TRACKER_METRICS[metric];
  const unit = mode === "rate" ? spec.unit : spec.volumeUnit;
  const decimals = mode === "volume" ? 3 : metric === "gas" ? 2 : 0;
  const fmt = (v: number | null) => (v === null ? "–" : decimals ? formatNumber(v, decimals) : formatInteger(v));

  const chartSeries = shown
    .map((group, slot) => ({ group, slot }))
    .filter(({ group }) => group && groups.includes(group))
    .map(({ group, slot }) => ({
      name: group,
      color: palette[slot],
      values: pivot.rows.find((r) => r.group === group)?.values || [],
    }));

  const shareCurrent = async () => {
    if (!assign) return;
    const state: StudioState = { from: fromYear, to: toYear, metric, granularity, mode, assign, shown };
    const url = new URL(window.location.href);
    url.hash = `${STUDIO_HASH_KEY}=${toBase64Url(JSON.stringify(state))}`;
    try {
      await navigator.clipboard.writeText(url.toString());
      setNotice("คัดลอกลิงก์แล้ว — คนที่เปิดลิงก์จะเห็นการจัดกลุ่มและตารางชุดเดียวกันนี้");
    } catch {
      window.prompt("คัดลอกลิงก์นี้เพื่อแชร์การวิเคราะห์:", url.toString());
    }
  };

  const downloadExcel = () => {
    const round = (v: number | null) => (v === null ? null : Math.round(v * 10000) / 10000);
    const valueLabel = mode === "rate" ? `อัตราการผลิตเฉลี่ย (${spec.unit})` : `ปริมาณการผลิตรวม (${spec.volumeUnit})`;
    const info = [
      ["ที่มา", "กรมเชื้อเพลิงธรรมชาติ (DMF) — จัดกลุ่มโดยผู้ใช้ในห้องวิเคราะห์ PTIT"],
      ["ตัวชี้วัด", `${spec.label} · ${valueLabel}`],
      ["ช่วงเวลา", `${fromYear}–${toYear} · ${granularity === "monthly" ? "รายเดือน" : "รายปี"}`],
      [],
    ];
    const header = ["กลุ่ม", ...pivot.periods.map((p) => p.label)];
    const body = pivot.rows.map((r) => [r.group, ...r.values.map(round)]);
    const totalRow = ["รวมทุกกลุ่ม", ...pivot.total.map(round)];
    const table = transpose
      ? header.map((_, col) => [header[col], ...body.map((row) => row[col]), totalRow[col]])
      : [header, ...body, totalRow];
    const book = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(book, XLSX.utils.aoa_to_sheet([...info, ...table]), "ตารางผลลัพธ์");

    const mappingSheet = [
      ["กลุ่ม", "แหล่ง (ชื่อตาม DMF)", "พื้นที่", "แปลงที่พบ", "ผู้ดำเนินการ", "ปีแรกที่พบ", "ปีล่าสุดที่พบ"],
      ...groups.flatMap((group) =>
        (membersOf.get(group) || []).map((f) => [
          group,
          f.name,
          regionLabel(f.region),
          f.blocks.join(", "),
          f.operators.join(", "),
          f.firstYear,
          f.lastYear,
        ]),
      ),
    ];
    XLSX.utils.book_append_sheet(book, XLSX.utils.aoa_to_sheet(mappingSheet), "การจัดกลุ่ม");

    const metricKeys = Object.values(TRACKER_METRICS);
    const raw = [
      ["ปี", "ลำดับเดือน", "เดือน", "กลุ่ม", "แหล่ง (ชื่อตาม DMF)", "แปลง", "พื้นที่", "ผู้ดำเนินการ", ...metricKeys.map((m) => `${m.label} (${m.unit})`)],
      ...records
        .filter((r) => {
          const y = Number(r.ปี);
          return y >= fromYear && y <= toYear && current[fieldKey(r)] !== undefined;
        })
        .sort((a, b) => Number(a.ปี) - Number(b.ปี) || Number(a.ลำดับเดือน) - Number(b.ลำดับเดือน))
        .map((r) => [
          Number(r.ปี),
          Number(r.ลำดับเดือน),
          r.เดือน,
          current[fieldKey(r)],
          fieldKey(r),
          r.แปลง_ไฟล์ดิบ,
          regionLabel(r.PTIT_Region),
          r.ผู้ดำเนินการ,
          ...metricKeys.map((m) => round(Number(r[m.column]) || 0)),
        ]),
    ];
    XLSX.utils.book_append_sheet(book, XLSX.utils.aoa_to_sheet(raw), "ข้อมูลรายเดือน (ดิบ)");
    XLSX.writeFile(book, `PTIT_วิเคราะห์การผลิต_${fromYear}-${toYear}.xlsx`);
  };

  const loading = !rangeLoaded || pendingCount > 0;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">Analyst Studio</p>
        <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">
          ห้องวิเคราะห์ข้อมูลการผลิต
        </h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600 dark:text-slate-400">
          เลือกแหล่งผลิต → จัดกลุ่มและตั้งชื่อเอง → ได้กราฟและตารางรายเดือน/รายปีทันที ไม่ต้องทำ Pivot หรือ clean ข้อมูลเอง
          · ระบบจำงานล่าสุดไว้ในเบราว์เซอร์นี้ให้อัตโนมัติ
        </p>
      </div>

      {notice && (
        <div role="status" className="flex items-start justify-between gap-3 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-900 dark:border-sky-900 dark:bg-sky-950/50 dark:text-sky-200">
          <span>{notice}</span>
          <button type="button" onClick={() => setNotice(null)} aria-label="ปิดข้อความ" className="-m-2 p-2">
            <X aria-hidden="true" className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* ---------------- Step 1 ---------------- */}
      <section aria-label="ขั้นที่ 1 เลือกแหล่งผลิต" className="glass-panel space-y-4 p-4 sm:p-5">
        <StepHeading n={1} title="เลือกช่วงปีและแหล่งผลิต" hint="รายชื่อแหล่งเป็นชื่อตามที่ DMF เผยแพร่ในแต่ละช่วงเวลา เรียงจากผลิตมากไปน้อย" />

        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
            ตั้งแต่ปี
            <select className={selectCls} value={fromYear} onChange={(e) => setFromYear(Math.min(Number(e.target.value), toYear))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
            ถึงปี
            <select className={selectCls} value={toYear} onChange={(e) => setToYear(Math.max(Number(e.target.value), fromYear))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </label>
          {loading && (
            <span className="inline-flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" /> กำลังโหลดข้อมูลปี {fromYear}–{toYear}…
            </span>
          )}
        </div>

        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <div className="relative">
            <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="ค้นหาชื่อแหล่ง แปลง หรือบริษัท"
              aria-label="ค้นหาแหล่งผลิต"
              className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            />
          </div>
          <select aria-label="กรองตามพื้นที่" className={selectCls} value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)}>
            <option value="">ทุกพื้นที่</option>
            <option value="Onshore">บนบก</option>
            <option value="Offshore">ในทะเล</option>
          </select>
          <select aria-label="กรองตามแปลง" className={selectCls} value={blockFilter} onChange={(e) => setBlockFilter(e.target.value)}>
            <option value="">ทุกแปลง</option>
            {blockOptions.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
          <select aria-label="กรองตามผู้ดำเนินการ" className={selectCls} value={operatorFilter} onChange={(e) => setOperatorFilter(e.target.value)}>
            <option value="">ทุกผู้ดำเนินการ</option>
            {operatorOptions.map((o) => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button type="button" className={btnSecondary} disabled={filtered.length === 0} onClick={() => addFields(filtered)}>
            <Check aria-hidden="true" className="h-4 w-4" /> เลือกทั้งหมดที่แสดง ({filtered.length})
          </button>
          <button
            type="button"
            className={btnSecondary}
            disabled={selectedFields.length === 0}
            onClick={() => removeFields(filtered.filter((f) => current[f.name] !== undefined).map((f) => f.name))}
          >
            <X aria-hidden="true" className="h-4 w-4" /> เอาออกทั้งหมดที่แสดง
          </button>
          <span className="text-sm text-slate-600 dark:text-slate-400">
            เลือกแล้ว <b className="text-slate-900 dark:text-white">{selectedFields.length}</b> จาก {catalog.length} แหล่ง
            {outOfRange > 0 && ` · อีก ${outOfRange} แหล่งที่เลือกไว้ไม่มีข้อมูลในช่วงปีนี้`}
          </span>
        </div>

        <div className="max-h-[26rem] overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-800">
          <table className="w-full text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50 text-left text-xs font-bold text-slate-500 dark:bg-slate-900 dark:text-slate-400">
              <tr>
                <th scope="col" className="w-10 px-3 py-2"><span className="sr-only">เลือก</span></th>
                <th scope="col" className="px-2 py-2">แหล่ง (ชื่อตาม DMF)</th>
                <th scope="col" className="hidden px-2 py-2 md:table-cell">แปลง</th>
                <th scope="col" className="hidden px-2 py-2 lg:table-cell">ผู้ดำเนินการ</th>
                <th scope="col" className="px-2 py-2">ปีที่มีข้อมูล</th>
                <th scope="col" className="px-3 py-2 text-right">สัดส่วนในช่วงนี้</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => {
                const checked = current[f.name] !== undefined;
                const share = totalVolume ? (f.volume / totalVolume) * 100 : 0;
                return (
                  <tr
                    key={f.name}
                    onClick={() => toggleField(f)}
                    className={`cursor-pointer border-t border-slate-100 dark:border-slate-800/80 ${
                      checked ? "bg-sky-50/80 dark:bg-sky-950/30" : "hover:bg-slate-50 dark:hover:bg-slate-900/60"
                    }`}
                  >
                    <td className="px-3 py-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleField(f)}
                        onClick={(e) => e.stopPropagation()}
                        aria-label={`เลือก ${f.name}`}
                        className="h-5 w-5 accent-sky-700"
                      />
                    </td>
                    <td className="px-2 py-2">
                      <div className="font-semibold text-slate-900 dark:text-white">{f.name}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {regionLabel(f.region)}
                        <span className="md:hidden"> · {f.latestBlock}</span>
                        {checked && current[f.name] !== f.name && <> · กลุ่ม: {current[f.name]}</>}
                      </div>
                    </td>
                    <td className="hidden px-2 py-2 text-slate-600 dark:text-slate-300 md:table-cell">{f.blocks.join(", ")}</td>
                    <td className="hidden px-2 py-2 text-slate-600 dark:text-slate-300 lg:table-cell">{f.operators.join(", ") || "–"}</td>
                    <td className="whitespace-nowrap px-2 py-2 tabular-nums text-slate-600 dark:text-slate-300">
                      {f.firstYear === f.lastYear ? f.firstYear : `${f.firstYear}–${f.lastYear}`}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums text-slate-700 dark:text-slate-200">
                      {share >= 0.05 ? `${formatNumber(share, 1)}%` : "<0.1%"}
                    </td>
                  </tr>
                );
              })}
              {!loading && filtered.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-3 py-6 text-center text-slate-500 dark:text-slate-400">ไม่พบแหล่งที่ตรงกับตัวกรอง</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* ---------------- Step 2 ---------------- */}
      <section aria-label="ขั้นที่ 2 จัดกลุ่ม" className="glass-panel space-y-4 p-4 sm:p-5">
        <StepHeading
          n={2}
          title="จัดกลุ่มแหล่ง"
          hint="กดปุ่มลัดด้านล่าง หรือคลิกเลือกแหล่ง (กดได้หลายอัน) แล้วรวมเป็นกลุ่มใหม่และตั้งชื่อเอง — แหล่งที่เปลี่ยนชื่อหรือถูกแยกตามสัมปทานก็รวมกลับเป็นเส้นเดียวได้"
        />

        <div className="flex flex-wrap gap-2" role="group" aria-label="จัดกลุ่มอัตโนมัติ">
          {GROUP_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              title={p.hint}
              disabled={selectedFields.length === 0}
              onClick={() => applyPreset(p.id)}
              className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-semibold disabled:opacity-50 ${
                preset === p.id
                  ? "border-sky-700 bg-sky-700 text-white dark:border-sky-500 dark:bg-sky-600"
                  : "border-slate-200 bg-white text-slate-700 hover:border-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
              }`}
            >
              {p.label}
            </button>
          ))}
          {customGroups.length > 0 && (
            <button type="button" onClick={applyMyGroups} className="inline-flex min-h-11 items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-4 text-sm font-semibold text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200">
              <Star aria-hidden="true" className="h-4 w-4" /> ใช้กลุ่มของฉัน ({customGroups.length})
            </button>
          )}
        </div>

        {picked.length > 0 && (
          <div className="sticky top-24 z-20 flex flex-wrap items-center gap-2 rounded-xl border border-sky-300 bg-sky-50 p-3 shadow-md dark:border-sky-800 dark:bg-sky-950">
            <span className="text-sm font-bold text-sky-900 dark:text-sky-200">เลือก {picked.length} แหล่ง</span>
            <input
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && moveTo(picked, newGroupName)}
              placeholder="ตั้งชื่อกลุ่มใหม่ เช่น กลุ่มเอราวัณรวม"
              aria-label="ชื่อกลุ่มใหม่"
              className="min-h-11 min-w-0 flex-1 rounded-xl border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900 sm:max-w-xs"
            />
            <button type="button" className={btnPrimary} disabled={!newGroupName.trim()} onClick={() => moveTo(picked, newGroupName)}>
              รวมเป็นกลุ่มนี้
            </button>
            <select
              aria-label="ย้ายไปกลุ่มที่มีอยู่"
              className={selectCls}
              value=""
              onChange={(e) => e.target.value && moveTo(picked, e.target.value)}
            >
              <option value="">ย้ายไปกลุ่มที่มีอยู่…</option>
              {groups.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
            <button type="button" className={btnSecondary} onClick={splitPicked}>
              <Split aria-hidden="true" className="h-4 w-4" /> แยกเป็นรายแหล่ง
            </button>
            <button type="button" className={btnSecondary} onClick={() => removeFields(picked)}>
              นำออกจากการวิเคราะห์
            </button>
            <button type="button" className="min-h-11 px-2 text-sm font-semibold text-slate-600 underline dark:text-slate-300" onClick={() => setPicked([])}>
              ยกเลิก
            </button>
          </div>
        )}

        {groups.length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">{loading ? "กำลังโหลด…" : "ยังไม่ได้เลือกแหล่ง — เลือกในขั้นที่ 1 ก่อน"}</p>
        ) : (
          <div className="grid max-h-[32rem] gap-3 overflow-y-auto pr-1 md:grid-cols-2 xl:grid-cols-3">
            {groups.map((group) => {
              const members = membersOf.get(group) || [];
              const color = colorOf(group);
              const summary = groupSummary.get(group);
              const isShown = !!color;
              return (
                <article key={group} className="rounded-xl border border-slate-200 bg-white/70 p-3 dark:border-slate-800 dark:bg-slate-900/60">
                  <div className="flex items-start justify-between gap-2">
                    {renaming?.group === group ? (
                      <input
                        autoFocus
                        value={renaming.value}
                        onChange={(e) => setRenaming({ group, value: e.target.value })}
                        onBlur={commitRename}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") commitRename();
                          if (e.key === "Escape") setRenaming(null);
                        }}
                        aria-label="ชื่อกลุ่ม"
                        className="min-h-11 min-w-0 flex-1 rounded-lg border border-sky-400 bg-white px-2 text-sm font-bold dark:bg-slate-900"
                      />
                    ) : (
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span
                            aria-hidden="true"
                            className="inline-block h-1 w-4 shrink-0 rounded"
                            style={{ background: color || "transparent", outline: color ? "none" : "1px dashed #94a3b8" }}
                          />
                          <h4 className="truncate text-sm font-extrabold text-slate-900 dark:text-white" title={group}>{group}</h4>
                        </div>
                        <p className="mt-0.5 text-xs tabular-nums text-slate-500 dark:text-slate-400">
                          {members.length} แหล่ง
                          {summary && ` · เฉลี่ย ${fmtRate(summary.averageRate, metric)} ${spec.unit} · รวม ${formatNumber(summary.volume, 3)} ${spec.volumeUnit}`}
                        </p>
                      </div>
                    )}
                    <div className="flex shrink-0 items-center">
                      <button
                        type="button"
                        onClick={() => setRenaming({ group, value: group })}
                        aria-label={`แก้ชื่อกลุ่ม ${group}`}
                        title="แก้ชื่อกลุ่ม"
                        className="inline-flex h-11 w-11 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
                      >
                        <Pencil aria-hidden="true" className="h-4 w-4" />
                      </button>
                      {members.length > 1 && (
                        <button
                          type="button"
                          onClick={() => splitGroup(group)}
                          aria-label={`แยกกลุ่ม ${group} เป็นรายแหล่ง`}
                          title="แยกกลุ่มเป็นรายแหล่ง"
                          className="inline-flex h-11 w-11 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
                        >
                          <Split aria-hidden="true" className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {members.map((f) => {
                      const on = picked.includes(f.name);
                      return (
                        <button
                          key={f.name}
                          type="button"
                          aria-pressed={on}
                          onClick={() => togglePick(f.name)}
                          title={`${f.blocks.join(", ")} · ${f.firstYear}–${f.lastYear}`}
                          className={`inline-flex min-h-9 items-center rounded-full border px-2.5 text-xs font-semibold ${
                            on
                              ? "border-sky-700 bg-sky-700 text-white dark:border-sky-500 dark:bg-sky-600"
                              : "border-slate-200 bg-white text-slate-700 hover:border-sky-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
                          }`}
                        >
                          {on && <Check aria-hidden="true" className="mr-1 h-3 w-3" />}
                          {f.name}
                        </button>
                      );
                    })}
                  </div>
                  <label className="mt-2 flex min-h-9 cursor-pointer items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-300">
                    <input
                      type="checkbox"
                      checked={isShown}
                      disabled={!isShown && shownCount >= MAX_SHOWN}
                      onChange={() => toggleShown(group)}
                      className="h-4 w-4 accent-sky-700"
                    />
                    แสดงในกราฟ {!isShown && shownCount >= MAX_SHOWN && "(เต็ม 8 เส้น)"}
                  </label>
                </article>
              );
            })}
          </div>
        )}
      </section>

      {/* ---------------- Step 3 ---------------- */}
      <section aria-label="ขั้นที่ 3 ผลลัพธ์" className="glass-panel space-y-4 p-4 sm:p-5">
        <StepHeading n={3} title="ดูแนวโน้มและตาราง" hint="ตารางแสดงทุกกลุ่ม กราฟแสดงกลุ่มที่ติ๊ก “แสดงในกราฟ” (สูงสุด 8 เส้น)" />

        <div className="flex flex-wrap items-center gap-3">
          <div role="group" aria-label="ตัวชี้วัด" className={segWrap}>
            {(Object.keys(TRACKER_METRICS) as TrackerMetric[]).map((m) => (
              <button key={m} type="button" aria-pressed={metric === m} onClick={() => setMetric(m)} className={segBtn(metric === m)}>
                {TRACKER_METRICS[m].label}
              </button>
            ))}
          </div>
          <div role="group" aria-label="ความละเอียด" className={segWrap}>
            <button type="button" aria-pressed={granularity === "monthly"} onClick={() => setGranularity("monthly")} className={segBtn(granularity === "monthly")}>รายเดือน</button>
            <button type="button" aria-pressed={granularity === "annual"} onClick={() => setGranularity("annual")} className={segBtn(granularity === "annual")}>รายปี</button>
          </div>
          <div role="group" aria-label="ค่าที่แสดง" className={segWrap}>
            <button type="button" aria-pressed={mode === "rate"} onClick={() => setMode("rate")} className={segBtn(mode === "rate")}>เฉลี่ยต่อวัน ({spec.unit})</button>
            <button type="button" aria-pressed={mode === "volume"} onClick={() => setMode("volume")} className={segBtn(mode === "volume")}>ปริมาณรวม ({spec.volumeUnit})</button>
          </div>
        </div>

        {chartSeries.length > 0 ? (
          <div>
            <ul aria-label="คำอธิบายเส้นกราฟ" className="mb-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-700 dark:text-slate-300">
              {chartSeries.map((s) => (
                <li key={s.name} className="flex items-center gap-1.5">
                  <span aria-hidden="true" className="inline-block h-0.5 w-4 rounded" style={{ background: s.color }} />
                  {s.name}
                </li>
              ))}
            </ul>
            <FieldTrendChart
              points={pivot.periods.map((p) => ({ year: p.year, month: p.month }))}
              series={chartSeries}
              unit={unit}
              decimals={decimals}
            />
          </div>
        ) : (
          <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
            {loading ? "กำลังโหลดข้อมูล…" : "ติ๊ก “แสดงในกราฟ” ที่กลุ่มในขั้นที่ 2 เพื่อดูกราฟ"}
          </p>
        )}

        <div className="flex flex-wrap items-center justify-between gap-2">
          <h4 className="text-sm font-extrabold text-slate-900 dark:text-white">
            ตาราง{mode === "rate" ? "อัตราการผลิตเฉลี่ย" : "ปริมาณการผลิตรวม"} — {spec.label} ({unit}) {granularity === "monthly" ? "รายเดือน" : "รายปี"}
          </h4>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={btnSecondary} onClick={() => setTranspose((t) => !t)}>
              <ArrowLeftRight aria-hidden="true" className="h-4 w-4" /> สลับแถว/คอลัมน์
            </button>
            <button type="button" className={btnSecondary} disabled={!assign} onClick={shareCurrent}>
              <Link2 aria-hidden="true" className="h-4 w-4" /> คัดลอกลิงก์แชร์
            </button>
            <button type="button" className={btnPrimary} disabled={groups.length === 0} onClick={downloadExcel}>
              <Download aria-hidden="true" className="h-4 w-4" /> ดาวน์โหลด Excel
            </button>
          </div>
        </div>

        {groups.length > 0 && (
          <div className="max-h-[32rem] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800">
            <table className="w-full border-collapse text-sm tabular-nums">
              {transpose ? (
                <>
                  <thead className="sticky top-0 z-10 bg-slate-50 text-xs font-bold text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                    <tr>
                      <th scope="col" className="sticky left-0 z-20 bg-slate-50 px-3 py-2 text-left dark:bg-slate-900">ช่วงเวลา</th>
                      {pivot.rows.map((r) => (
                        <th key={r.group} scope="col" className="min-w-24 px-3 py-2 text-right">{r.group}</th>
                      ))}
                      <th scope="col" className="min-w-24 px-3 py-2 text-right text-slate-900 dark:text-white">รวม</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pivot.periods.map((p, i) => (
                      <tr key={p.label} className="border-t border-slate-100 dark:border-slate-800/80">
                        <th scope="row" className="sticky left-0 whitespace-nowrap bg-white px-3 py-1.5 text-left font-semibold text-slate-700 dark:bg-slate-950 dark:text-slate-200">{p.label}</th>
                        {pivot.rows.map((r) => (
                          <td key={r.group} className="px-3 py-1.5 text-right text-slate-700 dark:text-slate-300">{fmt(r.values[i])}</td>
                        ))}
                        <td className="px-3 py-1.5 text-right font-bold text-slate-900 dark:text-white">{fmt(pivot.total[i])}</td>
                      </tr>
                    ))}
                  </tbody>
                </>
              ) : (
                <>
                  <thead className="sticky top-0 z-10 bg-slate-50 text-xs font-bold text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                    <tr>
                      <th scope="col" className="sticky left-0 z-20 bg-slate-50 px-3 py-2 text-left dark:bg-slate-900">กลุ่ม</th>
                      {pivot.periods.map((p) => (
                        <th key={p.label} scope="col" className="whitespace-nowrap px-3 py-2 text-right">{p.label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {pivot.rows.map((r) => (
                      <tr key={r.group} className="border-t border-slate-100 dark:border-slate-800/80">
                        <th scope="row" className="sticky left-0 max-w-[14rem] truncate bg-white px-3 py-1.5 text-left font-semibold text-slate-700 dark:bg-slate-950 dark:text-slate-200" title={r.group}>{r.group}</th>
                        {r.values.map((v, i) => (
                          <td key={i} className="px-3 py-1.5 text-right text-slate-700 dark:text-slate-300">{fmt(v)}</td>
                        ))}
                      </tr>
                    ))}
                    <tr className="border-t-2 border-slate-300 dark:border-slate-700">
                      <th scope="row" className="sticky left-0 bg-white px-3 py-1.5 text-left font-extrabold text-slate-900 dark:bg-slate-950 dark:text-white">รวมทุกกลุ่ม</th>
                      {pivot.total.map((v, i) => (
                        <td key={i} className="px-3 py-1.5 text-right font-bold text-slate-900 dark:text-white">{fmt(v)}</td>
                      ))}
                    </tr>
                  </tbody>
                </>
              )}
            </table>
          </div>
        )}

        <p className="text-xs text-slate-500 dark:text-slate-400">
          “–” = DMF ไม่มีรายงานของกลุ่มนั้นในช่วงเวลานั้น · ค่าเฉลี่ยรายปีถ่วงน้ำหนักตามจำนวนวันของเดือนที่ DMF เผยแพร่แล้ว
          (ปีที่ยังไม่ครบ 12 เดือนจะระบุจำนวนเดือนไว้) · ไฟล์ Excel มี 3 ชีต: ตารางผลลัพธ์, การจัดกลุ่ม, ข้อมูลรายเดือนดิบสำหรับทำ Pivot ต่อ
        </p>
      </section>
    </div>
  );
}

function fmtRate(value: number, metric: TrackerMetric) {
  return metric === "gas" ? formatNumber(value, 1) : formatInteger(value);
}
