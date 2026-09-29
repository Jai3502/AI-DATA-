"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: "⌂",
  },
  {
    name: "Datasets",
    href: "/datasets",
    icon: "▣",
  },
  {
    name: "AI Analyst",
    href: "/dashboard/analyst",
    icon: "✦",
  },
  {
    name: "Reports",
    href: "/dashboard/reports",
    icon: "▤",
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: "⚙",
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-slate-800 bg-slate-950 lg:flex lg:flex-col">
      
      {/* Brand */}
      <div className="flex h-20 items-center border-b border-slate-800 px-6">
        <Link
          href="/dashboard"
          className="flex items-center gap-3"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-lg font-bold text-white">
            AI
          </div>

          <div>
            <p className="text-sm font-semibold text-white">
              AI Data Analyst
            </p>

            <p className="text-xs text-slate-500">
              Analytics Platform
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6">
        <p className="mb-3 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Workspace
        </p>

        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-600/15 text-blue-400"
                    : "text-slate-400 hover:bg-slate-900 hover:text-white"
                }`}
              >
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-lg text-base ${
                    isActive
                      ? "bg-blue-600/20 text-blue-400"
                      : "bg-slate-900 text-slate-500"
                  }`}
                >
                  {item.icon}
                </span>

                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom */}
      <div className="border-t border-slate-800 p-4">
        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-xs font-medium text-slate-300">
            AI Data Workspace
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Analyze your business data with AI-powered insights.
          </p>
        </div>
      </div>
    </aside>
  );
}