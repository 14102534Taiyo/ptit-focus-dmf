"use client";

import React, { useState, useMemo } from "react";
import { Search, Download, ShieldCheck, Filter } from "lucide-react";
import { ProductionMasterData, MatrixRow } from "@/types/hydrocarbon";
import { formatNumber } from "@/lib/utils";
import * as XLSX from "xlsx";

interface ProductionMatrixTableProps {
  data: ProductionMasterData;
}

const THAI_MONTH_COLUMNS = [
  "มกราคม",
  "กุมภาพันธ์",
  "มีนาคม",
  "เมษายน",
  "พฤษภาคม",
  "มิถุนายน",
  "กรกฎาคม",
  "สิงหาคม",
  "กันยายน",
  "ตุลาคม",
  "พฤศจิกายน",
  "ธันวาคม",
];

const THAI_SHORT_MONTHS: Record<string, string> = {
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

export function ProductionMatrixTable({ data }: ProductionMatrixTableProps) {
  const [selectedMetric, setSelectedMetric] = useState<"gas_mmscfd" | "condensate_bpd" | "crude_bpd" | "total_boed">("gas_mmscfd");
  const [regionFilter, setRegionFilter] = useState<"all" | "Onshore" | "Offshore">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const activeMatrix = data.matrices[selectedMetric];
  const unitLabel = activeMatrix?.unit || "MMSCFD";

  // Filter rows
  const filteredRows = useMemo(() => {
    if (!activeMatrix?.rows) return [];
    return activeMatrix.rows.filter((row) => {
      // Region match
      if (regionFilter !== "all" && row.PTIT_Region !== regionFilter) return false;
      // Search match
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const fieldMatch = String(row.PTIT_Operator_Field || "").toLowerCase().includes(query);
        const regionMatch = String(row.PTIT_Region || "").toLowerCase().includes(query);
        if (!fieldMatch && !regionMatch) return false;
      }
      return true;
    });
  }, [activeMatrix, regionFilter, searchQuery]);

  // Compute Subtotals and Grand Total
  const { onshoreRows, offshoreRows, onshoreSubtotal, offshoreSubtotal, grandTotal } = useMemo(() => {
    const onshore: MatrixRow[] = [];
    const offshore: MatrixRow[] = [];

    filteredRows.forEach((r) => {
      if (r.PTIT_Region === "Onshore") onshore.push(r);
      else offshore.push(r);
    });

    const sumList = (list: MatrixRow[]) => {
      const sum: Record<string, number> = {};
      THAI_MONTH_COLUMNS.forEach((m) => (sum[m] = 0));
      sum["เฉลี่ยทั้งปี"] = 0;
      sum["สะสมทั้งปี"] = 0;

      list.forEach((r) => {
        THAI_MONTH_COLUMNS.forEach((m) => {
          sum[m] += Number(r[m]) || 0;
        });
        sum["เฉลี่ยทั้งปี"] += Number(r["เฉลี่ยทั้งปี"]) || 0;
        sum["สะสมทั้งปี"] += Number(r["สะสมทั้งปี"]) || 0;
      });
      return sum;
    };

    return {
      onshoreRows: onshore,
      offshoreRows: offshore,
      onshoreSubtotal: sumList(onshore),
      offshoreSubtotal: sumList(offshore),
      grandTotal: sumList(filteredRows),
    };
  }, [filteredRows]);

  // Client-side Excel Export
  const handleExportExcel = () => {
    const wb = XLSX.utils.book_new();
    const exportRows: any[] = [];

    // Title rows
    exportRows.push(["PETROLEUM INSTITUTE OF THAILAND"]);
    exportRows.push([`12-MONTH DOMESTIC PETROLEUM PRODUCTION MATRIX (2569) - ${activeMatrix.column_name}`]);
    exportRows.push([`Unit: ${unitLabel}`]);
    exportRows.push([]);

    // Table Header
    const headers = ["Operator / Field", ...THAI_MONTH_COLUMNS, "เฉลี่ยทั้งปี", "สะสมทั้งปี"];
    exportRows.push(headers);

    // Helper for rows
    const appendRow = (label: string, rowData: Record<string, any>) => {
      const r: (string | number)[] = [label];
      THAI_MONTH_COLUMNS.forEach((m) => r.push(rowData[m] ? Number(rowData[m]) : "-"));
      r.push(rowData["เฉลี่ยทั้งปี"] ? Number(rowData["เฉลี่ยทั้งปี"]) : "-");
      r.push(rowData["สะสมทั้งปี"] ? Number(rowData["สะสมทั้งปี"]) : "-");
      exportRows.push(r);
    };

    // Onshore
    if (onshoreRows.length > 0) {
      exportRows.push(["--- ONSHORE FIELDS ---"]);
      onshoreRows.forEach((r) => appendRow(r.PTIT_Operator_Field, r));
      appendRow("SUBTOTAL ONSHORE", onshoreSubtotal);
      exportRows.push([]);
    }

    // Offshore
    if (offshoreRows.length > 0) {
      exportRows.push(["--- OFFSHORE FIELDS (GULF OF THAILAND) ---"]);
      offshoreRows.forEach((r) => appendRow(r.PTIT_Operator_Field, r));
      appendRow("SUBTOTAL OFFSHORE", offshoreSubtotal);
      exportRows.push([]);
    }

    // Grand Total
    appendRow("GRAND TOTAL THAILAND", grandTotal);

    const ws = XLSX.utils.aoa_to_sheet(exportRows);
    XLSX.utils.book_append_sheet(wb, ws, "Matrix_2569");
    XLSX.writeFile(wb, `PTIT_Focus_Production_Matrix_2569_${selectedMetric}.xlsx`);
  };

  return (
    <div className="glass-panel p-5 mb-8">
      {/* Table Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-slate-800">
        <div>
          <h2 className="text-base font-extrabold text-slate-900 dark:text-white tracking-tight flex items-center space-x-2">
            <span>ตารางการผลิตปิโตรเลียม 12 เดือน (12-Month Production Matrix)</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            ตัวชี้วัดปัจจุบัน: <span className="font-semibold text-sky-600 dark:text-sky-400">{activeMatrix?.column_name}</span> ({unitLabel})
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Metric Selector */}
          <div className="inline-flex rounded-xl p-1 bg-slate-100 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-xs">
            {[
              { key: "gas_mmscfd", label: "ก๊าซ (MMSCFD)" },
              { key: "condensate_bpd", label: "คอนเดนเสท (BPD)" },
              { key: "crude_bpd", label: "น้ำมันดิบ (BPD)" },
              { key: "total_boed", label: "รวม (BOED)" },
            ].map((m) => (
              <button
                key={m.key}
                onClick={() => setSelectedMetric(m.key as any)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  selectedMetric === m.key
                    ? "bg-white dark:bg-slate-800 text-sky-700 dark:text-sky-300 shadow-sm font-semibold"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>

          {/* Region Filter */}
          <div className="inline-flex rounded-xl p-1 bg-slate-100 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-xs">
            {[
              { key: "all", label: "ทั้งหมด" },
              { key: "Onshore", label: "บนบก" },
              { key: "Offshore", label: "ในอ่าว" },
            ].map((rf) => (
              <button
                key={rf.key}
                onClick={() => setRegionFilter(rf.key as any)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  regionFilter === rf.key
                    ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm font-semibold"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                {rf.label}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="ค้นหาแหล่ง / บริษัท..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500 w-36 sm:w-48 text-slate-800 dark:text-slate-200"
            />
          </div>

          {/* Export Excel Button */}
          <button
            onClick={handleExportExcel}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Excel Matrix</span>
          </button>
        </div>
      </div>

      {/* Responsive Matrix Table Container */}
      <div className="overflow-x-auto mt-4 rounded-xl border border-slate-200/70 dark:border-slate-800 shadow-sm max-h-[640px] overflow-y-auto">
        <table className="w-full text-left border-collapse text-xs">
          {/* Sticky Header */}
          <thead className="sticky top-0 z-20 bg-slate-900 text-white shadow-sm font-semibold">
            <tr>
              <th className="py-3 px-3.5 min-w-[220px] sticky left-0 z-30 bg-slate-900 border-r border-slate-800">
                Operator / Field (แหล่งสัมปทาน)
              </th>
              {THAI_MONTH_COLUMNS.map((m) => (
                <th key={m} className="py-3 px-2 text-right min-w-[70px] border-r border-slate-800/80">
                  {THAI_SHORT_MONTHS[m]}
                </th>
              ))}
              <th className="py-3 px-2.5 text-right min-w-[85px] bg-sky-950 border-r border-slate-800 text-sky-200">
                เฉลี่ย/วัน
              </th>
              <th className="py-3 px-2.5 text-right min-w-[85px] bg-amber-950 text-amber-200">
                สะสมทั้งปี
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white/70 dark:bg-slate-950/70">
            {/* 1. Onshore Section */}
            {onshoreRows.length > 0 && (
              <>
                <tr className="bg-slate-100/90 dark:bg-slate-900/90 font-bold text-slate-800 dark:text-slate-200">
                  <td colSpan={15} className="py-2 px-3.5 tracking-wider uppercase text-[11px] text-sky-800 dark:text-sky-300">
                    ─── บนบก (Onshore Fields)
                  </td>
                </tr>
                {onshoreRows.map((r, idx) => renderDataRow(r, idx, unitLabel))}
                {renderSubtotalRow("รวมบนบก (Subtotal Onshore)", onshoreSubtotal, unitLabel, "bg-sky-50/80 dark:bg-sky-950/40 text-sky-900 dark:text-sky-200")}
              </>
            )}

            {/* 2. Offshore Section */}
            {offshoreRows.length > 0 && (
              <>
                <tr className="bg-slate-100/90 dark:bg-slate-900/90 font-bold text-slate-800 dark:text-slate-200">
                  <td colSpan={15} className="py-2 px-3.5 tracking-wider uppercase text-[11px] text-sky-800 dark:text-sky-300">
                    ─── ในอ่าวไทย (Offshore - Gulf of Thailand)
                  </td>
                </tr>
                {offshoreRows.map((r, idx) => renderDataRow(r, idx, unitLabel))}
                {renderSubtotalRow("รวมในอ่าวไทย (Subtotal Offshore)", offshoreSubtotal, unitLabel, "bg-sky-50/80 dark:bg-sky-950/40 text-sky-900 dark:text-sky-200")}
              </>
            )}

            {/* 3. Grand Total */}
            {renderSubtotalRow(
              "ยอดรวมทั้งประเทศ (GRAND TOTAL THAILAND)",
              grandTotal,
              unitLabel,
              "bg-gradient-to-r from-amber-100/90 via-amber-50 to-amber-100/90 dark:from-amber-950/80 dark:to-amber-900/80 text-amber-950 dark:text-amber-100 font-extrabold text-sm border-t-2 border-amber-500"
            )}
          </tbody>
        </table>
      </div>

      {/* Footnotes */}
      <div className="mt-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between text-[11px] text-slate-500 dark:text-slate-400 gap-2">
        <div>
          หมายเหตุ: 1. ตัวเลขอัตราเฉลี่ยต่อวันคำนวณตามจำนวนวันดำเนินการจริงของแต่ละเดือน (รวม 29 วันของ ก.พ. ปีอธิกสุรทิน)
          2. ยอดสะสมทั้งปี: ก๊าซเป็น BCF (พันล้าน ลบ.ฟุต), ของเหลวเป็น MMbbl (ล้านบาร์เรล), BOED เป็น MMBOE
        </div>
        <div className="font-semibold text-slate-600 dark:text-slate-300">
          Source: DMF & DEDP • PTIT Focus Statistics
        </div>
      </div>
    </div>
  );
}

function renderDataRow(row: MatrixRow, idx: number, unitLabel: string) {
  const isFang = String(row.PTIT_Operator_Field || "").toLowerCase().includes("fang");
  const isZebra = idx % 2 === 1;

  return (
    <tr
      key={row.PTIT_Operator_Field + idx}
      className={`hover:bg-sky-50/50 dark:hover:bg-slate-800/50 transition-colors ${
        isZebra ? "bg-slate-50/40 dark:bg-slate-900/20" : ""
      }`}
    >
      <td className="py-2.5 px-3.5 font-medium text-slate-900 dark:text-slate-100 sticky left-0 z-10 bg-white/95 dark:bg-slate-950/95 border-r border-slate-200/70 dark:border-slate-800">
        <div className="flex items-center space-x-2">
          <span>{row.PTIT_Operator_Field}</span>
          {isFang && (
            <span className="inline-flex items-center space-x-0.5 px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
              <ShieldCheck className="w-2.5 h-2.5" />
              <span>DEDP</span>
            </span>
          )}
        </div>
      </td>

      {THAI_MONTH_COLUMNS.map((m) => {
        const val = row[m];
        return (
          <td key={m} className="py-2.5 px-2 text-right tabular-nums text-slate-700 dark:text-slate-300 border-r border-slate-100 dark:border-slate-800/40">
            {val !== undefined && val !== null && Number(val) > 0.0001
              ? formatNumber(Number(val), unitLabel.includes("MMSCF") ? 2 : 0)
              : "-"}
          </td>
        );
      })}

      <td className="py-2.5 px-2.5 text-right tabular-nums font-bold text-sky-800 dark:text-sky-300 bg-sky-50/30 dark:bg-sky-950/20 border-r border-slate-100 dark:border-slate-800">
        {row["เฉลี่ยทั้งปี"] ? formatNumber(Number(row["เฉลี่ยทั้งปี"]), unitLabel.includes("MMSCF") ? 2 : 0) : "-"}
      </td>
      <td className="py-2.5 px-2.5 text-right tabular-nums font-bold text-amber-800 dark:text-amber-300 bg-amber-50/30 dark:bg-amber-950/20">
        {row["สะสมทั้งปี"] ? formatNumber(Number(row["สะสมทั้งปี"]), 2) : "-"}
      </td>
    </tr>
  );
}

function renderSubtotalRow(
  label: string,
  sums: Record<string, number>,
  unitLabel: string,
  extraClasses: string
) {
  return (
    <tr className={`font-bold border-y border-slate-200 dark:border-slate-700 ${extraClasses}`}>
      <td className="py-2.5 px-3.5 sticky left-0 z-10 bg-inherit border-r border-slate-200 dark:border-slate-700">
        {label}
      </td>
      {THAI_MONTH_COLUMNS.map((m) => (
        <td key={m} className="py-2.5 px-2 text-right tabular-nums border-r border-inherit">
          {sums[m] > 0 ? formatNumber(sums[m], unitLabel.includes("MMSCF") ? 2 : 0) : "-"}
        </td>
      ))}
      <td className="py-2.5 px-2.5 text-right tabular-nums border-r border-inherit">
        {sums["เฉลี่ยทั้งปี"] > 0 ? formatNumber(sums["เฉลี่ยทั้งปี"], unitLabel.includes("MMSCF") ? 2 : 0) : "-"}
      </td>
      <td className="py-2.5 px-2.5 text-right tabular-nums">
        {sums["สะสมทั้งปี"] > 0 ? formatNumber(sums["สะสมทั้งปี"], 2) : "-"}
      </td>
    </tr>
  );
}
