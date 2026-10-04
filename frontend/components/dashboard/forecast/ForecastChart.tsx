"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  ForecastPoint,
  HistoricalPoint,
} from "@/lib/api";

type ForecastChartProps = {
  historical: HistoricalPoint[];
  forecast: ForecastPoint[];
};

type ChartPoint = {
  date: string;
  actual?: number;
  forecast?: number;
};

function formatDate(date: string) {
  const value = new Date(`${date}T00:00:00`);

  return value.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatSales(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value);
}

function mergeChartData(
  historical: HistoricalPoint[],
  forecast: ForecastPoint[],
): ChartPoint[] {
  const historicalPoints: ChartPoint[] = historical.map(
    (point) => ({
      date: point.date,
      actual: point.actual,
    }),
  );

  const forecastPoints: ChartPoint[] = forecast.map(
    (point) => ({
      date: point.date,
      forecast: point.forecast,
    }),
  );

  return [...historicalPoints, ...forecastPoints];
}

export default function ForecastChart({
  historical,
  forecast,
}: ForecastChartProps) {
  const chartData = mergeChartData(
    historical,
    forecast,
  );

  return (
    <div className="h-[420px] w-full">
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 20,
            left: 10,
            bottom: 10,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(148, 163, 184, 0.12)"
          />

          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{
              fill: "#94a3b8",
              fontSize: 12,
            }}
            tickLine={false}
            axisLine={false}
            minTickGap={40}
          />

          <YAxis
            tickFormatter={(value) =>
              `${(Number(value) / 1000000).toFixed(0)}M`
            }
            tick={{
              fill: "#94a3b8",
              fontSize: 12,
            }}
            tickLine={false}
            axisLine={false}
            width={55}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "12px",
              color: "#ffffff",
            }}
            labelFormatter={(label) =>
              formatDate(String(label))
            }
            formatter={(value, name) => {
              const numericValue = Number(value);

              return [
                formatSales(numericValue),
                name === "actual"
                  ? "Historical Sales"
                  : "Forecast",
              ];
            }}
          />

          <Line
            type="monotone"
            dataKey="actual"
            name="actual"
            connectNulls={false}
            strokeWidth={2}
            dot={false}
            stroke="#60a5fa"
          />

          <Line
            type="monotone"
            dataKey="forecast"
            name="forecast"
            connectNulls={false}
            strokeWidth={2}
            dot={false}
            stroke="#a78bfa"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}