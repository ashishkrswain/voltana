'use client';

import { useState } from 'react';
import type { TripPlanResponse, TripStop } from '@/lib/api';

interface ItinerarySheetProps {
  itinerary: TripPlanResponse | null;
  vehicleName?: string;
  originName?: string;
  destName?: string;
  onSelectCharger?: (stop: TripStop) => void;
  onStartJourney?: () => void;
  isPlanning?: boolean;
}

function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

export function ItinerarySheet({
  itinerary,
  vehicleName = 'Nexon EV Long Range',
  originName = 'Bengaluru',
  destName = 'Goa',
  onSelectCharger,
  onStartJourney,
  isPlanning = false,
}: ItinerarySheetProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate charging stops count and charge time
  const chargingStops = itinerary
    ? itinerary.legs.filter((l) => l.stop !== null)
    : [];
  const totalChargeTimeMin = chargingStops.reduce(
    (acc, l) => acc + (l.stop?.estimated_charge_time_min || 0),
    0
  );

  const totalDistanceKm = itinerary ? itinerary.total_distance_km : 560;
  const totalDurationMin = itinerary ? itinerary.total_estimated_duration_min : 585;
  const stopsCount = chargingStops.length > 0 ? chargingStops.length : 2;
  const chargeTimeMin = totalChargeTimeMin > 0 ? totalChargeTimeMin : 60;

  return (
    <div
      className={`absolute left-0 right-0 bottom-0 z-30 bg-[#FAF9F5] rounded-t-3xl shadow-[-6px_0_24px_rgba(0,0,0,0.18)] border-t border-[#E2DED3] transition-all duration-300 flex flex-col ${
        isExpanded ? 'max-h-[85%]' : 'max-h-[58%] md:max-h-[50%]'
      }`}
    >
      {/* Handle */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full py-2 flex items-center justify-center cursor-pointer select-none"
      >
        <div className="w-9 h-1 bg-[#D5D7DA] rounded-full hover:bg-gray-400 transition-colors" />
      </div>

      {/* Route Summary */}
      <div className="px-5 pb-3.5 border-b border-[#E2DED3]">
        <div className="flex items-center justify-between">
          <div className="text-[17px] font-bold text-[#16221D] flex items-center gap-1.5 font-serif-custom">
            {originName} → {destName}
          </div>
          {isPlanning && (
            <span className="text-xs bg-[#E1EAE4] text-[#2F5C50] font-semibold px-2 py-0.5 rounded-full animate-pulse">
              Calculating...
            </span>
          )}
        </div>
        <div className="text-xs text-[#8C8778] mt-0.5">
          via NH48 · charge-optimised for {vehicleName}
        </div>

        {/* Metrics Row */}
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

        {/* Start Journey CTA */}
        <button
          onClick={onStartJourney}
          className="mt-3.5 w-full bg-[#2F5C50] text-white rounded-full py-2.5 px-5 text-sm font-semibold flex items-center justify-center gap-2 hover:bg-[#254b41] active:scale-[0.99] transition-all shadow-md"
        >
          <span>▶</span> Start journey
        </button>
      </div>

      {/* Step-by-step leg list */}
      <div className="overflow-y-auto px-5 py-3 flex-1 no-scrollbar divide-y divide-[#F1EFE8]">
        {itinerary ? (
          <>
            {/* Start point */}
            <div className="flex items-start gap-3 py-2.5">
              <div className="w-7 h-7 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                ●
              </div>
              <div className="flex-1">
                <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                  <span>Depart {originName}</span>
                  <span className="font-mono-custom text-[11px] text-[#8C8778]">km 0</span>
                </div>
                <div className="text-xs text-[#8C8778] mt-0.5">
                  <b className="font-mono-custom text-[#2F5C50] font-bold">100%</b> battery
                </div>
              </div>
            </div>

            {/* Intermediate legs and charging stops */}
            {itinerary.legs.map((leg, idx) => {
              if (leg.stop) {
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
                          {Math.round(stop.arrival_battery_pct)}% → {Math.round(stop.charge_to_pct)}%
                        </span>
                        <span>·</span>
                        <span>
                          {Math.round(stop.estimated_charge_time_min)} min ·{' '}
                          {stop.power_kw ? `${stop.power_kw.toFixed(0)} kW DC` : '50 kW DC'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              }
              return null;
            })}

            {/* Destination Point */}
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
                    ~{Math.max(15, Math.round(itinerary.legs[itinerary.legs.length - 1]?.battery_end_pct || 18))}%
                  </b>{' '}
                  battery remaining
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Static preview fallback matching mockup */
          <>
            <div className="flex items-start gap-3 py-2.5">
              <div className="w-7 h-7 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                ●
              </div>
              <div className="flex-1">
                <div className="text-[13.5px] font-semibold text-[#16221D] flex justify-between">
                  <span>Depart Bengaluru</span>
                  <span className="font-mono-custom text-[11px] text-[#8C8778]">km 0</span>
                </div>
                <div className="text-xs text-[#8C8778] mt-0.5">
                  <b className="font-mono-custom text-[#2F5C50] font-bold">100%</b> battery
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
                  charger_address: 'NH48, near Hassan Bypass, Karnataka 573201',
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
                  <span className="hover:text-[#96692A] transition-colors">
                    Statiq — NH48, Hassan
                  </span>
                  <span className="font-mono-custom text-[11px] text-[#8C8778]">km 187</span>
                </div>
                <div className="text-xs text-[#8C8778] mt-0.5 flex items-center gap-2">
                  <span className="font-mono-custom text-[#2F5C50] font-bold">24% → 80%</span>
                  <span>·</span>
                  <span>32 min · 60 kW DC</span>
                </div>
              </div>
            </div>

            <div
              onClick={() =>
                onSelectCharger &&
                onSelectCharger({
                  charger_name: 'Tata Power — Belur Bypass',
                  km_marker: 341,
                  arrival_battery_pct: 21,
                  charge_to_pct: 75,
                  estimated_charge_time_min: 28,
                  charger_id: 'mock-2',
                  charger_address: 'NH73 / Belur Bypass, Karnataka',
                  power_kw: 50,
                  network_name: 'Tata Power EZ Charge',
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
                  <span className="hover:text-[#96692A] transition-colors">
                    Tata Power — Belur Bypass
                  </span>
                  <span className="font-mono-custom text-[11px] text-[#8C8778]">km 341</span>
                </div>
                <div className="text-xs text-[#8C8778] mt-0.5 flex items-center gap-2">
                  <span className="font-mono-custom text-[#2F5C50] font-bold">21% → 75%</span>
                  <span>·</span>
                  <span>28 min · 50 kW DC</span>
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
                  <span className="font-mono-custom text-[11px] text-[#8C8778]">km 560</span>
                </div>
                <div className="text-xs text-[#8C8778] mt-0.5">
                  <b className="font-mono-custom text-[#2F5C50] font-bold">~18%</b> battery remaining
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Disclaimer */}
      <div className="text-[10.5px] text-[#8C8778] text-center px-5 py-2.5 border-t border-[#E2DED3] bg-white/60">
        Live charger availability not yet tracked — verify before departure
      </div>
    </div>
  );
}
