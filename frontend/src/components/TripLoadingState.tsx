'use client';

interface TripLoadingStateProps {
  vehicleName?: string;
  routeName?: string;
}

const STEPS = [
  { label: 'Fetched road route', done: true },
  { label: 'Found compatible chargers', done: true },
  { label: 'Optimising stop order', done: false },
];

export function TripLoadingState({
  vehicleName = 'your EV',
  routeName = 'your route',
}: TripLoadingStateProps) {
  return (
    <div className="absolute inset-0 z-20 bg-[#FAF9F5]/95 backdrop-blur-xs flex flex-col items-center justify-center px-10 pt-20 animate-fadeIn">
      {/* Thread dots */}
      <div className="flex flex-col items-center gap-2.5 mb-8">
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-[#2F5C50]" />
          <span className="w-[34px] h-0.5 bg-[repeating-linear-gradient(to_right,#E2DED3_0,#E2DED3_4px,transparent_4px,transparent_8px)]" />
          <span className="w-3 h-3 rounded-full bg-[#B8863F] animate-pulse" />
          <span className="w-[34px] h-0.5 bg-[repeating-linear-gradient(to_right,#E2DED3_0,#E2DED3_4px,transparent_4px,transparent_8px)]" />
          <span className="w-3 h-3 rounded-full bg-[#E2DED3]" />
        </div>
      </div>

      <div className="font-serif-custom text-lg text-[#16221D] text-center">
        Charting your route
      </div>
      <div className="text-xs text-[#8C8778] text-center max-w-[240px] leading-relaxed mt-2">
        Matching charger power output to your {vehicleName}&apos;s charge curve
        along {routeName}.
      </div>

      <div className="mt-7 flex flex-col gap-2.5 w-full max-w-[260px]">
        {STEPS.map((step) => (
          <div
            key={step.label}
            className={`flex items-center gap-2.5 text-xs font-mono-custom ${
              step.done ? 'text-[#3E4A44]' : 'text-[#8C8778]'
            }`}
          >
            <span
              className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] flex-shrink-0 ${
                step.done
                  ? 'bg-[#E1EAE4] text-[#2F5C50]'
                  : 'bg-[#E2DED3] text-transparent'
              }`}
            >
              ✓
            </span>
            {step.label}
          </div>
        ))}
      </div>
    </div>
  );
}
