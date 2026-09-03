'use client';

import type { SavedTrip } from '@/lib/api';

interface TripHistorySheetProps {
  isOpen: boolean;
  onClose: () => void;
  trips: SavedTrip[];
  loading?: boolean;
  onPlanAgain: (trip: SavedTrip) => void;
  onDelete?: (id: string) => void;
}

function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

function formatRelative(iso: string): string {
  try {
    const then = new Date(iso).getTime();
    const now = Date.now();
    const days = Math.max(0, Math.floor((now - then) / 86400000));
    if (days === 0) return 'today';
    if (days === 1) return 'yesterday';
    return `${days} days ago`;
  } catch {
    return '';
  }
}

export function TripHistorySheet({
  isOpen,
  onClose,
  trips,
  loading = false,
  onPlanAgain,
  onDelete,
}: TripHistorySheetProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex flex-col justify-end sm:items-center sm:justify-center p-0 sm:p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-[#FAF9F5] rounded-t-3xl sm:rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-5 pt-5 pb-4 border-b border-[#E2DED3] bg-white flex items-start justify-between">
          <div>
            <div className="font-mono-custom text-[10px] tracking-[0.2em] uppercase text-[#B8863F]">
              Voltana
            </div>
            <div className="font-serif-custom text-2xl font-medium text-[#16221D]">
              Your trips
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 text-xs font-bold"
          >
            ✕
          </button>
        </div>

        {/* Trip list */}
        <div className="overflow-y-auto flex-1 p-4">
          {loading ? (
            <div className="text-center py-10 text-xs text-[#8C8778]">
              Loading trips…
            </div>
          ) : trips.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-3xl mb-3">🕘</div>
              <div className="text-sm font-semibold text-[#16221D]">
                No trips yet
              </div>
              <div className="text-xs text-[#8C8778] mt-1 max-w-[240px] mx-auto">
                Plan a route and it&apos;ll show up here so you can re-plan it
                in one tap.
              </div>
            </div>
          ) : (
            trips.map((t) => (
              <div
                key={t.id}
                className="bg-white border border-[#E2DED3] rounded-2xl p-4 mb-3"
              >
                <div className="flex items-center justify-between">
                  <div className="font-serif-custom text-[15px] font-medium text-[#16221D]">
                    {t.origin_name} → {t.dest_name}
                  </div>
                  {onDelete && (
                    <button
                      onClick={() => onDelete(t.id)}
                      title="Delete trip"
                      className="text-[#B14B3F] text-xs opacity-60 hover:opacity-100 px-1"
                    >
                      ✕
                    </button>
                  )}
                </div>
                <div className="text-[11px] text-[#8C8778] mt-0.5">
                  {formatRelative(t.created_at)} ·{' '}
                  {t.vehicle_make} {t.vehicle_model}
                  {t.vehicle_variant ? ` ${t.vehicle_variant}` : ''}
                </div>
                <div className="flex gap-4 mt-2.5 font-mono-custom text-[11.5px] text-[#3E4A44]">
                  <span>🧭 {t.total_distance_km.toFixed(0)} km</span>
                  <span>🕐 {formatDuration(t.total_estimated_duration_min)}</span>
                </div>
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={() => onPlanAgain(t)}
                    className="text-[11.5px] font-semibold text-[#96692A] flex items-center gap-1 hover:underline"
                  >
                    ↻ Plan again
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
