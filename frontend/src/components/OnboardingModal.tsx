'use client';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPickVehicle: () => void;
  hasVehicle?: boolean;
  vehicleName?: string;
}

export function OnboardingModal({
  isOpen,
  onClose,
  onPickVehicle,
  hasVehicle = false,
  vehicleName = '',
}: OnboardingModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 animate-fadeIn">
      <div className="w-full max-w-md bg-[#FAF9F5] rounded-3xl shadow-2xl border border-[#E2DED3] overflow-hidden">
        {/* Hero */}
        <div className="flex flex-col items-center justify-center px-8 pt-10 pb-6 text-center">
          <div className="w-16 h-16 rounded-[18px] bg-[#16221D] flex items-center justify-center mb-7">
            <span className="font-serif-custom text-[#B8863F] text-[28px] font-semibold">
              V
            </span>
          </div>
          <div className="font-serif-custom text-[26px] font-medium text-[#16221D]">
            Add your vehicle
          </div>
          <div className="text-[13.5px] text-[#3E4A44] leading-relaxed max-w-[270px] mt-2.5">
            Voltana plans every stop around your exact battery and range — not
            a generic estimate. Takes ten seconds.
          </div>
          <div className="flex gap-1.5 mt-6">
            <span className="w-1.5 h-1.5 rounded-full bg-[#E2DED3]" />
            <span className="w-[18px] h-1.5 rounded-[4px] bg-[#B8863F]" />
            <span className="w-1.5 h-1.5 rounded-full bg-[#E2DED3]" />
          </div>
        </div>

        {/* Footer */}
        <div className="px-7 pb-8">
          <button
            onClick={onPickVehicle}
            className="w-full bg-[#B8863F] text-white py-3.5 rounded-full text-sm font-medium hover:bg-[#96692A] active:scale-[0.99] transition-all"
          >
            {hasVehicle
              ? `Select vehicle (currently ${vehicleName})`
              : 'Select my vehicle'}
          </button>
          <div
            onClick={onClose}
            className="text-center text-xs text-[#8C8778] mt-3 cursor-pointer hover:underline"
          >
            I&apos;ll add it later
          </div>
        </div>
      </div>
    </div>
  );
}
