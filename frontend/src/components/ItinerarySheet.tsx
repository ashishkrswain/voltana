'use client';

import { useRef, useState } from 'react';
import type { TripPlanResponse, TripStop } from '@/lib/api';

interface ItinerarySheetProps {
  itinerary: TripPlanResponse | null;
  vehicleName?: string;
  originName?: string;
  destName?: string;
  onSelectCharger?: (stop: TripStop) => void;
  onStartJourney?: () => void;
  isPlanning?: boolean;
  /** Start expanded (showing full card) or collapsed (mini bar). Default: collapsed. */
  defaultExpanded?: boolean;
  /** Vehicle battery capacity in kWh — used to estimate charging cost. */
  batteryKwh?: number;
}

const COLLAPSED_HEIGHT = 100; // px — handle + summary bar
const MAX_VISIBLE_HEIGHT = 'min(72vh, 620px)';

function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

// Rough per-kWh rates (₹) by network slug. Fallback is a mid DC-fast price.
// DC fast is typically ₹18–24/kWh in India; AC is cheaper (~₹12–15).
const RATE_BY_SLUG: Record<string, number> = {
  'bolt-earth': 22,
  'statiq': 22,
  'tata-power-ez': 20,
  'chargezone': 22,
  'jio-bp-pulse': 21,
  'ather-grid': 15,
};

function costForStop(batteryKwh: number, stop: TripStop): number {
  const energyKwh =
    batteryKwh * (Math.max(0, stop.charge_to_pct - stop.arrival_battery_pct)) / 100;
  const slug = (stop.network_slug || '').toLowerCase();
  const rate = RATE_BY_SLUG[slug] ?? 22;
  return energyKwh * rate;
}

function estimateTripCost(batteryKwh: number, itinerary: TripPlanResponse | null): number {
  if (!itinerary || batteryKwh <= 0) return 0;
  return itinerary.legs.reduce(
    (sum, leg) => (leg.stop ? sum + costForStop(batteryKwh, leg.stop) : sum),
    0
  );
}

export function ItinerarySheet({
  itinerary,
  vehicleName = 'Nexon EV Long Range',
  originName = 'Bengaluru',
  destName = 'Goa',
  onSelectCharger,
  onStartJourney,
  isPlanning = false,
  defaultExpanded = false,
  batteryKwh = 0,
}: ItinerarySheetProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [dragging, setDragging] = useState(false);
  const [dragDelta, setDragDelta] = useState(0);
  const gesture = useRef<{
    startY: number;
    expandedAtStart: boolean;
    moved: boolean;
  } | null>(null);
  const didDragRef = useRef(false);

  // Charging-stops summary. Live from itinerary; small static preview only
  // before the first plan resolves.
  const chargingStops = itinerary
    ? itinerary.legs.filter((l) => l.stop !== null)
    : [];
  const totalChargeTimeMin = chargingStops.reduce(
    (acc, l) => acc + (l.stop?.estimated_charge_time_min || 0),
    0
  );
  const showMockFallback = itinerary === null && !isPlanning;
  const totalDistanceKm = itinerary
    ? itinerary.total_distance_km
    : showMockFallback
      ? 560
      : 0;
  const totalDurationMin = itinerary
    ? itinerary.total_estimated_duration_min
    : showMockFallback
      ? 585
      : 0;
  const stopsCount = itinerary ? chargingStops.length : showMockFallback ? 2 : 0;
  const chargeTimeMin = itinerary ? totalChargeTimeMin : showMockFallback ? 60 : 0;
  const tripCost = estimateTripCost(batteryKwh, itinerary);
  const showCost = tripCost > 0;

  // ---- Drag handlers (touch / pen / mouse) ----
  const onPointerDown = (e: React.PointerEvent) => {
    gesture.current = {
      startY: e.clientY,
      expandedAtStart: expanded,
      moved: false,
    };
    didDragRef.current = false;
    setDragging(true);
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const g = gesture.current;
    if (!g) return;
    const delta = e.clientY - g.startY;
    if (Math.abs(delta) > 6) {
      g.moved = true;
      didDragRef.current = true;
    }
    // Only allow pulling the sheet down (minimize), not up beyond full.
    setDragDelta(Math.max(0, delta));
  };

  const endGesture = () => {
    const g = gesture.current;
    // Pull-down gesture on the expanded sheet collapses it.
    if (g && g.moved && g.expandedAtStart) setExpanded(false);
    setDragging(false);
    setDragDelta(0);
    gesture.current = null;
  };

  const toggle = () => setExpanded((v) => !v);

  const style: React.CSSProperties = {
    height: expanded ? MAX_VISIBLE_HEIGHT : COLLAPSED_HEIGHT,
    transform: dragging ? `translateY(${dragDelta}px)` : undefined,
    transition: dragging
      ? 'none'
      : 'height 300ms cubic-bezier(0.22, 1, 0.36, 1), transform 300ms cubic-bezier(0.22, 1, 0.36, 1)',
  };

  return (
    <div
      className="absolute left-0 right-0 bottom-0 z-30 bg-[#FAF9F5] rounded-t-3xl shadow-[-6px_0_24px_rgba(0,0,0,0.18)] border-t border-[#E2DED3] flex flex-col overflow-hidden"
      style={style}
    >
      {/* Grab zone: handle + always-visible route header */}
      <div
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endGesture}
        onPointerCancel={endGesture}
        onClick={() => {
          // Toggle on a plain tap (no drag movement).
          if (!didDragRef.current) toggle();
          didDragRef.current = false;
        }}
        className="w-full flex-shrink-0 cursor-pointer select-none"
        style={{ touchAction: 'pan-y' }}
      >
        {/* Handle */}
        <div className="w-full py-2 flex items-center justify-center">
          <div className="w-9 h-1 bg-[#D5D7DA] rounded-full" />
        </div>

        {/* Route header */}
        <div className="px-5 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="text-[#16221D] font-bold text-[15px] truncate font-serif-custom">
                {originName} → {destName}
              </div>
              {isPlanning && (
                <span className="text-[10px] bg-[#E1EAE4] text-[#2F5C50] font-semibold px-2 py-0.5 rounded-full animate-pulse whitespace-nowrap">
                  Calculating…
                </span>
              )}
            </div>
            <span
              className={`text-[#8C8778] text-sm flex-shrink-0 ml-2 transition-transform duration-300 ${
                expanded ? '' : 'rotate-180'
              }`}
            >
              ▼
            </span>
          </div>
          <div className="text-[11px] text-[#8C8778] mt-0.5 font-mono-custom">
            {totalDistanceKm.toFixed(0)} km · {formatDuration(totalDurationMin)} ·{' '}
            {stopsCount} {stopsCount === 1 ? 'stop' : 'stops'} ·{' '}
            {chargeTimeMin.toFixed(0)} min charging
            {showCost && <> · ~₹{Math.round(tripCost).toLocaleString('en-IN')}</>}
          </div>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="flex-1 min-h-0 flex flex-col">
          {/* Metrics + CTA */}
          <div className="px-5 pb-3.5 border-t border-[#E2DED3] bg-white/40">
            <div className="flex gap-4 mt-3">
              <div className="flex flex-col">
                <div className="font-mono-custom text-[15px] font-bold text-[#16221D]">
                  {totalDistanceKm.toFixed(0)} km
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#8C8778] mt-0.5">
                  distance
                </div>
              </div>
              <div className="flex flex-col">
                <div className="font-mono-custom text-[15px] font-bold text-[#16221D]">
                  {formatDuration(totalDurationMin)}
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#8C8778] mt-0.5">
                  total time
                </div>
              </div>
              <div className="flex flex-col">
                <div className="font-mono-custom text-[15px] font-bold text-[#96692A]">
                  {stopsCount} {stopsCount === 1 ? 'stop' : 'stops'}
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#8C8778] mt-0.5">
                  charging
                </div>
              </div>
              <div className="flex flex-col">
                <div className="font-mono-custom text-[15px] font-bold text-[#16221D]">
                  {chargeTimeMin.toFixed(0)} min
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#8C8778] mt-0.5">
                  charge time
                </div>
              </div>
            </div>

            <div className="text-[11px] text-[#8C8778] mt-2 flex items-center justify-between gap-2">
              <span className="truncate">
                via NH48 · charge-optimised for {vehicleName}
              </span>
              {showCost && (
                <span className="font-mono-custom font-bold text-[#96692A] flex-shrink-0">
                  ~₹{Math.round(tripCost).toLocaleString('en-IN')}
                </span>
              )}
            </div>

            <button
              onClick={onStartJourney}
              className="mt-3 w-full bg-[#2F5C50] text-white rounded-full py-2.5 px-5 text-sm font-semibold flex items-center justify-center gap-2 hover:bg-[#254b41] active:scale-[0.99] transition-all shadow-md"
            >
              <span>▶</span> Start journey
            </button>
          </div>

          {/* Leg list */}
          <div className="overflow-y-auto px-5 py-3 flex-1 no-scrollbar divide-y divide-[#F1EFE8]">
            {itinerary ? (
              <>
                <div className="flex items-start gap-3 py-2.5">
                  <div className="w-7 h-7 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    ●
                  </div>
                  <div className="flex-1">
                    <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                      <span>Depart {originName}</span>
                      <span className="font-mono-custom text-[11px] text-[#8C8778]">
                        km 0
                      </span>
                    </div>
                    <div className="text-xs text-[#8C8778] mt-0.5">
                      <b className="font-mono-custom text-[#2F5C50] font-bold">
                        {Math.round(
                          itinerary.legs[0]?.battery_start_pct ?? 100
                        )}
                        %
                      </b>{' '}
                      battery
                    </div>
                  </div>
                </div>

                {itinerary.legs.map((leg, idx) => {
                  if (!leg.stop) return null;
                  const stop = leg.stop;
                  return (
                    <div
                      key={idx}
                      onClick={() => onSelectCharger && onSelectCharger(stop)}
                      className="flex items-start gap-3 py-2.5 cursor-pointer hover:bg-[#E1EAE4]/30 rounded-xl px-1 -mx-1 transition-colors"
                    >
                      <div className="w-7 h-7 rounded-full bg-[#FBEFDC] border-1.5 border-[#B8863F] text-[#96692A] flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                        ⚡
                      </div>
                      <div className="flex-1">
                        <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between items-center">
                          <span className="hover:text-[#96692A] transition-colors">
                            {stop.charger_name}
                          </span>
                          <span className="font-mono-custom text-[11px] text-[#8C8778]">
                            km {stop.km_marker.toFixed(0)}
                          </span>
                        </div>
                        <div className="text-xs text-[#8C8778] mt-0.5 flex items-center gap-2">
                          <span className="font-mono-custom text-[#2F5C50] font-bold">
                            {Math.round(stop.arrival_battery_pct)}% →{' '}
                            {Math.round(stop.charge_to_pct)}%
                          </span>
                          <span>·</span>
                          <span>
                            {Math.round(stop.estimated_charge_time_min)} min ·{' '}
                            {stop.power_kw
                              ? `${stop.power_kw.toFixed(0)} kW DC`
                              : '50 kW DC'}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}

                <div className="flex items-start gap-3 py-2.5">
                  <div className="w-7 h-7 rounded-full bg-[#16221D] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    ◆
                  </div>
                  <div className="flex-1">
                    <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                      <span>Arrive {destName}</span>
                      <span className="font-mono-custom text-[11px] text-[#8C8778]">
                        km {itinerary.total_distance_km.toFixed(0)}
                      </span>
                    </div>
                    <div className="text-xs text-[#8C8778] mt-0.5">
                      <b className="font-mono-custom text-[#2F5C50] font-bold">
                        ~
                        {Math.max(
                          10,
                          Math.round(
                            itinerary.legs[itinerary.legs.length - 1]
                              ?.battery_end_pct ?? 18
                          )
                        )}
                        %
                      </b>{' '}
                      battery remaining
                    </div>
                  </div>
                </div>
              </>
            ) : showMockFallback ? (
              <>
                <div className="flex items-start gap-3 py-2.5">
                  <div className="w-7 h-7 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    ●
                  </div>
                  <div className="flex-1">
                    <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                      <span>Depart Bengaluru</span>
                      <span className="font-mono-custom text-[11px] text-[#8C8778]">
                        km 0
                      </span>
                    </div>
                    <div className="text-xs text-[#8C8778] mt-0.5">
                      <b className="font-mono-custom text-[#2F5C50] font-bold">
                        100%
                      </b>{' '}
                      battery
                    </div>
                  </div>
                </div>

                <div
                  onClick={() =>
                    onSelectCharger &&
                    onSelectCharger({
                      charger_name: 'Statiq — NH48, Hassan',
                      km_marker: 187,
                      arrival_battery_pct: 24,
                      charge_to_pct: 80,
                      estimated_charge_time_min: 32,
                      charger_id: 'mock-1',
                      charger_address:
                        'NH48, near Hassan Bypass, Karnataka 573201',
                      power_kw: 60,
                      network_name: 'Statiq',
                      connector_types: 'CCS2, Type 2',
                    })
                  }
                  className="flex items-start gap-3 py-2.5 cursor-pointer hover:bg-[#E1EAE4]/30 rounded-xl px-1 -mx-1 transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-[#FBEFDC] border-1.5 border-[#B8863F] text-[#96692A] flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    ⚡
                  </div>
                  <div className="flex-1">
                    <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between items-center">
                      <span>Statiq — NH48, Hassan</span>
                      <span className="font-mono-custom text-[11px] text-[#8C8778]">
                        km 187
                      </span>
                    </div>
                    <div className="text-xs text-[#8C8778] mt-0.5 flex items-center gap-2">
                      <span className="font-mono-custom text-[#2F5C50] font-bold">
                        24% → 80%
                      </span>
                      <span>·</span>
                      <span>32 min · 60 kW DC</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3 py-2.5">
                  <div className="w-7 h-7 rounded-full bg-[#16221D] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    ◆
                  </div>
                  <div className="flex-1">
                    <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                      <span>Arrive Goa</span>
                      <span className="font-mono-custom text-[11px] text-[#8C8778]">
                        km 560
                      </span>
                    </div>
                    <div className="text-xs text-[#8C8778] mt-0.5">
                      <b className="font-mono-custom text-[#2F5C50] font-bold">
                        ~18%
                      </b>{' '}
                      battery remaining
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-10 text-xs text-[#8C8778]">
                Plan a route to see your charging itinerary.
              </div>
            )}
          </div>

          {/* Disclaimer */}
          <div className="text-[10.5px] text-[#8C8778] text-center px-5 py-2.5 border-t border-[#E2DED3] bg-white/60 flex-shrink-0">
            Live charger availability not yet tracked — verify before departure
          </div>
        </div>
      )}
    </div>
  );
}
