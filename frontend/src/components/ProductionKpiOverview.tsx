"use client";

import React from "react";
import { Droplets, Flame, Gauge, TrendingUp } from "lucide-react";
import { formatInteger, formatNumber } from "@/lib/utils";
import { ReportingPeriod } from "@/lib/reporting";

interface ProductionSummary {
  gasRate: number;
  condensateRate: number;
  crudeRate: number;
  boedRate: number;
  gasVolumeBcf: number;
  condensateVolumeMillionBarrels: number;
  crudeVolumeMillionBarrels: number;
  boeVolumeMillion: number;
  activeFields: number;
  isCompleteYear: boolean;
  yearDays: number;
}

interface ProductionKpiOverviewProps {
  summary: ProductionSummary;
  period: ReportingPeriod;
  month: string;
  yearBE: number;
  unitMode: "rate" | "boed";
}

export function ProductionKpiOverview({
  summary,
  period,
  month,
  yearBE,
  unitMode,
}: ProductionKpiOverviewProps) {
  const isAnnual = period === "annual";
  const gasRate = summary.gasRate * (unitMode === "boed" ? 178 : 1);
  const condensateRate = summary.condensateRate * (unitMode === "boed" ? 0.95 : 1);
  const crudeRate = summary.crudeRate;
  const unit = unitMode === "boed" ? "BOED" : undefined;
  const cards = [
    {
      label: "ก๊าซธรรมชาติ",
      english: "Natural Gas",
      value: unit ? formatInteger(gasRate) : formatNumber(gasRate, 2),
      unit: unit || "MMSCFD",
      volume: `${formatNumber(summary.gasVolumeBcf, 2)} BCF`,
      icon: Flame,
      accent: "cyan",
    },
    {
      label: "คอนเดนเสท",
      english: "Condensate",
      value: formatInteger(condensateRate),
      unit: unit || "BPD",
      volume: `${formatNumber(summary.condensateVolumeMillionBarrels, 2)} MMbbl`,
      icon: Droplets,
      accent: "violet",
    },
    {
      label: "น้ำมันดิบ",
      english: "Crude Oil",
      value: formatInteger(crudeRate),
      unit: unit || "BPD",
      volume: `${formatNumber(summary.crudeVolumeMillionBarrels, 2)} MMbbl`,
      icon: Gauge,
      accent: "amber",
    },
    {
      label: "ปิโตรเลียมรวมเทียบเท่าน้ำมัน",
      english: "Total Hydrocarbon Equivalence",
      value: formatInteger(summary.boedRate),
      unit: "BOED",
      volume: `${formatNumber(summary.boeVolumeMillion, 2)} MMBOE`,
      icon: TrendingUp,
      accent: "emerald",
    },
  ];

  const accentClasses: Record<string, string> = {
    cyan: "border-t-cyan-500 text-cyan-700 dark:text-cyan-300 bg-cyan-500/10",
    violet: "border-t-violet-500 text-violet-700 dark:text-violet-300 bg-violet-500/10",
    amber: "border-t-amber-500 text-amber-800 dark:text-amber-300 bg-amber-500/10",
    emerald: "border-t-emerald-500 text-emerald-800 dark:text-emerald-300 bg-emerald-500/10",
  };

  return (
    <section aria-label="ตัวชี้วัดการผลิต" className="space-y-3">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
            {isAnnual ? "ภาพรวมสะสมตั้งแต่ต้นปี" : `สรุปการผลิต · ${month}`}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {isAnnual
              ? `อัตราเฉลี่ยรายวันและ${summary.isCompleteYear ? "ปริมาณรวมทั้งปี" : "ปริมาณสะสม YTD"} · ${summary.yearDays} วันข้อมูล`
              : "อัตราเฉลี่ยรายวันและปริมาณผลิตประจำเดือน"}
            {" · "}ปี {yearBE} ({yearBE - 543})
          </p>
        </div>
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
          {summary.activeFields} แหล่งผลิต
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <article
              key={card.english}
              className={`glass-panel border-t-2 p-5 ${accentClasses[card.accent]}`}
            >
              <div className="flex items-center gap-3">
                <span className={`rounded-xl p-2 ${accentClasses[card.accent]}`}>
                  <Icon aria-hidden="true" className="h-5 w-5" />
                </span>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">{card.label}</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{card.english}</p>
                </div>
              </div>
              <div className="mt-5 flex items-baseline gap-2">
                <span className="text-3xl font-black tracking-tight text-slate-950 dark:text-white tabular-nums">
                  {card.value}
                </span>
                <span className="text-xs font-bold text-slate-500">{card.unit}</span>
              </div>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                {isAnnual ? "อัตราเฉลี่ยในช่วงข้อมูล" : "อัตราเฉลี่ยต่อวัน"}
              </p>
              <div className="mt-4 flex items-center justify-between border-t border-slate-200/70 pt-3 text-xs dark:border-slate-800">
                <span className="text-slate-500">
                  {isAnnual
                    ? summary.isCompleteYear
                      ? "ปริมาณรวมทั้งปี"
                      : "ปริมาณสะสม YTD"
                    : "ปริมาณเดือนนี้"}
                </span>
                <span className="font-bold text-slate-800 dark:text-slate-200 tabular-nums">
                  {card.volume}
                </span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
