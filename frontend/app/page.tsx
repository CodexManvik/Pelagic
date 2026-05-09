import Globe from "../components/Globe";
import MetricCard from "../components/MetricCard";
import QueryPanel from "../components/QueryPanel";

export default function HomePage() {
  const pillars = [
    {
      title: "Live Ingestion Fabric",
      body: "Serverless producer + queue-backed delivery keeps ocean telemetry flowing under free-tier constraints.",
    },
    {
      title: "Explainable Agent Core",
      body: "LangGraph routes intent, validates SQL, and returns domain-aware scientific narratives with traceability.",
    },
    {
      title: "Operational Visibility",
      body: "Freshness lag, p95, and quality telemetry are surfaced for fast debugging and interview-grade architecture storytelling.",
    },
  ];

  return (
    <main className="min-h-screen px-4 py-8 md:px-10 md:py-12">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-10">
        <header className="relative overflow-hidden rounded-[28px] border border-white/10 bg-gradient-to-br from-[#0c2b34]/70 via-[#0b1d24]/75 to-[#0a161b]/90 p-7 shadow-glow md:p-10">
          <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-coral/20 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-20 left-12 h-72 w-72 rounded-full bg-kelp/20 blur-3xl" />

          <div className="relative z-[1] grid gap-8 md:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-6">
              <p className="text-xs uppercase tracking-[0.5em] text-kelp">Project Leviathan</p>
              <h1 className="font-serif text-4xl leading-tight md:text-6xl">
                Ocean intelligence from live ARGO streams to explainable AI insights.
              </h1>
              <p className="max-w-2xl text-base text-foam/85 md:text-lg">
                FloatChat AI combines event-driven ingestion, domain-safe SQL generation, and
                geospatial analytics into one production-style research platform.
              </p>

              <div className="flex flex-wrap gap-3 text-xs uppercase tracking-[0.22em] text-foam/70">
                <span className="rounded-full border border-white/20 bg-white/5 px-3 py-1">Live ARGO</span>
                <span className="rounded-full border border-white/20 bg-white/5 px-3 py-1">LangGraph</span>
                <span className="rounded-full border border-white/20 bg-white/5 px-3 py-1">Neon + Vector</span>
                <span className="rounded-full border border-white/20 bg-white/5 px-3 py-1">QStash + Redis</span>
              </div>
            </div>

            <div className="grid gap-4 md:justify-self-end">
              <MetricCard label="Freshness Lag" value="12 min" hint="Source to query readiness" />
              <MetricCard label="Query p95" value="3.9 s" hint="Router -> SQL -> Interpretation" />
              <MetricCard label="Events/Day" value="480k" hint="Ingestion throughput" />
            </div>
          </div>

          <div className="relative z-[1] mt-8 grid gap-4 md:grid-cols-3">
            {pillars.map((pillar) => (
              <article
                key={pillar.title}
                className="rounded-2xl border border-white/10 bg-black/20 p-4 backdrop-blur"
              >
                <p className="font-serif text-xl text-foam">{pillar.title}</p>
                <p className="mt-2 text-sm leading-relaxed text-foam/75">{pillar.body}</p>
              </article>
            ))}
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.45fr_0.55fr]">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur">
            <Globe />
          </div>
          <QueryPanel />
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <article className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-kelp">Reliability</p>
            <p className="mt-2 font-serif text-2xl">Idempotent ingestion and replay-safe writes</p>
          </article>
          <article className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-kelp">Safety</p>
            <p className="mt-2 font-serif text-2xl">SQL allowlist + query cost guardrail</p>
          </article>
          <article className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-kelp">Clarity</p>
            <p className="mt-2 font-serif text-2xl">Scientific answer with evidence trail</p>
          </article>
        </section>
      </section>
    </main>
  );
}
