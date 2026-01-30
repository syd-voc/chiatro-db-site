import {
    ResponsiveContainer,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from "recharts";

type ScatterPoint = {
    title: string;
    contentId: string;
    startTime: number;
    viewCounter: number;
};

export default function ScatterCorrectChart({
    data,
}: {
    data: ScatterPoint[];
}) {
    const safeData = data.filter(d => d.viewCounter > 0);
    const yearTicks = (() => {
        const min = new Date(Math.min(...data.map(d => d.startTime))).getFullYear();
        const max = new Date(Math.max(...data.map(d => d.startTime))).getFullYear();

        const ticks = [];
        for (let y = min + 1; y <= max; y++) {
            ticks.push(new Date(`${y}-01-01`).getTime());
        }
        return ticks;
    })();


    if (!safeData.length) {
        return <p>データがありません</p>;
    }

    return (
        <ResponsiveContainer width="100%" height={400}>
            <ScatterChart margin={{
                top: 20,
                right: 10,
                bottom: 30,
                left: 30,
            }}>
                <CartesianGrid opacity={0.4} />

                {/* ⭐ X軸：投稿日時 */}
                <XAxis
                    type="number"
                    dataKey="startTime"
                    scale="time"
                    domain={["auto", "auto"]}
                    tickFormatter={(v) =>
                        new Date(v).getFullYear().toString()
                    }
                    ticks={yearTicks}
                />

                {/* ⭐ Y軸：再生数（対数） */}
                <YAxis
                    type="number"
                    dataKey="viewCounter"
                    scale="log"
                    domain={["auto", "auto"]}
                />

                <Tooltip
                    content={({ active, payload }) => {
                        if (!active || !payload?.length) return null;

                        const d = payload[0].payload;

                        return (
                            <div className="scatter-tooltip">
                                <div className="title">
                                    <a href={`/songs/${d.contentId}`}>
                                        {d.title}
                                    </a>
                                </div>

                                <div>
                                    投稿日：
                                    {new Date(d.startTime).toLocaleDateString("ja-JP")}
                                </div>

                                <div>
                                    再生数：
                                    {d.viewCounter.toLocaleString()}
                                </div>
                            </div>
                        );
                    }}
                />

                <Scatter data={safeData} dataKey="viewCounter" fillOpacity={0.7} fill="#1F9CEF" />
            </ScatterChart>
        </ResponsiveContainer>
    );
}
