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

const METRICS: { key: ProductionMetricKey; label: string; short: string; volumeUnit: string }[] = [
  { key: "gas_mmscfd", label: "ก๊าซธรรมชาติ (MMSCFD)", short: "ก๊าซธรรมชาติ", volumeUnit: "BCF" },
  { key: "condensate_bpd", label: "คอนเดนเสท (BPD)", short: "คอนเดนเสท", volumeUnit: "MMbbl" },
  { key: "crude_bpd", label: "น้ำมันดิบ (BPD)", short: "น้ำมันดิบ", volumeUnit: "MMbbl" },
  { key: "total_boed", label: "รวม (BOED)", short: "รวมเทียบเท่าน้ำมันดิบ", volumeUnit: "MMBOE" },
];

type MetricChoice = ProductionMetricKey | "all";

/** One table column: which product matrix and which field of its row (a month, เฉลี่ยทั้งปี or สะสมทั้งปี). */
interface TableColumn {
  id: string;
  metric: ProductionMetricKey;
  field: string;
  label: string;
  /** Header group label (only in the all-products annual view) */
  group?: string;
  precision: number;
  tone?: "avg" | "cum";
}

const ratePrecision = (metric: ProductionMetricKey) => (metric === "gas_mmscfd" ? 2 : 0);

export function ProductionPeriodTable({
  data,
  yearBE,
  period,
  selectedMonth,
}: ProductionPeriodTableProps) {
  const [selectedMetric, setSelectedMetric] = useState<MetricChoice>("all");
  const [regionFilter, setRegionFilter] = useState<"all" | "Onshore" | "Offshore">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const matrices = useMemo(
    () => productionMatricesForYear(data.flat_records, yearBE),
    [data.flat_records, yearBE],
  );
  // Every product matrix has the same rows in the same order, so a row index identifies a field in all of them
  const baseMatrix = matrices[selectedMetric === "all" ? "total_boed" : selectedMetric];
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
  const cumLabel = isCompleteYear ? "สะสมทั้งปี" : "สะสม YTD";
  const allProducts = selectedMetric === "all";

  const columns: TableColumn[] = useMemo(() => {
    if (!allProducts) {
      const metric = selectedMetric as ProductionMetricKey;
      const cols: TableColumn[] = displayMonths.map((month) => ({
        id: month, metric, field: month, label: month, precision: ratePrecision(metric),
      }));
      if (showYearSummary) {
        cols.push(
          { id: "avg", metric, field: "เฉลี่ยทั้งปี", label: "เฉลี่ย/วัน", precision: ratePrecision(metric), tone: "avg" },
          { id: "cum", metric, field: "สะสมทั้งปี", label: cumLabel, precision: 2, tone: "cum" },
        );
      }
      return cols;
    }
    if (!showYearSummary) {
      return METRICS.map((m) => ({
        id: m.key, metric: m.key, field: selectedMonth, label: `${m.short} (${matrices[m.key].unit})`, precision: ratePrecision(m.key),
      }));
    }
    return METRICS.flatMap((m) => [
      { id: `${m.key}-avg`, metric: m.key, field: "เฉลี่ยทั้งปี", label: `เฉลี่ย/วัน (${matrices[m.key].unit})`, group: m.short, precision: ratePrecision(m.key), tone: "avg" as const },
      { id: `${m.key}-cum`, metric: m.key, field: "สะสมทั้งปี", label: `${cumLabel} (${m.volumeUnit})`, group: m.short, precision: 2, tone: "cum" as const },
    ]);
  }, [allProducts, selectedMetric, displayMonths, showYearSummary, cumLabel, selectedMonth, matrices]);

  const indexedRows = baseMatrix.rows
    .map((row, index) => ({ row, index }))
    .filter(({ row }) => {
      if (regionFilter !== "all" && row.PTIT_Region !== regionFilter) return false;
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        return `${row.PTIT_Field_Name} ${row.PTIT_Operator} ${row.PTIT_Concession} ${row.PTIT_Region}`
          .toLowerCase()
          .includes(query);
      }
      return true;
    });
  const onshoreRows = indexedRows.filter(({ row }) => row.PTIT_Region === "Onshore");
  const offshoreRows = indexedRows.filter(({ row }) => row.PTIT_Region !== "Onshore");

  const cellValue = (index: number, column: TableColumn) =>
    Number(matrices[column.metric].rows[index]?.[column.field]) || 0;

  const sumRows = (items: { index: number }[]) =>
    columns.map((column) => items.reduce((sum, { index }) => sum + cellValue(index, column), 0));

  const onshoreTotals = sumRows(onshoreRows);
  const offshoreTotals = sumRows(offshoreRows);
  const grandTotals = sumRows(indexedRows);
  const hasGroups = columns.some((c) => c.group);
  const colCount = 1 + columns.length;

  const subtitle = allProducts
    ? "ทุกผลิตภัณฑ์ · ก๊าซ MMSCFD · ของเหลว BPD · รวม BOED"
    : `${baseMatrix.column_name} · ${baseMatrix.unit}`;

  const exportExcel = () => {
    const header1 = ["ชื่อแหล่งผลิต", "ผู้ดำเนินการ", "แปลงสัมปทาน", ...columns.map((c) => c.group || "")];
    const header2 = ["", "", "", ...columns.map((c) => c.label)];
    const matrixRows: (string | number)[][] = [
      ["PETROLEUM INSTITUTE OF THAILAND"],
      [
        period === "annual"
          ? `DOMESTIC PETROLEUM PRODUCTION ${isCompleteYear ? "ANNUAL" : "YTD"} ${yearBE} (${yearBE - 543})`
          : `DOMESTIC PETROLEUM PRODUCTION ${selectedMonth} ${yearBE} (${yearBE - 543})`,
      ],
      [subtitle],
      [],
      ...(hasGroups
        ? [header1, header2]
        : [["ชื่อแหล่งผลิต", "ผู้ดำเนินการ", "แปลงสัมปทาน", ...columns.map((c) => c.label)]]),
    ];
    const pushRow = (label: string, operator: string, concession: string, values: number[]) =>
      matrixRows.push([label, operator, concession, ...values]);
    if (regionFilter !== "Offshore" && onshoreRows.length) {
      onshoreRows.forEach(({ row, index }) =>
        pushRow(row.PTIT_Field_Name, row.PTIT_Operator, row.PTIT_Concession, columns.map((c) => cellValue(index, c))),
      );
      pushRow("รวมบนบก", "", "", onshoreTotals);
    }
    if (regionFilter !== "Onshore" && offshoreRows.length) {
      offshoreRows.forEach(({ row, index }) =>
        pushRow(row.PTIT_Field_Name, row.PTIT_Operator, row.PTIT_Concession, columns.map((c) => cellValue(index, c))),
      );
      pushRow("รวมในทะเล", "", "", offshoreTotals);
    }
    pushRow("รวมประเทศ", "", "", grandTotals);

    const worksheet = XLSX.utils.aoa_to_sheet(matrixRows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Production");
    const monthSuffix = period === "monthly" ? `_${selectedMonth}` : "_YTD";
    XLSX.writeFile(workbook, `PTIT_Production_${yearBE}${monthSuffix}_${selectedMetric}.xlsx`);
  };

  const toneClass = (column: TableColumn) =>
    column.tone === "avg"
      ? "bg-sky-50/50 font-semibold dark:bg-sky-950/20"
      : column.tone === "cum"
        ? "bg-amber-50/50 font-semibold dark:bg-amber-950/20"
        : "";
  // A thin divider before each product in the all-products view
  const groupStart = (i: number) =>
    allProducts && i > 0 && (hasGroups ? columns[i].group !== columns[i - 1].group : true);
  const divider = (i: number) => (groupStart(i) ? "border-l border-slate-200 dark:border-slate-700" : "");

  const renderDataRow = ({ row, index }: { row: MatrixRow; index: number }, position: number) => (
    <tr
      key={`${row.PTIT_Region}-${row.PTIT_Concession}-${row.PTIT_Field_Name}-${index}`}
      className={`border-b border-slate-100 dark:border-slate-800 ${
        position % 2 ? "bg-slate-50/60 dark:bg-slate-900/30" : ""
      }`}
    >
      <th scope="row" className="sticky left-0 min-w-56 bg-inherit px-3 py-3 text-left text-slate-800 dark:text-slate-200">
        <span className="block font-semibold">{row.PTIT_Field_Name}</span>
        <span className="mt-0.5 block text-[11px] font-normal text-slate-500 dark:text-slate-400">
          {[row.PTIT_Operator, row.PTIT_Concession].filter(Boolean).join(" · ")}
        </span>
      </th>
      {columns.map((column, i) => {
        const value = cellValue(index, column);
        return (
          <td key={column.id} className={`px-3 py-3 text-right tabular-nums ${toneClass(column)} ${divider(i)}`}>
            {value > 0 ? formatNumber(value, column.precision) : "-"}
          </td>
        );
      })}
    </tr>
  );

  const renderSubtotal = (label: string, totals: number[], className: string) => (
    <tr className={`border-y border-slate-200 font-bold dark:border-slate-700 ${className}`}>
      <th scope="row" className="sticky left-0 bg-inherit px-3 py-3 text-left">{label}</th>
      {columns.map((column, i) => (
        <td key={column.id} className={`px-3 py-3 text-right tabular-nums ${divider(i)}`}>
          {formatNumber(totals[i], column.precision)}
        </td>
      ))}
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
            {subtitle} · ปี {yearBE} ({yearBE - 543})
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only" htmlFor="production-metric">เลือกตัวชี้วัด</label>
          <select
            id="production-metric"
            value={selectedMetric}
            onChange={(event) => setSelectedMetric(event.target.value as MetricChoice)}
            className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold dark:border-slate-700 dark:bg-slate-900"
          >
            <option value="all">ทุกผลิตภัณฑ์ (แยกคอลัมน์)</option>
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
            {hasGroups && (
              <tr>
                <th scope="col" rowSpan={2} className="sticky left-0 min-w-56 bg-slate-900 px-3 py-3 text-left align-bottom">ชื่อแหล่งผลิต</th>
                {columns
                  .filter((c, i) => i === 0 || c.group !== columns[i - 1].group)
                  .map((c) => (
                    <th
                      key={c.group}
                      scope="colgroup"
                      colSpan={columns.filter((x) => x.group === c.group).length}
                      className="border-l border-slate-700 px-3 pt-3 text-center"
                    >
                      {c.group}
                    </th>
                  ))}
              </tr>
            )}
            <tr>
              {!hasGroups && (
                <th scope="col" className="sticky left-0 min-w-56 bg-slate-900 px-3 py-3 text-left">ชื่อแหล่งผลิต</th>
              )}
              {columns.map((column, i) => (
                <th
                  key={column.id}
                  scope="col"
                  className={`min-w-28 px-3 py-3 text-right ${
                    column.tone === "avg" ? "bg-sky-950" : column.tone === "cum" ? "bg-amber-950" : ""
                  } ${groupStart(i) ? "border-l border-slate-700" : ""}`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {regionFilter !== "Offshore" && onshoreRows.length > 0 && (
              <>
                <tr className="bg-slate-100 font-bold text-sky-900 dark:bg-slate-800 dark:text-sky-200">
                  <th scope="rowgroup" colSpan={colCount} className="px-3 py-2 text-left">
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
                  <th scope="rowgroup" colSpan={colCount} className="px-3 py-2 text-left">
                    ในทะเล · Offshore
                  </th>
                </tr>
                {offshoreRows.map(renderDataRow)}
                {renderSubtotal("รวมในทะเล", offshoreTotals, "bg-sky-50 text-sky-950 dark:bg-sky-950/50 dark:text-sky-100")}
              </>
            )}
            {indexedRows.length > 0 ? (
              renderSubtotal("รวมประเทศ · Thailand", grandTotals, "bg-amber-100 text-amber-950 dark:bg-amber-950/80 dark:text-amber-100")
            ) : (
              <tr>
                <td colSpan={colCount} className="px-4 py-10 text-center text-slate-500">
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
