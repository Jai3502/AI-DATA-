"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

type User = {
  full_name: string;
  email: string;
};

export default function Topbar() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          return;
        }

        const data = await apiRequest<User>("/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setUser(data);
      } catch {
        setUser(null);
      }
    }

    loadUser();
  }, []);

  const initials =
    user?.full_name
      ?.split(" ")
      .map((name) => name[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  return (
    <header className="fixed inset-x-0 top-0 z-30 hidden h-20 border-b border-slate-800 bg-slate-950/95 backdrop-blur lg:block lg:pl-64">
      <div className="flex h-full items-center justify-between px-8">
        {/* Left */}
        <div>
          <p className="text-sm text-slate-500">
            Analytics Workspace
          </p>

          <p className="text-sm font-medium text-slate-200">
            Your data, analyzed intelligently.
          </p>
        </div>

        {/* Right */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <button
            type="button"
            className="hidden rounded-xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-500 transition hover:border-slate-700 hover:text-slate-300 xl:block"
          >
            Search anything...
          </button>

          {/* Notification */}
          <button
            type="button"
            aria-label="Notifications"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-slate-400 transition hover:border-slate-700 hover:text-white"
          >
            🔔
          </button>

          {/* User */}
          <div className="flex items-center gap-3 border-l border-slate-800 pl-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
              {initials}
            </div>

            <div className="hidden min-w-0 md:block">
              <p className="max-w-40 truncate text-sm font-medium text-white">
                {user?.full_name || "User"}
              </p>

              <p className="max-w-40 truncate text-xs text-slate-500">
                {user?.email || ""}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}