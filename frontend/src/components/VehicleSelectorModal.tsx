'use client';

import { useState, useEffect } from 'react';
import { listVehicles, listMakes, Vehicle } from '@/lib/api';

interface VehicleSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectVehicle: (vehicle: Vehicle) => void;
  selectedVehicle: Vehicle | null;
  batteryPct: number;
  onBatteryChange: (pct: number) => void;
}

export function VehicleSelectorModal({
  isOpen,
  onClose,
  onSelectVehicle,
  selectedVehicle,
  batteryPct,
  onBatteryChange,
}: VehicleSelectorModalProps) {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [makes, setMakes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [make, setMake] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadMakes();
      loadVehicles();
    }
  }, [isOpen, category, make, search]);

  async function loadMakes() {
    try {
      const data = await listMakes();
      setMakes(data);
    } catch (e) {
      console.error('Failed to load makes', e);
    }
  }

  async function loadVehicles() {
    setLoading(true);
    try {
      const data = await listVehicles({
        category: category || undefined,
        make: make || undefined,
        search: search || undefined,
      });
      setVehicles(data.vehicles);
    } catch (e) {
      console.error('Failed to load vehicles', e);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-[#FAF9F5] rounded-t-3xl sm:rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden flex flex-col max-h-[88vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-[#E2DED3] bg-white flex items-center justify-between">
          <div>
            <div className="font-serif-custom text-lg font-bold text-[#16221D]">
              Select Your EV
            </div>
            <div className="text-xs text-[#8C8778]">
              Choose vehicle model &amp; battery level
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 text-xs font-bold"
          >
            ✕
          </button>
        </div>

        {/* Battery Slider */}
        <div className="p-4 bg-white/60 border-b border-[#E2DED3]">
          <div className="flex justify-between items-center mb-1.5 text-xs">
            <span className="font-semibold text-[#16221D]">Starting Battery State (SoC)</span>
            <span className="font-mono-custom font-bold text-[#B8863F] text-sm">{batteryPct}%</span>
          </div>
          <input
            type="range"
            min="20"
            max="100"
            step="5"
            value={batteryPct}
            onChange={(e) => onBatteryChange(Number(e.target.value))}
            className="w-full accent-[#2F5C50] cursor-pointer"
          />
        </div>

        {/* Category & Filters */}
        <div className="p-3 bg-[#FAF9F5] flex gap-2 overflow-x-auto no-scrollbar border-b border-[#E2DED3]">
          <button
            onClick={() => setCategory('')}
            className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              category === ''
                ? 'bg-[#2F5C50] text-white shadow-xs'
                : 'bg-white border border-[#E2DED3] text-[#16221D]'
            }`}
          >
            All Types
          </button>
          <button
            onClick={() => setCategory('four_wheeler')}
            className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              category === 'four_wheeler'
                ? 'bg-[#2F5C50] text-white shadow-xs'
                : 'bg-white border border-[#E2DED3] text-[#16221D]'
            }`}
          >
            🚗 Cars (4W)
          </button>
          <button
            onClick={() => setCategory('two_wheeler')}
            className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              category === 'two_wheeler'
                ? 'bg-[#2F5C50] text-white shadow-xs'
                : 'bg-white border border-[#E2DED3] text-[#16221D]'
            }`}
          >
            🛵 2W Scooters
          </button>
        </div>

        {/* Search */}
        <div className="px-4 py-2 bg-[#FAF9F5]">
          <input
            type="text"
            placeholder="Search model (Nexon, ZS EV, Ola, Ather)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-[#E2DED3] rounded-xl px-3 py-2 text-xs text-[#16221D] outline-none"
          />
        </div>

        {/* Vehicle list */}
        <div className="p-3 overflow-y-auto flex-1 no-scrollbar space-y-2">
          {loading ? (
            <div className="text-center py-8 text-xs text-[#8C8778]">Loading vehicles...</div>
          ) : vehicles.length === 0 ? (
            <div className="text-center py-8 text-xs text-[#8C8778]">No vehicles found</div>
          ) : (
            vehicles.map((v) => {
              const isSelected = selectedVehicle?.id === v.id;
              return (
                <div
                  key={v.id}
                  onClick={() => {
                    onSelectVehicle(v);
                    onClose();
                  }}
                  className={`p-3 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#E1EAE4] border-[#2F5C50] shadow-sm'
                      : 'bg-white border-[#E2DED3] hover:border-gray-400'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-sm font-bold text-[#16221D]">
                        {v.make} {v.model} {v.variant}
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-[11px] text-[#8C8778] flex-wrap">
                        <span className="font-mono-custom text-[#2F5C50] font-semibold">
                          {v.real_world_range_km} km real range
                        </span>
                        <span>•</span>
                        <span>{v.battery_capacity_kwh} kWh</span>
                        {v.max_dc_charge_kw && (
                          <>
                            <span>•</span>
                            <span>{v.max_dc_charge_kw} kW DC</span>
                          </>
                        )}
                        {v.price_ex_showroom_inr && (
                          <>
                            <span>•</span>
                            <span>₹{(v.price_ex_showroom_inr / 1e5).toFixed(1)}L</span>
                          </>
                        )}
                      </div>
                    </div>
                    {isSelected && (
                      <span className="w-5 h-5 rounded-full bg-[#2F5C50] text-white flex items-center justify-center text-xs font-bold">
                        ✓
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
