"use client";

import { useState } from "react";
import { postJson } from "../lib/api";

export default function QueryPanel() {
  const [question, setQuestion] = useState(
    "Show average temperature at 100m in the last 7 days."
  );
  const [answer, setAnswer] = useState<string | null>(null);
  const [sql, setSql] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setAnswer(null);
    setSql(null);

    try {
      const response = await postJson("/api/v1/query", {
        question,
        time_window_days: 7,
      });
      setAnswer(response.answer);
      setSql(response.sql);
    } catch (error) {
      setAnswer("Query failed. Check API keys or backend status.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex h-full flex-col justify-between gap-6 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-[#0a2027]/90 via-[#08161b]/90 to-[#071318]/95 p-6 shadow-glow">
      <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-coral/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-16 -left-10 h-44 w-44 rounded-full bg-kelp/20 blur-3xl" />

      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.45em] text-kelp">Agent Query</p>
        <h2 className="font-serif text-2xl">Ask the ocean a high-value question</h2>
        <p className="text-sm text-foam/70">
          The LangGraph pipeline routes intent, writes SQL, and returns a scientific interpretation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative z-[1] space-y-4">
        <textarea
          className="h-32 w-full resize-none rounded-2xl border border-white/15 bg-black/25 p-3 text-sm text-foam outline-none transition placeholder:text-foam/35 focus:border-coral/60 focus:ring-2 focus:ring-coral/20"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Example: Compare mean salinity in north_atlantic vs indian basin over the last 7 days."
        />
        <button
          type="submit"
          className="w-full rounded-2xl bg-gradient-to-r from-coral to-[#ff986f] px-4 py-3 text-sm font-semibold text-ink transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
          disabled={loading}
        >
          {loading ? "Running agents..." : "Run query"}
        </button>
      </form>

      <div className="relative z-[1] space-y-3 rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-foam/80">
        <p className="text-xs uppercase tracking-[0.3em] text-foam/50">Result</p>
        <p>{answer ?? "Awaiting your question."}</p>
        {sql ? (
          <pre className="overflow-x-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-foam/70">
            {sql}
          </pre>
        ) : null}
      </div>
    </div>
  );
}
