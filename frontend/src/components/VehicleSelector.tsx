'use client';

import { useState, useEffect } from 'react';
import { listVehicles, listMakes, Vehicle } from '@/lib/api';

interface VehicleSelectorProps {
  onSelect: (vehicle: Vehicle) => void;
  selectedVehicle: Vehicle | null;
}

export function VehicleSelector({ onSelect, selectedVehicle }: VehicleSelectorProps) {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [makes, setMakes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    make: '',
    search: '',
    page: 1,
  });
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    loadMakes();
  }, []);

  useEffect(() => {
    loadVehicles();
  }, [filters]);

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
        page: filters.page,
        page_size: pageSize,
        category: filters.category || undefined,
        make: filters.make || undefined,
        search: filters.search || undefined,
      });
      setVehicles(data.vehicles);
      setTotal(data.total);
    } catch (e) {
      console.error('Failed to load vehicles', e);
    } finally {
      setLoading(false);
    }
  }

  function handleFilterChange(key: string, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  }

  function formatCategory(cat: string) {
    return cat.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Select Your Vehicle</h2>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <select
          value={filters.category}
          onChange={(e) => handleFilterChange('category', e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">All Categories</option>
          <option value="two_wheeler">Two Wheeler</option>
          <option value="three_wheeler">Three Wheeler</option>
          <option value="four_wheeler">Four Wheeler</option>
        </select>

        <select
          value={filters.make}
          onChange={(e) => handleFilterChange('make', e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">All Makes</option>
          {makes.map((make) => (
            <option key={make} value={make}>
              {make}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Search model..."
          value={filters.search}
          onChange={(e) => handleFilterChange('search', e.target.value)}
          className="border rounded px-3 py-2"
        />
      </div>

      {/* Vehicle List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading vehicles...</div>
      ) : vehicles.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No vehicles found</div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {vehicles.map((vehicle) => (
            <button
              key={vehicle.id}
              onClick={() => onSelect(vehicle)}
              className={`w-full text-left p-4 rounded-lg border transition-colors ${
                selectedVehicle?.id === vehicle.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">
                    {vehicle.make} {vehicle.model} {vehicle.variant}
                  </div>
                  <div className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                      {formatCategory(vehicle.category)}
                    </span>
                    <span>•</span>
                    <span>{vehicle.real_world_range_km} km real range</span>
                    <span>•</span>
                    <span>{vehicle.battery_capacity_kwh} kWh</span>
                    {vehicle.max_dc_charge_kw && (
                      <>
                        <span>•</span>
                        <span>DC {vehicle.max_dc_charge_kw} kW</span>
                      </>
                    )}
                    <span>•</span>
                    <span>
                      {vehicle.ac_charge_port_type || 'AC'} /{' '}
                      {vehicle.dc_charge_port_type || 'portable'}
                    </span>
                  </div>
                </div>
                {selectedVehicle?.id === vehicle.id && (
                  <svg
                    className="w-5 h-5 text-blue-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => setFilters((p) => ({ ...p, page: p.page - 1 }))}
            disabled={filters.page === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="flex items-center px-3 text-sm text-gray-600">
            Page {filters.page} of {Math.ceil(total / pageSize)}
          </span>
          <button
            onClick={() => setFilters((p) => ({ ...p, page: p.page + 1 }))}
            disabled={filters.page >= Math.ceil(total / pageSize)}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}