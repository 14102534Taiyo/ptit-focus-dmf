import { SalesRecord } from "@/types/hydrocarbon";

export interface SalesVolumeSummaryRow {
  field: string;
  operator: string;
  product: string;
  measure: string;
  unit: string;
  monthlyVolumes: Record<string, number>;
  periodTotal: number;
}

interface SalesVolumeMeasure {
  key: string;
  label: string;
  unit: string;
  quantity: number;
}

function measuresForRecord(record: SalesRecord): SalesVolumeMeasure[] {
  if (record.ประเภทปิโตรเลียม === "ก๊าซธรรมชาติ") {
    return [
      {
        key: "gas-volume",
        label: "ปริมาณก๊าซ",
        unit: "MMSCF",
        quantity: Number(record.ปริมาณการขาย_MMSCF) || 0,
      },
      {
        key: "gas-heat",
        label: "ปริมาณความร้อน",
        unit: "MMBTU",
        quantity: Number(record.ปริมาณการขาย_MMBTU) || 0,
      },
    ];
  }

  return [
    {
      key: `${record.ประเภทปิโตรเลียม}|${record.หน่วยปริมาณ}`,
      label: "ปริมาณขาย",
      unit: record.หน่วยปริมาณ,
      quantity: Number(record.ปริมาณการขาย_หน่วยหลัก) || 0,
    },
  ];
}

export function summarizeSalesVolumes(
  records: SalesRecord[],
  months: string[],
): { fields: SalesVolumeSummaryRow[]; products: SalesVolumeSummaryRow[] } {
  const fieldRows = new Map<string, SalesVolumeSummaryRow>();
  const productRows = new Map<string, SalesVolumeSummaryRow>();

  records.forEach((record) => {
    if (!months.includes(record.เดือน)) return;

    measuresForRecord(record).forEach((measure) => {
      const productKey = `${record.ประเภทปิโตรเลียม}\u0000${measure.key}`;
      const productRow = productRows.get(productKey) || {
        field: "",
        operator: "",
        product: record.ประเภทปิโตรเลียม,
        measure: measure.label,
        unit: measure.unit,
        monthlyVolumes: {},
        periodTotal: 0,
      };

      productRow.monthlyVolumes[record.เดือน] =
        (productRow.monthlyVolumes[record.เดือน] || 0) + measure.quantity;
      productRow.periodTotal += measure.quantity;
      productRows.set(productKey, productRow);

      const fieldKey = [
        record.แหล่ง_ไฟล์ดิบ,
        record.ผู้ดำเนินการ,
        record.ประเภทปิโตรเลียม,
        measure.key,
      ].join("\u0000");
      const fieldRow = fieldRows.get(fieldKey) || {
        field: record.แหล่ง_ไฟล์ดิบ,
        operator: record.ผู้ดำเนินการ,
        product: record.ประเภทปิโตรเลียม,
        measure: measure.label,
        unit: measure.unit,
        monthlyVolumes: {},
        periodTotal: 0,
      };

      fieldRow.monthlyVolumes[record.เดือน] =
        (fieldRow.monthlyVolumes[record.เดือน] || 0) + measure.quantity;
      fieldRow.periodTotal += measure.quantity;
      fieldRows.set(fieldKey, fieldRow);
    });
  });

  const sortRows = (rows: SalesVolumeSummaryRow[]) =>
    rows.sort(
      (a, b) =>
        a.product.localeCompare(b.product) ||
        a.field.localeCompare(b.field) ||
        a.measure.localeCompare(b.measure),
    );

  return {
    fields: sortRows(Array.from(fieldRows.values())),
    products: sortRows(Array.from(productRows.values())),
  };
}
