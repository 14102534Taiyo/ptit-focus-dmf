"use client";

import React from "react";
import { ShieldCheck, Printer, RefreshCw, Layers, Database } from "lucide-react";
import { SyncManifest } from "@/types/hydrocarbon";

interface HeaderProps {
  manifest?: SyncManifest | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  unitMode: "rate" | "boed";
  setUnitMode: (mode: "rate" | "boed") => void;
  theme: "light" | "dark";
  setTheme: (theme: "light" | "dark") => void;
}

export function Header({
  manifest,
  activeTab,
  setActiveTab,
  unitMode,
  setUnitMode,
  theme,
  setTheme,
}: HeaderProps) {
  const syncDate = manifest?.timestamp
    ? new Date(manifest.timestamp).toLocaleDateString("th-TH", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "อัปเดตล่าสุด: ส.ค. 2569";

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-200/80 dark:border-slate-800/80 backdrop-blur-xl bg-white/85 dark:bg-slate-950/85 mb-6 shadow-sm no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Brand & Masthead */}
          <div className="flex items-center space-x-3.5">
            <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-sky-600 to-indigo-900 text-white font-black text-sm tracking-wider shadow-md shadow-sky-600/25">
              PTIT
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight">
                  Siam Hydrocarbon Intelligence
                </h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300/60 dark:border-amber-700/60">
                  PTIT FOCUS 2026
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                สถาบันปิโตรเลียมแห่งประเทศไทย • Petroleum Institute of Thailand
              </p>
            </div>
          </div>

          {/* Controls & Status Bar */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Live Sync Status Badge */}
            <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-100/90 dark:bg-slate-900/90 border border-slate-200/80 dark:border-slate-800 text-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-live-pulse shadow-sm shadow-emerald-500/50" />
              <span className="text-slate-700 dark:text-slate-300 font-medium hidden sm:inline">
                DMF Portal:
              </span>
              <span className="text-emerald-700 dark:text-emerald-400 font-semibold">
                {manifest?.latest_production_month || "สิงหาคม"} 2569 (ซิงค์แล้ว)
              </span>
            </div>

            {/* Global Unit Switcher */}
            <div className="inline-flex rounded-xl p-1 bg-slate-100 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-xs">
              <button
                onClick={() => setUnitMode("rate")}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  unitMode === "rate"
                    ? "bg-white dark:bg-slate-800 text-sky-700 dark:text-sky-300 shadow-sm"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                MMSCFD / BPD
              </button>
              <button
                onClick={() => setUnitMode("boed")}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  unitMode === "boed"
                    ? "bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-300 shadow-sm"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                BOED (เทียบเท่าน้ำมัน)
              </button>
            </div>

            {/* Print A4 Executive Button */}
            <button
              onClick={() => window.print()}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium transition-colors shadow-sm"
              title="พิมพ์รายงาน A4 Executive Landscape"
            >
              <Printer className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">พิมพ์รายงาน (A4)</span>
            </button>

            {/* Dark/Light Toggle */}
            <button
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              className="p-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 text-xs shadow-sm"
              title="สลับโหมด Dark / Light"
            >
              {theme === "light" ? "🌙" : "☀️"}
            </button>
          </div>
        </div>

        {/* Executive Navigation Tabs */}
        <nav className="flex space-x-2 mt-4 pt-3 border-t border-slate-200/60 dark:border-slate-800/60 overflow-x-auto no-scrollbar">
          {[
            { id: "production", label: "สถิติการผลิตในประเทศ (Production)", icon: Layers },
            { id: "sales", label: "ยอดจำหน่ายและค่าภาคหลวง (Sales & Royalty)", icon: Database },
            { id: "converter", label: "แปลงหน่วยพลังงานมาตรฐาน PTIT", icon: RefreshCw },
            { id: "system", label: "ระบบ Auto-Sync (GitHub Actions ETL)", icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-sky-600 text-white shadow-sm shadow-sky-600/30"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-white" : "text-slate-500"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
