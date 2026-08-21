'use client';

import type { Vehicle } from '@/lib/api';

interface VehiclePillProps {
  vehicle: Vehicle | null;
  batteryPct?: number;
  onClick?: () => void;
}

export function VehiclePill({
  vehicle,
  batteryPct = 78,
  onClick,
}: VehiclePillProps) {
  const vehicleName = vehicle
    ? `${vehicle.model} · ${vehicle.variant || ''}`.trim()
    : 'Nexon EV · LR';

  return (
    <div
      onClick={onClick}
      className="absolute top-24 left-3 z-20 bg-[#16221D] text-white rounded-full py-1.5 px-3 pl-2.5 flex items-center gap-2 shadow-lg hover:bg-black/90 active:scale-95 transition-all cursor-pointer border border-white/10"
      title="Click to change vehicle or battery SoC"
    >
      <span className="text-xs">🔋</span>
      <span className="text-xs font-medium tracking-tight truncate max-w-[140px]">
        {vehicleName}
      </span>
      <span className="font-mono-custom text-xs font-bold text-[#B8863F]">
        {batteryPct}%
      </span>
    </div>
  );
}
