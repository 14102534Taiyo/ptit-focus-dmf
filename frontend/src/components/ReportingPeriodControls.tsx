"use client";

import React from "react";
import { CalendarDays, CalendarRange } from "lucide-react";
import { ReportingPeriod } from "@/lib/reporting";

interface ReportingPeriodControlsProps {
  period: ReportingPeriod;
  setPeriod: (period: ReportingPeriod) => void;
  yearBE: number;
  setYearBE: (year: number) => void;
  yearsBE: number[];
  month: string;
  setMonth: (month: string) => void;
  months: string[];
  latestMonth: string;
}

export function ReportingPeriodControls({
  period,
  setPeriod,
  yearBE,
  setYearBE,
  yearsBE,
  month,
  setMonth,
  months,
  latestMonth,
}: ReportingPeriodControlsProps) {
  const isCompleteYear = months.includes("ธันวาคม");
  const periodRange = isCompleteYear
    ? "ม.ค.–ธ.ค."
    : `ม.ค.–${latestMonth}`;

  return (
    <section
      aria-label="ตัวเลือกช่วงเวลารายงาน"
      className="glass-panel flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          ช่วงเวลารายงาน
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="text-sm font-extrabold text-slate-900 dark:text-white">
            {period === "annual"
              ? isCompleteYear
                ? "สรุปรายปี"
                : "สรุปสะสมตั้งแต่ต้นปี (YTD)"
              : `รายเดือน · ${month}`}
          </span>
          <span className="rounded-full bg-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-900 dark:bg-amber-950/70 dark:text-amber-300">
            ปี {yearBE} / {yearBE - 543}
          </span>
          {period === "annual" && (
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {periodRange} {isCompleteYear ? "(ทั้งปี)" : ""}
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div
          role="group"
          aria-label="เลือกมุมมองรายงาน"
          className="inline-flex rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-900"
        >
          <button
            type="button"
            aria-pressed={period === "monthly"}
            onClick={() => setPeriod("monthly")}
            className={`inline-flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600 ${
              period === "monthly"
                ? "bg-white text-sky-800 shadow-sm dark:bg-slate-800 dark:text-sky-300"
                : "text-slate-600 hover:text-slate-950 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <CalendarDays aria-hidden="true" className="h-4 w-4" />
            รายเดือน
          </button>
          <button
            type="button"
            aria-pressed={period === "annual"}
            onClick={() => setPeriod("annual")}
            className={`inline-flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600 ${
              period === "annual"
                ? "bg-white text-sky-800 shadow-sm dark:bg-slate-800 dark:text-sky-300"
                : "text-slate-600 hover:text-slate-950 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <CalendarRange aria-hidden="true" className="h-4 w-4" />
            {isCompleteYear ? "รายปี" : "รายปี / YTD"}
          </button>
        </div>

        <label className="sr-only" htmlFor="report-year">
          เลือกปีรายงาน
        </label>
        <select
          id="report-year"
          value={yearBE}
          onChange={(event) => setYearBE(Number(event.target.value))}
          className="min-h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        >
          {yearsBE.map((year) => (
            <option key={year} value={year}>
              {year} / {year - 543}
            </option>
          ))}
        </select>

        {period === "monthly" && (
          <>
            <label className="sr-only" htmlFor="report-month">
              เลือกเดือนรายงาน
            </label>
            <select
              id="report-month"
              value={month}
              onChange={(event) => setMonth(event.target.value)}
              className="min-h-11 min-w-36 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            >
              {months.map((availableMonth) => (
                <option key={availableMonth} value={availableMonth}>
                  {availableMonth}
                </option>
              ))}
            </select>
          </>
        )}
      </div>
    </section>
  );
}
