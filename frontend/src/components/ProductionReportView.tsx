"use client";

import React, { useMemo, useState } from "react";
import { ProductionMasterData } from "@/types/hydrocarbon";
import {
  ReportingPeriod,
  THAI_MONTHS,
  productionSummary,
} from "@/lib/reporting";
import { DynamicPivotStudio } from "@/components/DynamicPivotStudio";
import { ProductionPeriodTable } from "@/components/ProductionPeriodTable";
import { ProductionTrendCharts } from "@/components/ProductionTrendCharts";
import { ProductionKpiOverview } from "@/components/ProductionKpiOverview";
import { ReportingPeriodControls } from "@/components/ReportingPeriodControls";
import { YearLoadStatus } from "@/components/YearLoadStatus";

interface ProductionReportViewProps {
  data: ProductionMasterData;
  unitMode: "rate" | "boed";
  /** Every year DMF publishes (from years_index.json); falls back to years present in data. */
  availableYears?: number[];
  onYearSelected?: (year: number) => void;
  loadingYear?: number | null;
  errorYear?: number | null;
}

export function ProductionReportView({
  data,
  unitMode,
  availableYears,
  onYearSelected,
  loadingYear,
  errorYear,
}: ProductionReportViewProps) {
  const yearsBE = useMemo(() => {
    const years = new Set(availableYears || []);
    data.flat_records.forEach((record) => years.add(Number(record.ปี)));
    return Array.from(years).filter(Number.isFinite).sort((a, b) => b - a);
  }, [availableYears, data.flat_records]);
  const [yearBE, setYearBEState] = useState(data.kpis.reporting_year_be || yearsBE[0]);
  const setYearBE = (year: number) => {
    setYearBEState(year);
    onYearSelected?.(year);
  };
  const [period, setPeriod] = useState<ReportingPeriod>("annual");
  const [month, setMonth] = useState(data.kpis.latest_month);

  const months = useMemo(
    () =>
      Array.from(
        new Set(
          data.flat_records
            .filter((record) => Number(record.ปี) === yearBE)
            .map((record) => record.เดือน),
        ),
      ).sort((a, b) => THAI_MONTHS.indexOf(a) - THAI_MONTHS.indexOf(b)),
    [data.flat_records, yearBE],
  );

  const selectedMonth = months.includes(month) ? month : months[months.length - 1] || "";
  const summary = useMemo(
    () => productionSummary(data.flat_records, yearBE, period, selectedMonth),
    [data.flat_records, yearBE, period, selectedMonth],
  );

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">
          PTIT FOCUS STATISTICS · DOMESTIC UPSTREAM
        </p>
        <h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">
          สถิติการผลิตปิโตรเลียมในประเทศ
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Domestic Petroleum Production · รายงานตามรูปแบบ PTIT จากข้อมูล DMF และ DEDP
        </p>
      </div>

      <ReportingPeriodControls
        period={period}
        setPeriod={setPeriod}
        yearBE={yearBE}
        setYearBE={setYearBE}
        yearsBE={yearsBE}
        month={selectedMonth}
        setMonth={setMonth}
        months={months}
        latestMonth={months[months.length - 1] || "-"}
      />

      <YearLoadStatus
        yearBE={yearBE}
        loadingYear={loadingYear}
        errorYear={errorYear}
        onRetry={onYearSelected}
      />

      {/* Historical years arrive asynchronously; charts need at least one month to draw */}
      {months.length > 0 && (
        <>
          <ProductionKpiOverview
            summary={summary}
            period={period}
            month={selectedMonth}
            yearBE={yearBE}
            unitMode={unitMode}
          />

          <ProductionTrendCharts
            data={data}
            yearBE={yearBE}
            selectedMonth={selectedMonth}
          />

          <ProductionPeriodTable
            data={data}
            yearBE={yearBE}
            period={period}
            selectedMonth={selectedMonth}
          />

          <DynamicPivotStudio records={summary.records} />
        </>
      )}
    </div>
  );
}
