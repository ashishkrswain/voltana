'use client';

interface SettingsSheetProps {
  isOpen: boolean;
  onClose: () => void;
  avgSpeed: number;
  safetyBuffer: number;
  onChange: (next: { avgSpeed: number; safetyBuffer: number }) => void;
}

export function SettingsSheet({
  isOpen,
  onClose,
  avgSpeed,
  safetyBuffer,
  onChange,
}: SettingsSheetProps) {
  if (!isOpen) return null;

  const setSpeed = (val: number) => {
    const clamped = Math.min(120, Math.max(20, val));
    onChange({ avgSpeed: clamped, safetyBuffer });
  };

  const setBuffer = (val: number) => {
    const clamped = Math.min(50, Math.max(5, val));
    onChange({ avgSpeed, safetyBuffer: clamped });
  };

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
              Settings
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 text-xs font-bold"
          >
            ✕
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-5">
          {/* Trip defaults */}
          <div className="text-[10px] tracking-[0.14em] uppercase text-[#8C8778] font-mono-custom mb-3">
            Trip defaults
          </div>

          <div className="bg-white border border-[#E2DED3] rounded-2xl px-4 py-3 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-[#E1EAE4] text-[#2F5C50] flex items-center justify-center text-[13px]">
                  ⚙
                </span>
                <div>
                  <div className="text-[13px] text-[#16221D]">
                    Default cruising speed
                  </div>
                  <div className="text-[11px] text-[#8C8778] mt-0.5">
                    Used for drive-time & range estimates
                  </div>
                </div>
              </div>
              <span className="font-mono-custom text-xs text-[#8C8778]">
                {avgSpeed} km/h
              </span>
            </div>
            <input
              type="range"
              min={20}
              max={120}
              step={5}
              value={avgSpeed}
              onChange={(e) => setSpeed(Number(e.target.value))}
              className="w-full accent-[#2F5C50] mt-3 cursor-pointer"
            />
          </div>

          <div className="bg-white border border-[#E2DED3] rounded-2xl px-4 py-3 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-[#E1EAE4] text-[#2F5C50] flex items-center justify-center text-[13px]">
                  🛡
                </span>
                <div>
                  <div className="text-[13px] text-[#16221D]">
                    Safety battery buffer
                  </div>
                  <div className="text-[11px] text-[#8C8778] mt-0.5">
                    Reserve % kept after each leg
                  </div>
                </div>
              </div>
              <span className="font-mono-custom text-xs text-[#8C8778]">
                {safetyBuffer}%
              </span>
            </div>
            <input
              type="range"
              min={5}
              max={50}
              step={1}
              value={safetyBuffer}
              onChange={(e) => setBuffer(Number(e.target.value))}
              className="w-full accent-[#2F5C50] mt-3 cursor-pointer"
            />
          </div>

          <div className="text-[10px] leading-relaxed text-[#8C8778] px-1">
            Changes re-plan the current route immediately with the new
            assumptions.
          </div>
        </div>
      </div>
    </div>
  );
}
