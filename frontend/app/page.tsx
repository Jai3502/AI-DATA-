export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 py-20 text-center">
        <div className="mb-6 rounded-full border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-300">
          AI-Powered Data Analytics Platform
        </div>

        <h1 className="max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl">
          Turn Your Data Into
          <span className="text-blue-500"> Business Insights</span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
          Upload your CSV or Excel data and let AI analyze your business
          data, discover patterns, generate visualizations, and answer
          important questions.
        </p>

        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <a
            href="/login"
            className="rounded-xl bg-blue-600 px-7 py-3.5 font-semibold transition hover:bg-blue-500"
          >
            Get Started
          </a>

          <a
            href="/dashboard"
            className="rounded-xl border border-slate-700 px-7 py-3.5 font-semibold text-slate-200 transition hover:bg-slate-900"
          >
            Open Dashboard
          </a>
        </div>

        <div className="mt-16 grid w-full max-w-4xl gap-5 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h2 className="text-lg font-semibold">Upload Data</h2>
            <p className="mt-2 text-sm text-slate-400">
              Upload CSV and Excel datasets securely.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h2 className="text-lg font-semibold">AI Analysis</h2>
            <p className="mt-2 text-sm text-slate-400">
              Automatically discover patterns and data quality issues.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h2 className="text-lg font-semibold">Business Insights</h2>
            <p className="mt-2 text-sm text-slate-400">
              Get charts, insights, recommendations, and answers.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}