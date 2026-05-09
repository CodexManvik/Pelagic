type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export default function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <div className="group animate-float-in rounded-2xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent px-4 py-4 backdrop-blur transition duration-300 hover:-translate-y-1 hover:border-coral/35 hover:shadow-glow">
      <p className="text-[10px] uppercase tracking-[0.35em] text-foam/60">{label}</p>
      <p className="mt-2 font-serif text-3xl leading-none text-foam">{value}</p>
      {hint ? <p className="mt-2 text-sm text-foam/75">{hint}</p> : null}
    </div>
  );
}
