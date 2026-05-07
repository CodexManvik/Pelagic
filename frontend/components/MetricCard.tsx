type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export default function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <div className="animate-float-in rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.3em] text-foam/60">{label}</p>
      <p className="mt-2 font-serif text-2xl text-foam">{value}</p>
      {hint ? <p className="text-sm text-foam/70">{hint}</p> : null}
    </div>
  );
}
