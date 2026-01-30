import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
} from "recharts";
import type { ReactNode } from "react";

/* =========================
   データ型
========================= */

type ChartRow = {
    era: string;
    songCount: number;
    extraCorrect: number;
};

type TooltipPayloadItem = {
    dataKey: "songCount" | "extraCorrect";
    value: number;
};

type EraTooltipProps = {
    active?: boolean;
    payload?: TooltipPayloadItem[];
    label?: string;
};

const ERA_ORDER = [
    "2007-2008",
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025-",
];

const COLOR_SONG = "#1a73e8";      // 正解曲数
const COLOR_EXTRA = "#8ab4f8";    // 延べ正解回数（超過分）

/* =========================
   Tooltip
========================= */

function EraTooltip({
    active,
    payload,
    label,
}: EraTooltipProps): ReactNode {
    if (!active || !payload || payload.length === 0) return null;

    const songCount =
        payload.find((p) => p.dataKey === "songCount")?.value ?? 0;

    const extraCorrect =
        payload.find((p) => p.dataKey === "extraCorrect")?.value ?? 0;

    const totalCorrect = songCount + extraCorrect;

    return (
        <div
            style={{
                background: "#fff",
                border: "1px solid #ccc",
                borderRadius: 6,
                padding: "6px 10px",
                fontSize: "0.85em",
            }}
        >
            <div style={{ fontWeight: "bold", marginBottom: 4 }}>
                {label}
            </div>
            <div style={{ color: COLOR_EXTRA }}>正解回数：{totalCorrect}</div>
            <div style={{ color: COLOR_SONG }}>正解曲数：{songCount}</div>
        </div>
    );
}

/* =========================
   Chart
========================= */

export default function EraCorrectChart({
    data,
}: {
    data: ChartRow[];
}) {
    const sortedData = ERA_ORDER.map((era) => {
        const row = data.find((d) => d.era === era);
        return (
            row ?? {
                era,
                songCount: 0,
                extraCorrect: 0,
            }
        );
    });
    return (
        <ResponsiveContainer width="100%" height={320}>
            <BarChart data={sortedData}>
                <XAxis dataKey="era" />
                <YAxis allowDecimals={false} />
                <Tooltip content={<EraTooltip />} />
                <Legend />

                <Bar
                    dataKey="songCount"
                    stackId="a"
                    fill={COLOR_SONG}
                    name="正解曲数"
                />
                <Bar
                    dataKey="extraCorrect"
                    stackId="a"
                    fill={COLOR_EXTRA}
                    name="延べ正解回数"
                />
            </BarChart>
        </ResponsiveContainer>
    );
}
