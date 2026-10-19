"use client";

import React, { useMemo, useState } from "react";
import { Download, Search } from "lucide-react";
import {
  ProductionMetricKey,
  ReportingPeriod,
  THAI_MONTHS,
  productionMatricesForYear,
} from "@/lib/reporting";
import { ProductionMasterData, MatrixRow } from "@/types/hydrocarbon";
import { formatNumber } from "@/lib/utils";
import * as XLSX from "xlsx";

interface ProductionPeriodTableProps {
  data: ProductionMasterData;
  yearBE: number;
  period: ReportingPeriod;
  selectedMonth: string;
}

const METRICS: { key: ProductionMetricKey; label: string }[] = [
  { key: "gas_mmscfd", label: "ก๊าซธรรมชาติ (MMSCFD)" },
  { key: "condensate_bpd", label: "คอนเดนเสท (BPD)" },
  { key: "crude_bpd", label: "น้ำมันดิบ (BPD)" },
  { key: "total_boed", label: "รวม (BOED)" },
];

export function ProductionPeriodTable({
  data,
  yearBE,
  period,
  selectedMonth,
}: ProductionPeriodTableProps) {
  const [selectedMetric, setSelectedMetric] = useState<ProductionMetricKey>("total_boed");
  const [regionFilter, setRegionFilter] = useState<"all" | "Onshore" | "Offshore">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const matrices = useMemo(
    () => productionMatricesForYear(data.flat_records, yearBE),
    [data.flat_records, yearBE],
  );
  const activeMatrix = matrices[selectedMetric];
  const unitLabel = activeMatrix.unit;
  const displayMonths = useMemo(() => {
    if (period === "monthly") return [selectedMonth];
    return THAI_MONTHS.filter((month) =>
      data.flat_records.some(
        (record) => Number(record.ปี) === yearBE && record.เดือน === month,
      ),
    );
  }, [data.flat_records, period, selectedMonth, yearBE]);
  const showYearSummary = period === "annual";
  const isCompleteYear = displayMonths.includes("ธันวาคม");

  const rows = activeMatrix.rows.filter((row) => {
    if (regionFilter !== "all" && row.PTIT_Region !== regionFilter) return false;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      return `${row.PTIT_Field_Name} ${row.PTIT_Operator} ${row.PTIT_Concession} ${row.PTIT_Region}`
        .toLowerCase()
        .includes(query);
    }
    return true;
  });
  const onshoreRows = rows.filter((row) => row.PTIT_Region === "Onshore");
  const offshoreRows = rows.filter((row) => row.PTIT_Region !== "Onshore");

  const sumRows = (items: MatrixRow[]) => {
    const totals: Record<string, number> = {};
    displayMonths.forEach((month) => (totals[month] = 0));
    totals["เฉลี่ยทั้งปี"] = 0;
    totals["สะสมทั้งปี"] = 0;
    items.forEach((row) => {
      displayMonths.forEach((month) => {
        totals[month] += Number(row[month]) || 0;
      });
      totals["เฉลี่ยทั้งปี"] += Number(row["เฉลี่ยทั้งปี"]) || 0;
      totals["สะสมทั้งปี"] += Number(row["สะสมทั้งปี"]) || 0;
    });
    return totals;
  };

  const onshoreTotals = sumRows(onshoreRows);
  const offshoreTotals = sumRows(offshoreRows);
  const grandTotals = sumRows(rows);
  const precision = unitLabel === "MMSCFD" ? 2 : 0;

  const exportExcel = () => {
    const matrixRows: (string | number)[][] = [
      ["PETROLEUM INSTITUTE OF THAILAND"],
      [
        period === "annual"
          ?           `DOMESTIC PETROLEUM PRODUCTION ${isCompleteYear ? "ANNUAL" : "YTD"} ${yearBE} (${yearBE - 543})`
          : `DOMESTIC PETROLEUM PRODUCTION ${selectedMonth} ${yearBE} (${yearBE - 543})`,
      ],
      [activeMatrix.column_name, `Unit: ${unitLabel}`],
      [],
      [
        "ชื่อแหล่งผลิต",
        "ผู้ดำเนินการ",
        "แปลงสัมปทาน",
        ...displayMonths,
        ...(showYearSummary
          ? ["เฉลี่ย/วัน", isCompleteYear ? "สะสมทั้งปี" : "สะสม YTD"]
          : []),
      ],
    ];

    rows.forEach((row) => {
      matrixRows.push([
        row.PTIT_Field_Name,
        row.PTIT_Operator,
        row.PTIT_Concession,
        ...displayMonths.map((month) => Number(row[month]) || 0),
        ...(showYearSummary
          ? [Number(row["เฉลี่ยทั้งปี"]) || 0, Number(row["สะสมทั้งปี"]) || 0]
          : []),
      ]);
    });

    const worksheet = XLSX.utils.aoa_to_sheet(matrixRows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Production");
    const monthSuffix = period === "monthly" ? `_${selectedMonth}` : "_YTD";
    XLSX.writeFile(
      workbook,
      `PTIT_Production_${yearBE}${monthSuffix}_${selectedMetric}.xlsx`,
    );
  };

  const renderDataRow = (row: MatrixRow, index: number) => (
    <tr
      key={`${row.PTIT_Region}-${row.PTIT_Concession}-${row.PTIT_Field_Name}-${index}`}
      className={`border-b border-slate-100 dark:border-slate-800 ${
        index % 2 ? "bg-slate-50/60 dark:bg-slate-900/30" : ""
      }`}
    >
      <th scope="row" className="sticky left-0 min-w-56 bg-inherit px-3 py-3 text-left text-slate-800 dark:text-slate-200">
        <span className="block font-semibold">{row.PTIT_Field_Name}</span>
        <span className="mt-0.5 block text-[11px] font-normal text-slate-500 dark:text-slate-400">
          {[row.PTIT_Operator, row.PTIT_Concession].filter(Boolean).join(" · ")}
        </span>
      </th>
      {displayMonths.map((month) => (
        <td key={month} className="px-3 py-3 text-right tabular-nums">
          {(Number(row[month]) || 0) > 0
            ? formatNumber(Number(row[month]), precision)
            : "-"}
        </td>
      ))}
      {showYearSummary && (
        <>
          <td className="bg-sky-50/50 px-3 py-3 text-right font-semibold tabular-nums dark:bg-sky-950/20">
            {formatNumber(Number(row["เฉลี่ยทั้งปี"]) || 0, precision)}
          </td>
          <td className="bg-amber-50/50 px-3 py-3 text-right font-semibold tabular-nums dark:bg-amber-950/20">
            {formatNumber(Number(row["สะสมทั้งปี"]) || 0, 2)}
          </td>
        </>
      )}
    </tr>
  );

  const renderSubtotal = (label: string, totals: Record<string, number>, className: string) => (
    <tr className={`border-y border-slate-200 font-bold dark:border-slate-700 ${className}`}>
      <th scope="row" className="sticky left-0 bg-inherit px-3 py-3 text-left">{label}</th>
      {displayMonths.map((month) => (
        <td key={month} className="px-3 py-3 text-right tabular-nums">
          {formatNumber(totals[month], precision)}
        </td>
      ))}
      {showYearSummary && (
        <>
          <td className="px-3 py-3 text-right tabular-nums">
            {formatNumber(totals["เฉลี่ยทั้งปี"], precision)}
          </td>
          <td className="px-3 py-3 text-right tabular-nums">
            {formatNumber(totals["สะสมทั้งปี"], 2)}
          </td>
        </>
      )}
    </tr>
  );

  return (
    <section className="glass-panel p-5">
      <div className="flex flex-col gap-4 border-b border-slate-200 pb-4 dark:border-slate-800 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
            {period === "annual" ? "ตารางสรุปการผลิตสะสมรายปี" : `รายละเอียดการผลิต · ${selectedMonth}`}
          </h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {activeMatrix.column_name} · {unitLabel} · ปี {yearBE} ({yearBE - 543})
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only" htmlFor="production-metric">เลือกตัวชี้วัด</label>
          <select
            id="production-metric"
            value={selectedMetric}
            onChange={(event) => setSelectedMetric(event.target.value as ProductionMetricKey)}
            className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold dark:border-slate-700 dark:bg-slate-900"
          >
            {METRICS.map((metric) => (
              <option key={metric.key} value={metric.key}>{metric.label}</option>
            ))}
          </select>
          <label className="sr-only" htmlFor="production-region">เลือกพื้นที่</label>
          <select
            id="production-region"
            value={regionFilter}
            onChange={(event) => setRegionFilter(event.target.value as typeof regionFilter)}
            className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"
          >
            <option value="all">ทุกพื้นที่</option>
            <option value="Onshore">บนบก (Onshore)</option>
            <option value="Offshore">ในทะเล (Offshore)</option>
          </select>
          <div className="relative">
            <Search aria-hidden="true" className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <label className="sr-only" htmlFor="production-search">ค้นหาแหล่งผลิต</label>
            <input
              id="production-search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="ค้นหาแหล่ง / บริษัท"
              className="min-h-11 w-48 rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm dark:border-slate-700 dark:bg-slate-900"
            />
          </div>
          <button
            type="button"
            onClick={exportExcel}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-emerald-700 px-3 text-sm font-semibold text-white hover:bg-emerald-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700"
          >
            <Download aria-hidden="true" className="h-4 w-4" />
            ส่งออก Excel
          </button>
        </div>
      </div>

      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-slate-900 text-xs font-bold text-white">
            <tr>
              <th scope="col" className="sticky left-0 min-w-56 bg-slate-900 px-3 py-3 text-left">ชื่อแหล่งผลิต</th>
              {displayMonths.map((month) => (
                <th key={month} scope="col" className="min-w-24 px-3 py-3 text-right">{month}</th>
              ))}
              {showYearSummary && (
                <>
                  <th scope="col" className="min-w-28 bg-sky-950 px-3 py-3 text-right">เฉลี่ย/วัน</th>
                  <th scope="col" className="min-w-28 bg-amber-950 px-3 py-3 text-right">
                    {isCompleteYear ? "สะสมทั้งปี" : "สะสม YTD"}
                  </th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {regionFilter !== "Offshore" && onshoreRows.length > 0 && (
              <>
                <tr className="bg-slate-100 font-bold text-sky-900 dark:bg-slate-800 dark:text-sky-200">
                  <th scope="rowgroup" colSpan={1 + displayMonths.length + (showYearSummary ? 2 : 0)} className="px-3 py-2 text-left">
                    บนบก · Onshore
                  </th>
                </tr>
                {onshoreRows.map(renderDataRow)}
                {renderSubtotal("รวมบนบก", onshoreTotals, "bg-sky-50 text-sky-950 dark:bg-sky-950/50 dark:text-sky-100")}
              </>
            )}
            {regionFilter !== "Onshore" && offshoreRows.length > 0 && (
              <>
                <tr className="bg-slate-100 font-bold text-sky-900 dark:bg-slate-800 dark:text-sky-200">
                  <th scope="rowgroup" colSpan={1 + displayMonths.length + (showYearSummary ? 2 : 0)} className="px-3 py-2 text-left">
                    ในทะเล · Offshore
                  </th>
                </tr>
                {offshoreRows.map(renderDataRow)}
                {renderSubtotal("รวมในทะเล", offshoreTotals, "bg-sky-50 text-sky-950 dark:bg-sky-950/50 dark:text-sky-100")}
              </>
            )}
            {rows.length > 0 ? (
              renderSubtotal("รวมประเทศ · Thailand", grandTotals, "bg-amber-100 text-amber-950 dark:bg-amber-950/80 dark:text-amber-100")
            ) : (
              <tr>
                <td colSpan={1 + displayMonths.length + (showYearSummary ? 2 : 0)} className="px-4 py-10 text-center text-slate-500">
                  ไม่พบข้อมูลตามตัวกรองที่เลือก
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
        {isCompleteYear ? "ยอดรวมทั้งปี" : "ยอดสะสม YTD"} คำนวณจากอัตรารายวัน × จำนวนวันในเดือนที่มีข้อมูล · ก๊าซเป็น BCF, ของเหลวเป็น MMbbl และ BOED เป็น MMBOE · ที่มา: DMF / DEDP · PTIT
      </p>
    </section>
  );
}
