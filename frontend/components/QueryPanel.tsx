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
    <div className="flex h-full flex-col justify-between gap-6 rounded-3xl border border-white/10 bg-white/5 p-6">
      <div className="space-y-3">
        <p className="text-sm uppercase tracking-[0.4em] text-kelp">Agent Query</p>
        <h2 className="font-serif text-2xl">Ask the ocean a question</h2>
        <p className="text-sm text-foam/70">
          The LangGraph pipeline routes intent, writes SQL, and returns a scientific interpretation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="h-28 w-full resize-none rounded-2xl border border-white/10 bg-ink/60 p-3 text-sm text-foam outline-none"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button
          type="submit"
          className="w-full rounded-2xl bg-coral px-4 py-3 text-sm font-semibold text-ink transition hover:brightness-110"
          disabled={loading}
        >
          {loading ? "Running agents..." : "Run query"}
        </button>
      </form>

      <div className="space-y-3 rounded-2xl border border-white/10 bg-ink/60 p-4 text-sm text-foam/80">
        <p className="text-xs uppercase tracking-[0.3em] text-foam/50">Result</p>
        <p>{answer ?? "Awaiting your question."}</p>
        {sql ? <pre className="overflow-x-auto text-xs text-foam/60">{sql}</pre> : null}
      </div>
    </div>
  );
}
