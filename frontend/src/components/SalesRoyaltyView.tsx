"use client";

import React, { useState, useMemo } from "react";
import { DollarSign, Landmark, Percent, Download, Search, Fuel } from "lucide-react";
import { SalesMasterData } from "@/types/hydrocarbon";
import { formatNumber } from "@/lib/utils";
import { ReportingPeriod, THAI_MONTHS } from "@/lib/reporting";
import { ReportingPeriodControls } from "@/components/ReportingPeriodControls";
import { SalesVolumeSummary } from "@/components/SalesVolumeSummary";
import { summarizeSalesVolumes } from "@/lib/sales-reporting";
import * as XLSX from "xlsx";

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

interface SalesRoyaltyViewProps {
  salesData: SalesMasterData;
}

export function SalesRoyaltyView({ salesData }: SalesRoyaltyViewProps) {
  const [selectedProduct, setSelectedProduct] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const availableYears = useMemo(
    () =>
      Array.from(new Set(salesData.flat_records.map((record) => Number(record.ปี))))
        .filter(Number.isFinite)
        .sort((a, b) => b - a),
    [salesData.flat_records],
  );
  const [yearBE, setYearBE] = useState(availableYears[0] || 2569);
  const [period, setPeriod] = useState<ReportingPeriod>("annual");
  const [month, setMonth] = useState("");

  const yearRecords = useMemo(
    () => salesData.flat_records.filter((record) => Number(record.ปี) === yearBE),
    [salesData.flat_records, yearBE],
  );
  const months = useMemo(
    () =>
      THAI_MONTHS.filter((monthName) =>
        yearRecords.some((record) => record.เดือน === monthName),
      ),
    [yearRecords],
  );
  const selectedMonth = months.includes(month) ? month : months[months.length - 1] || "";

  const products = useMemo(() => {
    const s = new Set<string>();
    yearRecords.forEach((r) => s.add(r.ประเภทปิโตรเลียม));
    return Array.from(s);
  }, [yearRecords]);

  // Filter records
  const filteredRecords = useMemo(() => {
    return yearRecords.filter((r) => {
      if (selectedProduct !== "all" && r.ประเภทปิโตรเลียม !== selectedProduct) return false;
      if (period === "monthly" && r.เดือน !== selectedMonth) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const fMatch = (r.แหล่ง_ไฟล์ดิบ || "").toLowerCase().includes(q);
        const opMatch = (r.ผู้ดำเนินการ || "").toLowerCase().includes(q);
        if (!fMatch && !opMatch) return false;
      }
      return true;
    });
  }, [yearRecords, selectedProduct, period, selectedMonth, searchQuery]);

  const fieldSortedRecords = useMemo(
    () =>
      [...filteredRecords].sort((a, b) => {
        const fieldOrder = (a.แหล่ง_ไฟล์ดิบ || "").localeCompare(b.แหล่ง_ไฟล์ดิบ || "");
        if (fieldOrder !== 0) return fieldOrder;
        const productOrder = a.ประเภทปิโตรเลียม.localeCompare(b.ประเภทปิโตรเลียม);
        return productOrder || a.ลำดับเดือน - b.ลำดับเดือน;
      }),
    [filteredRecords],
  );
  const volumeSummaryRecords = useMemo(
    () =>
      yearRecords.filter(
        (record) =>
          selectedProduct === "all" || record.ประเภทปิโตรเลียม === selectedProduct,
      ),
    [yearRecords, selectedProduct],
  );

  // Totals for filtered view
  const { totalVal, totalRoyalty, avgRoyaltyPct } = useMemo(() => {
    let v = 0;
    let roy = 0;
    filteredRecords.forEach((r) => {
      v += Number(r.มูลค่าการขาย_บาท) || 0;
      roy += Number(r.ค่าภาคหลวง_บาท) || 0;
    });
    return {
      totalVal: v,
      totalRoyalty: roy,
      avgRoyaltyPct: v > 0 ? (roy / v) * 100 : 0,
    };
  }, [filteredRecords]);

  const monthlySales = useMemo(
    () =>
      months.map((monthName) => {
        const monthRecords = yearRecords.filter((record) => record.เดือน === monthName);
        return {
          month: monthName,
          value: monthRecords.reduce((sum, record) => sum + (Number(record.มูลค่าการขาย_บาท) || 0), 0),
          royalty: monthRecords.reduce((sum, record) => sum + (Number(record.ค่าภาคหลวง_บาท) || 0), 0),
        };
      }),
    [months, yearRecords],
  );
  const maxMonthlySales = Math.max(...monthlySales.map((item) => item.value), 1);

  // Export to Excel
  const handleExport = () => {
    const wb = XLSX.utils.book_new();
    const rows = fieldSortedRecords.map((r) => ({
      แหล่ง: r.แหล่ง_ไฟล์ดิบ,
      ผู้ดำเนินการ: r.ผู้ดำเนินการ,
      ประเภทปิโตรเลียม: r.ประเภทปิโตรเลียม,
      ปี: r.ปี,
      เดือน: r.เดือน,
      ปริมาณการขาย: r.ปริมาณการขาย_หน่วยหลัก,
      หน่วย: r.หน่วยปริมาณ,
      "มูลค่าการขาย (บาท)": r.มูลค่าการขาย_บาท,
      "ค่าภาคหลวง (บาท)": r.ค่าภาคหลวง_บาท,
      ราคาปากหลุม: r.ราคาปากหลุม_Wellhead_Price,
      หน่วยราคาปากหลุม: r.หน่วยราคาปากหลุม,
      "อัตราค่าภาคหลวง (%)": r.อัตราค่าภาคหลวงที่แท้จริง_Pct,
    }));
    const ws = XLSX.utils.json_to_sheet(rows);
    XLSX.utils.book_append_sheet(wb, ws, "Sales_Data");
    const summaryMonths = period === "monthly" ? [selectedMonth] : months;
    const { fields } = summarizeSalesVolumes(fieldSortedRecords, summaryMonths);
    const { products: productTotals } = summarizeSalesVolumes(
      volumeSummaryRecords,
      summaryMonths,
    );
    const monthlyHeaders = period === "annual" ? summaryMonths : [];
    const periodTotalHeader =
      period === "monthly"
        ? `ปริมาณรวมเดือน ${selectedMonth}`
        : months.includes("ธันวาคม")
          ? "ปริมาณรวมทั้งปี"
          : "ปริมาณรวม YTD";
    const volumeHeaders = [
      "ชื่อแหล่ง",
      "ผู้ดำเนินการ",
      "ประเภทปิโตรเลียม",
      "ตัวชี้วัด",
      "หน่วย",
      ...monthlyHeaders,
      periodTotalHeader,
    ];
    const fieldVolumeSheet = XLSX.utils.aoa_to_sheet([
      volumeHeaders,
      ...fields.map((row) => [
        row.field,
        row.operator,
        row.product,
        row.measure,
        row.unit,
        ...monthlyHeaders.map((monthName) => row.monthlyVolumes[monthName] || 0),
        row.periodTotal,
      ]),
    ]);
    XLSX.utils.book_append_sheet(wb, fieldVolumeSheet, "Volume_By_Field");
    const countryVolumeSheet = XLSX.utils.aoa_to_sheet([
      volumeHeaders.slice(2),
      ...productTotals.map((row) => [
        row.product,
        row.measure,
        row.unit,
        ...monthlyHeaders.map((monthName) => row.monthlyVolumes[monthName] || 0),
        row.periodTotal,
      ]),
    ]);
    XLSX.utils.book_append_sheet(wb, countryVolumeSheet, "Monthly_Volume_Totals");
    const periodLabel =
      period === "monthly"
        ? selectedMonth
        : months.includes("ธันวาคม")
          ? "Annual"
          : "YTD";
    XLSX.writeFile(wb, `PTIT_Petroleum_Sales_Royalty_${yearBE}_${periodLabel}.xlsx`);
  };

  return (
    <div className="space-y-6 mb-8">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">
          PTIT FOCUS STATISTICS · DOMESTIC SALES
        </p>
        <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">
          สถิติการจำหน่ายปิโตรเลียมและค่าภาคหลวง
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Petroleum Sales & Royalty · รายงานตามรูปแบบ PTIT จากกรมเชื้อเพลิงธรรมชาติ (DMF)
        </p>
      </div>

      <ReportingPeriodControls
        period={period}
        setPeriod={setPeriod}
        yearBE={yearBE}
        setYearBE={(year) => {
          setYearBE(year);
          setSelectedProduct("all");
        }}
        yearsBE={availableYears}
        month={selectedMonth}
        setMonth={setMonth}
        months={months}
        latestMonth={months[months.length - 1] || "-"}
      />

      {/* 4-Tier Fiscal Bento KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {/* Total Sales Value */}
        <div className="glass-panel p-5 border-t-2 border-t-sky-500">
          <div className="flex items-center space-x-2 text-sky-600 mb-2">
            <div className="p-2 rounded-xl bg-sky-500/10">
              <DollarSign className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              มูลค่าการจำหน่ายรวม
            </span>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white tabular-nums">
            {formatNumber(totalVal / 1_000_000, 1)}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">ล้านบาท (THB Million)</div>
        </div>

        {/* Total Royalty */}
        <div className="glass-panel p-5 border-t-2 border-t-amber-500">
          <div className="flex items-center space-x-2 text-amber-600 mb-2">
            <div className="p-2 rounded-xl bg-amber-500/10">
              <Landmark className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              ค่าภาคหลวงจัดเก็บรวม
            </span>
          </div>
          <div className="text-2xl font-black text-amber-700 dark:text-amber-400 tabular-nums">
            {formatNumber(totalRoyalty / 1_000_000, 1)}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">ล้านบาท (เข้าคลังแผ่นดิน)</div>
        </div>

        {/* Effective Royalty Rate */}
        <div className="glass-panel p-5 border-t-2 border-t-emerald-500">
          <div className="flex items-center space-x-2 text-emerald-600 mb-2">
            <div className="p-2 rounded-xl bg-emerald-500/10">
              <Percent className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              อัตราค่าภาคหลวงแท้จริง
            </span>
          </div>
          <div className="text-2xl font-black text-emerald-700 dark:text-emerald-400 tabular-nums">
            {avgRoyaltyPct.toFixed(2)}%
          </div>
          <div className="text-xs text-slate-500 mt-0.5">Effective Royalty Rate</div>
        </div>

        {/* Record count */}
        <div className="glass-panel p-5 border-t-2 border-t-indigo-500">
          <div className="flex items-center space-x-2 text-indigo-600 mb-2">
            <div className="p-2 rounded-xl bg-indigo-500/10">
              <Fuel className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              จำนวนธุรกรรมที่ประมวลผล
            </span>
          </div>
          <div className="text-2xl font-black text-indigo-700 dark:text-indigo-400 tabular-nums">
            {filteredRecords.length}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">
            รายการใน{period === "annual"
              ? months.includes("ธันวาคม")
                ? "ทั้งปี"
                : "ช่วง YTD"
              : "เดือน " + selectedMonth} · ปี {yearBE} ({yearBE - 543})
          </div>
        </div>
      </div>

      <section className="glass-panel p-5">
        <div className="flex flex-wrap items-end justify-between gap-2">
          <div>
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              แนวโน้มมูลค่าการจำหน่ายและค่าภาคหลวง
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              ทุกผลิตภัณฑ์ · เปรียบเทียบรายเดือน · ล้านบาท · ปี {yearBE} ({yearBE - 543})
            </p>
          </div>
          <span className="text-xs font-medium text-slate-500">
            เลือกแท่งเดือนเพื่อเปิดรายละเอียดรายเดือน
          </span>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-4 lg:grid-cols-6 xl:grid-cols-12">
          {monthlySales.map((item) => {
            const selected = selectedMonth === item.month;
            return (
              <button
                key={item.month}
                type="button"
                aria-label={`ดูรายงานเดือน ${item.month}`}
                aria-pressed={period === "monthly" && selected}
                onClick={() => {
                  setMonth(item.month);
                  setPeriod("monthly");
                }}
                className="group flex min-h-32 flex-col items-center justify-end gap-2 rounded-xl px-2 py-3 text-center hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-600 dark:hover:bg-slate-900"
              >
                <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  {formatNumber(item.value / 1_000_000, 0)}
                </span>
                <span className="flex h-20 w-full items-end justify-center gap-1 border-b border-slate-200 dark:border-slate-700">
                  <span
                    className={`w-3 rounded-t-sm transition-colors ${selected ? "bg-sky-700" : "bg-sky-400 group-hover:bg-sky-600"}`}
                    style={{ height: `${Math.max((item.value / maxMonthlySales) * 100, 2)}%` }}
                    title={`มูลค่าการจำหน่าย ${formatNumber(item.value / 1_000_000, 1)} ล้านบาท`}
                  />
                  <span
                    className={`w-3 rounded-t-sm transition-colors ${selected ? "bg-amber-600" : "bg-amber-300 group-hover:bg-amber-500"}`}
                    style={{ height: `${Math.max((item.royalty / maxMonthlySales) * 100, 2)}%` }}
                    title={`ค่าภาคหลวง ${formatNumber(item.royalty / 1_000_000, 1)} ล้านบาท`}
                  />
                </span>
                <span className={`text-xs font-bold ${selected ? "text-sky-800 dark:text-sky-300" : "text-slate-700 dark:text-slate-300"}`}>
                  {THAI_SHORT_MONTHS[item.month] || item.month}
                </span>
              </button>
            );
          })}
        </div>
        <div className="mt-4 flex flex-wrap gap-4 border-t border-slate-200 pt-3 text-xs text-slate-600 dark:border-slate-800 dark:text-slate-300">
          <span className="inline-flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-sky-500" />มูลค่าการจำหน่าย</span>
          <span className="inline-flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-sm bg-amber-400" />ค่าภาคหลวง</span>
        </div>
      </section>

      <SalesVolumeSummary
        records={volumeSummaryRecords}
        detailRecords={filteredRecords}
        months={months}
        selectedMonth={selectedMonth}
        period={period}
        yearBE={yearBE}
      />

      {/* Main Table Panel */}
      <div className="glass-panel p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-slate-800">
          <div>
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
              สถิติยอดจำหน่ายปิโตรเลียมและค่าภาคหลวง (Petroleum Sales & Royalty)
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              ข้อมูลจากแบบรายงานการจำหน่ายปิโตรเลียม กรมเชื้อเพลิงธรรมชาติ (DMF)
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Product filter */}
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-semibold"
            >
              <option value="all">ทุกผลิตภัณฑ์</option>
              {products.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>

            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="ค้นหาแหล่งผลิต..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 w-36"
              />
            </div>

            {/* Export */}
            <button
              onClick={handleExport}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>ส่งออก Excel</span>
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto mt-4 rounded-xl border border-slate-200/70 dark:border-slate-800 max-h-[520px] overflow-y-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 z-20 bg-slate-900 text-white shadow-sm font-semibold">
              <tr>
                <th className="py-2.5 px-3">แหล่งผลิต</th>
                <th className="py-2.5 px-3">ผู้ดำเนินการ</th>
                <th className="py-2.5 px-3">ประเภทปิโตรเลียม</th>
                <th className="py-2.5 px-3">เดือน</th>
                <th className="py-2.5 px-3 text-right">ปริมาณการจำหน่าย</th>
                <th className="py-2.5 px-3 text-right">มูลค่าการขาย (บาท)</th>
                <th className="py-2.5 px-3 text-right">ค่าภาคหลวง (บาท)</th>
                <th className="py-2.5 px-3 text-right">ราคาปากหลุม</th>
                <th className="py-2.5 px-3 text-right">อัตราค่าภาคหลวง</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white/70 dark:bg-slate-950/70">
              {fieldSortedRecords.slice(0, 150).map((r, i) => (
                <tr
                  key={i}
                  className={`hover:bg-sky-50/50 dark:hover:bg-slate-800/50 ${
                    i % 2 === 1 ? "bg-slate-50/40 dark:bg-slate-900/20" : ""
                  }`}
                >
                  <td className="py-2 px-3 font-medium text-slate-900 dark:text-slate-100">
                    {r.แหล่ง_ไฟล์ดิบ}
                  </td>
                  <td className="py-2 px-3 text-slate-600 dark:text-slate-400">
                    {r.ผู้ดำเนินการ}
                  </td>
                  <td className="py-2 px-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {r.ประเภทปิโตรเลียม}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-medium text-slate-800 dark:text-slate-200">
                    {r.เดือน}
                  </td>
                  <td className="py-2 px-3 text-right tabular-nums">
                    {formatNumber(r.ปริมาณการขาย_หน่วยหลัก, 1)} {r.หน่วยปริมาณ}
                  </td>
                  <td className="py-2 px-3 text-right tabular-nums font-semibold text-slate-900 dark:text-white">
                    {formatNumber(r.มูลค่าการขาย_บาท, 0)}
                  </td>
                  <td className="py-2 px-3 text-right tabular-nums font-semibold text-amber-700 dark:text-amber-400">
                    {formatNumber(r.ค่าภาคหลวง_บาท, 0)}
                  </td>
                  <td className="py-2 px-3 text-right tabular-nums text-slate-600 dark:text-slate-400">
                    {r.ราคาปากหลุม_Wellhead_Price > 0
                      ? `${formatNumber(r.ราคาปากหลุม_Wellhead_Price, 2)} ${r.หน่วยราคาปากหลุม}`
                      : "-"}
                  </td>
                  <td className="py-2 px-3 text-right tabular-nums text-emerald-600 dark:text-emerald-400 font-semibold">
                    {r.อัตราค่าภาคหลวงที่แท้จริง_Pct > 0
                      ? `${r.อัตราค่าภาคหลวงที่แท้จริง_Pct.toFixed(2)}%`
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
