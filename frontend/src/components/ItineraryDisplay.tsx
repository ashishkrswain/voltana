'use client';

import { TripPlanResponse, TripLeg, TripStop } from '@/lib/api';

interface ItineraryDisplayProps {
  itinerary: TripPlanResponse | null;
  vehicleName: string;
}

function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

function formatBattery(pct: number): string {
  return `${Math.round(pct)}%`;
}

function getBatteryColor(pct: number): string {
  if (pct >= 50) return 'text-green-600';
  if (pct >= 20) return 'text-yellow-600';
  return 'text-red-600';
}

export function ItineraryDisplay({ itinerary, vehicleName }: ItineraryDisplayProps) {
  if (!itinerary) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Trip Itinerary</h2>
        <div className="text-sm text-gray-500">
          Vehicle: <span className="font-medium text-gray-900">{vehicleName}</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm text-blue-600">Total Distance</div>
          <div className="text-2xl font-bold text-blue-900">{itinerary.total_distance_km.toFixed(1)} km</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm text-green-600">Total Duration</div>
          <div className="text-2xl font-bold text-green-900">{formatDuration(itinerary.total_estimated_duration_min)}</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-sm text-purple-600">Avg Speed</div>
          <div className="text-2xl font-bold text-purple-900">{itinerary.assumed_avg_speed_kmph} km/h</div>
        </div>
      </div>

      {/* Legs */}
      <div className="space-y-4">
        {itinerary.legs.map((leg, index) => (
          <div key={index} className="border rounded-lg overflow-hidden">
            {/* Leg Header */}
            <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                  {index + 1}
                </div>
                <div>
                  <div className="font-medium">Leg {index + 1}</div>
                  <div className="text-sm text-gray-500">
                    {leg.from_km.toFixed(1)} km → {leg.to_km.toFixed(1)} km
                    ({formatDuration(leg.duration_min)} drive)
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <span className={`font-mono ${getBatteryColor(leg.battery_start_pct)}`}>
                  {formatBattery(leg.battery_start_pct)}
                </span>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 11l-5 5m0 0l-5-5m5 5V3" />
                </svg>
                <span className={`font-mono ${getBatteryColor(leg.battery_end_pct)}`}>
                  {formatBattery(leg.battery_end_pct)}
                </span>
              </div>
            </div>

            {/* Stop Details */}
            {leg.stop && (
              <div className="p-4 bg-amber-50 border-t">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <span className="font-medium text-amber-900">Charging Stop</span>
                  </div>
                  <span className="text-sm text-amber-700 px-2 py-1 bg-amber-100 rounded">
                    @ km {leg.stop.km_marker.toFixed(1)}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-amber-700 font-medium">{leg.stop.charger_name}</div>
                    <div className="text-gray-600">Arrive: {formatBattery(leg.stop.arrival_battery_pct)}</div>
                    <div className="text-gray-600">Charge to: {formatBattery(leg.stop.charge_to_pct)}</div>
                    <div className="text-gray-600">Time: {formatDuration(leg.stop.estimated_charge_time_min)}</div>
                  </div>
                </div>

                {/* Visual battery bar */}
                <div className="mt-3">
                  <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                    <span>Battery:</span>
                    <span>{formatBattery(leg.stop.arrival_battery_pct)}</span>
                    <span>→</span>
                    <span>{formatBattery(leg.stop.charge_to_pct)}</span>
                  </div>
                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all"
                      style={{ width: `${leg.stop.arrival_battery_pct}%` }}
                    />
                  </div>
                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden mt-1">
                    <div
                      className="h-full bg-blue-500 rounded-full transition-all"
                      style={{ width: `${leg.stop.charge_to_pct}%` }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* No stops message */}
        {itinerary.legs.length === 1 && !itinerary.legs[0].stop && (
          <div className="text-center py-8 text-green-600">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-medium">No charging stops needed!</p>
            <p className="text-sm text-gray-500 mt-1">Your vehicle can complete this trip on a single charge.</p>
          </div>
        )}
      </div>
    </div>
  );
}