"use client";

import React, { useEffect, useMemo, useState } from "react";
import { CheckCircle2, ExternalLink, KeyRound, Loader2, LogOut, RotateCcw, Save, Search, TriangleAlert } from "lucide-react";
import * as XLSX from "xlsx";
import { FieldGroupRow, STATUS_CONFIRMED } from "@/lib/field-tracker";
import { ACTIONS_URL, NEW_TOKEN_URL, REPO, checkAccess, commitFiles, loadToken, readFile, storeToken } from "@/lib/github";

// Must match field_mapping.py (COLUMNS / RELATION_OPTIONS / STATUS_OPTIONS)
const COLUMNS: (keyof FieldGroupRow)[] = [
  "แหล่ง_ไฟล์ดิบ", "กลุ่มติดตาม", "ความสัมพันธ์", "สถานะ", "หมายเหตุ", "ปีที่พบในข้อมูล", "แปลงที่พบ", "พื้นที่", "แก้ไขล่าสุด",
];
const EDITABLE = ["กลุ่มติดตาม", "ความสัมพันธ์", "สถานะ", "หมายเหตุ"] as const;
type Editable = (typeof EDITABLE)[number];
const RELATION_OPTIONS = [
  "ชื่อเดิม (ไม่เปลี่ยน)",
  "สะกดต่าง / พิมพ์ต่าง",
  "เปลี่ยนชื่อ",
  "รวมเป็นกลุ่ม (หลายแหล่ง → 1 ชื่อ)",
  "แยกย่อย (1 ชื่อ → หลายแหล่ง)",
  "อื่นๆ (ดูหมายเหตุ)",
];
const STATUS_OPTIONS = ["ร่าง", STATUS_CONFIRMED];
const MAPPING_JSON = "field_group_mapping.json";
const MAPPING_XLSX = "field_group_mapping.xlsx";

type Edits = Record<string, Partial<Pick<FieldGroupRow, Editable>>>;

interface MappingEditorViewProps {
  /** Published rows (include auto columns and any DMF names added since the last save). */
  rows: FieldGroupRow[];
}

/** Official mapping editor for PTIT admins — commits field_group_mapping.json/.xlsx to GitHub. */
export function MappingEditorView({ rows }: MappingEditorViewProps) {
  const [token, setToken] = useState("");
  const [remember, setRemember] = useState(true);
  const [account, setAccount] = useState<{ login: string; canWrite: boolean } | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [base, setBase] = useState<FieldGroupRow[]>(rows);
  const [baseSha, setBaseSha] = useState<string | null>(null);
  const [edits, setEdits] = useState<Edits>({});
  const [picked, setPicked] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ทั้งหมด");
  const [onlyChanged, setOnlyChanged] = useState(false);
  const [bulkGroup, setBulkGroup] = useState("");
  const [commitNote, setCommitNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<{ url: string; count: number } | null>(null);

  const connect = async (value: string) => {
    if (!value.trim()) return;
    setConnecting(true);
    setError(null);
    try {
      const info = await checkAccess(value.trim());
      if (!info.canWrite) throw new Error(`บัญชี @${info.login} ไม่มีสิทธิ์เขียน repo ${REPO.owner}/${REPO.name}`);
      // Start from the file currently on GitHub so edits made since this page was built are not lost
      const live = await readFile(value.trim(), MAPPING_JSON);
      const liveRows = (JSON.parse(live.text).rows || []) as FieldGroupRow[];
      const liveByName = new Map(liveRows.map((r) => [r.แหล่ง_ไฟล์ดิบ, r]));
      setBase(rows.map((r) => ({ ...r, ...pickEditable(liveByName.get(r.แหล่ง_ไฟล์ดิบ)), แก้ไขล่าสุด: liveByName.get(r.แหล่ง_ไฟล์ดิบ)?.แก้ไขล่าสุด ?? r.แก้ไขล่าสุด })));
      setBaseSha(live.sha);
      setAccount(info);
      setToken(value.trim());
      if (remember) storeToken(value.trim());
    } catch (e) {
      setError(`เชื่อมต่อไม่สำเร็จ: ${(e as Error).message}`);
    } finally {
      setConnecting(false);
    }
  };

  useEffect(() => {
    const stored = loadToken();
    if (stored) connect(stored);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const disconnect = () => {
    storeToken(null);
    setAccount(null);
    setToken("");
    setBaseSha(null);
  };

  const current = (row: FieldGroupRow): FieldGroupRow => ({ ...row, ...edits[row.แหล่ง_ไฟล์ดิบ] });
  const isChanged = (row: FieldGroupRow) => {
    const e = edits[row.แหล่ง_ไฟล์ดิบ];
    return !!e && EDITABLE.some((k) => e[k] !== undefined && e[k] !== row[k]);
  };
  const changedRows = base.filter(isChanged);

  const setField = (name: string, key: Editable, value: string) =>
    setEdits((prev) => ({ ...prev, [name]: { ...prev[name], [key]: value } }));

  const groupNames = useMemo(() => Array.from(new Set(base.map((r) => current(r).กลุ่มติดตาม))).sort((a, b) => a.localeCompare(b, "th")),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [base, edits]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return base.filter((row) => {
      const r = current(row);
      if (onlyChanged && !isChanged(row)) return false;
      if (statusFilter !== "ทั้งหมด" && r.สถานะ !== statusFilter) return false;
      return !q || [r.แหล่ง_ไฟล์ดิบ, r.กลุ่มติดตาม, r.แปลงที่พบ].some((v) => v.toLowerCase().includes(q));
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [base, edits, query, statusFilter, onlyChanged]);

  const applyBulk = (key: Editable, value: string) => {
    if (!value) return;
    setEdits((prev) => {
      const next = { ...prev };
      picked.forEach((name) => (next[name] = { ...next[name], [key]: value }));
      return next;
    });
  };

  const save = async () => {
    if (!account || changedRows.length === 0) return;
    setSaving(true);
    setError(null);
    try {
      const live = await readFile(token, MAPPING_JSON);
      if (baseSha && live.sha !== baseSha) {
        throw new Error("ไฟล์ Mapping บน GitHub ถูกแก้ไขโดยคนอื่นหลังจากคุณเปิดหน้านี้ — กรุณาโหลดหน้าใหม่แล้วแก้อีกครั้ง");
      }
      const today = new Date().toISOString().slice(0, 10);
      const finalRows = base.map((row) => {
        const r = current(row);
        const out = Object.fromEntries(COLUMNS.map((c) => [c, String(r[c] ?? "")])) as unknown as FieldGroupRow;
        if (!out.กลุ่มติดตาม.trim()) out.กลุ่มติดตาม = out.แหล่ง_ไฟล์ดิบ;
        if (isChanged(row)) out.แก้ไขล่าสุด = today;
        return out;
      });
      const json = JSON.stringify({ columns: COLUMNS, rows: finalRows }, null, 2);
      const sheet = XLSX.utils.json_to_sheet(finalRows, { header: COLUMNS as string[] });
      sheet["!cols"] = [34, 34, 28, 12, 70, 22, 24, 14, 14].map((wch) => ({ wch }));
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, sheet, "Field_Group_Mapping");
      const xlsx = new Uint8Array(XLSX.write(wb, { type: "array", bookType: "xlsx" }) as ArrayBuffer);
      const summary = changedRows.slice(0, 8).map((r) => `- ${r.แหล่ง_ไฟล์ดิบ} → ${current(r).กลุ่มติดตาม} (${current(r).สถานะ})`).join("\n");
      const commit = await commitFiles(
        token,
        `mapping: update ${changedRows.length} field(s) via web editor (@${account.login})\n\n${commitNote ? `${commitNote}\n\n` : ""}${summary}${changedRows.length > 8 ? "\n- …" : ""}`,
        [
          { path: MAPPING_JSON, content: json },
          { path: MAPPING_XLSX, content: xlsx },
        ],
      );
      const after = await readFile(token, MAPPING_JSON);
      setBase(finalRows);
      setBaseSha(after.sha);
      setEdits({});
      setPicked([]);
      setCommitNote("");
      setSaved({ url: commit.html_url, count: changedRows.length });
    } catch (e) {
      setError(`บันทึกไม่สำเร็จ: ${(e as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  const inputClass =
    "min-h-11 w-full rounded-lg border border-slate-200 bg-white px-2 text-sm text-slate-800 disabled:bg-slate-50 disabled:text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-900/50";
  const readOnly = !account;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">PTIT FOCUS STATISTICS · ADMIN</p>
        <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">จัดการ Mapping แหล่งผลิต (ทางการ)</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600 dark:text-slate-400">
          กำหนดว่าชื่อแหล่งตาม DMF ชื่อใดนับเป็นกลุ่มเดียวกันต่อเนื่องข้ามปี · ใช้เฉพาะแถว <b>ยืนยันแล้ว</b> · บันทึกแล้วระบบจะ commit ไฟล์ขึ้น GitHub และอัปเดตเว็บให้ทุกคนภายในประมาณ 5 นาที
        </p>
      </div>

      {/* Connection */}
      <section aria-label="เชื่อมต่อ GitHub" className="glass-panel space-y-3 p-4">
        {account ? (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
              เชื่อมต่อแล้วในชื่อ @{account.login} · แก้ไขได้
            </span>
            <button type="button" onClick={disconnect} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-white dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900">
              <LogOut aria-hidden="true" className="h-4 w-4" />
              ออกจากระบบ (ลบ token จากเบราว์เซอร์นี้)
            </button>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              <KeyRound aria-hidden="true" className="mr-1 inline h-4 w-4" />
              ใส่ <b>GitHub fine-grained token</b> ที่มีสิทธิ์ <b>Contents: Read and write</b> เฉพาะ repo {REPO.owner}/{REPO.name} ·{" "}
              <a href={NEW_TOKEN_URL} target="_blank" rel="noreferrer" className="font-semibold text-sky-700 underline dark:text-sky-300">
                สร้าง token <ExternalLink aria-hidden="true" className="inline h-3 w-3" />
              </a>{" "}
              · token เก็บไว้ในเบราว์เซอร์นี้เท่านั้น
            </p>
            <form
              className="flex flex-wrap items-center gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                connect(token);
              }}
            >
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="github_pat_…"
                aria-label="GitHub token"
                autoComplete="off"
                className="min-h-11 min-w-64 flex-1 rounded-xl border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"
              />
              <label className="inline-flex min-h-11 items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="h-4 w-4" />
                จำไว้ในเบราว์เซอร์นี้
              </label>
              <button type="submit" disabled={connecting || !token.trim()} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-sky-700 px-4 text-sm font-semibold text-white hover:bg-sky-800 disabled:opacity-50">
                {connecting && <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />}
                เชื่อมต่อ
              </button>
            </form>
            <p className="text-xs text-slate-500 dark:text-slate-400">ยังไม่เชื่อมต่อ: ดูตารางได้ แต่แก้ไขไม่ได้</p>
          </>
        )}
        {error && (
          <p role="alert" className="flex items-start gap-2 rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:bg-amber-950/50 dark:text-amber-200">
            <TriangleAlert aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </p>
        )}
        {saved && (
          <p role="status" className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-200">
            บันทึก {saved.count} แถวขึ้น GitHub แล้ว ·{" "}
            <a href={saved.url} target="_blank" rel="noreferrer" className="font-semibold underline">ดู commit</a> ·{" "}
            <a href={ACTIONS_URL} target="_blank" rel="noreferrer" className="font-semibold underline">ดูสถานะการอัปเดตเว็บ</a> (ประมาณ 5 นาที)
          </p>
        )}
      </section>

      {/* Filters + bulk actions */}
      <section aria-label="ค้นหาและแก้หลายแถว" className="glass-panel flex flex-wrap items-center gap-3 p-4">
        <div className="relative min-w-60 flex-1">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ค้นหาชื่อแหล่ง กลุ่ม หรือแปลง…" aria-label="ค้นหา" className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm dark:border-slate-700 dark:bg-slate-900" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} aria-label="กรองสถานะ" className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900">
          {["ทั้งหมด", ...STATUS_OPTIONS].map((s) => <option key={s}>{s}</option>)}
        </select>
        <label className="inline-flex min-h-11 items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
          <input type="checkbox" checked={onlyChanged} onChange={(e) => setOnlyChanged(e.target.checked)} className="h-4 w-4" />
          เฉพาะที่แก้ไข ({changedRows.length})
        </label>
        {picked.length > 0 && !readOnly && (
          <div className="flex w-full flex-wrap items-center gap-2 rounded-xl bg-sky-50 p-2 dark:bg-sky-950/40">
            <span className="text-sm font-semibold text-sky-900 dark:text-sky-200">เลือก {picked.length} แถว:</span>
            <input list="mapping-groups" value={bulkGroup} onChange={(e) => setBulkGroup(e.target.value)} placeholder="ชื่อกลุ่มติดตาม" aria-label="ตั้งกลุ่มให้แถวที่เลือก" className="min-h-11 min-w-56 rounded-lg border border-slate-200 bg-white px-2 text-sm dark:border-slate-700 dark:bg-slate-900" />
            <button type="button" onClick={() => applyBulk("กลุ่มติดตาม", bulkGroup.trim())} disabled={!bulkGroup.trim()} className="min-h-11 rounded-lg bg-sky-700 px-3 text-sm font-semibold text-white disabled:opacity-50">ตั้งเป็นกลุ่มเดียวกัน</button>
            <button type="button" onClick={() => applyBulk("สถานะ", STATUS_CONFIRMED)} className="min-h-11 rounded-lg border border-emerald-400 px-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">ยืนยันทั้งหมดที่เลือก</button>
            <button type="button" onClick={() => setPicked([])} className="min-h-11 rounded-lg px-3 text-sm text-slate-600 dark:text-slate-300">ล้างการเลือก</button>
          </div>
        )}
        <datalist id="mapping-groups">
          {groupNames.map((g) => <option key={g} value={g} />)}
        </datalist>
      </section>

      {/* Table */}
      <section className="glass-panel overflow-hidden p-0">
        <div className="max-h-[65vh] overflow-auto">
          <table className="w-full min-w-[1100px] text-left text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50 text-xs text-slate-500 dark:bg-slate-900 dark:text-slate-400">
              <tr>
                <th scope="col" className="w-10 px-3 py-2">
                  <input
                    type="checkbox"
                    aria-label="เลือกทุกแถวที่แสดง"
                    disabled={readOnly}
                    checked={visible.length > 0 && visible.every((r) => picked.includes(r.แหล่ง_ไฟล์ดิบ))}
                    onChange={(e) => setPicked(e.target.checked ? visible.map((r) => r.แหล่ง_ไฟล์ดิบ) : [])}
                    className="h-4 w-4"
                  />
                </th>
                <th scope="col" className="px-3 py-2">ชื่อแหล่งตาม DMF</th>
                <th scope="col" className="px-3 py-2">กลุ่มติดตาม</th>
                <th scope="col" className="px-3 py-2">ความสัมพันธ์</th>
                <th scope="col" className="px-3 py-2">สถานะ</th>
                <th scope="col" className="px-3 py-2">หมายเหตุ</th>
                <th scope="col" className="px-3 py-2">ปีที่พบ</th>
                <th scope="col" className="px-3 py-2">แปลง</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => {
                const r = current(row);
                const name = row.แหล่ง_ไฟล์ดิบ;
                return (
                  <tr key={name} className={`border-b border-slate-100 align-top dark:border-slate-800/70 ${isChanged(row) ? "bg-amber-50/70 dark:bg-amber-950/20" : ""}`}>
                    <td className="px-3 py-2">
                      <input type="checkbox" aria-label={`เลือก ${name}`} disabled={readOnly} checked={picked.includes(name)} onChange={(e) => setPicked((p) => (e.target.checked ? [...p, name] : p.filter((x) => x !== name)))} className="mt-3 h-4 w-4" />
                    </td>
                    <th scope="row" className="whitespace-nowrap px-3 py-2 pt-4 font-semibold text-slate-800 dark:text-slate-100">{name}</th>
                    <td className="min-w-56 px-3 py-2">
                      <input list="mapping-groups" value={r.กลุ่มติดตาม} disabled={readOnly} onChange={(e) => setField(name, "กลุ่มติดตาม", e.target.value)} aria-label={`กลุ่มติดตามของ ${name}`} className={inputClass} />
                    </td>
                    <td className="min-w-48 px-3 py-2">
                      <select value={r.ความสัมพันธ์} disabled={readOnly} onChange={(e) => setField(name, "ความสัมพันธ์", e.target.value)} aria-label={`ความสัมพันธ์ของ ${name}`} className={inputClass}>
                        {RELATION_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                      </select>
                    </td>
                    <td className="min-w-32 px-3 py-2">
                      <select value={r.สถานะ} disabled={readOnly} onChange={(e) => setField(name, "สถานะ", e.target.value)} aria-label={`สถานะของ ${name}`} className={`${inputClass} ${r.สถานะ === STATUS_CONFIRMED ? "font-semibold text-emerald-800 dark:text-emerald-300" : "font-semibold text-amber-800 dark:text-amber-300"}`}>
                        {STATUS_OPTIONS.map((o) => <option key={o}>{o}</option>)}
                      </select>
                    </td>
                    <td className="min-w-72 px-3 py-2">
                      <input value={r.หมายเหตุ} disabled={readOnly} onChange={(e) => setField(name, "หมายเหตุ", e.target.value)} aria-label={`หมายเหตุของ ${name}`} className={inputClass} />
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 pt-4 tabular-nums text-slate-600 dark:text-slate-300">{row.ปีที่พบในข้อมูล}</td>
                    <td className="px-3 py-2 pt-4 text-slate-600 dark:text-slate-300">{row.แปลงที่พบ || "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Save bar */}
      {!readOnly && (
        <section className="glass-panel sticky bottom-4 flex flex-wrap items-center gap-3 p-4">
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">แก้ไขแล้ว {changedRows.length} แถว</span>
          <input value={commitNote} onChange={(e) => setCommitNote(e.target.value)} placeholder="บันทึกเหตุผลการแก้ไข (ไม่บังคับ)" aria-label="เหตุผลการแก้ไข" className="min-h-11 min-w-60 flex-1 rounded-xl border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900" />
          <button type="button" onClick={() => setEdits({})} disabled={changedRows.length === 0 || saving} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-slate-300 px-3 text-sm font-semibold text-slate-700 disabled:opacity-50 dark:border-slate-700 dark:text-slate-200">
            <RotateCcw aria-hidden="true" className="h-4 w-4" />
            ยกเลิกการแก้ไข
          </button>
          <button type="button" onClick={save} disabled={changedRows.length === 0 || saving} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-emerald-700 px-4 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50">
            {saving ? <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" /> : <Save aria-hidden="true" className="h-4 w-4" />}
            บันทึกขึ้น GitHub
          </button>
        </section>
      )}
    </div>
  );
}

function pickEditable(row?: FieldGroupRow): Partial<FieldGroupRow> {
  if (!row) return {};
  return Object.fromEntries(EDITABLE.filter((k) => row[k] !== undefined).map((k) => [k, String(row[k])]));
}
