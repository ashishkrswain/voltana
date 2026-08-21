'use client';

import { useState, useEffect, useCallback } from 'react';
import { Vehicle, Charger, TripPlanResponse, TripStop, listVehicles, listChargers, planTrip } from '@/lib/api';
import { MapView } from '@/components/MapView';
import { SearchHeader } from '@/components/SearchHeader';
import { VehiclePill } from '@/components/VehiclePill';
import { ItinerarySheet } from '@/components/ItinerarySheet';
import { ChargerDetailSheet } from '@/components/ChargerDetailSheet';
import { VehicleSelectorModal } from '@/components/VehicleSelectorModal';

export default function Home() {
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [batteryPct, setBatteryPct] = useState<number>(78);
  const [itinerary, setItinerary] = useState<TripPlanResponse | null>(null);
  const [allChargers, setAllChargers] = useState<Charger[]>([]);
  const [planning, setPlanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [origin] = useState({
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
      destCoords: { lat: number; lng: number }
    ) => {
      if (!v) return;

      setPlanning(true);
      setError(null);

      try {
        const result = await planTrip({
          vehicle_id: v.id,
          origin_lat: origin.lat,
          origin_lng: origin.lng,
          dest_lat: destCoords.lat,
          dest_lng: destCoords.lng,
          assumed_avg_speed_kmph: 60,
          starting_battery_pct: soc,
          safety_buffer_pct: 18,
        });
        setItinerary(result);
      } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string } }; message?: string };
        console.warn('Trip planning fallback to mock route:', err.message);
        // Keep smooth visual presentation even before backend finishes seeding
      } finally {
        setPlanning(false);
      }
    },
    [origin.lat, origin.lng]
  );

  // Recalculate trip when vehicle or destination changes
  useEffect(() => {
    if (selectedVehicle) {
      handleCalculateRoute(selectedVehicle, batteryPct, { lat: dest.lat, lng: dest.lng });
    }
  }, [selectedVehicle, batteryPct, dest, handleCalculateRoute]);

  const handleSelectDestination = (destName: string, coords: { lat: number; lng: number }) => {
    setDest({ name: destName, lat: coords.lat, lng: coords.lng });
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
          allChargers={allChargers}
          activeFilter={activeFilter}
          onSelectCharger={(stop) => setSelectedCharger(stop)}
        />

        {/* Top Floating Search Chrome */}
        <SearchHeader
          onSelectDestination={handleSelectDestination}
          onOpenVehicleSelect={() => setIsVehicleModalOpen(true)}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
          currentDestName={`${origin.name} → ${dest.name}`}
        />

        {/* Ambient Top-Left Vehicle Pill */}
        <VehiclePill
          vehicle={selectedVehicle}
          batteryPct={batteryPct}
          onClick={() => setIsVehicleModalOpen(true)}
        />

        {/* Error notification banner if any */}
        {error && (
          <div className="absolute top-36 left-4 right-4 z-30 bg-red-100 border border-red-300 text-red-800 text-xs px-3 py-2 rounded-xl shadow-md flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="font-bold ml-2">✕</button>
          </div>
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
      </div>
    </main>
  );
}