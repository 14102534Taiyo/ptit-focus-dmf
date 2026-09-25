import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(val: number | null | undefined, decimals = 2): string {
  if (val === null || val === undefined || isNaN(val)) return "-";
  if (Math.abs(val) < 0.0001) return "-";
  return val.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatInteger(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "-";
  return Math.round(val).toLocaleString("en-US");
}
