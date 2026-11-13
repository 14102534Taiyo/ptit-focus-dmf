"use client";

import { useCallback, useMemo, useRef, useState } from "react";

export type DatasetKind = "production" | "sales";

export interface YearsIndex {
  generated?: string;
  production: Record<string, number[]>;
  sales: Record<string, number[]>;
}

interface ColumnarPayload {
  columns: string[];
  rows: unknown[][];
}

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "";

function columnarToRecords<T>(payload: ColumnarPayload): T[] {
  const { columns, rows } = payload;
  return rows.map((row) => {
    const record: Record<string, unknown> = {};
    columns.forEach((column, index) => {
      record[column] = row[index];
    });
    return record as T;
  });
}

export function yearsFromIndex(index: YearsIndex | undefined, kind: DatasetKind): number[] {
  return Object.keys(index?.[kind] || {})
    .map(Number)
    .filter(Number.isFinite)
    .sort((a, b) => b - a);
}

/**
 * Keeps the bundled latest-year records and lazily fetches other years
 * from /data/{kind}/{year}.json (written by the ETL) the first time they are selected.
 */
export function useYearRecords<T extends { ปี: number | string }>(
  kind: DatasetKind,
  initialRecords: T[],
) {
  const initialYears = useMemo(
    () => Array.from(new Set(initialRecords.map((record) => Number(record.ปี)))),
    [initialRecords],
  );
  const [extraRecords, setExtraRecords] = useState<Record<number, T[]>>({});
  const [loadingYear, setLoadingYear] = useState<number | null>(null);
  const [errorYear, setErrorYear] = useState<number | null>(null);
  const requested = useRef(new Set<number>(initialYears));

  const ensureYear = useCallback(
    async (year: number) => {
      if (requested.current.has(year)) return;
      requested.current.add(year);
      setLoadingYear(year);
      setErrorYear(null);
      try {
        const response = await fetch(`${BASE_PATH}/data/${kind}/${year}.json`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = (await response.json()) as ColumnarPayload;
        const records = columnarToRecords<T>(payload);
        setExtraRecords((current) => ({ ...current, [year]: records }));
      } catch (error) {
        console.error(`Failed to load ${kind} ${year}`, error);
        requested.current.delete(year);
        setErrorYear(year);
      } finally {
        setLoadingYear((current) => (current === year ? null : current));
      }
    },
    [kind],
  );

  const records = useMemo(
    () => initialRecords.concat(...Object.values(extraRecords)),
    [initialRecords, extraRecords],
  );

  return { records, ensureYear, loadingYear, errorYear };
}
