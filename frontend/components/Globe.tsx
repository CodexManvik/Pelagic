"use client";

import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { GlobeView } from "@deck.gl/core";
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
    <div className="relative h-[420px] w-full overflow-hidden rounded-2xl bg-ink">
      <DeckGL
        views={new GlobeView()}
        controller={{ dragRotate: true, scrollZoom: true }}
        initialViewState={{ longitude: -30, latitude: 0, zoom: 0.3 }}
        layers={layers}
        getTooltip={({ object }) =>
          object ? `${object.name} \u2014 activity ${object.intensity}` : null
        }
      />
      <div className="pointer-events-none absolute inset-x-6 bottom-6 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm text-foam/80">
        Sample globe view. Replace with live ARGO layer once ingestion is enabled.
      </div>
    </div>
  );
}
