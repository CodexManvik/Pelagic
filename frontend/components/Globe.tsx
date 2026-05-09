"use client";

import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { _GlobeView as GlobeView } from "@deck.gl/core";
import { ScatterplotLayer } from "@deck.gl/layers";

const sampleFloats = [
  { name: "North Pacific", position: [-150, 32], intensity: 0.6 },
  { name: "South Atlantic", position: [-20, -35], intensity: 0.8 },
  { name: "Indian Ocean", position: [85, -15], intensity: 0.5 },
  { name: "Southern Ocean", position: [30, -55], intensity: 0.9 },
];

export default function Globe() {
  const layers = useMemo(
    () => [
      new ScatterplotLayer({
        id: "float-points",
        data: sampleFloats,
        getPosition: (d) => d.position,
        getFillColor: (d) => [
          Math.round(255 * d.intensity),
          120,
          69,
          180,
        ],
        getRadius: 120000,
        radiusMinPixels: 3,
        radiusMaxPixels: 20,
        pickable: true,
      }),
    ],
    []
  );

  return (
    <div className="relative h-[460px] w-full overflow-hidden rounded-3xl border border-white/10 bg-ink/70">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,122,69,0.18),transparent_35%),radial-gradient(circle_at_80%_75%,rgba(11,124,106,0.24),transparent_42%)]" />
      <DeckGL
        views={new GlobeView()}
        controller={{ dragRotate: true, scrollZoom: true }}
        initialViewState={{ longitude: -30, latitude: 0, zoom: 0.3 }}
        layers={layers}
        getTooltip={({ object }) =>
          object ? `${object.name} \u2014 activity ${object.intensity}` : null
        }
      />
      <div className="pointer-events-none absolute inset-x-6 top-6 flex items-center justify-between rounded-2xl border border-white/15 bg-black/30 px-4 py-3 text-xs uppercase tracking-[0.25em] text-foam/75 backdrop-blur">
        <span>Global Float Activity</span>
        <span>Live-style Demo Layer</span>
      </div>
      <div className="pointer-events-none absolute inset-x-6 bottom-6 rounded-2xl border border-white/15 bg-black/35 px-4 py-3 text-sm text-foam/80 backdrop-blur">
        Prototype globe layer with regional activity intensity. Connect this component to live ARGO API slices for production mode.
      </div>
    </div>
  );
}
