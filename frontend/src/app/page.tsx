"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { BentoKpiGrid } from "@/components/BentoKpiGrid";
import { ProductionMatrixTable } from "@/components/ProductionMatrixTable";
import { ProductionTrendCharts } from "@/components/ProductionTrendCharts";
import { DynamicPivotStudio } from "@/components/DynamicPivotStudio";
import { SalesRoyaltyView } from "@/components/SalesRoyaltyView";
import { PetroleumUnitConverter } from "@/components/PetroleumUnitConverter";
import { SystemStatusView } from "@/components/SystemStatusView";

// Import pre-aggregated JSON datasets
import prodDataRaw from "../../public/data/production_master.json";
import salesDataRaw from "../../public/data/sales_master.json";
import manifestRaw from "../../public/data/sync_manifest.json";
import { ProductionMasterData, SalesMasterData, SyncManifest } from "@/types/hydrocarbon";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("production");
  const [unitMode, setUnitMode] = useState<"rate" | "boed">("rate");
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const prodData = prodDataRaw as unknown as ProductionMasterData;
  const salesData = salesDataRaw as unknown as SalesMasterData;
  const manifest = manifestRaw as unknown as SyncManifest;

  // Sync theme with HTML document class
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100 pb-16">
      {/* Global Executive Navigation Header */}
      <Header
        manifest={manifest}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        unitMode={unitMode}
        setUnitMode={setUnitMode}
        theme={theme}
        setTheme={setTheme}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Executive Letterhead Banner (Prints seamlessly in A4 Landscape) */}
        <div className="glass-panel p-6 mb-6 text-center border-t-4 border-t-sky-700 bg-white/90 dark:bg-slate-900/90 shadow-sm">
          <div className="inline-block mb-1">
            <span className="text-[11px] font-bold tracking-[0.2em] uppercase text-sky-800 dark:text-sky-300">
              PETROLEUM INSTITUTE OF THAILAND • FOCUS STATISTICS
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-950 dark:text-white tracking-tight">
            รายงานสถิติการผลิตและยอดจำหน่ายปิโตรเลียมในประเทศ ประจำปี 2569
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 font-medium">
            Domestic Petroleum Production & Fiscal Sales Intelligence (January - August 2026)
          </p>

          <div className="mt-3.5 inline-flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200/60 dark:border-slate-800/80 pt-2.5">
            <div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">แหล่งข้อมูล:</span> กรมเชื้อเพลิงธรรมชาติ (DMF) และ กรมการพลังงานทหาร (DEDP)
            </div>
            <div>•</div>
            <div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">การรับรอง:</span> รวมน้ำมันดิบแหล่งฝาง 610.4 BPD
            </div>
            <div>•</div>
            <div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">ระบบประมวลผล:</span> Decoupled GitHub Actions ETL Pipeline
            </div>
          </div>
        </div>

        {/* Tab 1: Production Intelligence */}
        {activeTab === "production" && (
          <div className="space-y-6">
            {/* Bento KPI Grid */}
            <BentoKpiGrid kpis={prodData.kpis} unitMode={unitMode} />

            {/* Time-Series Charts & Operator Breakdown */}
            <ProductionTrendCharts data={prodData} />

            {/* Flagship 12-Month Production Matrix Table */}
            <ProductionMatrixTable data={prodData} />

            {/* Dynamic Slicing & Pivot Studio */}
            <DynamicPivotStudio records={prodData.flat_records} />
          </div>
        )}

        {/* Tab 2: Sales & Royalty Intelligence */}
        {activeTab === "sales" && (
          <SalesRoyaltyView salesData={salesData} />
        )}

        {/* Tab 3: Petroleum Unit Converter Hub */}
        {activeTab === "converter" && (
          <PetroleumUnitConverter />
        )}

        {/* Tab 4: System Health & GitHub Actions ETL */}
        {activeTab === "system" && (
          <SystemStatusView manifest={manifest} />
        )}
      </main>

      {/* Sovereign Executive Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-16 pt-8 border-t border-slate-200/80 dark:border-slate-800/80 text-center text-xs text-slate-500 dark:text-slate-400 no-print">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 rounded-md bg-sky-600 text-white font-extrabold flex items-center justify-center text-[10px]">
              P
            </div>
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              สถาบันปิโตรเลียมแห่งประเทศไทย (Petroleum Institute of Thailand)
            </span>
          </div>
          <div>
            PTIT Focus Statistics • Sovereign Hydrocarbon Intelligence Platform v2.0
          </div>
        </div>
      </footer>
    </div>
  );
}
