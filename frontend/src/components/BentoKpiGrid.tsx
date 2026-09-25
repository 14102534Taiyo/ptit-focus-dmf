"use client";

import React from "react";
import { Flame, Droplets, Gauge, ShieldCheck, TrendingUp } from "lucide-react";
import { ProductionKPIs } from "@/types/hydrocarbon";
import { formatNumber, formatInteger } from "@/lib/utils";

interface BentoKpiGridProps {
  kpis: ProductionKPIs;
  unitMode: "rate" | "boed";
}

export function BentoKpiGrid({ kpis, unitMode }: BentoKpiGridProps) {
  // Conversion factors (PTIT standard)
  // Gas BOED: gas_mmscfd * 1000 * 0.178
  // Condensate BOED: cond_bpd * 0.95
  // Crude BOED: crude_bpd * 1.0
  const gasBoed = kpis.latest_gas_mmscfd * 1000 * 0.178;
  const condBoed = kpis.latest_cond_bpd * 0.95;
  const crudeBoed = kpis.latest_crude_bpd * 1.0;
  const totalBoed = gasBoed + condBoed + crudeBoed;

  const gasShare = totalBoed > 0 ? (gasBoed / totalBoed) * 100 : 0;
  const condShare = totalBoed > 0 ? (condBoed / totalBoed) * 100 : 0;
  const crudeShare = totalBoed > 0 ? (crudeBoed / totalBoed) * 100 : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* 1. Natural Gas KPI */}
      <div className="glass-panel p-5 relative overflow-hidden border-t-2 border-t-cyan-500/80">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                ก๊าซธรรมชาติ (Natural Gas)
              </h3>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                {unitMode === "boed" ? "เทียบเท่าน้ำมันดิบ (BOED)" : "อัตราผลิต (MMSCFD)"}
              </p>
            </div>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-800 dark:bg-cyan-950/80 dark:text-cyan-300">
            {gasShare.toFixed(1)}% พลังงานรวม
          </span>
        </div>

        <div className="my-2">
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums tracking-tight">
            {unitMode === "boed"
              ? formatInteger(gasBoed)
              : formatNumber(kpis.latest_gas_mmscfd, 2)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            {unitMode === "boed" ? "บาร์เรล/วัน (BOED)" : "ล้าน ลบ.ฟุต/วัน (MMSCFD)"}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>เดือน {kpis.latest_month} 2569</span>
          <span className="text-cyan-600 dark:text-cyan-400 font-medium">
            ~{(kpis.latest_gas_mmscfd * 31 / 1000).toFixed(2)} BCF/เดือน
          </span>
        </div>
      </div>

      {/* 2. Condensate KPI */}
      <div className="glass-panel p-5 relative overflow-hidden border-t-2 border-t-violet-500/80">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-violet-500/10 text-violet-600 dark:text-violet-400">
              <Droplets className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                คอนเดนเสท (Condensate)
              </h3>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                {unitMode === "boed" ? "เทียบเท่าน้ำมันดิบ (BOED)" : "อัตราผลิต (BPD)"}
              </p>
            </div>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 text-violet-800 dark:bg-violet-950/80 dark:text-violet-300">
            {condShare.toFixed(1)}% พลังงานรวม
          </span>
        </div>

        <div className="my-2">
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums tracking-tight">
            {unitMode === "boed"
              ? formatInteger(condBoed)
              : formatInteger(kpis.latest_cond_bpd)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            {unitMode === "boed" ? "บาร์เรล/วัน (BOED)" : "บาร์เรล/วัน (BPD)"}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>เดือน {kpis.latest_month} 2569</span>
          <span className="text-violet-600 dark:text-violet-400 font-medium">
            ~{(kpis.latest_cond_bpd * 31 / 1_000_000).toFixed(2)} MMbbl/เดือน
          </span>
        </div>
      </div>

      {/* 3. Crude Oil KPI */}
      <div className="glass-panel p-5 relative overflow-hidden border-t-2 border-t-amber-500/80">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <Gauge className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                น้ำมันดิบ (Crude Oil)
              </h3>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                {unitMode === "boed" ? "เทียบเท่าน้ำมันดิบ (BOED)" : "อัตราผลิต (BPD)"}
              </p>
            </div>
          </div>
          <span className="inline-flex items-center space-x-1 text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300">
            <ShieldCheck className="w-3 h-3 text-emerald-600" />
            <span>DEDP FANG รวมแล้ว</span>
          </span>
        </div>

        <div className="my-2">
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white tabular-nums tracking-tight">
            {formatInteger(kpis.latest_crude_bpd)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            บาร์เรล/วัน (BPD)
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>เดือน {kpis.latest_month} 2569</span>
          <span className="text-amber-600 dark:text-amber-400 font-medium">
            ~{(kpis.latest_crude_bpd * 31 / 1_000_000).toFixed(2)} MMbbl/เดือน
          </span>
        </div>
      </div>

      {/* 4. Total BOED KPI */}
      <div className="glass-panel p-5 relative overflow-hidden border-t-2 border-t-emerald-500/80 bg-gradient-to-b from-emerald-50/20 to-transparent dark:from-emerald-950/10">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                รวมปิโตรเลียมเทียบเท่าน้ำมัน
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                Total Hydrocarbon Equivalence
              </p>
            </div>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-600 text-white shadow-sm">
            100% รวมทุกชนิด
          </span>
        </div>

        <div className="my-2">
          <div className="text-3xl font-black text-emerald-700 dark:text-emerald-400 tabular-nums tracking-tight">
            {formatInteger(totalBoed)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            บาร์เรลเทียบเท่าน้ำมันดิบ/วัน (BOED)
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>ทั้งประเทศ 30 แหล่งผลิต</span>
          <span className="text-emerald-700 dark:text-emerald-400 font-bold">
            ~{(totalBoed * 31 / 1_000_000).toFixed(2)} MMBOE/เดือน
          </span>
        </div>
      </div>
    </div>
  );
}
