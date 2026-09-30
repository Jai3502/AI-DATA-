"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export type HistogramPoint = {
  range_start: number;
  range_end: number;
  count: number;
};

type HistogramChartProps = {
  title: string;
  xAxis: string;
  yAxis: string;
  data: HistogramPoint[];
};

export default function HistogramChart({
  title,
  xAxis,
  yAxis,
  data,
}: HistogramChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    range: `${item.range_start} – ${item.range_end}`,
  }));

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white">
          {title}
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          {xAxis} distribution
        </p>
      </div>

      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{
              top: 10,
              right: 20,
              left: 10,
              bottom: 55,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1e293b"
            />

            <XAxis
              dataKey="range"
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              angle={-35}
              textAnchor="end"
              interval="preserveStartEnd"
            />

            <YAxis
              dataKey="count"
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              label={{
                value: yAxis,
                angle: -90,
                position: "insideLeft",
                fill: "#94a3b8",
              }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "12px",
                color: "#ffffff",
              }}
              labelStyle={{
                color: "#cbd5e1",
              }}
              formatter={(value) => [value, yAxis]}
            />

            <Bar
              dataKey="count"
              fill="#3b82f6"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}