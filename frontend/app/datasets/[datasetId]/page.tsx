"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiRequest } from "@/lib/api";
import TimeSeriesChart from "@/components/dashboard/charts/TimeSeriesChart";
import CategoryBarChart from "@/components/dashboard/charts/CategoryBarChart";
import HistogramChart from "@/components/dashboard/charts/HistogramChart";
import CorrelationHeatmap from "@/components/dashboard/charts/CorrelationHeatmap";

type DatasetProfile = {
  id: string;
  dataset_id: string;
  row_count: number;
  column_count: number;
  profile_data: {
    columns: {
      name: string;
      dtype: string;
      semantic_type: string;
      missing_count: number;
      missing_percentage: number;
      unique_count: number;
    }[];
  };
  created_at: string;
  updated_at: string;
};
type VisualizationKPI = {
  column: string;
  count: number;
  mean: number;
  median: number;
  min: number;
  max: number;
  std: number;
};

type VisualizationChart = {
  type: "bar" | "histogram" | "line" | "heatmap";
  chart_id: string;
  title: string;
  x_axis: string;
  y_axis: string;
  aggregation?: string;
  source_date_count?: number;
  data: Record<string, string | number | null>[];
};

type VisualizationResponse = {
  row_count: number;
  column_count: number;
  numeric_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  kpis: VisualizationKPI[];
  chart_count: number;
  charts: VisualizationChart[];
};

export default function DatasetDetailPage() {
  const params = useParams();
  const datasetId = params.datasetId as string;

  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [visualizations, setVisualizations] =
  useState<VisualizationResponse | null>(null);

const [visualizationsLoading, setVisualizationsLoading] =
  useState(true);

const [visualizationsError, setVisualizationsError] =
  useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);
        setError("");

        const data = await apiRequest<DatasetProfile>(
          `/datasets/${datasetId}/profile`,
        );
        try {
  setVisualizationsLoading(true);
  setVisualizationsError("");

  const visualizationData =
    await apiRequest<VisualizationResponse>(
      `/datasets/${datasetId}/visualizations`,
    );

  setVisualizations(visualizationData);
} catch (err) {
  setVisualizationsError(
    err instanceof Error
      ? err.message
      : "Failed to load dataset visualizations.",
  );
} finally {
  setVisualizationsLoading(false);
}

        setProfile(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load dataset profile.",
        );
      } finally {
        setLoading(false);
      }
    }

    if (datasetId) {
      loadProfile();
    }
  }, [datasetId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#020617] text-white">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Loading dataset profile...
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-[#020617] text-white">
        <div className="mx-auto max-w-7xl px-6 py-10">

          <Link
            href="/datasets"
            className="text-sm text-blue-400 hover:text-blue-300"
          >
            ← Back to datasets
          </Link>

          <div className="mt-6 rounded-xl border border-red-800 bg-red-950/40 p-6">
            <p className="text-red-400">
              {error}
            </p>
          </div>

        </div>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen bg-[#020617] text-white">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <p className="text-slate-400">
            Dataset profile not found.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Back */}
        <Link
          href="/datasets"
          className="text-sm text-blue-400 transition hover:text-blue-300"
        >
          ← Back to datasets
        </Link>

        {/* Header */}
        <div className="mt-6 mb-8">
          <p className="text-sm text-blue-400">
            Dataset Analysis
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Dataset Profile
          </h1>

          <p className="mt-2 text-slate-400">
            Structural overview and column-level metadata.
          </p>
        </div>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">
              Total rows
            </p>

            <p className="mt-2 text-3xl font-bold">
              {profile.row_count.toLocaleString()}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">
              Total columns
            </p>

            <p className="mt-2 text-3xl font-bold">
              {profile.column_count}
            </p>
          </div>

        </div>
        {/* Visualizations */}
<section className="mb-8">
  <div className="mb-6">
    <p className="text-sm font-medium text-blue-400">
      Analytics
    </p>

    <h2 className="mt-2 text-2xl font-bold text-white">
      Data Visualizations
    </h2>

    <p className="mt-2 text-sm text-slate-400">
      Automatically generated charts and statistical summaries
      from your dataset.
    </p>
  </div>

  {/* Visualization Loading */}
  {visualizationsLoading && (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-8">
      <p className="text-sm text-slate-400">
        Generating visualizations...
      </p>
    </div>
  )}

  {/* Visualization Error */}
  {!visualizationsLoading && visualizationsError && (
    <div className="rounded-2xl border border-red-800 bg-red-950/40 p-6">
      <p className="text-sm text-red-400">
        {visualizationsError}
      </p>
    </div>
  )}

  {/* Visualization Content */}
  {!visualizationsLoading &&
    !visualizationsError &&
    visualizations && (
      <div className="space-y-8">

        {/* KPI Cards */}
        {visualizations.kpis.length > 0 && (
          <div>
            <h3 className="mb-4 text-lg font-semibold text-white">
              Numeric Summary
            </h3>

            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {visualizations.kpis.map((kpi) => (
                <div
                  key={kpi.column}
                  className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"
                >
                  <p className="text-sm font-medium text-slate-400">
                    {kpi.column}
                  </p>

                  <p className="mt-3 text-2xl font-bold text-white">
                    {kpi.mean.toLocaleString(undefined, {
                      maximumFractionDigits: 2,
                    })}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Mean
                  </p>

                  <div className="mt-5 grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-slate-500">
                        Median
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-300">
                        {kpi.median.toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500">
                        Count
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-300">
                        {kpi.count.toLocaleString()}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500">
                        Minimum
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-300">
                        {kpi.min.toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500">
                        Maximum
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-300">
                        {kpi.max.toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Charts */}
        <div>
          <h3 className="mb-4 text-lg font-semibold text-white">
            Charts
          </h3>

          <div className="grid gap-6 xl:grid-cols-2">
            {visualizations.charts.map((chart) => {
              if (chart.type === "line") {
                const data = chart.data.map((point) => ({
                  date: String(point.date ?? ""),
                  value: Number(point.value ?? 0),
                }));

                return (
                  <TimeSeriesChart
                    key={chart.chart_id}
                    title={chart.title}
                    xAxis={chart.x_axis}
                    yAxis={chart.y_axis}
                    data={data}
                  />
                );
              }

              if (chart.type === "bar") {
                const data = chart.data.map((point) => ({
                  category: String(point.category ?? ""),
                  count: Number(point.count ?? 0),
                }));

                return (
                  <CategoryBarChart
                    key={chart.chart_id}
                    title={chart.title}
                    xAxis={chart.x_axis}
                    yAxis={chart.y_axis}
                    data={data}
                  />
                );
              }

              if (chart.type === "histogram") {
                const data = chart.data.map((point) => ({
                  range_start: Number(point.range_start ?? 0),
                  range_end: Number(point.range_end ?? 0),
                  count: Number(point.count ?? 0),
                }));

                return (
                  <HistogramChart
                    key={chart.chart_id}
                    title={chart.title}
                    xAxis={chart.x_axis}
                    yAxis={chart.y_axis}
                    data={data}
                  />
                );
              }

              if (chart.type === "heatmap") {
                const data = chart.data.map((point) => ({
                  x: String(point.x ?? ""),
                  y: String(point.y ?? ""),
                  correlation: Number(
                    point.correlation ?? 0,
                  ),
                }));

                return (
                  <div
                    key={chart.chart_id}
                    className="xl:col-span-2"
                  >
                    <CorrelationHeatmap
                      title={chart.title}
                      data={data}
                    />
                  </div>
                );
              }

              return null;
            })}
          </div>
        </div>
      </div>
    )}
</section>

        {/* Column Profile */}
        <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

          <div className="border-b border-slate-800 px-6 py-5">
            <h2 className="text-xl font-semibold">
              Column Profile
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Automatically detected metadata for each column.
            </p>
          </div>

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="border-b border-slate-800 bg-slate-950">
                <tr>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Column
                  </th>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Data Type
                  </th>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Semantic Type
                  </th>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Missing
                  </th>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Missing %
                  </th>

                  <th className="px-6 py-4 text-sm text-slate-400">
                    Unique
                  </th>

                </tr>
              </thead>

              <tbody>

                {profile.profile_data.columns.map((column) => (
                  <tr
                    key={column.name}
                    className="border-b border-slate-800 last:border-b-0"
                  >

                    <td className="px-6 py-5">
                      <p className="font-semibold text-white">
                        {column.name}
                      </p>
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {column.dtype}
                    </td>

                    <td className="px-6 py-5">

                      <span className="rounded-full bg-blue-500/10 px-3 py-1 text-sm text-blue-400">
                        {column.semantic_type || "unknown"}
                      </span>

                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {column.missing_count.toLocaleString()}
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {column.missing_percentage.toFixed(2)}%
                    </td>

                    <td className="px-6 py-5 text-slate-300">
                      {column.unique_count.toLocaleString()}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>

      </div>
    </main>
  );
}