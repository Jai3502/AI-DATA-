"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useEffect, useState } from "react";

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

type Organization = {
  id: string;
  name: string;
  slug: string;
};

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [organizationId, setOrganizationId] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showUploadForm, setShowUploadForm] = useState(false);
  const [datasetName, setDatasetName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  async function loadDatasets() {
    try {
      setLoading(true);
      setError("");

      const organizations = await apiRequest<Organization[]>(
        "/organizations",
      );

      if (!organizations.length) {
        setDatasets([]);
        setOrganizationId("");
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

  useEffect(() => {
    loadDatasets();
  }, []);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setUploadError("");
    setUploadSuccess("");
  }

  async function handleUpload(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setUploadError("");
    setUploadSuccess("");

    if (!organizationId) {
      setUploadError("No organization selected.");
      return;
    }

    if (!datasetName.trim()) {
      setUploadError("Dataset name is required.");
      return;
    }

    if (!selectedFile) {
      setUploadError("Please select a CSV or Excel file.");
      return;
    }

    const extension = selectedFile.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (
      extension !== "csv" &&
      extension !== "xlsx" &&
      extension !== "xls"
    ) {
      setUploadError(
        "Unsupported file type. Please upload CSV, XLSX, or XLS.",
      );
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setUploadError(
        "File size cannot exceed 50 MB.",
      );
      return;
    }

    try {
      setUploading(true);

      const formData = new FormData();

      formData.append(
        "organization_id",
        organizationId,
      );

      formData.append(
        "name",
        datasetName.trim(),
      );

      if (description.trim()) {
        formData.append(
          "description",
          description.trim(),
        );
      }

      formData.append("file", selectedFile);

      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL ||
        "http://127.0.0.1:8000";

      const response = await fetch(
        `${apiUrl}/datasets/upload`,
        {
          method: "POST",
          headers: {
            ...(token
              ? {
                  Authorization: `Bearer ${token}`,
                }
              : {}),
          },
          body: formData,
        },
      );

      if (!response.ok) {
        let message = "Dataset upload failed.";

        try {
          const errorData = await response.json();

          if (errorData?.detail) {
            message =
              typeof errorData.detail === "string"
                ? errorData.detail
                : message;
          }
        } catch {
          message = `Upload failed with status ${response.status}.`;
        }

        throw new Error(message);
      }

      await response.json();

      setUploadSuccess(
        "Dataset uploaded and profiled successfully.",
      );

      setDatasetName("");
      setDescription("");
      setSelectedFile(null);
      setShowUploadForm(false);

      await loadDatasets();
    } catch (err) {
      setUploadError(
        err instanceof Error
          ? err.message
          : "Dataset upload failed.",
      );
    } finally {
      setUploading(false);
    }
  }

  function resetUploadForm() {
    setDatasetName("");
    setDescription("");
    setSelectedFile(null);
    setUploadError("");
    setUploadSuccess("");
    setShowUploadForm(false);
  }

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
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

          <button
            type="button"
            onClick={() => {
              setShowUploadForm(true);
              setUploadError("");
              setUploadSuccess("");
            }}
            className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500"
          >
            + Upload Dataset
          </button>
        </div>

        {/* Upload Form */}
        {showUploadForm && (
          <section className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold">
                Upload Dataset
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Upload CSV or Excel data for analysis.
              </p>
            </div>

            <form
              onSubmit={handleUpload}
              className="space-y-5"
            >
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Dataset Name
                </label>

                <input
                  type="text"
                  value={datasetName}
                  onChange={(event) =>
                    setDatasetName(event.target.value)
                  }
                  placeholder="e.g. Sales Performance 2026"
                  maxLength={255}
                  disabled={uploading}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Description
                  <span className="ml-2 text-xs text-slate-500">
                    Optional
                  </span>
                </label>

                <textarea
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                  placeholder="Describe what this dataset contains..."
                  rows={4}
                  disabled={uploading}
                  className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Dataset File
                </label>

                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  disabled={uploading}
                  className="block w-full cursor-pointer rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-400 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:font-medium file:text-white hover:file:bg-blue-500"
                />

                <p className="mt-2 text-xs text-slate-500">
                  CSV, XLSX, XLS • Maximum 50 MB
                </p>

                {selectedFile && (
                  <p className="mt-3 text-sm text-blue-400">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              {uploadError && (
                <div className="rounded-xl border border-red-800 bg-red-950/40 p-4">
                  <p className="text-sm text-red-400">
                    {uploadError}
                  </p>
                </div>
              )}

              <div className="flex flex-col gap-3 pt-2 sm:flex-row">
                <button
                  type="submit"
                  disabled={uploading}
                  className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {uploading
                    ? "Uploading..."
                    : "Upload Dataset"}
                </button>

                <button
                  type="button"
                  onClick={resetUploadForm}
                  disabled={uploading}
                  className="rounded-xl border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </section>
        )}

        {/* Success */}
        {uploadSuccess && (
          <div className="mb-6 rounded-xl border border-emerald-800 bg-emerald-950/40 p-4">
            <p className="text-sm text-emerald-400">
              {uploadSuccess}
            </p>
          </div>
        )}

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

                <button
                  type="button"
                  onClick={() => {
                    setShowUploadForm(true);
                    setUploadError("");
                    setUploadSuccess("");
                  }}
                  className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500"
                >
                  Upload Your First Dataset
                </button>
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

                          <td className="px-6 py-5 text-slate-300">
                            {dataset.original_filename}
                          </td>

                          <td className="px-6 py-5 text-slate-300">
                            {dataset.row_count ?? "—"}
                          </td>

                          <td className="px-6 py-5 text-slate-300">
                            {dataset.column_count ?? "—"}
                          </td>

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