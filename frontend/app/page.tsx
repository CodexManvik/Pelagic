import Globe from "../components/Globe";
import MetricCard from "../components/MetricCard";
import QueryPanel from "../components/QueryPanel";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-12 md:px-12">
      <section className="mx-auto flex max-w-6xl flex-col gap-10">
        <header className="grid gap-6 md:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.4em] text-kelp">Project Leviathan</p>
            <h1 className="font-serif text-4xl leading-tight md:text-6xl">
              FloatChat AI surfaces live ocean intelligence with explainable agent workflows.
            </h1>
            <p className="max-w-xl text-lg text-foam/80">
              Explore ARGO trajectories, inspect profiles, and ask natural language questions with
              traceable SQL evidence. Built for free-tier, production-grade demos.
            </p>
          </div>
          <div className="grid gap-4 md:justify-self-end">
            <MetricCard label="Freshness Lag" value="12 min" hint="Live ARGO ingest" />
            <MetricCard label="Query p95" value="3.9 s" hint="LLM + SQL" />
            <MetricCard label="Events/Day" value="480k" hint="Ingest throughput" />
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-4 shadow-glow">
            <Globe />
          </div>
          <QueryPanel />
        </section>
      </section>
    </main>
  );
}
