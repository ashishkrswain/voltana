'use client';

import { useState } from 'react';

interface SearchHeaderProps {
  onSelectDestination: (destName: string, coords: { lat: number; lng: number }) => void;
  onOpenVehicleSelect?: () => void;
  activeFilter?: string;
  onFilterChange?: (filter: string) => void;
  currentDestName?: string;
}

export function SearchHeader({
  onSelectDestination,
  onOpenVehicleSelect,
  activeFilter = 'route',
  onFilterChange,
  currentDestName = 'Bengaluru → Goa',
}: SearchHeaderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [query, setQuery] = useState('');

  const suggestions = [
    {
      title: 'Panaji, Goa',
      sub: '560 km · 2 charging stops needed',
      lat: 15.4909,
      lng: 73.8278,
      icon: '📍',
    },
    {
      title: 'Calangute Beach, Goa',
      sub: '572 km · 2 charging stops needed',
      lat: 15.5439,
      lng: 73.7554,
      icon: '📍',
    },
    {
      title: 'Margao, Goa',
      sub: '545 km · 2 charging stops needed',
      lat: 15.2832,
      lng: 73.9862,
      icon: '📍',
    },
    {
      title: 'Statiq — NH48, Hassan',
      sub: 'Charging station · 187 km away',
      lat: 13.0033,
      lng: 76.1004,
      icon: '⚡',
    },
    {
      title: 'Mangalore, Karnataka',
      sub: '350 km · 1 charging stop needed',
      lat: 12.9141,
      lng: 74.856,
      icon: '📍',
    },
    {
      title: 'Mysuru, Karnataka',
      sub: '145 km · 0 charging stops needed',
      lat: 12.2958,
      lng: 76.6394,
      icon: '📍',
    },
  ];

  const recent = [
    {
      title: 'Bengaluru, Karnataka',
      sub: 'Home · last used yesterday',
      lat: 12.9716,
      lng: 77.5946,
    },
  ];

  const filteredSuggestions = query.trim()
    ? suggestions.filter((s) => s.title.toLowerCase().includes(query.toLowerCase()))
    : suggestions;

  const handleSelect = (item: { title: string; lat: number; lng: number }) => {
    onSelectDestination(item.title, { lat: item.lat, lng: item.lng });
    setIsSearchOpen(false);
  };

  return (
    <div className="absolute top-4 left-3 right-3 z-30 max-w-md mx-auto">
      {/* Search Input Bar */}
      <div
        onClick={() => setIsSearchOpen(true)}
        className="bg-white rounded-full shadow-md border border-gray-100 px-4 py-3 flex items-center gap-3 cursor-pointer hover:shadow-lg transition-all"
      >
        <div className="w-5 h-3.5 flex flex-col justify-between">
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
          <span className="block h-0.5 bg-[#5F6368] rounded-full" />
        </div>
        <div className="flex-1 text-[14.5px] text-[#16221D] truncate font-medium">
          {currentDestName || 'Search Voltana — place, charger, route'}
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

      {/* Autocomplete Search Modal / Overlay */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex flex-col justify-start p-3 sm:p-6 animate-fadeIn">
          <div className="w-full max-w-md mx-auto bg-[#FAF9F5] rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden flex flex-col max-h-[85vh]">
            {/* Header Input */}
            <div className="p-4 border-b border-[#E2DED3] bg-white">
              <div className="flex items-center gap-2.5 bg-[#FAF9F5] border-1.5 border-[#16221D] rounded-2xl px-3.5 py-2.5">
                <span className="text-sm text-gray-500">🔍</span>
                <input
                  type="text"
                  autoFocus
                  placeholder="Where to?"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1 bg-transparent border-none outline-none text-sm text-[#16221D] font-medium"
                />
                <button
                  onClick={() => setIsSearchOpen(false)}
                  className="text-xs text-[#96692A] font-semibold px-1 py-0.5 hover:underline"
                >
                  Cancel
                </button>
              </div>
            </div>

            {/* Scrollable list */}
            <div className="overflow-y-auto flex-1 p-2">
              {!query && (
                <>
                  <div className="text-[10px] tracking-wider uppercase text-[#8C8778] font-mono-custom px-4 pt-3 pb-1">
                    Recent
                  </div>
                  {recent.map((r, i) => (
                    <div
                      key={i}
                      onClick={() => handleSelect(r)}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-[#E1EAE4]/50 rounded-xl cursor-pointer transition-colors border-b border-[#F1EFE8] last:border-none"
                    >
                      <div className="w-8 h-8 rounded-full bg-[#F0EEE7] text-[#8C8778] flex items-center justify-center text-xs flex-shrink-0">
                        🕐
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-[#16221D]">{r.title}</div>
                        <div className="text-xs text-[#8C8778]">{r.sub}</div>
                      </div>
                    </div>
                  ))}
                </>
              )}

              <div className="text-[10px] tracking-wider uppercase text-[#8C8778] font-mono-custom px-4 pt-4 pb-1">
                Suggestions
              </div>
              {filteredSuggestions.map((s, i) => (
                <div
                  key={i}
                  onClick={() => handleSelect(s)}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-[#E1EAE4]/50 rounded-xl cursor-pointer transition-colors border-b border-[#F1EFE8] last:border-none"
                >
                  <div className="w-8 h-8 rounded-full bg-[#E1EAE4] text-[#2F5C50] flex items-center justify-center text-xs flex-shrink-0">
                    {s.icon}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-[#16221D]">{s.title}</div>
                    <div className="text-xs text-[#8C8778]">{s.sub}</div>
                  </div>
                  <div className="text-xs text-[#2F5C50] font-bold">›</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
