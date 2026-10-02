"use client";

import { FormEvent, useEffect, useState } from "react";

import { apiRequest } from "@/lib/api";

type Organization = {
  id: string;
  name: string;
  slug: string;
};

type Dataset = {
  id: string;
  organization_id: string;
  name: string;
  original_filename: string;
  file_type: string;
  status: string;
  row_count: number | null;
  column_count: number | null;
};

type AnalystColumn = {
  column: string;
  outlier_count: number;
  outlier_percentage: number;
  severity: string;
};

type AnalystResult = {
  row_count?: number;
  numeric_column_count?: number;
  total_outlier_count?: number;
  columns?: AnalystColumn[];
};

type AnalystResponse = {
  question: string;
  tool: string;
  reason: string;
  answer: string;
  result: AnalystResult;
};

export default function AnalystPage() {
  const [organizations, setOrganizations] = useState<
    Organization[]
  >([]);

  const [datasets, setDatasets] = useState<Dataset[]>(
    [],
  );

  const [selectedDatasetId, setSelectedDatasetId] =
    useState("");

  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(true);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  const [answer, setAnswer] =
    useState<AnalystResponse | null>(null);

  async function loadAnalystData() {
    try {
      setLoading(true);
      setError("");

      const orgs =
        await apiRequest<Organization[]>(
          "/organizations",
        );

      setOrganizations(orgs);

      if (!orgs.length) {
        setError(
          "No organization is available for your account.",
        );
        return;
      }

      const organizationId = orgs[0].id;

      const data =
        await apiRequest<Dataset[]>(
          `/datasets?organization_id=${organizationId}`,
        );

      setDatasets(data);

      if (data.length > 0) {
        setSelectedDatasetId(data[0].id);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load AI Analyst.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnalystData();
  }, []);

  async function handleAsk(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setAnswer(null);

    if (!selectedDatasetId) {
      setError(
        "Please select a dataset first.",
      );
      return;
    }

    if (!question.trim()) {
      setError(
        "Please enter a question.",
      );
      return;
    }

    try {
      setAsking(true);

      const result =
        await apiRequest<AnalystResponse>(
          `/datasets/${selectedDatasetId}/analyst`,
          {
            method: "POST",
            body: JSON.stringify({
              question: question.trim(),
            }),
          },
        );

      setAnswer(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "AI Analyst request failed.",
      );
    } finally {
      setAsking(false);
    }
  }

  const selectedDataset = datasets.find(
    (dataset) =>
      dataset.id === selectedDatasetId,
  );

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <div className="mx-auto max-w-6xl px-6 py-10">

        {/* Header */}

        <div className="mb-8">
          <p className="text-sm font-medium text-blue-400">
            AI Data Analyst
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Ask questions about your data
          </h1>

          <p className="mt-2 max-w-2xl text-slate-400">
            Ask questions about your dataset and get
            data-backed answers from the analysis engine.
          </p>
        </div>

        {/* Loading */}

        {loading && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Loading datasets...
            </p>
          </div>
        )}

        {/* Error */}

        {!loading && error && (
          <div className="mb-6 rounded-2xl border border-red-800 bg-red-950/40 p-5">
            <p className="text-sm text-red-400">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Dataset selector */}

            <section className="mb-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold">
                  Select Dataset
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Choose the dataset you want to analyze.
                </p>
              </div>

              <select
                value={selectedDatasetId}
                onChange={(event) => {
                  setSelectedDatasetId(
                    event.target.value,
                  );

                  setAnswer(null);
                  setError("");
                }}
                disabled={asking}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
              >
                <option value="">
                  Select a dataset
                </option>

                {datasets.map((dataset) => (
                  <option
                    key={dataset.id}
                    value={dataset.id}
                  >
                    {dataset.name} —{" "}
                    {dataset.row_count ?? "—"} rows
                  </option>
                ))}
              </select>

              {selectedDataset && (
                <div className="mt-4 flex flex-wrap gap-3">

                  <span className="rounded-lg bg-slate-800 px-3 py-2 text-xs text-slate-300">
                    {selectedDataset.row_count ?? "—"} rows
                  </span>

                  <span className="rounded-lg bg-slate-800 px-3 py-2 text-xs text-slate-300">
                    {selectedDataset.column_count ?? "—"} columns
                  </span>

                  <span className="rounded-lg bg-emerald-500/10 px-3 py-2 text-xs text-emerald-400">
                    {selectedDataset.status}
                  </span>

                </div>
              )}
            </section>

            {/* Ask question */}

            <section className="mb-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-4">
                <h2 className="text-lg font-semibold">
                  Ask AI Analyst
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Ask a question in natural language.
                </p>
              </div>

              <form
                onSubmit={handleAsk}
                className="space-y-4"
              >
                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(event.target.value)
                  }
                  placeholder="e.g. Mere dataset mein kitne outliers hain?"
                  rows={4}
                  disabled={asking}
                  className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
                />

                <div className="flex items-center justify-between gap-4">

                  <p className="text-xs text-slate-500">
                    AI Analyst uses computed dataset
                    results to answer your question.
                  </p>

                  <button
                    type="submit"
                    disabled={
                      asking ||
                      !selectedDatasetId ||
                      !question.trim()
                    }
                    className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {asking
                      ? "Analyzing..."
                      : "Ask AI"}
                  </button>

                </div>
              </form>
            </section>

            {/* Answer */}

            {answer && (
              <section className="rounded-2xl border border-blue-900/60 bg-slate-900 p-6">

                <div className="mb-5 flex items-center justify-between gap-4">

                  <div>
                    <p className="text-sm text-blue-400">
                      AI Analyst
                    </p>

                    <h2 className="mt-1 text-xl font-semibold">
                      Analysis Result
                    </h2>
                  </div>

                  <span className="rounded-lg bg-blue-500/10 px-3 py-2 text-xs text-blue-400">
                    {answer.tool}
                  </span>

                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                  <p className="whitespace-pre-line leading-7 text-slate-200">
                    {answer.answer}
                  </p>
                </div>

                {/* Structured result */}

                {answer.result?.columns &&
                  answer.result.columns.length > 0 && (
                    <div className="mt-6">

                      <h3 className="mb-4 text-lg font-semibold">
                        Breakdown
                      </h3>

                      <div className="overflow-x-auto rounded-xl border border-slate-800">

                        <table className="w-full text-left">

                          <thead className="border-b border-slate-800 bg-slate-950">

                            <tr>

                              <th className="px-5 py-4 text-sm text-slate-400">
                                Column
                              </th>

                              <th className="px-5 py-4 text-sm text-slate-400">
                                Count
                              </th>

                              <th className="px-5 py-4 text-sm text-slate-400">
                                Percentage
                              </th>

                              <th className="px-5 py-4 text-sm text-slate-400">
                                Severity
                              </th>

                            </tr>

                          </thead>

                          <tbody>

                            {answer.result.columns.map(
                              (column) => (
                                <tr
                                  key={column.column}
                                  className="border-b border-slate-800 last:border-b-0"
                                >

                                  <td className="px-5 py-4 font-medium text-white">
                                    {column.column}
                                  </td>

                                  <td className="px-5 py-4 text-slate-300">
                                    {column.outlier_count.toLocaleString()}
                                  </td>

                                  <td className="px-5 py-4 text-slate-300">
                                    {column.outlier_percentage.toFixed(
                                      2,
                                    )}
                                    %
                                  </td>

                                  <td className="px-5 py-4">

                                    <span
                                      className={
                                        column.severity ===
                                        "high"
                                          ? "rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-400"
                                          : column.severity ===
                                              "low"
                                            ? "rounded-full bg-yellow-500/10 px-3 py-1 text-xs text-yellow-400"
                                            : "rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400"
                                      }
                                    >
                                      {
                                        column.severity
                                      }
                                    </span>

                                  </td>

                                </tr>
                              ),
                            )}

                          </tbody>

                        </table>

                      </div>

                    </div>
                  )}

              </section>
            )}

          </>
        )}

      </div>
    </main>
  );
}