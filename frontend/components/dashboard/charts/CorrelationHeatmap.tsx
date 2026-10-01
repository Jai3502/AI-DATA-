"use client";

export type CorrelationPoint = {
  x: string;
  y: string;
  correlation: number;
};

type CorrelationHeatmapProps = {
  title: string;
  data: CorrelationPoint[];
};

function getCorrelationClass(value: number) {
  const absolute = Math.abs(value);

  if (absolute >= 0.7) {
    return value >= 0
      ? "bg-blue-600/80"
      : "bg-red-600/80";
  }

  if (absolute >= 0.4) {
    return value >= 0
      ? "bg-blue-500/50"
      : "bg-red-500/50";
  }

  if (absolute >= 0.2) {
    return value >= 0
      ? "bg-blue-500/30"
      : "bg-red-500/30";
  }

  return "bg-slate-800";
}

export default function CorrelationHeatmap({
  title,
  data,
}: CorrelationHeatmapProps) {
  const columns = Array.from(
    new Set(data.map((item) => item.x)),
  );

  const getValue = (x: string, y: string) => {
    return (
      data.find(
        (item) => item.x === x && item.y === y,
      )?.correlation ?? null
    );
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white">
          {title}
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Correlation between numeric columns
        </p>
      </div>

      <div className="overflow-x-auto">
        <div
          className="grid min-w-[700px]"
          style={{
            gridTemplateColumns: `180px repeat(${columns.length}, minmax(90px, 1fr))`,
          }}
        >
          <div className="border-b border-slate-800 p-3" />

          {columns.map((column) => (
            <div
              key={column}
              className="border-b border-slate-800 p-3 text-center text-xs font-medium text-slate-400"
            >
              {column}
            </div>
          ))}

          {columns.map((row) => (
            <div key={row} className="contents">
              <div className="border-b border-slate-800 p-3 text-sm font-medium text-slate-300">
                {row}
              </div>

              {columns.map((column) => {
                const value = getValue(row, column);

                return (
                  <div
                    key={`${row}-${column}`}
                    className={`border-b border-l border-slate-800 p-2 ${value !== null ? getCorrelationClass(value) : "bg-slate-900"}`}
                    title={
                      value !== null
                        ? `${row} vs ${column}: ${value.toFixed(4)}`
                        : "No correlation data"
                    }
                  >
                    <div className="flex h-14 items-center justify-center rounded-lg">
                      <span className="text-xs font-semibold text-white">
                        {value !== null
                          ? value.toFixed(2)
                          : "—"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-4 text-xs text-slate-500">
        <span>Strong: |r| ≥ 0.70</span>
        <span>Moderate: |r| ≥ 0.40</span>
        <span>Weak: |r| ≥ 0.20</span>
      </div>
    </div>
  );
}