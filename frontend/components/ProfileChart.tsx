"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ProfileDatum = {
  depth: number;
  temperature: number | null;
  salinity: number | null;
};

type ProfileChartProps = {
  profile_data: ProfileDatum[];
};

function formatDepth(value: number) {
  return `${value} m`;
}

export default function ProfileChart({ profile_data }: ProfileChartProps) {
  const hasData = profile_data.length > 0;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-foam/60">Vertical Profile</p>
          <h3 className="mt-2 font-serif text-2xl text-foam">T-S Profile vs Depth</h3>
        </div>
        <p className="text-xs text-foam/60">Depth axis inverted (surface at top)</p>
      </div>

      {!hasData ? (
        <div className="rounded-2xl border border-dashed border-white/15 px-4 py-10 text-center text-sm text-foam/60">
          No profile points available.
        </div>
      ) : (
        <div className="h-[420px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={profile_data}
              margin={{ top: 16, right: 24, bottom: 12, left: 8 }}
            >
              <CartesianGrid stroke="rgba(231,247,243,0.15)" strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="temperature"
                name="Temperature"
                unit=" degC"
                stroke="rgba(231,247,243,0.8)"
                tick={{ fill: "rgba(231,247,243,0.8)", fontSize: 12 }}
                label={{
                  value: "Temperature (degC)",
                  position: "insideBottom",
                  offset: -5,
                  fill: "rgba(231,247,243,0.75)",
                }}
              />
              <YAxis
                type="number"
                dataKey="depth"
                name="Depth"
                unit=" m"
                reversed
                stroke="rgba(231,247,243,0.8)"
                tick={{ fill: "rgba(231,247,243,0.8)", fontSize: 12 }}
                tickFormatter={formatDepth}
                label={{
                  value: "Depth (m)",
                  angle: -90,
                  position: "insideLeft",
                  fill: "rgba(231,247,243,0.75)",
                }}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(7, 20, 24, 0.95)",
                  border: "1px solid rgba(231,247,243,0.2)",
                  borderRadius: 12,
                  color: "#e7f7f3",
                }}
                formatter={(value: number, name: string) => {
                  if (name === "temperature") {
                    return [`${value.toFixed(2)} degC`, "Temperature"];
                  }
                  if (name === "salinity") {
                    return [`${value.toFixed(3)} PSU`, "Salinity"];
                  }
                  return [value, name];
                }}
                labelFormatter={(label: number) => `Depth: ${label.toFixed(1)} m`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="temperature"
                name="Temperature"
                stroke="#ff7a45"
                strokeWidth={2.5}
                dot={false}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="salinity"
                name="Salinity"
                stroke="#3ad1b8"
                strokeWidth={2.5}
                dot={false}
                connectNulls
                xAxisId={0}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
