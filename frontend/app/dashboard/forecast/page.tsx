"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/dashboard/layout/Sidebar";
import Topbar from "@/components/dashboard/layout/Topbar";
import ForecastChart from "@/components/dashboard/forecast/ForecastChart";

import {
  apiRequest,
  generateForecast,
  type ForecastResponse,
} from "@/lib/api";

type Organization = {
  id: string;
  name: string;
  slug: string;
};

type Dataset = {
  id: string;
  organization_id: string;
  created_by: string;
  name: string;
  original_filename: string;
  file_type: string;
  status: string;
  row_count: number | null;
  column_count: number | null;
  description: string | null;
};

const HORIZON_OPTIONS = [4, 8, 12, 24, 52];

export default function ForecastPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);

  const [datasetId, setDatasetId] = useState("");
  const [horizon, setHorizon] = useState(12);

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const [error, setError] = useState("");
  const [forecastError, setForecastError] = useState("");

  const [forecastResult, setForecastResult] =
    useState<ForecastResponse | null>(null);

  useEffect(() => {
    async function loadForecastData() {
      try {
        setLoading(true);
        setError("");

        const token = localStorage.getItem("access_token");

        if (!token) {
          window.location.href = "/login";
          return;
        }

        const authHeaders = {
          Authorization: `Bearer ${token}`,
        };

        const organizationData = await apiRequest<Organization[]>(
          "/organizations",
          {
            headers: authHeaders,
          },
        );

        setOrganizations(organizationData);

        if (organizationData.length === 0) {
          setDatasets([]);
          return;
        }

        const allDatasets: Dataset[] = [];

        for (const organization of organizationData) {
          const organizationDatasets = await apiRequest<Dataset[]>(
            `/datasets?organization_id=${organization.id}`,
            {
              headers: authHeaders,
            },
          );

          allDatasets.push(...organizationDatasets);
        }

        setDatasets(allDatasets);

        if (allDatasets.length > 0) {
          setDatasetId(allDatasets[0].id);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load datasets.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadForecastData();
  }, []);

  async function handleGenerateForecast() {
    if (!datasetId) {
      setForecastError("Please select a dataset.");
      return;
    }

    try {
      setGenerating(true);
      setForecastError("");
      setForecastResult(null);

      const result = await generateForecast(
        datasetId,
        horizon,
      );

      setForecastResult(result);
    } catch (err) {
      setForecastError(
        err instanceof Error
          ? err.message
          : "Failed to generate forecast.",
      );
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <Sidebar />
      <Topbar />

      <div className="lg:pl-64 lg:pt-20">
        <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">

          {/* Header */}
          <div className="mb-8">
            <p className="text-sm font-medium text-blue-400">
              Predictive Analytics
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">
              Sales Forecast
            </h1>

            <p className="mt-2 max-w-2xl text-slate-400">
              Generate future sales forecasts from your historical dataset
              using the forecasting engine.
            </p>
          </div>

          {/* Configuration */}
          {loading ? (
            <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-8">
              <p className="text-sm text-slate-400">
                Loading datasets...
              </p>
            </section>
          ) : error ? (
            <section className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
              <p className="text-sm text-red-300">
                {error}
              </p>
            </section>
          ) : (
            <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">

              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white">
                  Forecast Configuration
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Select a dataset and choose how many future weeks you want
                  to forecast.
                </p>
              </div>

              <div className="grid gap-6 md:grid-cols-2">

                {/* Dataset */}
                <div>
                  <label
                    htmlFor="dataset"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Dataset
                  </label>

                  <select
                    id="dataset"
                    value={datasetId}
                    onChange={(event) => {
                      setDatasetId(event.target.value);
                      setForecastResult(null);
                      setForecastError("");
                    }}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
                  >
                    <option value="">
                      Select a dataset
                    </option>

                    {datasets.map((dataset) => (
                      <option
                        key={dataset.id}
                        value={dataset.id}
                      >
                        {dataset.name}
                      </option>
                    ))}
                  </select>

                  {datasets.length === 0 && (
                    <p className="mt-2 text-xs text-slate-500">
                      No datasets are available for forecasting.
                    </p>
                  )}
                </div>

                {/* Horizon */}
                <div>
                  <label
                    htmlFor="horizon"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Forecast Horizon
                  </label>

                  <select
                    id="horizon"
                    value={horizon}
                    onChange={(event) => {
                      setHorizon(Number(event.target.value));
                      setForecastResult(null);
                      setForecastError("");
                    }}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
                  >
                    {HORIZON_OPTIONS.map((option) => (
                      <option
                        key={option}
                        value={option}
                      >
                        {option} weeks
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Generate Button */}
              <div className="mt-6">
                <button
                  type="button"
                  onClick={handleGenerateForecast}
                  disabled={!datasetId || generating}
                  className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {generating
                    ? "Generating Forecast..."
                    : "Generate Forecast"}
                </button>
              </div>

              {/* API Error */}
              {forecastError && (
                <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3">
                  <p className="text-sm text-red-300">
                    {forecastError}
                  </p>
                </div>
              )}
            </section>
          )}

          {/* Forecast Result */}
          {forecastResult && (
            <section className="mt-8">

              <div className="mb-5">
                <h2 className="text-xl font-semibold text-white">
                  Forecast Results
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {forecastResult.horizon} future weeks generated using the{" "}
                  {forecastResult.model.replace("_", " ")} model.
                </p>
              </div>

              {/* Metrics */}
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

                {/* MAPE */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                  <p className="text-sm text-slate-500">
                    MAPE
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {forecastResult.metrics.mape.toFixed(2)}%
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Walk-forward validation
                  </p>
                </div>

                {/* MAE */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                  <p className="text-sm text-slate-500">
                    MAE
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {forecastResult.metrics.mae.toLocaleString(
                      undefined,
                      {
                        maximumFractionDigits: 0,
                      },
                    )}
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Mean absolute error
                  </p>
                </div>

                {/* RMSE */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                  <p className="text-sm text-slate-500">
                    RMSE
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {forecastResult.metrics.rmse.toLocaleString(
                      undefined,
                      {
                        maximumFractionDigits: 0,
                      },
                    )}
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Root mean squared error
                  </p>
                </div>

                {/* Historical Data */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                  <p className="text-sm text-slate-500">
                    Historical Data
                  </p>

                  <p className="mt-2 text-lg font-bold text-white">
                    {forecastResult.historical_start}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    to {forecastResult.historical_end}
                  </p>
                </div>
              </div>

              {/* Forecast Chart */}
              <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70">

                <div className="border-b border-slate-800 px-6 py-5">
                  <h3 className="font-semibold text-white">
                    Historical vs Forecast
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Historical sales and future weekly sales predictions.
                  </p>
                </div>

                <div className="p-6">
                  <ForecastChart
                    historical={forecastResult.historical}
                    forecast={forecastResult.forecast}
                  />
                </div>
              </div>

              {/* Forecast Table */}
              <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70">

                <div className="border-b border-slate-800 px-6 py-5">
                  <h3 className="font-semibold text-white">
                    Forecasted Sales
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Future weekly sales predictions.
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">

                    <thead className="border-b border-slate-800 bg-slate-950/60">
                      <tr>
                        <th className="px-6 py-4 font-medium text-slate-400">
                          Week
                        </th>

                        <th className="px-6 py-4 font-medium text-slate-400">
                          Forecast
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {forecastResult.forecast.map(
                        (point, index) => (
                          <tr
                            key={`${point.date}-${index}`}
                            className="border-b border-slate-800/70 last:border-b-0"
                          >
                            <td className="px-6 py-4 text-slate-300">
                              {point.date}
                            </td>

                            <td className="px-6 py-4 font-medium text-white">
                              {point.forecast.toLocaleString(
                                undefined,
                                {
                                  maximumFractionDigits: 0,
                                },
                              )}
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>

                  </table>
                </div>
              </div>

              {/* Warnings */}
              {forecastResult.warnings.length > 0 && (
                <div className="mt-6 rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">

                  <h3 className="font-semibold text-amber-300">
                    Forecast Notes
                  </h3>

                  <ul className="mt-3 space-y-2">
                    {forecastResult.warnings.map(
                      (warning, index) => (
                        <li
                          key={index}
                          className="text-sm leading-6 text-amber-200/70"
                        >
                          {warning}
                        </li>
                      ),
                    )}
                  </ul>

                </div>
              )}

            </section>
          )}

        </div>
      </div>
    </main>
  );
}