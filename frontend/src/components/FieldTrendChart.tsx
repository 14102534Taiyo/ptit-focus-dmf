"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { formatInteger, formatNumber } from "@/lib/utils";

const SHORT_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];

export interface TrendSeries {
  name: string;
  color: string;
  values: (number | null)[];
}

export interface TrendPoint {
  year: number;
  /** 1–12 for monthly points, 0 for annual points */
  month: number;
}

interface FieldTrendChartProps {
  points: TrendPoint[];
  series: TrendSeries[];
  unit: string;
  decimals: number;
}

const HEIGHT = 340;
const PAD = { top: 16, right: 112, bottom: 30, left: 64 };

function useWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    if (!ref.current) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  return { ref, width };
}

function niceMax(value: number) {
  if (value <= 0) return 1;
  const exponent = Math.pow(10, Math.floor(Math.log10(value)));
  const fraction = value / exponent;
  const nice = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 2.5 ? 2.5 : fraction <= 5 ? 5 : 10;
  return nice * exponent;
}

function pointLabel(point: TrendPoint) {
  return point.month ? `${SHORT_MONTHS[point.month - 1]} ${point.year}` : `ปี ${point.year}`;
}

/** Multi-series line chart: one line per field, gaps where a field has no DMF row. */
export function FieldTrendChart({ points, series, unit, decimals }: FieldTrendChartProps) {
  const { ref, width } = useWidth<HTMLDivElement>();
  const [hover, setHover] = useState<number | null>(null);
  const narrow = width < 560;
  const pad = narrow ? { ...PAD, right: 16, left: 52 } : PAD;
  const plotW = Math.max(width - pad.left - pad.right, 10);
  const plotH = HEIGHT - pad.top - pad.bottom;

  const yMax = useMemo(() => {
    const max = Math.max(0, ...series.flatMap((s) => s.values.filter((v): v is number => v !== null)));
    return niceMax(max * 1.05);
  }, [series]);

  const x = (index: number) =>
    pad.left + (points.length > 1 ? (index / (points.length - 1)) * plotW : plotW / 2);
  const y = (value: number) => pad.top + plotH - (value / yMax) * plotH;

  // Year ticks: first point of each year; thin them out so labels never collide
  const yearTicks = useMemo(() => {
    const firsts = points
      .map((p, index) => ({ year: p.year, index }))
      .filter((p, index, all) => index === 0 || all[index - 1].year !== p.year);
    const maxLabels = Math.max(2, Math.floor(plotW / 44));
    const step = Math.ceil(firsts.length / maxLabels);
    return firsts.filter((_, i) => i % step === 0);
  }, [points, plotW]);

  const paths = series.map((s) => {
    let d = "";
    let pen = false;
    s.values.forEach((value, index) => {
      if (value === null) {
        pen = false;
        return;
      }
      d += `${pen ? "L" : "M"}${x(index).toFixed(1)},${y(value).toFixed(1)}`;
      pen = true;
    });
    const lastIndex = s.values.reduce<number>((acc, v, i) => (v !== null ? i : acc), -1);
    return { ...s, d, lastIndex };
  });

  // Direct labels at each line's end, nudged apart vertically
  const endLabels = useMemo(() => {
    const labels = paths
      .filter((p) => p.lastIndex >= 0)
      .map((p) => ({ name: p.name, color: p.color, ty: y(p.values[p.lastIndex] as number), x: x(p.lastIndex) }))
      .sort((a, b) => a.ty - b.ty);
    for (let i = 1; i < labels.length; i++) {
      if (labels[i].ty - labels[i - 1].ty < 14) labels[i].ty = labels[i - 1].ty + 14;
    }
    return labels;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paths.map((p) => p.d).join("|"), width]);

  const onMove = (event: React.PointerEvent<SVGRectElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const index = points.length > 1 ? Math.round((px / rect.width) * (points.length - 1)) : 0;
    setHover(Math.min(Math.max(index, 0), points.length - 1));
  };

  const fmt = (v: number) => (decimals ? formatNumber(v, decimals) : formatInteger(v));
  const hoverX = hover !== null ? x(hover) : 0;
  const tooltipLeft = hover !== null && hoverX > pad.left + plotW / 2;

  return (
    <div ref={ref} className="relative w-full">
      {width > 0 && (
        <svg width={width} height={HEIGHT} role="img" aria-label={`กราฟแนวโน้มการผลิตรายแหล่ง หน่วย ${unit}`} className="select-none">
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const value = yMax * ratio;
            return (
              <g key={ratio}>
                <line x1={pad.left} x2={pad.left + plotW} y1={y(value)} y2={y(value)} className="stroke-slate-200 dark:stroke-slate-800" strokeWidth={1} />
                <text x={pad.left - 8} y={y(value) + 4} textAnchor="end" className="fill-slate-500 dark:fill-slate-400 text-[11px] tabular-nums">
                  {fmt(value)}
                </text>
              </g>
            );
          })}
          {yearTicks.map((tick) => (
            <g key={tick.index}>
              <line x1={x(tick.index)} x2={x(tick.index)} y1={pad.top + plotH} y2={pad.top + plotH + 4} className="stroke-slate-300 dark:stroke-slate-700" />
              <text x={x(tick.index)} y={HEIGHT - 8} textAnchor="middle" className="fill-slate-500 dark:fill-slate-400 text-[11px] tabular-nums">
                {tick.year}
              </text>
            </g>
          ))}

          {paths.map((p) => (
            <path key={p.name} d={p.d} fill="none" stroke={p.color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
          ))}

          {!narrow &&
            endLabels.map((label) => (
              <g key={label.name}>
                <line x1={label.x + 4} x2={label.x + 12} y1={label.ty} y2={label.ty} stroke={label.color} strokeWidth={2} />
                <text x={label.x + 16} y={label.ty + 4} className="fill-slate-700 dark:fill-slate-200 text-[11px] font-semibold">
                  {label.name.length > 12 ? `${label.name.slice(0, 12)}…` : label.name}
                </text>
              </g>
            ))}

          {hover !== null && (
            <g pointerEvents="none">
              <line x1={hoverX} x2={hoverX} y1={pad.top} y2={pad.top + plotH} className="stroke-slate-400 dark:stroke-slate-500" strokeWidth={1} />
              {paths.map((p) => {
                const value = p.values[hover];
                return value === null ? null : (
                  <circle key={p.name} cx={hoverX} cy={y(value)} r={4.5} fill={p.color} className="stroke-white dark:stroke-slate-950" strokeWidth={2} />
                );
              })}
            </g>
          )}

          <rect
            x={pad.left}
            y={pad.top}
            width={plotW}
            height={plotH}
            fill="transparent"
            onPointerMove={onMove}
            onPointerLeave={() => setHover(null)}
          />
        </svg>
      )}

      {hover !== null && (
        <div
          role="tooltip"
          className="pointer-events-none absolute top-3 z-10 min-w-44 rounded-xl border border-slate-200 bg-white/95 px-3 py-2 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-900/95"
          style={tooltipLeft ? { right: width - hoverX + 12 } : { left: hoverX + 12 }}
        >
          <div className="mb-1 font-semibold text-slate-500 dark:text-slate-400">{pointLabel(points[hover])}</div>
          {series.map((s) => {
            const value = s.values[hover];
            return (
              <div key={s.name} className="flex items-center justify-between gap-3 py-0.5">
                <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                  <span aria-hidden="true" className="inline-block h-0.5 w-3 rounded" style={{ background: s.color }} />
                  {s.name}
                </span>
                <span className="font-bold tabular-nums text-slate-900 dark:text-white">
                  {value === null ? "ไม่มีรายงาน" : `${fmt(value)} ${unit}`}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
