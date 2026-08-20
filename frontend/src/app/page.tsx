'use client';

import { useState } from 'react';
import { Vehicle, TripPlanResponse } from '@/lib/api';
import { VehicleSelector } from '@/components/VehicleSelector';
import { RouteInput } from '@/components/RouteInput';
import { ItineraryDisplay } from '@/components/ItineraryDisplay';

export default function Home() {
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [itinerary, setItinerary] = useState<TripPlanResponse | null>(null);
  const [planning, setPlanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePlanTrip = async (origin: { lat: number; lng: number }, dest: { lat: number; lng: number }) => {
    if (!selectedVehicle) return;

    setPlanning(true);
    setError(null);

    try {
      const { planTrip } = await import('@/lib/api');
      const result = await planTrip({
        vehicle_id: selectedVehicle.id,
        origin_lat: origin.lat,
        origin_lng: origin.lng,
        dest_lat: dest.lat,
        dest_lng: dest.lng,
        assumed_avg_speed_kmph: 60,
        starting_battery_pct: 100,
        safety_buffer_pct: 20,
      });
      setItinerary(result);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setError(err.response?.data?.detail || err.message || 'Failed to plan trip');
    } finally {
      setPlanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <h1 className="text-2xl font-bold text-gray-900">Voltana</h1>
            </div>
            <p className="text-sm text-gray-500">India EV Route & Charging Planner</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Vehicle Selector */}
          <div className="lg:col-span-1">
            <VehicleSelector
              onSelect={setSelectedVehicle}
              selectedVehicle={selectedVehicle}
            />
          </div>

          {/* Right Column - Route Input + Itinerary */}
          <div className="lg:col-span-2 space-y-6">
            <RouteInput
              onPlan={handlePlanTrip}
              disabled={!selectedVehicle || planning}
            />

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                {error}
              </div>
            )}

            {planning && (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <div className="flex items-center justify-center gap-3">
                  <svg className="animate-spin w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="text-gray-600">Planning your trip...</span>
                </div>
              </div>
            )}

            <ItineraryDisplay
              itinerary={itinerary}
              vehicleName={selectedVehicle ? `${selectedVehicle.make} ${selectedVehicle.model} ${selectedVehicle.variant}` : ''}
            />

            {!selectedVehicle && !itinerary && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <p className="text-lg font-medium text-gray-700">Welcome to Voltana</p>
                <p className="mt-2">Select a vehicle from the left panel to start planning your EV trip.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}