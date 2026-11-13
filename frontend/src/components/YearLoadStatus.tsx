"use client";

import React from "react";
import { Loader2, TriangleAlert } from "lucide-react";

interface YearLoadStatusProps {
  yearBE: number;
  loadingYear?: number | null;
  errorYear?: number | null;
  onRetry?: (year: number) => void;
}

/** Shown while a historical year's data file is being fetched, or if fetching failed. */
export function YearLoadStatus({ yearBE, loadingYear, errorYear, onRetry }: YearLoadStatusProps) {
  if (loadingYear === yearBE) {
    return (
      <div
        role="status"
        className="glass-panel flex items-center gap-3 p-4 text-sm font-semibold text-sky-800 dark:text-sky-300"
      >
        <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
        กำลังโหลดข้อมูลปี {yearBE} ({yearBE - 543}) จากคลังข้อมูลย้อนหลัง DMF…
      </div>
    );
  }
  if (errorYear === yearBE) {
    return (
      <div
        role="alert"
        className="glass-panel flex flex-wrap items-center gap-3 p-4 text-sm font-semibold text-amber-900 dark:text-amber-300"
      >
        <TriangleAlert aria-hidden="true" className="h-4 w-4" />
        โหลดข้อมูลปี {yearBE} ไม่สำเร็จ
        {onRetry && (
          <button
            type="button"
            onClick={() => onRetry(yearBE)}
            className="min-h-11 rounded-lg border border-amber-300 px-3 text-amber-900 hover:bg-amber-50 dark:border-amber-700 dark:text-amber-200 dark:hover:bg-amber-950/50"
          >
            ลองใหม่
          </button>
        )}
      </div>
    );
  }
  return null;
}
