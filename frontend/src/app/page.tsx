"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { ProductionReportView } from "@/components/ProductionReportView";
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
        latestProductionYearBE={prodData.kpis.reporting_year_be}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        unitMode={unitMode}
        setUnitMode={setUnitMode}
        theme={theme}
        setTheme={setTheme}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Tab 1: Production Intelligence */}
        {activeTab === "production" && (
          <ProductionReportView data={prodData} unitMode={unitMode} />
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
