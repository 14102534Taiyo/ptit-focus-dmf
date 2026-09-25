"use client";

import React, { useState, useMemo } from "react";
import { Sliders, Download, Search, Table as TableIcon } from "lucide-react";
import { ProductionRecord } from "@/types/hydrocarbon";
import { formatNumber } from "@/lib/utils";
import * as XLSX from "xlsx";

interface DynamicPivotStudioProps {
  records: ProductionRecord[];
}

const METRIC_OPTIONS = [
  { key: "รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)", label: "รวมเทียบเท่าน้ำมันดิบ (BOED)" },
  { key: "ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)", label: "ก๊าซธรรมชาติ (MMSCFD)" },
  { key: "ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)", label: "ก๊าซธรรมชาติเหลว / คอนเดนเสท (BPD)" },
  { key: "น้ำมันดิบ (บาร์เรล/วัน)", label: "น้ำมันดิบ (BPD)" },
];

const DIMENSION_OPTIONS = [
  { key: "ผู้ดำเนินการ", label: "ผู้ดำเนินการ (Operator)" },
  { key: "แอ่งปิโตรเลียม", label: "แอ่งปิโตรเลียม (Basin)" },
  { key: "ประเภทสัญญา", label: "ประเภทสัญญา (Contract Type)" },
  { key: "พื้นที่", label: "พื้นที่ (Region: บนบก / ในอ่าว)" },
  { key: "แปลง_ไฟล์ดิบ", label: "แปลงสัมปทาน (Concession / Block)" },
];

const MONTH_ORDER = [
  "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
  "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม"
];

export function DynamicPivotStudio({ records }: DynamicPivotStudioProps) {
  const [rowDimension, setRowDimension] = useState<string>("ผู้ดำเนินการ");
  const [metricKey, setMetricKey] = useState<string>("รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)");
  const [searchFilter, setSearchFilter] = useState<string>("");

  // Build Pivot Table
  const { pivotRows, uniqueMonths, grandTotalRow, columnTotals } = useMemo(() => {
    const pivotMap: Record<string, Record<string, number>> = {};
    const colTotals: Record<string, number> = {};
    MONTH_ORDER.forEach((m) => (colTotals[m] = 0));
    let grandSum = 0;

    records.forEach((r) => {
      const dimVal = (r as any)[rowDimension] || "ไม่ระบุ";
      const month = r.เดือน;
      const val = Number((r as any)[metricKey]) || 0;

      if (!pivotMap[dimVal]) {
        pivotMap[dimVal] = {};
        MONTH_ORDER.forEach((m) => (pivotMap[dimVal][m] = 0));
      }

      if (pivotMap[dimVal][month] !== undefined) {
        pivotMap[dimVal][month] += val;
        colTotals[month] += val;
        grandSum += val;
      }
    });

    // Filter by search
    let rows = Object.entries(pivotMap).map(([rowKey, monthVals]) => {
      const rowSum = Object.values(monthVals).reduce((a, b) => a + b, 0);
      const rowAvg = rowSum / (MONTH_ORDER.length || 1);
      return {
        rowKey,
        monthVals,
        rowSum,
        rowAvg,
      };
    });

    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      rows = rows.filter((r) => r.rowKey.toLowerCase().includes(q));
    }

    // Sort by row sum descending
    rows.sort((a, b) => b.rowSum - a.rowSum);

    return {
      pivotRows: rows,
      uniqueMonths: MONTH_ORDER,
      grandTotalRow: grandSum,
      columnTotals: colTotals,
    };
  }, [records, rowDimension, metricKey, searchFilter]);

  // Export to Excel
  const handleExport = () => {
    const wb = XLSX.utils.book_new();
    const rows: any[] = [];
    rows.push([`PTIT PIVOT ANALYSIS - BY ${rowDimension.toUpperCase()} (${metricKey})`]);
    rows.push([]);
    rows.push([rowDimension, ...uniqueMonths, "รวมทุกเดือน", "เฉลี่ยต่อเดือน"]);

    pivotRows.forEach((r) => {
      const rowData = [
        r.rowKey,
        ...uniqueMonths.map((m) => (r.monthVals[m] > 0 ? r.monthVals[m] : "-")),
        r.rowSum,
        r.rowAvg,
      ];
      rows.push(rowData);
    });

    const totalRow = [
      "ยอดรวมทั้งสิ้น (GRAND TOTAL)",
      ...uniqueMonths.map((m) => columnTotals[m]),
      grandTotalRow,
      grandTotalRow / uniqueMonths.length,
    ];
    rows.push(totalRow);

    const ws = XLSX.utils.aoa_to_sheet(rows);
    XLSX.utils.book_append_sheet(wb, ws, "Pivot_Summary");
    XLSX.writeFile(wb, `PTIT_Pivot_${rowDimension}_2569.xlsx`);
  };

  return (
    <div className="glass-panel p-5 mb-8">
      {/* Studio Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-slate-800">
        <div>
          <h2 className="text-base font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-sky-600" />
            <span>Dynamic Pivot Studio (วิเคราะห์และจัดกลุ่มข้อมูลตามมิติ)</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            ปรับแต่งมิติการจัดกลุ่มและตัวชี้วัดเพื่อวิเคราะห์ความเข้มข้นของการผลิตปิโตรเลียมในประเทศ
          </p>
        </div>

        {/* Studio Selectors */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Dimension Selector */}
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-slate-500 font-medium">จัดกลุ่มตาม:</span>
            <select
              value={rowDimension}
              onChange={(e) => setRowDimension(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              {DIMENSION_OPTIONS.map((d) => (
                <option key={d.key} value={d.key}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          {/* Metric Selector */}
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-slate-500 font-medium">ตัวชี้วัด:</span>
            <select
              value={metricKey}
              onChange={(e) => setMetricKey(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-semibold text-sky-700 dark:text-sky-300 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              {METRIC_OPTIONS.map((m) => (
                <option key={m.key} value={m.key}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="กรองรายการ..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none w-36"
            />
          </div>

          {/* Export Button */}
          <button
            onClick={handleExport}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>ส่งออก Pivot</span>
          </button>
        </div>
      </div>

      {/* Pivot Table View */}
      <div className="overflow-x-auto mt-4 rounded-xl border border-slate-200/70 dark:border-slate-800 shadow-sm max-h-[500px] overflow-y-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="sticky top-0 z-20 bg-slate-900 text-white shadow-sm font-semibold">
            <tr>
              <th className="py-2.5 px-3.5 min-w-[200px] sticky left-0 z-30 bg-slate-900 border-r border-slate-800">
                {rowDimension}
              </th>
              {uniqueMonths.map((m) => (
                <th key={m} className="py-2.5 px-2 text-right min-w-[75px] border-r border-slate-800/80">
                  {m.slice(0, 4)}
                </th>
              ))}
              <th className="py-2.5 px-2.5 text-right min-w-[90px] bg-sky-950 border-r border-slate-800 text-sky-200">
                รวมสะสม
              </th>
              <th className="py-2.5 px-2.5 text-right min-w-[90px] bg-amber-950 text-amber-200">
                เฉลี่ย/เดือน
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white/70 dark:bg-slate-950/70">
            {pivotRows.map((r, idx) => {
              const isZebra = idx % 2 === 1;
              return (
                <tr
                  key={r.rowKey}
                  className={`hover:bg-sky-50/50 dark:hover:bg-slate-800/50 transition-colors ${
                    isZebra ? "bg-slate-50/40 dark:bg-slate-900/20" : ""
                  }`}
                >
                  <td className="py-2.5 px-3.5 font-semibold text-slate-800 dark:text-slate-200 sticky left-0 z-10 bg-white/95 dark:bg-slate-950/95 border-r border-slate-200/70 dark:border-slate-800">
                    {r.rowKey}
                  </td>
                  {uniqueMonths.map((m) => (
                    <td key={m} className="py-2.5 px-2 text-right tabular-nums text-slate-700 dark:text-slate-300 border-r border-slate-100 dark:border-slate-800/40">
                      {r.monthVals[m] > 0 ? formatNumber(r.monthVals[m], 1) : "-"}
                    </td>
                  ))}
                  <td className="py-2.5 px-2.5 text-right tabular-nums font-bold text-sky-800 dark:text-sky-300 bg-sky-50/30 dark:bg-sky-950/20 border-r border-slate-100 dark:border-slate-800">
                    {formatNumber(r.rowSum, 1)}
                  </td>
                  <td className="py-2.5 px-2.5 text-right tabular-nums font-bold text-amber-800 dark:text-amber-300 bg-amber-50/30 dark:bg-amber-950/20">
                    {formatNumber(r.rowAvg, 1)}
                  </td>
                </tr>
              );
            })}

            {/* Total Row */}
            <tr className="font-extrabold border-t-2 border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white">
              <td className="py-2.5 px-3.5 sticky left-0 z-10 bg-inherit border-r border-slate-300 dark:border-slate-700">
                ยอดรวมทั้งสิ้น (GRAND TOTAL)
              </td>
              {uniqueMonths.map((m) => (
                <td key={m} className="py-2.5 px-2 text-right tabular-nums border-r border-inherit">
                  {formatNumber(columnTotals[m], 1)}
                </td>
              ))}
              <td className="py-2.5 px-2.5 text-right tabular-nums border-r border-inherit text-sky-700 dark:text-sky-300">
                {formatNumber(grandTotalRow, 1)}
              </td>
              <td className="py-2.5 px-2.5 text-right tabular-nums text-amber-700 dark:text-amber-300">
                {formatNumber(grandTotalRow / uniqueMonths.length, 1)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
