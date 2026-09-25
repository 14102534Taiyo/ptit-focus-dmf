"use client";

import React, { useState } from "react";
import { RefreshCw, Zap, BookOpen, ArrowRightLeft, Scale } from "lucide-react";
import { formatNumber, formatInteger } from "@/lib/utils";

export function PetroleumUnitConverter() {
  const [inputVal, setInputVal] = useState<number>(1000);
  const [inputUnit, setInputUnit] = useState<"gas_mmscfd" | "crude_bpd" | "cond_bpd" | "boed">("gas_mmscfd");

  // PTIT Conversion Standards
  // 1 MMSCFD = 178 BOED (1000 SCF = 0.178 BOE)
  // 1 BPD Condensate = 0.95 BOED
  // 1 BPD Crude = 1.0 BOED
  // 1 Tonne Crude ≈ 7.33 Barrels (API 32°)

  let gasMmscfd = 0;
  let condBpd = 0;
  let crudeBpd = 0;
  let boed = 0;

  if (inputUnit === "gas_mmscfd") {
    gasMmscfd = inputVal;
    boed = inputVal * 178;
    crudeBpd = boed;
    condBpd = boed / 0.95;
  } else if (inputUnit === "crude_bpd") {
    crudeBpd = inputVal;
    boed = inputVal * 1.0;
    gasMmscfd = boed / 178;
    condBpd = boed / 0.95;
  } else if (inputUnit === "cond_bpd") {
    condBpd = inputVal;
    boed = inputVal * 0.95;
    crudeBpd = boed;
    gasMmscfd = boed / 178;
  } else if (inputUnit === "boed") {
    boed = inputVal;
    crudeBpd = boed;
    condBpd = boed / 0.95;
    gasMmscfd = boed / 178;
  }

  // Energy & Annual equivalents
  const mmbtud = gasMmscfd * 1000; // ~1,000 BTU/SCF
  const bcfPerYear = (gasMmscfd * 365) / 1000;
  const mmbblPerYear = (crudeBpd * 365) / 1_000_000;
  const mmboePerYear = (boed * 365) / 1_000_000;
  const tonnesCrudePerYear = (crudeBpd * 365) / 7.33;

  return (
    <div className="space-y-6 mb-8">
      {/* Interactive Converter Hub */}
      <div className="glass-panel p-6 border-t-2 border-t-sky-500">
        <div className="flex items-center space-x-2.5 pb-4 border-b border-slate-200/80 dark:border-slate-800">
          <div className="p-2.5 rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400">
            <RefreshCw className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
              ระบบแปลงหน่วยปิโตรเลียมและพลังงานเทียบเท่า (Petroleum Unit Conversion Hub)
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              มาตรฐานการคำนวณสถิติพลังงาน สถาบันปิโตรเลียมแห่งประเทศไทย (PTIT Standard)
            </p>
          </div>
        </div>

        {/* Input Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
          <div className="md:col-span-2">
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
              ใส่ค่าปริมาณที่ต้องการแปลง:
            </label>
            <div className="relative">
              <input
                type="number"
                value={inputVal || ""}
                onChange={(e) => setInputVal(parseFloat(e.target.value) || 0)}
                className="w-full text-2xl font-bold px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500 tabular-nums"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
              หน่วยตั้งต้น (Input Unit):
            </label>
            <select
              value={inputUnit}
              onChange={(e) => setInputUnit(e.target.value as any)}
              className="w-full text-sm font-semibold px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="gas_mmscfd">ก๊าซธรรมชาติ (MMSCFD)</option>
              <option value="crude_bpd">น้ำมันดิบ (BPD)</option>
              <option value="cond_bpd">ก๊าซธรรมชาติเหลว / คอนเดนเสท (BPD)</option>
              <option value="boed">รวมเทียบเท่าน้ำมันดิบ (BOED)</option>
            </select>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2 mb-6 text-xs">
          <span className="text-slate-500 font-medium">ตัวอย่างข้อมูลสัมปทานจริง:</span>
          {[
            { label: "แหล่งเอราวัณ (G1/61): 800 MMSCFD", unit: "gas_mmscfd", val: 800 },
            { label: "แหล่งบงกช (G2/61): 700 MMSCFD", unit: "gas_mmscfd", val: 700 },
            { label: "แหล่งสิริกิติ์ (S1): 22,000 BPD", unit: "crude_bpd", val: 22000 },
            { label: "แหล่งฝาง (DEDP): 610 BPD", unit: "crude_bpd", val: 610.4 },
          ].map((preset) => (
            <button
              key={preset.label}
              onClick={() => {
                setInputUnit(preset.unit as any);
                setInputVal(preset.val);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Real-Time Conversion Matrix */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
          {/* Equivalent BOED */}
          <div className="p-4 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/60">
            <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider">
              พลังงานเทียบเท่าน้ำมัน (BOED)
            </span>
            <div className="text-2xl font-black text-emerald-900 dark:text-emerald-300 mt-1 tabular-nums">
              {formatInteger(boed)}
            </div>
            <div className="text-xs text-emerald-700/80 dark:text-emerald-400/80 mt-0.5">
              ~{formatNumber(mmboePerYear, 2)} MMBOE/ปี
            </div>
          </div>

          {/* Equivalent Gas */}
          <div className="p-4 rounded-xl bg-cyan-50/60 dark:bg-cyan-950/20 border border-cyan-200/80 dark:border-cyan-800/60">
            <span className="text-[11px] font-bold text-cyan-800 dark:text-cyan-400 uppercase tracking-wider">
              ก๊าซธรรมชาติเทียบเท่า (MMSCFD)
            </span>
            <div className="text-2xl font-black text-cyan-900 dark:text-cyan-300 mt-1 tabular-nums">
              {formatNumber(gasMmscfd, 2)}
            </div>
            <div className="text-xs text-cyan-700/80 dark:text-cyan-400/80 mt-0.5">
              ~{formatNumber(bcfPerYear, 2)} BCF/ปี
            </div>
          </div>

          {/* Equivalent Crude */}
          <div className="p-4 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/60">
            <span className="text-[11px] font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wider">
              น้ำมันดิบเทียบเท่า (BPD)
            </span>
            <div className="text-2xl font-black text-amber-900 dark:text-amber-300 mt-1 tabular-nums">
              {formatInteger(crudeBpd)}
            </div>
            <div className="text-xs text-amber-700/80 dark:text-amber-400/80 mt-0.5">
              ~{formatNumber(mmbblPerYear, 2)} MMbbl/ปี
            </div>
          </div>

          {/* Equivalent Tonnes */}
          <div className="p-4 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200/80 dark:border-indigo-800/60">
            <span className="text-[11px] font-bold text-indigo-800 dark:text-indigo-400 uppercase tracking-wider">
              ปริมาณตันเทียบเท่า (Tonnes/yr)
            </span>
            <div className="text-2xl font-black text-indigo-900 dark:text-indigo-300 mt-1 tabular-nums">
              {formatInteger(tonnesCrudePerYear)}
            </div>
            <div className="text-xs text-indigo-700/80 dark:text-indigo-400/80 mt-0.5">
              ตันต่อปี (API 32° Basis)
            </div>
          </div>
        </div>
      </div>

      {/* Official PTIT Conversion Standards Table */}
      <div className="glass-panel p-6">
        <h3 className="text-sm font-extrabold text-slate-900 dark:text-white mb-3 flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-sky-600" />
          <span>ตารางค่าคงที่มาตรฐานสถาบันปิโตรเลียมแห่งประเทศไทย (PTIT Standard Constants)</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
            <div className="font-bold text-slate-800 dark:text-slate-200 mb-1">
              สูตรแปลงก๊าซธรรมชาติเป็น BOED (Gas-to-Oil Ratio)
            </div>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-mono">
              BOED = (MMSCFD × 1,000) × 0.178
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              อิงค่าความร้อนเฉลี่ยของก๊าซในอ่าวไทย 1,000 BTU/SCF (1,000 SCF = 0.178 BOE)
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
            <div className="font-bold text-slate-800 dark:text-slate-200 mb-1">
              สูตรแปลงคอนเดนเสทเป็น BOED (Condensate Ratio)
            </div>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-mono">
              BOED = คอนเดนเสท (BPD) × 0.95
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              อิงความหนาแน่นและค่าพลังงานความร้อนเทียบเท่าน้ำมันดิบมาตรฐานที่ 0.95 เท่า
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
