import { MatrixRow, ProductionMasterData, ProductionRecord } from "@/types/hydrocarbon";

export const THAI_MONTHS = [
  "มกราคม",
  "กุมภาพันธ์",
  "มีนาคม",
  "เมษายน",
  "พฤษภาคม",
  "มิถุนายน",
  "กรกฎาคม",
  "สิงหาคม",
  "กันยายน",
  "ตุลาคม",
  "พฤศจิกายน",
  "ธันวาคม",
];

export type ReportingPeriod = "monthly" | "annual";
export type ProductionMetricKey = keyof ProductionMasterData["matrices"];

const METRIC_COLUMNS: Record<ProductionMetricKey, string> = {
  gas_mmscfd: "ก๊าซธรรมชาติ (ล้านลบ.ฟุต/วัน)",
  condensate_bpd: "ก๊าซธรรมชาติเหลว (บาร์เรล/วัน)",
  crude_bpd: "น้ำมันดิบ (บาร์เรล/วัน)",
  total_boed: "รวมเทียบเท่าน้ำมันดิบ (บาร์เรล/วัน)",
};

const METRIC_UNITS: Record<ProductionMetricKey, string> = {
  gas_mmscfd: "MMSCFD",
  condensate_bpd: "BPD",
  crude_bpd: "BPD",
  total_boed: "BOED",
};

export function daysInMonth(month: number, yearBE: number): number {
  const yearCE = yearBE > 2400 ? yearBE - 543 : yearBE;
  return new Date(yearCE, month, 0).getDate();
}

export function productionMatricesForYear(
  records: ProductionRecord[],
  yearBE: number,
): ProductionMasterData["matrices"] {
  const yearRecords = records.filter((record) => Number(record.ปี) === yearBE);
  const activeMonths = Array.from(
    new Set(yearRecords.map((record) => Number(record.ลำดับเดือน))),
  ).sort((a, b) => a - b);
  const yearDays = activeMonths.reduce(
    (sum, month) => sum + daysInMonth(month, yearBE),
    0,
  );

  const matrices = {} as ProductionMasterData["matrices"];

  (Object.keys(METRIC_COLUMNS) as ProductionMetricKey[]).forEach((metric) => {
    const metricColumn = METRIC_COLUMNS[metric];
    const groups = new Map<string, MatrixRow>();
    const groupOperators = new Map<string, Set<string>>();

    yearRecords.forEach((record) => {
      const fieldName = record.แหล่ง_ไฟล์ดิบ?.trim() || record.PTIT_Operator_Field;
      const concession = record.แปลง_ไฟล์ดิบ?.trim() || "";
      const key = `${record.PTIT_Region}\u0000${concession}\u0000${fieldName}`;
      let row = groups.get(key);
      if (!row) {
        row = {
          PTIT_Region: record.PTIT_Region,
          PTIT_Field_Name: fieldName,
          PTIT_Concession: concession,
          PTIT_Operator: "",
          PTIT_Order: Number(record.PTIT_Order) || 99,
        };
        groups.set(key, row);
        groupOperators.set(key, new Set());
      }

      const operator = record.ผู้ดำเนินการ?.trim();
      if (operator) groupOperators.get(key)?.add(operator);
      const value = Number(record[metricColumn as keyof ProductionRecord]) || 0;
      row[record.เดือน] = (Number(row[record.เดือน]) || 0) + value;
    });

    const rows = Array.from(groups.values()).map((row) => {
      const key = `${row.PTIT_Region}\u0000${row.PTIT_Concession}\u0000${row.PTIT_Field_Name}`;
      row.PTIT_Operator = Array.from(groupOperators.get(key) || []).join(", ");
      let totalVolume = 0;
      activeMonths.forEach((month) => {
        const monthName = THAI_MONTHS[month - 1];
        totalVolume += (Number(row[monthName]) || 0) * daysInMonth(month, yearBE);
      });
      row["เฉลี่ยทั้งปี"] = yearDays > 0 ? totalVolume / yearDays : 0;
      row["สะสมทั้งปี"] =
        totalVolume /
        (metric === "gas_mmscfd" ? 1000 : 1_000_000);
      return row;
    });

    rows.sort((a, b) => {
      const regionOrder = (a.PTIT_Region === "Onshore" ? 0 : 1) -
        (b.PTIT_Region === "Onshore" ? 0 : 1);
      return regionOrder ||
        a.PTIT_Order - b.PTIT_Order ||
        a.PTIT_Field_Name.localeCompare(b.PTIT_Field_Name);
    });

    matrices[metric] = {
      column_name: metricColumn,
      unit: METRIC_UNITS[metric],
      rows,
    };
  });

  return matrices;
}

export function productionSummary(
  records: ProductionRecord[],
  yearBE: number,
  period: ReportingPeriod,
  monthName: string,
) {
  const yearRecords = records.filter((record) => Number(record.ปี) === yearBE);
  const displayedRecords =
    period === "monthly"
      ? yearRecords.filter((record) => record.เดือน === monthName)
      : yearRecords;
  const months = Array.from(
    new Set(yearRecords.map((record) => Number(record.ลำดับเดือน))),
  );
  const days = period === "monthly"
    ? daysInMonth(
        Number(displayedRecords[0]?.ลำดับเดือน) || 1,
        yearBE,
      )
    : months.reduce((sum, month) => sum + daysInMonth(month, yearBE), 0);

  const volumeAndRate = (column: string) => {
    const volume = displayedRecords.reduce((sum, record) => {
      const rate = Number(record[column as keyof ProductionRecord]) || 0;
      const recordDays =
        period === "monthly"
          ? days
          : daysInMonth(Number(record.ลำดับเดือน), yearBE);
      return sum + rate * recordDays;
    }, 0);
    return {
      averageRate: days > 0 ? volume / days : 0,
      volume,
    };
  };

  const gas = volumeAndRate(METRIC_COLUMNS.gas_mmscfd);
  const condensate = volumeAndRate(METRIC_COLUMNS.condensate_bpd);
  const crude = volumeAndRate(METRIC_COLUMNS.crude_bpd);
  const boed = volumeAndRate(METRIC_COLUMNS.total_boed);

  return {
    records: displayedRecords,
    gasRate: gas.averageRate,
    condensateRate: condensate.averageRate,
    crudeRate: crude.averageRate,
    boedRate: boed.averageRate,
    gasVolumeBcf: gas.volume / 1000,
    condensateVolumeMillionBarrels: condensate.volume / 1_000_000,
    crudeVolumeMillionBarrels: crude.volume / 1_000_000,
    boeVolumeMillion: boed.volume / 1_000_000,
    activeFields: new Set(
      displayedRecords.map((record) =>
        [
          record.PTIT_Region,
          record.แปลง_ไฟล์ดิบ,
          record.แหล่ง_ไฟล์ดิบ || record.PTIT_Operator_Field,
        ].join("\u0000"),
      ),
    ).size,
    concessions: new Set(displayedRecords.map((record) => record.แปลง_ไฟล์ดิบ)).size,
    operators: new Set(displayedRecords.map((record) => record.ผู้ดำเนินการ)).size,
    yearDays: days,
    monthCount: period === "annual" ? months.length : 1,
    isCompleteYear: months.includes(12),
  };
}
