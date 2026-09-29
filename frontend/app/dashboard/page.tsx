"use client";

import { useEffect, useState } from "react";

import { apiRequest } from "@/lib/api";

import Sidebar from "@/components/dashboard/layout/Sidebar";

import Topbar from "@/components/dashboard/layout/Topbar";

import StatCard from "@/components/dashboard/ui/StatCard";

type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

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

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
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

        const [userData, organizationData] = await Promise.all([
          apiRequest<User>("/auth/me", {
            headers: authHeaders,
          }),

          apiRequest<Organization[]>("/organizations", {
            headers: authHeaders,
          }),
        ]);

        setUser(userData);
        setOrganizations(organizationData);

        // ---------------------------------------------------
        // Load datasets for the first available organization
        // ---------------------------------------------------

        if (organizationData.length > 0) {
          const selectedOrganizationId =
            organizationData[0].id;

          const datasetData = await apiRequest<Dataset[]>(
            `/datasets?organization_id=${selectedOrganizationId}`,
            {
              headers: authHeaders,
            },
          );

          setDatasets(datasetData);
        } else {
          setDatasets([]);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load dashboard.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020617] text-white">
        <p className="text-slate-400">
          Loading dashboard...
        </p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020617] px-6 text-white">
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-6 py-4 text-red-300">
          {error}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      {/* Desktop navigation */}
      <Sidebar />

      {/* Desktop topbar */}
      <Topbar />

      {/* Main content */}
      <div className="lg:pl-64 lg:pt-20">
        <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">

          {/* Page header */}
          <div className="mb-8">
            <p className="text-sm font-medium text-blue-400">
              Overview
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">
              Dashboard
            </h1>

            <p className="mt-2 text-slate-400">
              Welcome back, {user?.full_name || "User"}.
              Here is your analytics workspace overview.
            </p>
          </div>

          {/* Stats */}
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              title="Organizations"
              value={organizations.length}
              description="Available workspaces"
              icon="⌂"
            />

            <StatCard
              title="Datasets"
              value={datasets.length}
              description="Uploaded datasets"
              icon="▣"
            />

            <StatCard
              title="Analyses"
              value={0}
              description="Completed analyses"
              icon="✦"
            />

            <StatCard
              title="Reports"
              value={0}
              description="Generated reports"
              icon="▤"
            />

          </div>

          {/* Workspace section */}
          <section className="mt-8">
            <div className="mb-5">
              <h2 className="text-xl font-semibold text-white">
                Your Organizations
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Select a workspace to work with your business data.
              </p>
            </div>

            {organizations.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-10 text-center">
                <p className="text-slate-400">
                  No organizations found.
                </p>
              </div>
            ) : (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {organizations.map((organization) => (
                  <button
                    key={organization.id}
                    type="button"
                    className="group rounded-2xl border border-slate-800 bg-slate-900/70 p-6 text-left transition hover:border-blue-500/50 hover:bg-slate-900"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600/10 text-lg text-blue-400">
                          ⌂
                        </div>

                        <h3 className="mt-5 text-lg font-semibold text-white">
                          {organization.name}
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          {organization.slug}
                        </p>
                      </div>

                      <span className="rounded-lg bg-blue-600/10 px-3 py-1 text-xs font-medium text-blue-400">
                        Workspace
                      </span>
                    </div>

                    <div className="mt-6 flex items-center text-sm font-medium text-slate-400 group-hover:text-blue-400">
                      Open workspace

                      <span className="ml-2 transition group-hover:translate-x-1">
                        →
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>

          {/* Recent activity */}
          <section className="mt-8">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Recent Activity
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Your latest data analysis activity will appear here.
                </p>
              </div>

              <div className="mt-8 flex min-h-32 items-center justify-center rounded-xl border border-dashed border-slate-800">
                <p className="text-sm text-slate-500">
                  No recent activity yet.
                </p>
              </div>
            </div>
          </section>

          {/* Account information */}
          <section className="mt-8">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h2 className="text-lg font-semibold text-white">
                Account
              </h2>

              <div className="mt-5 grid gap-5 md:grid-cols-2">
                <div>
                  <p className="text-sm text-slate-500">
                    Name
                  </p>

                  <p className="mt-1 font-medium text-slate-200">
                    {user?.full_name}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-500">
                    Email
                  </p>

                  <p className="mt-1 font-medium text-slate-200">
                    {user?.email}
                  </p>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </main>
  );
}