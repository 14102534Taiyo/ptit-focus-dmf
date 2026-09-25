"use client";

import React, { useState, useMemo } from "react";
import { DollarSign, Landmark, Percent, Download, Search, Fuel } from "lucide-react";
import { SalesMasterData, SalesRecord } from "@/types/hydrocarbon";
import { formatNumber, formatInteger } from "@/lib/utils";
import * as XLSX from "xlsx";

interface SalesRoyaltyViewProps {
  salesData: SalesMasterData;
}

export function SalesRoyaltyView({ salesData }: SalesRoyaltyViewProps) {
  const [selectedProduct, setSelectedProduct] = useState<string>("all");
  const [selectedMonth, setSelectedMonth] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const months = useMemo(() => {
    const s = new Set<string>();
    salesData.flat_records.forEach((r) => s.add(r.เดือน));
    return Array.from(s);
  }, [salesData]);

  const products = useMemo(() => {
    const s = new Set<string>();
    salesData.flat_records.forEach((r) => s.add(r.ประเภทปิโตรเลียม));
    return Array.from(s);
  }, [salesData]);

  // Filter records
  const filteredRecords = useMemo(() => {
    return salesData.flat_records.filter((r) => {
      if (selectedProduct !== "all" && r.ประเภทปิโตรเลียม !== selectedProduct) return false;
      if (selectedMonth !== "all" && r.เดือน !== selectedMonth) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const fMatch = (r.แหล่ง_ไฟล์ดิบ || "").toLowerCase().includes(q);
        const opMatch = (r.ผู้ดำเนินการ || "").toLowerCase().includes(q);
        if (!fMatch && !opMatch) return false;
      }
      return true;
    });
  }, [salesData, selectedProduct, selectedMonth, searchQuery]);

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

  // Export to Excel
  const handleExport = () => {
    const wb = XLSX.utils.book_new();
    const rows = filteredRecords.map((r) => ({
      ปี: r.ปี,
      เดือน: r.เดือน,
      ประเภทปิโตรเลียม: r.ประเภทปิโตรเลียม,
      แหล่ง: r.แหล่ง_ไฟล์ดิบ,
      ผู้ดำเนินการ: r.ผู้ดำเนินการ,
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
    XLSX.writeFile(wb, `PTIT_Petroleum_Sales_Royalty_2026.xlsx`);
  };

  return (
    <div className="space-y-6 mb-8">
      {/* 4-Tier Fiscal Bento KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
            {formatNumber(salesData.kpis.total_sales_value_million_thb, 1)}
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
            {formatNumber(salesData.kpis.total_royalty_million_thb, 1)}
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
            {salesData.kpis.effective_royalty_rate_pct.toFixed(2)}%
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
            {salesData.flat_records.length}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">รายการ (ม.ค. - ก.ค. 2026)</div>
        </div>
      </div>

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

            {/* Month filter */}
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-semibold"
            >
              <option value="all">ทุกเดือน</option>
              {months.map((m) => (
                <option key={m} value={m}>
                  {m}
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
                <th className="py-2.5 px-3">เดือน</th>
                <th className="py-2.5 px-3">ประเภทปิโตรเลียม</th>
                <th className="py-2.5 px-3">แหล่งผลิต</th>
                <th className="py-2.5 px-3">ผู้ดำเนินการ</th>
                <th className="py-2.5 px-3 text-right">ปริมาณการจำหน่าย</th>
                <th className="py-2.5 px-3 text-right">มูลค่าการขาย (บาท)</th>
                <th className="py-2.5 px-3 text-right">ค่าภาคหลวง (บาท)</th>
                <th className="py-2.5 px-3 text-right">ราคาปากหลุม</th>
                <th className="py-2.5 px-3 text-right">อัตราค่าภาคหลวง</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white/70 dark:bg-slate-950/70">
              {filteredRecords.slice(0, 150).map((r, i) => (
                <tr
                  key={i}
                  className={`hover:bg-sky-50/50 dark:hover:bg-slate-800/50 ${
                    i % 2 === 1 ? "bg-slate-50/40 dark:bg-slate-900/20" : ""
                  }`}
                >
                  <td className="py-2 px-3 font-medium text-slate-800 dark:text-slate-200">
                    {r.เดือน}
                  </td>
                  <td className="py-2 px-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {r.ประเภทปิโตรเลียม}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-medium text-slate-900 dark:text-slate-100">
                    {r.แหล่ง_ไฟล์ดิบ}
                  </td>
                  <td className="py-2 px-3 text-slate-600 dark:text-slate-400">
                    {r.ผู้ดำเนินการ}
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
