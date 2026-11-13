"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Header } from "@/components/Header";
import { ProductionReportView } from "@/components/ProductionReportView";
import { SalesRoyaltyView } from "@/components/SalesRoyaltyView";
import { PetroleumUnitConverter } from "@/components/PetroleumUnitConverter";
import { SystemStatusView } from "@/components/SystemStatusView";

// Import pre-aggregated JSON datasets
import prodDataRaw from "../../public/data/production_master.json";
import salesDataRaw from "../../public/data/sales_master.json";
import manifestRaw from "../../public/data/sync_manifest.json";
import yearsIndexRaw from "../../public/data/years_index.json";
import {
  ProductionMasterData,
  ProductionRecord,
  SalesMasterData,
  SalesRecord,
  SyncManifest,
} from "@/types/hydrocarbon";
import { YearsIndex, useYearRecords, yearsFromIndex } from "@/lib/year-data";

const prodBase = prodDataRaw as unknown as ProductionMasterData;
const salesBase = salesDataRaw as unknown as SalesMasterData;
const manifest = manifestRaw as unknown as SyncManifest;
const yearsIndex = yearsIndexRaw as unknown as YearsIndex;
const productionYears = yearsFromIndex(yearsIndex, "production");
const salesYears = yearsFromIndex(yearsIndex, "sales");

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("production");
  const [unitMode, setUnitMode] = useState<"rate" | "boed">("rate");
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Latest year ships in the bundle; older years are fetched when selected
  const prodYears = useYearRecords<ProductionRecord>("production", prodBase.flat_records);
  const saleYears = useYearRecords<SalesRecord>("sales", salesBase.flat_records);
  const prodData = useMemo(
    () => ({ ...prodBase, flat_records: prodYears.records }),
    [prodYears.records],
  );
  const salesData = useMemo(
    () => ({ ...salesBase, flat_records: saleYears.records }),
    [saleYears.records],
  );

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
          <ProductionReportView
            data={prodData}
            unitMode={unitMode}
            availableYears={productionYears}
            onYearSelected={prodYears.ensureYear}
            loadingYear={prodYears.loadingYear}
            errorYear={prodYears.errorYear}
          />
        )}

        {/* Tab 2: Sales & Royalty Intelligence */}
        {activeTab === "sales" && (
          <SalesRoyaltyView
            salesData={salesData}
            availableYears={salesYears}
            onYearSelected={saleYears.ensureYear}
            loadingYear={saleYears.loadingYear}
            errorYear={saleYears.errorYear}
          />
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
