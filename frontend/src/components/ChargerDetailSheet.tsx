'use client';

import type { TripStop } from '@/lib/api';

interface ChargerDetailSheetProps {
  stop: TripStop | null;
  onClose: () => void;
  onConfirmStop?: (stop: TripStop) => void;
}

export function ChargerDetailSheet({
  stop,
  onClose,
  onConfirmStop,
}: ChargerDetailSheetProps) {
  if (!stop) return null;

  const networkName = stop.network_name || 'Statiq';
  const address =
    stop.charger_address ||
    'NH48, near Hassan Bypass, Karnataka 573201';
  const powerKw = stop.power_kw || 60;
  const chargeTimeMin = Math.round(stop.estimated_charge_time_min || 32);
  const fromPct = Math.round(stop.arrival_battery_pct || 24);
  const toPct = Math.round(stop.charge_to_pct || 80);
  const kmMarker = Math.round(stop.km_marker || 187);

  const getNetworkAppUrl = () => {
    const slug = stop.network_slug?.toLowerCase() || '';
    if (slug.includes('bolt')) return 'https://bolt.earth';
    if (slug.includes('tata')) return 'https://evcharging.tatapower.com';
    if (slug.includes('chargezone')) return 'https://chargezone.in';
    if (slug.includes('ather')) return 'https://atherenergy.com/grid';
    if (slug.includes('jio')) return 'https://www.jiobp.com';
    return 'https://statiq.in';
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-[#FAF9F5] rounded-t-3xl sm:rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden flex flex-col max-h-[90vh]">
        {/* Mini Map Strip */}
        <div className="h-36 bg-gradient-to-br from-[#dfe6de] to-[#eef1ea] relative flex items-center justify-center border-b border-[#E2DED3]">
          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_40%_40%,rgba(184,134,63,0.3),transparent_60%)]" />
          <button
            onClick={onClose}
            className="absolute top-3 right-3 w-7 h-7 rounded-full bg-white/80 backdrop-blur-xs text-gray-700 font-bold flex items-center justify-center hover:bg-white shadow-sm transition-all"
          >
            ✕
          </button>
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-[#B8863F] border-3 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold animate-bounce">
              ⚡
            </div>
          </div>
        </div>

        {/* Card Body */}
        <div className="p-5 overflow-y-auto flex-1 no-scrollbar">
          <span className="inline-block font-mono-custom text-[10px] uppercase tracking-wider bg-[#EFE2C9] text-[#96692A] px-2.5 py-1 rounded-full font-bold mb-2">
            km {kmMarker} on your route
          </span>

          <div className="font-serif-custom font-semibold text-xl text-[#16221D] mb-1">
            {stop.charger_name}
          </div>
          <div className="text-xs text-[#8C8778] mb-4">{address}</div>

          {/* 2x2 Stat Grid */}
          <div className="grid grid-cols-2 gap-2.5 mb-4">
            <div className="bg-white border border-[#E2DED3] rounded-xl p-2.5">
              <div className="text-[10px] text-[#8C8778] uppercase tracking-wider font-mono-custom">
                Power output
              </div>
              <div className="font-mono-custom text-sm font-bold text-[#16221D] mt-0.5">
                {powerKw} kW DC
              </div>
            </div>
            <div className="bg-white border border-[#E2DED3] rounded-xl p-2.5">
              <div className="text-[10px] text-[#8C8778] uppercase tracking-wider font-mono-custom">
                Est. charge time
              </div>
              <div className="font-mono-custom text-sm font-bold text-[#16221D] mt-0.5">
                {chargeTimeMin} min
              </div>
            </div>
            <div className="bg-white border border-[#E2DED3] rounded-xl p-2.5">
              <div className="text-[10px] text-[#8C8778] uppercase tracking-wider font-mono-custom">
                Charge target
              </div>
              <div className="font-mono-custom text-sm font-bold text-[#2F5C50] mt-0.5">
                {fromPct}% → {toPct}%
              </div>
            </div>
            <div className="bg-white border border-[#E2DED3] rounded-xl p-2.5">
              <div className="text-[10px] text-[#8C8778] uppercase tracking-wider font-mono-custom">
                Network
              </div>
              <div className="font-mono-custom text-sm font-bold text-[#16221D] mt-0.5 truncate">
                {networkName}
              </div>
            </div>
          </div>

          {/* Connectors */}
          <div className="flex gap-2 mb-4 flex-wrap">
            <span className="text-xs bg-[#E1EAE4] text-[#2F5C50] px-3 py-1 rounded-full font-mono-custom font-semibold">
              CCS2
            </span>
            <span className="text-xs bg-[#E1EAE4] text-[#2F5C50] px-3 py-1 rounded-full font-mono-custom font-semibold">
              Compatible ✓
            </span>
          </div>

          {/* Disclaimer status box */}
          <div className="flex items-start gap-2.5 bg-[#FBF3E4] border border-[#E9D4A8] rounded-xl p-3 mb-4">
            <span className="text-[#96692A] text-sm mt-0.5">ⓘ</span>
            <span className="text-xs text-[#7A5A26] leading-relaxed">
              Live availability isn&apos;t tracked yet. Confirm this charger is working in the {networkName} app before you arrive.
            </span>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2.5 pt-1">
            <a
              href={getNetworkAppUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-3 px-4 rounded-full text-center text-xs font-semibold bg-white border border-[#E2DED3] text-[#16221D] hover:bg-gray-50 active:scale-95 transition-all"
            >
              Open in {networkName} app
            </a>
            <button
              onClick={() => {
                if (onConfirmStop) onConfirmStop(stop);
                onClose();
              }}
              className="flex-1 py-3 px-4 rounded-full text-center text-xs font-semibold bg-[#B8863F] text-white hover:bg-[#96692A] active:scale-95 transition-all shadow-sm"
            >
              Set as my stop
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
