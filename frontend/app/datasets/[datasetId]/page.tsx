"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiRequest } from "@/lib/api";

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

export default function DatasetDetailPage() {
  const params = useParams();
  const datasetId = params.datasetId as string;

  const [profile, setProfile] = useState<DatasetProfile | null>(null);
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