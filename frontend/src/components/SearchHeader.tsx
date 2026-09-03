'use client';

import { useEffect, useRef, useState } from 'react';

interface Place {
  name: string;
  lat: number;
  lng: number;
}

interface SearchHeaderProps {
  originName?: string;
  destName?: string;
  onOpenVehicleSelect?: () => void;
  activeFilter?: string;
  onFilterChange?: (filter: string) => void;
  onSelectPlace: (kind: 'origin' | 'dest', place: Place) => void;
  currentDestName?: string;
}

interface GeocodeResult {
  display_name: string;
  lat: string;
  lon: string;
  type: string;
}

// A few useful quick-picks shown before the user types anything.
const QUICK_PICKS: Place[] = [
  { name: 'Bengaluru, Karnataka', lat: 12.9716, lng: 77.5946 },
  { name: 'Goa', lat: 15.2993, lng: 74.124 },
  { name: 'Mysuru, Karnataka', lat: 12.2958, lng: 76.6394 },
  { name: 'Mangaluru, Karnataka', lat: 12.9141, lng: 74.856 },
  { name: 'Hubballi, Karnataka', lat: 15.3647, lng: 75.124 },
  { name: 'Pune, Maharashtra', lat: 18.5204, lng: 73.8567 },
  { name: 'Hyderabad, Telangana', lat: 17.385, lng: 78.4867 },
  { name: 'Chennai, Tamil Nadu', lat: 13.0827, lng: 80.2707 },
];

function shorten(name: string): string {
  // Nominatim returns long display names ("Bengaluru, Bengaluru Urban, Karnataka, India").
  // Keep the first two comma parts for a compact chip.
  return name.split(',').slice(0, 2).join(',').trim();
}

export function SearchHeader({
  originName = 'Bengaluru',
  destName = 'Goa',
  onOpenVehicleSelect,
  activeFilter = 'route',
  onFilterChange,
  onSelectPlace,
}: SearchHeaderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [activeField, setActiveField] = useState<'origin' | 'dest'>('dest');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GeocodeResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Live geocoding search with debounce.
  useEffect(() => {
    if (!isSearchOpen) return;
    const trimmed = query.trim();
    if (trimmed.length < 3) {
      setResults([]);
      setSearching(false);
      setSearchError(null);
      return;
    }

    setSearching(true);
    setSearchError(null);
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&limit=6&countrycodes=in&q=${encodeURIComponent(trimmed)}`,
          { signal: controller.signal }
        );
        if (!res.ok) throw new Error(`Geocoder error ${res.status}`);
        const data = (await res.json()) as GeocodeResult[];
        setResults(data || []);
      } catch (e) {
        if ((e as Error).name !== 'AbortError') {
          setSearchError('Search unavailable — check your internet connection.');
        }
      } finally {
        if (!controller.signal.aborted) setSearching(false);
      }
    }, 400);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, isSearchOpen]);

  const openSearch = (field: 'origin' | 'dest') => {
    setActiveField(field);
    setQuery('');
    setResults([]);
    setSearchError(null);
    setIsSearchOpen(true);
  };

  const handlePick = (place: Place) => {
    onSelectPlace(activeField, place);
    setIsSearchOpen(false);
  };

  const currentValue = activeField === 'origin' ? originName : destName;

  return (
    <div className="absolute top-4 left-3 right-3 z-30 max-w-md mx-auto">
      {/* Search Input Bar */}
      <div
        onClick={() => openSearch('dest')}
        className="bg-white rounded-full shadow-md border border-gray-100 px-4 py-3 flex items-center gap-3 cursor-pointer hover:shadow-lg transition-all"
      >
        <div className="w-5 h-3.5 flex flex-col justify-between">
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[10px] uppercase tracking-wider text-[#8C8778] font-mono-custom truncate">
            {originName} → {destName}
          </div>
          <div className="text-[14.5px] text-[#16221D] truncate font-medium">
            {destName}
          </div>
        </div>
        <div
          onClick={(e) => {
            e.stopPropagation();
            if (onOpenVehicleSelect) onOpenVehicleSelect();
          }}
          className="w-7 h-7 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-semibold shadow-sm hover:opacity-90"
        >
          ⚡
        </div>
      </div>

      {/* Chip Row */}
      <div className="flex gap-2 mt-2.5 overflow-x-auto pb-1 no-scrollbar">
        <button
          onClick={() => onFilterChange && onFilterChange('route')}
          className={`rounded-full px-3.5 py-1.5 text-xs font-medium whitespace-nowrap shadow-sm transition-all flex items-center gap-1.5 ${
            activeFilter === 'route'
              ? 'bg-[#2F5C50] text-white shadow-md'
              : 'bg-white text-[#16221D] border border-gray-100 hover:bg-gray-50'
          }`}
        >
          🧭 Route
        </button>
        <button
          onClick={() => onFilterChange && onFilterChange('chargers')}
          className={`rounded-full px-3.5 py-1.5 text-xs font-medium whitespace-nowrap shadow-sm transition-all flex items-center gap-1.5 ${
            activeFilter === 'chargers'
              ? 'bg-[#2F5C50] text-white shadow-md'
              : 'bg-white text-[#16221D] border border-gray-100 hover:bg-gray-50'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-[#B8863F]" />
          Chargers nearby
        </button>
        <button
          onClick={() => onFilterChange && onFilterChange('dc_fast')}
          className={`rounded-full px-3.5 py-1.5 text-xs font-medium whitespace-nowrap shadow-sm transition-all flex items-center gap-1.5 ${
            activeFilter === 'dc_fast'
              ? 'bg-[#2F5C50] text-white shadow-md'
              : 'bg-white text-[#16221D] border border-gray-100 hover:bg-gray-50'
          }`}
        >
          ⚡ DC fast only
        </button>
        <button
          onClick={() => onFilterChange && onFilterChange('nh48')}
          className={`rounded-full px-3.5 py-1.5 text-xs font-medium whitespace-nowrap shadow-sm transition-all flex items-center gap-1.5 ${
            activeFilter === 'nh48'
              ? 'bg-[#2F5C50] text-white shadow-md'
              : 'bg-white text-[#16221D] border border-gray-100 hover:bg-gray-50'
          }`}
        >
          🅿️ Along NH48
        </button>
      </div>

      {/* Route Search Modal */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex flex-col justify-start p-3 sm:p-6 animate-fadeIn">
          <div className="w-full max-w-md mx-auto bg-[#FAF9F5] rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden flex flex-col max-h-[85vh]">
            {/* Header Input */}
            <div className="p-4 border-b border-[#E2DED3] bg-white">
              {/* From / To toggle */}
              <div className="flex items-center gap-1.5 bg-[#F0EEE7] rounded-full p-1 mb-3">
                <button
                  onClick={() => {
                    setActiveField('origin');
                    setQuery('');
                    setResults([]);
                  }}
                  className={`flex-1 py-1.5 px-3 rounded-full text-xs font-semibold transition-all ${
                    activeField === 'origin'
                      ? 'bg-white text-[#16221D] shadow-sm'
                      : 'text-[#8C8778]'
                  }`}
                >
                  From: {originName}
                </button>
                <button
                  onClick={() => {
                    setActiveField('dest');
                    setQuery('');
                    setResults([]);
                  }}
                  className={`flex-1 py-1.5 px-3 rounded-full text-xs font-semibold transition-all ${
                    activeField === 'dest'
                      ? 'bg-white text-[#16221D] shadow-sm'
                      : 'text-[#8C8778]'
                  }`}
                >
                  To: {destName}
                </button>
              </div>

              <div className="flex items-center gap-2.5 bg-[#FAF9F5] border-1.5 border-[#16221D] rounded-2xl px-3.5 py-2.5">
                <span className="text-sm text-gray-500">🔍</span>
                <input
                  type="text"
                  autoFocus
                  placeholder={
                    activeField === 'origin' ? 'Where from?' : 'Where to?'
                  }
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1 bg-transparent border-none outline-none text-sm text-[#16221D] font-medium"
                />
                {searching && (
                  <span className="text-xs text-[#8C8778] animate-pulse">searching…</span>
                )}
                <button
                  onClick={() => setIsSearchOpen(false)}
                  className="text-xs text-[#96692A] font-semibold px-1 py-0.5 hover:underline"
                >
                  Cancel
                </button>
              </div>
              <div className="text-[10px] text-[#8C8778] px-1 pt-1.5 truncate">
                Currently set: {currentValue}
              </div>
            </div>

            {/* Scrollable results */}
            <div className="overflow-y-auto flex-1 p-2">
              {searchError && (
                <div className="text-xs text-red-600 px-4 py-3">{searchError}</div>
              )}

              {!query.trim() && (
                <>
                  <div className="text-[10px] tracking-wider uppercase text-[#8C8778] font-mono-custom px-4 pt-3 pb-1">
                    Quick picks
                  </div>
                  {QUICK_PICKS.map((p, i) => (
                    <div
                      key={i}
                      onClick={() => handlePick(p)}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-[#E1EAE4]/50 rounded-xl cursor-pointer transition-colors border-b border-[#F1EFE8] last:border-none"
                    >
                      <div className="w-8 h-8 rounded-full bg-[#E1EAE4] text-[#2F5C50] flex items-center justify-center text-xs flex-shrink-0">
                        📍
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-semibold text-[#16221D]">
                          {p.name}
                        </div>
                        <div className="text-xs text-[#8C8778]">
                          {activeField === 'origin' ? 'Starting point' : 'Destination'}
                        </div>
                      </div>
                      <div className="text-xs text-[#2F5C50] font-bold">›</div>
                    </div>
                  ))}
                </>
              )}

              {query.trim().length >= 3 && results.length > 0 && (
                <>
                  <div className="text-[10px] tracking-wider uppercase text-[#8C8778] font-mono-custom px-4 pt-3 pb-1">
                    Search results
                  </div>
                  {results.map((r, i) => (
                    <div
                      key={i}
                      onClick={() =>
                        handlePick({
                          name: shorten(r.display_name),
                          lat: parseFloat(r.lat),
                          lng: parseFloat(r.lon),
                        })
                      }
                      className="flex items-center gap-3 px-4 py-3 hover:bg-[#E1EAE4]/50 rounded-xl cursor-pointer transition-colors border-b border-[#F1EFE8] last:border-none"
                    >
                      <div className="w-8 h-8 rounded-full bg-[#E1EAE4] text-[#2F5C50] flex items-center justify-center text-xs flex-shrink-0">
                        {r.type === 'city' || r.type === 'town' ? '🏙️' : '📍'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-[#16221D] truncate">
                          {shorten(r.display_name)}
                        </div>
                        <div className="text-[11px] text-[#8C8778] truncate">
                          {r.display_name}
                        </div>
                      </div>
                      <div className="text-xs text-[#2F5C50] font-bold">›</div>
                    </div>
                  ))}
                </>
              )}

              {query.trim().length >= 3 && results.length === 0 && !searching && (
                <div className="text-center py-8 text-xs text-[#8C8778]">
                  No places found for “{query}”
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
