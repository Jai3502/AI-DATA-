"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

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

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [organizationId, setOrganizationId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDatasets() {
      try {
        setLoading(true);
        setError("");

        const organizations = await apiRequest<
          {
            id: string;
            name: string;
            slug: string;
          }[]
        >("/organizations");

        if (!organizations.length) {
          setDatasets([]);
          return;
        }

        const selectedOrganizationId = organizations[0].id;

        setOrganizationId(selectedOrganizationId);

        const data = await apiRequest<Dataset[]>(
          `/datasets?organization_id=${selectedOrganizationId}`,
        );

        setDatasets(data);
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

    loadDatasets();
  }, []);

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}
        <div className="mb-8">
          <p className="text-sm text-blue-400">
            Workspace
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Datasets
          </h1>

          <p className="mt-2 text-slate-400">
            Manage and analyze your uploaded business data.
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              Loading datasets...
            </p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="rounded-xl border border-red-800 bg-red-950/40 p-6">
            <p className="text-red-400">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Stats */}
            <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Total datasets
                </p>

                <p className="mt-2 text-3xl font-bold">
                  {datasets.length}
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Organization
                </p>

                <p className="mt-2 truncate text-lg font-semibold">
                  {organizationId || "—"}
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">
                  Profiled datasets
                </p>

                <p className="mt-2 text-3xl font-bold">
                  {
                    datasets.filter(
                      (dataset) =>
                        dataset.status === "profiled",
                    ).length
                  }
                </p>
              </div>

            </div>

            {/* Empty State */}
            {datasets.length === 0 ? (
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-10 text-center">

                <h2 className="text-xl font-semibold">
                  No datasets found
                </h2>

                <p className="mt-2 text-slate-400">
                  Upload a CSV or Excel file to start
                  analyzing your data.
                </p>

              </div>
            ) : (

              /* Dataset Table */
              <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

                <div className="overflow-x-auto">

                  <table className="w-full text-left">

                    <thead className="border-b border-slate-800 bg-slate-950">
                      <tr>

                        <th className="px-6 py-4 text-sm text-slate-400">
                          Dataset
                        </th>

                        <th className="px-6 py-4 text-sm text-slate-400">
                          File
                        </th>

                        <th className="px-6 py-4 text-sm text-slate-400">
                          Rows
                        </th>

                        <th className="px-6 py-4 text-sm text-slate-400">
                          Columns
                        </th>

                        <th className="px-6 py-4 text-sm text-slate-400">
                          Status
                        </th>

                      </tr>
                    </thead>

                    <tbody>

                      {datasets.map((dataset) => (
                        <tr
                          key={dataset.id}
                          className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/40"
                        >

                          {/* Dataset */}
                          <td className="px-6 py-5">

                            <Link
                              href={`/datasets/${dataset.id}`}
                              className="group block"
                            >
                              <p className="font-semibold text-white transition group-hover:text-blue-400">
                                {dataset.name}
                              </p>

                              {dataset.description && (
                                <p className="mt-1 text-sm text-slate-500">
                                  {dataset.description}
                                </p>
                              )}

                              <p className="mt-2 text-xs text-blue-500 opacity-0 transition group-hover:opacity-100">
                                Open dataset →
                              </p>
                            </Link>

                          </td>

                          {/* File */}
                          <td className="px-6 py-5 text-slate-300">
                            {dataset.original_filename}
                          </td>

                          {/* Rows */}
                          <td className="px-6 py-5 text-slate-300">
                            {dataset.row_count ?? "—"}
                          </td>

                          {/* Columns */}
                          <td className="px-6 py-5 text-slate-300">
                            {dataset.column_count ?? "—"}
                          </td>

                          {/* Status */}
                          <td className="px-6 py-5">

                            <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">
                              {dataset.status}
                            </span>

                          </td>

                        </tr>
                      ))}

                    </tbody>

                  </table>

                </div>

              </div>
            )}

          </>
        )}

      </div>
    </main>
  );
}