'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Vehicle,
  Charger,
  TripPlanResponse,
  TripStop,
  SavedTrip,
  listVehicles,
  listChargers,
  planTrip,
  saveTrip,
  listTrips,
  deleteTrip,
} from '@/lib/api';
import { MapView } from '@/components/MapView';
import { SearchHeader } from '@/components/SearchHeader';
import { VehiclePill } from '@/components/VehiclePill';
import { ItinerarySheet } from '@/components/ItinerarySheet';
import { ChargerDetailSheet } from '@/components/ChargerDetailSheet';
import { VehicleSelectorModal } from '@/components/VehicleSelectorModal';
import { TripLoadingState } from '@/components/TripLoadingState';
import { TripErrorState } from '@/components/TripErrorState';
import { TripHistorySheet } from '@/components/TripHistorySheet';
import { OnboardingModal } from '@/components/OnboardingModal';
import { SettingsSheet } from '@/components/SettingsSheet';

interface PlanError {
  message: string;
  gap?: {
    gap_start_km: number;
    gap_end_km: number;
    remaining_range_km: number;
    current_battery_pct: number;
    current_km: number;
  } | null;
}

const ONBOARDING_SEEN_KEY = 'voltana_onboarding_seen';
const DEFAULTS_KEY = 'voltana_trip_defaults';

interface TripDefaults {
  avgSpeed: number;
  safetyBuffer: number;
}

function loadDefaults(): TripDefaults {
  try {
    const raw = localStorage.getItem(DEFAULTS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<TripDefaults>;
      return {
        avgSpeed:
          typeof parsed.avgSpeed === 'number' && parsed.avgSpeed >= 20 && parsed.avgSpeed <= 120
            ? parsed.avgSpeed
            : 60,
        safetyBuffer:
          typeof parsed.safetyBuffer === 'number' &&
          parsed.safetyBuffer >= 5 &&
          parsed.safetyBuffer <= 50
            ? parsed.safetyBuffer
            : 18,
      };
    }
  } catch {
    /* ignore */
  }
  return { avgSpeed: 60, safetyBuffer: 18 };
}

function formatTripDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
    });
  } catch {
    return '';
  }
}

export default function Home() {
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [batteryPct, setBatteryPct] = useState<number>(78);
  const [itinerary, setItinerary] = useState<TripPlanResponse | null>(null);
  const [allChargers, setAllChargers] = useState<Charger[]>([]);
  const [acChargers, setAcChargers] = useState<Charger[] | null>(null);
  const [planning, setPlanning] = useState(false);
  const [error, setError] = useState<PlanError | null>(null);

  const [origin, setOrigin] = useState({
    name: 'Bengaluru',
    lat: 12.9716,
    lng: 77.5946,
  });

  const [dest, setDest] = useState({
    name: 'Goa',
    lat: 15.2993,
    lng: 74.124,
  });

  const [activeFilter, setActiveFilter] = useState('route');
  const [selectedCharger, setSelectedCharger] = useState<TripStop | null>(null);
  const [isVehicleModalOpen, setIsVehicleModalOpen] = useState(false);

  // Trip defaults (speed + safety buffer), persisted locally
  const [defaults, setDefaults] = useState<TripDefaults>(loadDefaults);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // History + onboarding state
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [history, setHistory] = useState<SavedTrip[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const savedVehicleRef = useRef<string | null>(null);

  // Initialize with the top Indian EV (e.g. Tata Nexon EV Long Range) and list chargers
  useEffect(() => {
    async function initData() {
      try {
        const [vData, cData] = await Promise.allSettled([
          listVehicles({ page: 1, page_size: 20 }),
          listChargers({ page: 1, page_size: 100 }),
        ]);

        if (vData.status === 'fulfilled' && vData.value.vehicles?.length > 0) {
          const nexon = vData.value.vehicles.find((v) => v.model.includes('Nexon')) || vData.value.vehicles[0];
          setSelectedVehicle(nexon);
        }

        if (cData.status === 'fulfilled' && cData.value.chargers) {
          setAllChargers(cData.value.chargers);
        }
      } catch (e) {
        console.error('Failed to load initial data', e);
      }
    }
    initData();
  }, []);

  const handleCalculateRoute = useCallback(
    async (
      v: Vehicle | null,
      soc: number,
      originPlace: { name: string; lat: number; lng: number },
      destPlace: { name: string; lat: number; lng: number }
    ) => {
      if (!v) return;

      setPlanning(true);
      setError(null);

      try {
        const result = await planTrip({
          vehicle_id: v.id,
          origin_lat: originPlace.lat,
          origin_lng: originPlace.lng,
          dest_lat: destPlace.lat,
          dest_lng: destPlace.lng,
          assumed_avg_speed_kmph: defaults.avgSpeed,
          starting_battery_pct: soc,
          safety_buffer_pct: defaults.safetyBuffer,
        });
        setItinerary(result);

        // Persist to trip history so the user can "plan again" later.
        const routeKey = `${originPlace.lat},${originPlace.lng}->${destPlace.lat},${destPlace.lng}`;
        if (savedVehicleRef.current !== routeKey) {
          savedVehicleRef.current = routeKey;
          try {
            await saveTrip({
              vehicle_id: v.id,
              origin_name: originPlace.name,
              origin_lat: originPlace.lat,
              origin_lng: originPlace.lng,
              dest_name: destPlace.name,
              dest_lat: destPlace.lat,
              dest_lng: destPlace.lng,
              assumed_avg_speed_kmph: defaults.avgSpeed,
              starting_battery_pct: soc,
              safety_buffer_pct: defaults.safetyBuffer,
              total_distance_km: result.total_distance_km,
              total_estimated_duration_min: result.total_estimated_duration_min,
            });
          } catch (saveErr) {
            console.warn('Failed to save trip to history', saveErr);
          }
        }
      } catch (e: unknown) {
        const err = e as {
          response?: { data?: { detail?: string | Record<string, unknown> } };
          message?: string;
        };
        const rawDetail = err.response?.data?.detail;
        if (rawDetail && typeof rawDetail === 'object') {
          const d = rawDetail as Record<string, unknown>;
          setError({
            message: typeof d.message === 'string' ? d.message : 'Could not plan this trip',
            gap:
              d.type === 'no_charger_gap' && typeof d.gap_start_km === 'number'
                ? {
                    gap_start_km: d.gap_start_km as number,
                    gap_end_km: d.gap_end_km as number,
                    remaining_range_km: d.remaining_range_km as number,
                    current_battery_pct: d.current_battery_pct as number,
                    current_km: d.current_km as number,
                  }
                : null,
          });
        } else {
          const detail =
            (typeof rawDetail === 'string' ? rawDetail : undefined) ||
            err.message ||
            'Could not plan this trip';
          setError({ message: detail, gap: null });
        }
        console.warn('Trip planning failed:', err);
      } finally {
        setPlanning(false);
      }
    },
    [defaults]
  );

  // Recalculate trip when vehicle, battery, origin, destination, or defaults change
  useEffect(() => {
    if (selectedVehicle) {
      handleCalculateRoute(selectedVehicle, batteryPct, origin, dest);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedVehicle, batteryPct, origin, dest, defaults]);

  // First-run onboarding (skippable, localStorage-backed)
  useEffect(() => {
    try {
      if (!localStorage.getItem(ONBOARDING_SEEN_KEY)) {
        const t = setTimeout(() => setShowOnboarding(true), 600);
        return () => clearTimeout(t);
      }
    } catch {
      // localStorage unavailable — skip onboarding
    }
  }, []);

  const openHistory = async () => {
    setIsHistoryOpen(true);
    setHistoryLoading(true);
    try {
      const data = await listTrips({ page: 1, page_size: 30 });
      setHistory(data.trips);
    } catch (e) {
      console.warn('Failed to load history', e);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handlePlanAgain = (trip: SavedTrip) => {
    setIsHistoryOpen(false);
    setOrigin({ name: trip.origin_name, lat: trip.origin_lat, lng: trip.origin_lng });
    setDest({ name: trip.dest_name, lat: trip.dest_lat, lng: trip.dest_lng });
    setBatteryPct(Math.round(trip.starting_battery_pct));
    setError(null);
  };

  const handleDeleteTrip = async (id: string) => {
    try {
      await deleteTrip(id);
      setHistory((prev) => prev.filter((t) => t.id !== id));
    } catch (e) {
      console.warn('Failed to delete trip', e);
    }
  };

  const handleDefaultsChange = (next: TripDefaults) => {
    setDefaults(next);
    try {
      localStorage.setItem(DEFAULTS_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
    setError(null);
  };

  // "Show AC charging options nearby" — filter the fetched chargers for ones
  // compatible with the vehicle's AC port and reveal them on the map.
  const handleShowACOptions = () => {
    if (!selectedVehicle) return;
    const acPort = selectedVehicle.ac_charge_port_type;
    const matches = allChargers.filter((c) => {
      if (!acPort) return false;
      const connectors = (c.connector_types || '').split(',').map((s) => s.trim());
      return connectors.includes(acPort);
    });
    setAcChargers(matches);
    setError(null);
    setActiveFilter('chargers');
    // Drop a pin so the user knows what to look at — surfaced via the sheet.
    if (matches.length === 0) {
      setError({
        message: `No AC (${acPort}) chargers found in the current dataset near this route.`,
        gap: null,
      });
    }
  };

  const handleClearACOptions = () => {
    setAcChargers(null);
  };

  const handleSelectPlace = (
    kind: 'origin' | 'dest',
    place: { name: string; lat: number; lng: number }
  ) => {
    if (kind === 'origin') {
      setOrigin({ name: place.name, lat: place.lat, lng: place.lng });
    } else {
      setDest({ name: place.name, lat: place.lat, lng: place.lng });
    }
    setError(null);
  };

  const handleStartJourney = () => {
    alert(`Starting trip from ${origin.name} to ${dest.name} in your ${selectedVehicle?.make || 'EV'} ${selectedVehicle?.model || ''}!`);
  };

  const vehicleDisplayName = selectedVehicle
    ? `${selectedVehicle.make} ${selectedVehicle.model} ${selectedVehicle.variant || ''}`.trim()
    : 'Nexon EV Long Range';

  return (
    <main className="w-screen h-screen overflow-hidden bg-[#16221D] flex items-center justify-center relative">
      {/* Phone App Container / Responsive Viewport */}
      <div className="w-full h-full max-w-[480px] max-h-[100vh] sm:max-h-[880px] sm:rounded-[38px] bg-[#F1F2F1] relative overflow-hidden shadow-2xl border-0 sm:border-[8px] sm:border-[#111827]">
        {/* Interactive Leaflet Map Layer */}
        <MapView
          itinerary={itinerary}
          originCoords={{ lat: origin.lat, lng: origin.lng }}
          destCoords={{ lat: dest.lat, lng: dest.lng }}
          originName={origin.name}
          destName={dest.name}
          allChargers={acChargers ?? allChargers}
          activeFilter={activeFilter}
          onSelectCharger={(stop) => setSelectedCharger(stop)}
        />

        {/* Top Floating Search Chrome */}
        <SearchHeader
          originName={origin.name}
          destName={dest.name}
          onSelectPlace={handleSelectPlace}
          onOpenVehicleSelect={() => setIsVehicleModalOpen(true)}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        {/* Ambient Top-Left Vehicle Pill */}
        <VehiclePill
          vehicle={selectedVehicle}
          batteryPct={batteryPct}
          onClick={() => setIsVehicleModalOpen(true)}
        />

        {/* History + Settings buttons (below search header, right side) */}
        <button
          onClick={openHistory}
          title="Trip history"
          className="absolute top-[136px] right-3 z-40 w-9 h-9 rounded-full bg-white shadow-md border border-gray-100 flex items-center justify-center text-base hover:bg-gray-50 active:scale-95 transition-all"
        >
          🕘
        </button>
        <button
          onClick={() => setIsSettingsOpen(true)}
          title="Settings"
          className="absolute top-[182px] right-3 z-40 w-9 h-9 rounded-full bg-white shadow-md border border-gray-100 flex items-center justify-center text-base hover:bg-gray-50 active:scale-95 transition-all"
        >
          ⚙️
        </button>

        {/* Error state */}
        {error && !planning && (
          <TripErrorState
            message={error.message}
            gap={error.gap}
            onRetry={() =>
              selectedVehicle &&
              handleCalculateRoute(selectedVehicle, batteryPct, origin, dest)
            }
            onSwitchVehicle={() => {
              setError(null);
              setIsVehicleModalOpen(true);
            }}
            onShowACOptions={handleShowACOptions}
          />
        )}

        {/* AC options notice (shown after "Show AC charging options") */}
        {acChargers && !error && !planning && (
          <div className="absolute top-[120px] left-3 z-40 bg-[#16221D] text-white rounded-2xl px-3.5 py-2.5 shadow-lg border border-white/10 text-xs flex items-center gap-2.5 max-w-[280px]">
            <span className="flex-shrink-0">⚡</span>
            <div className="min-w-0">
              <div className="font-semibold truncate">
                {acChargers.length} AC-compatible charger
                {acChargers.length === 1 ? '' : 's'} found
              </div>
              <div className="text-[10px] text-white/70">
                {selectedVehicle?.ac_charge_port_type || 'AC'} outlets near this
                route
              </div>
            </div>
            <button
              onClick={handleClearACOptions}
              className="ml-auto text-white/70 hover:text-white font-bold text-sm pl-1"
            >
              ✕
            </button>
          </div>
        )}

        {/* Route-calculating loading overlay */}
        {planning && (
          <TripLoadingState
            vehicleName={
              selectedVehicle
                ? `${selectedVehicle.make} ${selectedVehicle.model}`
                : 'your EV'
            }
            routeName={`${origin.name} → ${dest.name}`}
          />
        )}

        {/* Bottom Itinerary Sheet */}
        <ItinerarySheet
          itinerary={itinerary}
          vehicleName={vehicleDisplayName}
          originName={origin.name}
          destName={dest.name}
          onSelectCharger={(stop) => setSelectedCharger(stop)}
          onStartJourney={handleStartJourney}
          isPlanning={planning}
        />

        {/* Charger Detail Sheet Modal */}
        <ChargerDetailSheet
          stop={selectedCharger}
          onClose={() => setSelectedCharger(null)}
          onConfirmStop={(stop) => {
            alert(`Stop set: ${stop.charger_name} at km ${stop.km_marker.toFixed(0)}`);
          }}
        />

        {/* Vehicle Selection & SoC Modal */}
        <VehicleSelectorModal
          isOpen={isVehicleModalOpen}
          onClose={() => setIsVehicleModalOpen(false)}
          onSelectVehicle={(v) => setSelectedVehicle(v)}
          selectedVehicle={selectedVehicle}
          batteryPct={batteryPct}
          onBatteryChange={(pct) => setBatteryPct(pct)}
        />

        {/* Trip History */}
        <TripHistorySheet
          isOpen={isHistoryOpen}
          onClose={() => setIsHistoryOpen(false)}
          trips={history}
          loading={historyLoading}
          onPlanAgain={handlePlanAgain}
          onDelete={handleDeleteTrip}
        />

        {/* First-run Onboarding */}
        <OnboardingModal
          isOpen={showOnboarding}
          onClose={() => {
            setShowOnboarding(false);
            try {
              localStorage.setItem(ONBOARDING_SEEN_KEY, '1');
            } catch {
              /* ignore */
            }
          }}
          onPickVehicle={() => {
            setShowOnboarding(false);
            try {
              localStorage.setItem(ONBOARDING_SEEN_KEY, '1');
            } catch {
              /* ignore */
            }
            setIsVehicleModalOpen(true);
          }}
          hasVehicle={selectedVehicle !== null}
          vehicleName={vehicleDisplayName}
        />

        {/* Settings */}
        <SettingsSheet
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          avgSpeed={defaults.avgSpeed}
          safetyBuffer={defaults.safetyBuffer}
          onChange={handleDefaultsChange}
        />
      </div>
    </main>
  );
}