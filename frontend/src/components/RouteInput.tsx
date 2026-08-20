'use client';

import { useState } from 'react';

interface RouteInputProps {
  onPlan: (origin: { lat: number; lng: number }, dest: { lat: number; lng: number }) => void;
  disabled?: boolean;
}

export function RouteInput({ onPlan, disabled }: RouteInputProps) {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [originCoords, setOriginCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [destCoords, setDestCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [geocoding, setGeocoding] = useState(false);

  const handleGeocode = async (address: string, setCoords: (c: { lat: number; lng: number }) => void, setInput: (s: string) => void) => {
    if (!address.trim()) return;
    setGeocoding(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`
      );
      const data = await res.json();
      if (data[0]) {
        const coords = { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) };
        setCoords(coords);
        setInput(data[0].display_name);
      }
    } catch (e) {
      console.error('Geocoding failed', e);
    } finally {
      setGeocoding(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (originCoords && destCoords) {
      onPlan(originCoords, destCoords);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Plan Your Trip</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
          <div className="relative">
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              onBlur={() => handleGeocode(origin, setOriginCoords, setOrigin)}
              placeholder="e.g., Bangalore, Karnataka"
              className="w-full border rounded px-3 py-2 pr-10"
              disabled={disabled}
            />
            {geocoding && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin">
                <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
            )}
            {originCoords && !geocoding && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-center my-2">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
          <div className="relative">
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              onBlur={() => handleGeocode(destination, setDestCoords, setDestination)}
              placeholder="e.g., Panjim, Goa"
              className="w-full border rounded px-3 py-2 pr-10"
              disabled={disabled}
            />
            {geocoding && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin">
                <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
            )}
            {destCoords && !geocoding && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={disabled || !originCoords || !destCoords}
        className="mt-6 w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Plan Trip
      </button>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Avg Speed (km/h)</label>
          <input
            type="number"
            defaultValue={60}
            min={20}
            max={120}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Starting Battery (%)</label>
          <input
            type="number"
            defaultValue={100}
            min={10}
            max={100}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Safety Buffer (%)</label>
          <input
            type="number"
            defaultValue={20}
            min={5}
            max={50}
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>
    </form>
  );
}