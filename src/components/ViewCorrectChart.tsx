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
    range: string;
    songCount: number;
    extraCorrect: number;
};

type TooltipPayloadItem = {
    dataKey: "songCount" | "extraCorrect";
    value: number;
};

type ViewTooltipProps = {
    active?: boolean;
    payload?: TooltipPayloadItem[];
    label?: string;
};
const COLOR_SONG = "#1a73e8";
const COLOR_EXTRA = "#8ab4f8";

/* =========================
   Tooltip
========================= */

function ViewTooltip({
    active,
    payload,
    label,
}: ViewTooltipProps): ReactNode {
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

export default function ViewCorrectChart({
    data,
}: {
    data: {
        range: string;
        songCount: number;
        extraCorrect: number;
    }[];
}) {
    return (
        <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data}>
                <XAxis dataKey="range" />
                <YAxis allowDecimals={false} />
                <Tooltip content={<ViewTooltip />} />
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
