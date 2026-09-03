'use client';

interface TripErrorStateProps {
  message?: string;
  /** Structured "no charger found" gap data from the planner (optional). */
  gap?: {
    gap_start_km: number;
    gap_end_km: number;
    remaining_range_km: number;
    current_battery_pct: number;
    current_km: number;
  } | null;
  onRetry?: () => void;
  onSwitchVehicle?: () => void;
  onShowACOptions?: () => void;
}

export function TripErrorState({
  message = 'Could not plan this trip',
  gap = null,
  onRetry,
  onSwitchVehicle,
  onShowACOptions,
}: TripErrorStateProps) {
  const hasGap = gap !== null;

  return (
    <div className="absolute inset-0 z-20 bg-[#FAF9F5]/95 backdrop-blur-xs flex flex-col items-center justify-center px-9 pt-20 text-center animate-fadeIn">
      <div className="w-14 h-14 rounded-full bg-[#F7E7E3] text-[#B14B3F] flex items-center justify-center text-[22px] mb-5">
        ⚠
      </div>

      <div className="font-serif-custom text-lg font-medium text-[#16221D]">
        {hasGap ? 'No charger found on this stretch' : 'Could not plan this trip'}
      </div>

      {hasGap ? (
        <>
          <div className="text-xs text-[#3E4A44] leading-relaxed max-w-[270px] mt-2">
            Between km {Math.round(gap.gap_start_km)} and{' '}
            {Math.round(gap.gap_end_km)}, there&apos;s no charger compatible with
            your vehicle&apos;s connector.
          </div>

          <div className="mt-5 bg-white border border-[#E2DED3] rounded-xl px-3.5 py-3 text-left w-full max-w-[280px] text-[11.5px] text-[#3E4A44] leading-relaxed">
            Gap: <b className="text-[#B14B3F] font-mono-custom">
              {Math.round(gap.gap_end_km - gap.gap_start_km)} km
            </b>{' '}
            without a compatible stop
            <br />
            Your range at this point:{' '}
            <b className="text-[#B14B3F] font-mono-custom">
              ~{Math.max(0, Math.round(gap.remaining_range_km - gap.current_km))}{' '}
              km
            </b>{' '}
            remaining
          </div>

          <div className="mt-5 flex flex-col gap-2 w-full max-w-[280px]">
            {onShowACOptions && (
              <button
                onClick={onShowACOptions}
                className="w-full py-3 rounded-full text-sm font-medium bg-[#16221D] text-white active:scale-95 transition-all"
              >
                Show AC charging options nearby
              </button>
            )}
            {onSwitchVehicle && (
              <button
                onClick={onSwitchVehicle}
                className="w-full py-3 rounded-full text-sm font-medium bg-transparent text-[#3E4A44] border border-[#E2DED3] active:scale-95 transition-all"
              >
                Try a different vehicle
              </button>
            )}
            {onRetry && !onShowACOptions && (
              <button
                onClick={onRetry}
                className="w-full py-3 rounded-full text-sm font-medium bg-[#16221D] text-white active:scale-95 transition-all"
              >
                Try again
              </button>
            )}
          </div>
        </>
      ) : (
        <>
          <div className="text-xs text-[#3E4A44] leading-relaxed max-w-[270px] mt-2">
            {message}
          </div>

          <div className="mt-5 bg-white border border-[#E2DED3] rounded-xl px-3.5 py-3 text-left w-full max-w-[280px] text-[11px] text-[#3E4A44] leading-relaxed">
            We couldn&apos;t find a compatible charging stop along this route.
            Try a different route, or pick a vehicle with a longer range.
          </div>

          <div className="mt-5 flex flex-col gap-2 w-full max-w-[280px]">
            {onRetry && (
              <button
                onClick={onRetry}
                className="w-full py-3 rounded-full text-sm font-medium bg-[#16221D] text-white active:scale-95 transition-all"
              >
                Try again
              </button>
            )}
            {onSwitchVehicle && (
              <button
                onClick={onSwitchVehicle}
                className="w-full py-3 rounded-full text-sm font-medium bg-transparent text-[#3E4A44] border border-[#E2DED3] active:scale-95 transition-all"
              >
                Try a different vehicle
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
