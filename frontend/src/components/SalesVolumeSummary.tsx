"use client";

import React, { useMemo } from "react";
import { SalesRecord } from "@/types/hydrocarbon";
import { summarizeSalesVolumes } from "@/lib/sales-reporting";
import { formatNumber } from "@/lib/utils";
import { ReportingPeriod } from "@/lib/reporting";

interface SalesVolumeSummaryProps {
  records: SalesRecord[];
  detailRecords: SalesRecord[];
  months: string[];
  selectedMonth: string;
  period: ReportingPeriod;
  yearBE: number;
}

const SHORT_MONTHS: Record<string, string> = {
  มกราคม: "ม.ค.",
  กุมภาพันธ์: "ก.พ.",
  มีนาคม: "มี.ค.",
  เมษายน: "เม.ย.",
  พฤษภาคม: "พ.ค.",
  มิถุนายน: "มิ.ย.",
  กรกฎาคม: "ก.ค.",
  สิงหาคม: "ส.ค.",
  กันยายน: "ก.ย.",
  ตุลาคม: "ต.ค.",
  พฤศจิกายน: "พ.ย.",
  ธันวาคม: "ธ.ค.",
};

export function SalesVolumeSummary({
  records,
  detailRecords,
  months,
  selectedMonth,
  period,
  yearBE,
}: SalesVolumeSummaryProps) {
  const displayMonths = period === "monthly" ? [selectedMonth] : months;
  const { products } = useMemo(
    () => summarizeSalesVolumes(records, displayMonths),
    [records, displayMonths],
  );
  const { fields: filteredFields } = useMemo(
    () => summarizeSalesVolumes(detailRecords, displayMonths),
    [detailRecords, displayMonths],
  );
  const isFullYear = months.includes("ธันวาคม");
  const totalLabel = period === "monthly"
    ? `รวมเดือน ${SHORT_MONTHS[selectedMonth] || selectedMonth}`
    : isFullYear
      ? "รวมทั้งปี"
      : "รวม YTD";

  const renderRows = (
    rows: typeof products,
    includeField: boolean,
  ) =>
    rows.map((row, index) => (
      <tr
        key={`${row.field}-${row.operator}-${row.product}-${row.measure}-${index}`}
        className={index % 2 ? "bg-slate-50/60 dark:bg-slate-900/30" : ""}
      >
        {includeField && (
          <>
            <th scope="row" className="px-3 py-2.5 text-left font-semibold">
              {row.field}
            </th>
            <td className="px-3 py-2.5 text-left text-slate-500 dark:text-slate-400">
              {row.operator || "-"}
            </td>
          </>
        )}
        <td className="px-3 py-2.5 text-left">{row.product}</td>
        <td className="px-3 py-2.5 text-left text-slate-500 dark:text-slate-400">
          {row.measure} ({row.unit})
        </td>
        {period === "annual" &&
          displayMonths.map((month) => (
            <td key={month} className="px-3 py-2.5 text-right tabular-nums">
              {formatNumber(row.monthlyVolumes[month] || 0, 2)}
            </td>
          ))}
        <td className="bg-sky-50/60 px-3 py-2.5 text-right font-bold tabular-nums dark:bg-sky-950/30">
          {formatNumber(row.periodTotal, 2)}
        </td>
      </tr>
    ));

  const renderTable = (rows: typeof products, includeField: boolean) => (
    <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
      <table className="w-full border-collapse text-xs">
        <thead className="bg-slate-900 text-white">
          <tr>
            {includeField && (
              <>
                <th scope="col" className="min-w-40 px-3 py-3 text-left">ชื่อแหล่ง</th>
                <th scope="col" className="min-w-36 px-3 py-3 text-left">ผู้ดำเนินการ</th>
              </>
            )}
            <th scope="col" className="min-w-36 px-3 py-3 text-left">ผลิตภัณฑ์</th>
            <th scope="col" className="min-w-36 px-3 py-3 text-left">ตัวชี้วัด / หน่วย</th>
            {period === "annual" &&
              displayMonths.map((month) => (
                <th key={month} scope="col" className="min-w-24 px-3 py-3 text-right">
                  {SHORT_MONTHS[month] || month}
                </th>
              ))}
            <th scope="col" className="min-w-28 bg-sky-950 px-3 py-3 text-right">
              {totalLabel}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white/70 dark:divide-slate-800 dark:bg-slate-950/70">
          {rows.length > 0 ? (
            renderRows(rows, includeField)
          ) : (
            <tr>
              <td
                colSpan={(includeField ? 2 : 0) + 3 + (period === "annual" ? displayMonths.length : 0)}
                className="px-4 py-8 text-center text-slate-500"
              >
                ไม่พบข้อมูลตามตัวกรองที่เลือก
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );

  return (
    <section className="glass-panel p-5">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-sky-700 dark:text-sky-300">
          MONTHLY SALES VOLUME
        </p>
        <h2 className="mt-1 text-base font-extrabold text-slate-900 dark:text-white">
          สรุปปริมาณการจำหน่ายรายเดือน
        </h2>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          ปี {yearBE} ({yearBE - 543}) · แยกตามผลิตภัณฑ์และชื่อแหล่ง · ไม่รวมหน่วยต่างชนิดเข้าด้วยกัน
        </p>
      </div>

      <h3 className="mt-5 text-sm font-bold text-slate-800 dark:text-slate-200">
        ปริมาณรวมทั้งประเทศ แยกตามผลิตภัณฑ์
      </h3>
      {renderTable(products, false)}

      <h3 className="mt-6 text-sm font-bold text-slate-800 dark:text-slate-200">
        ปริมาณขายแยกตามแหล่งผลิต
      </h3>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
        ยอดรวมตามช่วงรายงานที่เลือก · ผลการค้นหากรองเฉพาะตารางแหล่งผลิต
      </p>
      {renderTable(filteredFields, true)}
    </section>
  );
}
