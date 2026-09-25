"use client";

import React, { useState } from "react";
import { ProductionMasterData } from "@/types/hydrocarbon";
import { formatNumber, formatInteger } from "@/lib/utils";

interface ProductionTrendChartsProps {
  data: ProductionMasterData;
}

const THAI_MONTH_COLUMNS = [
  "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
  "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม"
];

const THAI_SHORT_MONTHS: Record<string, string> = {
  มกราคม: "ม.ค.", กุมภาพันธ์: "ก.พ.", มีนาคม: "มี.ค.", เมษายน: "เม.ย.",
  พฤษภาคม: "พ.ค.", มิถุนายน: "มิ.ย.", กรกฎาคม: "ก.ค.", สิงหาคม: "ส.ค."
};

export function ProductionTrendCharts({ data }: ProductionTrendChartsProps) {
  const [selectedChartMetric, setSelectedChartMetric] = useState<"gas" | "cond" | "crude" | "boed">("boed");

  // Aggregate monthly totals for each metric across the active months
  const monthlyData = THAI_MONTH_COLUMNS.map((month) => {
    let gas = 0;
    let cond = 0;
    let crude = 0;
    let boed = 0;

    data.flat_records.forEach((r) => {
      if (r.เดือน === month) {
        gas += Number(r["ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)"]) || 0;
        cond += Number(r["ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)"]) || 0;
        crude += Number(r["น้ำมันดิบ (บาร์เรล/วัน)"]) || 0;
        boed += Number(r["รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)"]) || 0;
      }
    });

    return {
      month,
      shortMonth: THAI_SHORT_MONTHS[month] || month,
      gas,
      cond,
      crude,
      boed,
    };
  });

  // Calculate Operator shares for latest month
  const latestMonth = data.kpis.latest_month || "สิงหาคม";
  const operatorMap: Record<string, number> = {};
  let totalOperatorBoed = 0;

  data.flat_records
    .filter((r) => r.เดือน === latestMonth)
    .forEach((r) => {
      const op = r.ผู้ดำเนินการ || "ไม่ระบุ";
      const val = Number(r["รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)"]) || 0;
      operatorMap[op] = (operatorMap[op] || 0) + val;
      totalOperatorBoed += val;
    });

  const sortedOperators = Object.entries(operatorMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([name, val]) => ({
      name,
      val,
      pct: totalOperatorBoed > 0 ? (val / totalOperatorBoed) * 100 : 0,
    }));

  // Selected series for chart
  const seriesValues = monthlyData.map((d) => d[selectedChartMetric]);
  const maxVal = Math.max(...seriesValues) * 1.15 || 100;
  const minVal = Math.min(...seriesValues) * 0.85 || 0;
  const valRange = maxVal - minVal || 1;

  // Chart configuration
  const metricConfigs = {
    gas: { title: "ก๊าซธรรมชาติ (Natural Gas)", unit: "MMSCFD", color: "#06B6D4", bgGradient: "rgba(6, 182, 212, 0.2)" },
    cond: { title: "คอนเดนเสท (Condensate)", unit: "BPD", color: "#8B5CF6", bgGradient: "rgba(139, 92, 246, 0.2)" },
    crude: { title: "น้ำมันดิบ (Crude Oil)", unit: "BPD", color: "#F59E0B", bgGradient: "rgba(245, 158, 11, 0.2)" },
    boed: { title: "รวมเทียบเท่าน้ำมันดิบ (Total BOED)", unit: "BOED", color: "#10B981", bgGradient: "rgba(16, 185, 129, 0.2)" },
  };

  const activeCfg = metricConfigs[selectedChartMetric];

  // SVG dimensions
  const svgWidth = 600;
  const svgHeight = 220;
  const paddingX = 45;
  const paddingY = 25;
  const plotWidth = svgWidth - paddingX * 2;
  const plotHeight = svgHeight - paddingY * 2;

  // Compute SVG Points
  const points = monthlyData.map((d, idx) => {
    const x = paddingX + (idx / (monthlyData.length - 1)) * plotWidth;
    const y = svgHeight - paddingY - ((d[selectedChartMetric] - minVal) / valRange) * plotHeight;
    return { x, y, val: d[selectedChartMetric], month: d.shortMonth };
  });

  const polylineStr = points.map((p) => `${p.x},${p.y}`).join(" ");
  const polygonStr = `${points[0].x},${svgHeight - paddingY} ${polylineStr} ${points[points.length - 1].x},${svgHeight - paddingY}`;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* 1. Time-Series Area Chart (2 Cols) */}
      <div className="lg:col-span-2 glass-panel p-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 border-b border-slate-200/80 dark:border-slate-800 gap-3">
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 dark:text-white">
              แนวโน้มการผลิตรายเดือน ปี 2569 (Monthly Production Trend)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {activeCfg.title} • หน่วย {activeCfg.unit}
            </p>
          </div>

          {/* Metric Selector Pills */}
          <div className="inline-flex rounded-xl p-1 bg-slate-100 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-xs self-start sm:self-auto">
            {(["boed", "gas", "cond", "crude"] as const).map((mKey) => (
              <button
                key={mKey}
                onClick={() => setSelectedChartMetric(mKey)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  selectedChartMetric === mKey
                    ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm font-semibold"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                {mKey.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* SVG Area Chart */}
        <div className="mt-4 relative overflow-hidden">
          <svg
            viewBox={`0 0 ${svgWidth} ${svgHeight}`}
            className="w-full h-56 select-none"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id={`grad-${selectedChartMetric}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={activeCfg.color} stopOpacity="0.45" />
                <stop offset="100%" stopColor={activeCfg.color} stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Horizontal Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
              const y = svgHeight - paddingY - ratio * plotHeight;
              const v = minVal + ratio * valRange;
              return (
                <g key={ratio}>
                  <line
                    x1={paddingX}
                    y1={y}
                    x2={svgWidth - paddingX}
                    y2={y}
                    stroke="currentColor"
                    className="text-slate-200 dark:text-slate-800 stroke-[1]"
                    strokeDasharray="4 4"
                  />
                  <text
                    x={paddingX - 8}
                    y={y + 3}
                    textAnchor="end"
                    className="text-[10px] fill-slate-400 font-mono"
                  >
                    {formatInteger(v)}
                  </text>
                </g>
              );
            })}

            {/* Area Fill */}
            <polygon points={polygonStr} fill={`url(#grad-${selectedChartMetric})`} />

            {/* Trend Line */}
            <polyline
              points={polylineStr}
              fill="none"
              stroke={activeCfg.color}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data Points */}
            {points.map((p, i) => (
              <g key={i}>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r="4"
                  fill="#FFFFFF"
                  stroke={activeCfg.color}
                  strokeWidth="2.5"
                  className="transition-transform hover:scale-150"
                />
                <text
                  x={p.x}
                  y={p.y - 10}
                  textAnchor="middle"
                  className="text-[10px] font-bold fill-slate-700 dark:fill-slate-200 font-mono"
                >
                  {formatInteger(p.val)}
                </text>
                {/* Month label on X-axis */}
                <text
                  x={p.x}
                  y={svgHeight - 6}
                  textAnchor="middle"
                  className="text-[10px] font-medium fill-slate-500 dark:fill-slate-400"
                >
                  {p.month}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </div>

      {/* 2. Operator Share Ranking (1 Col) */}
      <div className="glass-panel p-5">
        <div className="pb-3 border-b border-slate-200/80 dark:border-slate-800">
          <h3 className="text-sm font-extrabold text-slate-900 dark:text-white">
            สัดส่วนผู้ดำเนินการรายใหญ่ (Top Operators)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            เดือน {latestMonth} 2569 • วัดจากปริมาณเทียบเท่าน้ำมันรวม (BOED)
          </p>
        </div>

        <div className="mt-4 space-y-3.5">
          {sortedOperators.map((op, idx) => (
            <div key={op.name} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[170px]">
                  {idx + 1}. {op.name}
                </span>
                <span className="font-mono text-slate-600 dark:text-slate-400 tabular-nums">
                  {formatInteger(op.val)} BOED ({op.pct.toFixed(1)}%)
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-sky-500 to-indigo-600"
                  style={{ width: `${Math.min(op.pct, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
