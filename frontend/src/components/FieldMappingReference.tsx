"use client";

import React, { useMemo, useState } from "react";
import { CheckCircle2, CircleDashed, Search } from "lucide-react";
import { FieldGroupRow, STATUS_CONFIRMED } from "@/lib/field-tracker";

interface FieldMappingReferenceProps {
  rows: FieldGroupRow[];
  generated?: string;
}

/** Read-only view of field_group_mapping.xlsx so data users can see which DMF names were merged and why. */
export function FieldMappingReference({ rows, generated }: FieldMappingReferenceProps) {
  const [query, setQuery] = useState("");
  const [showDrafts, setShowDrafts] = useState(true);

  const groups = useMemo(() => {
    const byGroup = new Map<string, FieldGroupRow[]>();
    rows.forEach((row) => {
      const group = row.กลุ่มติดตาม.trim() || row.แหล่ง_ไฟล์ดิบ;
      byGroup.set(group, [...(byGroup.get(group) || []), row]);
    });
    const q = query.trim().toLowerCase();
    return Array.from(byGroup.entries())
      .filter(([, members]) => members.length > 1)
      .filter(([, members]) => showDrafts || members.every((m) => m.สถานะ === STATUS_CONFIRMED))
      .filter(([group, members]) =>
        !q ||
        group.toLowerCase().includes(q) ||
        members.some((m) => m.แหล่ง_ไฟล์ดิบ.toLowerCase().includes(q) || m.แปลงที่พบ.toLowerCase().includes(q)),
      )
      .sort((a, b) => a[0].localeCompare(b[0], "th"));
  }, [rows, query, showDrafts]);

  const draftCount = rows.filter((r) => r.สถานะ !== STATUS_CONFIRMED).length;

  return (
    <section aria-labelledby="mapping-ref-title" className="glass-panel space-y-4 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 id="mapping-ref-title" className="text-sm font-extrabold text-slate-900 dark:text-white">
            ตาราง Mapping แหล่งผลิตข้ามปี
          </h3>
          <p className="mt-1 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
            ชื่อแหล่งตามรายงาน DMF ที่ทีม PTIT กำหนดให้นับต่อเนื่องเป็นกลุ่มเดียวกัน (เปลี่ยนชื่อ สะกดต่าง รวมกลุ่ม หรือแยกย่อยเมื่อเปลี่ยนสัมปทาน)
            · กราฟด้านบนรวมเฉพาะแถว <b>ยืนยันแล้ว</b> · แถว <b>ร่าง</b> เป็นข้อเสนอที่ยังไม่ถูกนำไปคำนวณ ({draftCount} ชื่อ)
            {generated && ` · ปรับปรุง ${generated.slice(0, 10)}`}
          </p>
        </div>
        <label className="inline-flex min-h-11 cursor-pointer items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
          <input type="checkbox" checked={showDrafts} onChange={(e) => setShowDrafts(e.target.checked)} className="h-4 w-4" />
          แสดงกลุ่มที่ยังเป็นร่าง
        </label>
      </div>

      <div className="relative max-w-md">
        <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="ค้นหาชื่อแหล่ง กลุ่ม หรือแปลง…"
          aria-label="ค้นหาใน Mapping"
          className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
      </div>

      {groups.length === 0 ? (
        <p className="py-6 text-center text-sm text-slate-500">ไม่พบกลุ่มที่ตรงกับเงื่อนไข</p>
      ) : (
        <div className="space-y-4">
          {groups.map(([group, members]) => {
            const allConfirmed = members.every((m) => m.สถานะ === STATUS_CONFIRMED);
            return (
              <div key={group} className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-50 px-4 py-2.5 dark:bg-slate-900/60">
                  <span className="text-sm font-bold text-slate-900 dark:text-white">{group}</span>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-bold ${
                      allConfirmed
                        ? "bg-emerald-100 text-emerald-900 dark:bg-emerald-950/70 dark:text-emerald-300"
                        : "bg-amber-100 text-amber-900 dark:bg-amber-950/70 dark:text-amber-300"
                    }`}
                  >
                    {allConfirmed ? <CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5" /> : <CircleDashed aria-hidden="true" className="h-3.5 w-3.5" />}
                    {allConfirmed ? "ยืนยันแล้ว · ใช้ในกราฟ" : "มีชื่อที่ยังเป็นร่าง"}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="text-slate-500 dark:text-slate-400">
                      <tr className="border-b border-slate-200 dark:border-slate-800">
                        <th scope="col" className="px-4 py-2 font-semibold">ชื่อแหล่งตาม DMF</th>
                        <th scope="col" className="px-4 py-2 font-semibold">ปีที่พบ</th>
                        <th scope="col" className="px-4 py-2 font-semibold">แปลง</th>
                        <th scope="col" className="px-4 py-2 font-semibold">ความสัมพันธ์</th>
                        <th scope="col" className="px-4 py-2 font-semibold">สถานะ</th>
                        <th scope="col" className="px-4 py-2 font-semibold">หมายเหตุ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {members.map((m) => (
                        <tr key={m.แหล่ง_ไฟล์ดิบ} className="border-b border-slate-100 align-top last:border-0 dark:border-slate-800/70">
                          <th scope="row" className="whitespace-nowrap px-4 py-2 font-semibold text-slate-800 dark:text-slate-100">{m.แหล่ง_ไฟล์ดิบ}</th>
                          <td className="whitespace-nowrap px-4 py-2 tabular-nums text-slate-600 dark:text-slate-300">{m.ปีที่พบในข้อมูล}</td>
                          <td className="px-4 py-2 text-slate-600 dark:text-slate-300">{m.แปลงที่พบ || "-"}</td>
                          <td className="whitespace-nowrap px-4 py-2 text-slate-600 dark:text-slate-300">{m.ความสัมพันธ์}</td>
                          <td className="whitespace-nowrap px-4 py-2">
                            <span className={m.สถานะ === STATUS_CONFIRMED ? "font-semibold text-emerald-800 dark:text-emerald-300" : "font-semibold text-amber-800 dark:text-amber-300"}>
                              {m.สถานะ === STATUS_CONFIRMED ? "ยืนยันแล้ว" : "ร่าง"}
                            </span>
                          </td>
                          <td className="min-w-64 px-4 py-2 text-slate-500 dark:text-slate-400">{m.หมายเหตุ || "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
