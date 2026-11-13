"use client";

import React, { useMemo, useState } from "react";
import { Check, Search, X } from "lucide-react";
import { CustomGroup, newGroupId } from "@/lib/custom-groups";

export interface FieldOption {
  name: string;
  years: string;
  blocks: string;
  area: string;
}

interface CustomGroupBuilderProps {
  options: FieldOption[];
  initial?: CustomGroup;
  existingNames: string[];
  onSave: (group: CustomGroup) => void;
  onCancel: () => void;
}

/** Lets any viewer pick DMF field names and name the group themselves (stored in their browser). */
export function CustomGroupBuilder({ options, initial, existingNames, onSave, onCancel }: CustomGroupBuilderProps) {
  const [name, setName] = useState(initial?.name || "");
  const [members, setMembers] = useState<string[]>(initial?.members || []);
  const [query, setQuery] = useState("");
  const [onlyPicked, setOnlyPicked] = useState(false);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return options.filter(
      (o) =>
        (!onlyPicked || members.includes(o.name)) &&
        (!q || o.name.toLowerCase().includes(q) || o.blocks.toLowerCase().includes(q)),
    );
  }, [options, query, onlyPicked, members]);

  const trimmed = name.trim();
  const duplicateName = existingNames.some((n) => n === trimmed && n !== initial?.name);
  const canSave = trimmed.length > 0 && members.length > 0 && !duplicateName;

  const toggle = (field: string) =>
    setMembers((current) => (current.includes(field) ? current.filter((m) => m !== field) : [...current, field]));

  return (
    <div className="space-y-3 rounded-xl border border-sky-200 bg-sky-50/60 p-4 dark:border-sky-900 dark:bg-sky-950/30">
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex min-w-60 flex-1 flex-col gap-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
          ชื่อกลุ่มของฉัน
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={60}
            placeholder="เช่น อ่าวไทยตอนบน, แหล่งของ PTTEP, เอราวัณ+บงกช"
            className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-normal text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </label>
        <span className="pb-3 text-sm text-slate-600 dark:text-slate-300">
          เลือกแล้ว <b className="tabular-nums">{members.length}</b> แหล่ง
        </span>
      </div>
      {duplicateName && <p className="text-xs font-semibold text-amber-800 dark:text-amber-300">มีกลุ่มชื่อนี้อยู่แล้ว</p>}

      {members.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {members.map((m) => (
            <span key={m} className="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200">
              {m}
              <button type="button" onClick={() => toggle(m)} aria-label={`เอา ${m} ออกจากกลุ่ม`} className="rounded-full p-0.5 hover:bg-slate-100 dark:hover:bg-slate-800">
                <X aria-hidden="true" className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-60 flex-1">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="ค้นหาชื่อแหล่งหรือแปลง…"
            aria-label="ค้นหาแหล่งเพื่อใส่ในกลุ่ม"
            className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <label className="inline-flex min-h-11 items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
          <input type="checkbox" checked={onlyPicked} onChange={(e) => setOnlyPicked(e.target.checked)} className="h-4 w-4" />
          แสดงเฉพาะที่เลือก
        </label>
      </div>

      <div className="max-h-72 overflow-y-auto rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <ul>
          {filtered.map((o) => {
            const picked = members.includes(o.name);
            return (
              <li key={o.name} className="border-b border-slate-100 last:border-0 dark:border-slate-800/70">
                <label className="flex min-h-11 cursor-pointer items-center gap-3 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-900">
                  <input type="checkbox" checked={picked} onChange={() => toggle(o.name)} className="h-4 w-4" />
                  <span className="flex-1 text-sm font-semibold text-slate-800 dark:text-slate-100">{o.name}</span>
                  <span className="hidden text-xs text-slate-500 sm:inline dark:text-slate-400">{o.blocks || "-"}</span>
                  <span className="text-xs tabular-nums text-slate-500 dark:text-slate-400">{o.years}</span>
                </label>
              </li>
            );
          })}
          {filtered.length === 0 && <li className="px-3 py-6 text-center text-sm text-slate-500">ไม่พบแหล่ง</li>}
        </ul>
      </div>

      <div className="flex flex-wrap justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="min-h-11 rounded-xl border border-slate-300 px-4 text-sm font-semibold text-slate-700 hover:bg-white dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
        >
          ยกเลิก
        </button>
        <button
          type="button"
          disabled={!canSave}
          onClick={() => onSave({ id: initial?.id || newGroupId(), name: trimmed, members })}
          className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-sky-700 px-4 text-sm font-semibold text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Check aria-hidden="true" className="h-4 w-4" />
          {initial ? "บันทึกการแก้ไข" : "สร้างกลุ่ม"}
        </button>
      </div>
    </div>
  );
}
