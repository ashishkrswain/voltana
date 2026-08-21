'use client';

import { useEffect, useRef } from 'react';
import type { TripPlanResponse, TripStop } from '@/lib/api';

interface MapViewProps {
  itinerary: TripPlanResponse | null;
  originCoords: { lat: number; lng: number } | null;
  destCoords: { lat: number; lng: number } | null;
  originName?: string;
  destName?: string;
  allChargers?: Array<{
    id: string;
    name: string;
    latitude: number;
    longitude: number;
    power_kw: number;
    connector_types: string;
    network?: { name: string; slug: string } | null;
    address?: string | null;
  }>;
  activeFilter?: string;
  onSelectCharger?: (stop: TripStop) => void;
}

const NETWORK_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  'bolt-earth': { bg: '#00D26A', text: '#0A341A', label: 'Bolt.Earth' },
  'statiq': { bg: '#0052FF', text: '#FFFFFF', label: 'Statiq' },
  'tata-power-ez': { bg: '#00A3E0', text: '#FFFFFF', label: 'Tata Power' },
  'chargezone': { bg: '#FF6B00', text: '#FFFFFF', label: 'ChargeZone' },
  'jio-bp-pulse': { bg: '#00A859', text: '#FFFFFF', label: 'Jio-BP' },
  'ather-grid': { bg: '#E64B17', text: '#FFFFFF', label: 'Ather' },
};

export function MapView({
  itinerary,
  originCoords,
  destCoords,
  originName = 'Start',
  destName = 'Destination',
  allChargers = [],
  activeFilter = 'route',
  onSelectCharger,
}: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const userMarkerRef = useRef<any>(null);
  const layerGroupRef = useRef<any>(null);

  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      if (!mapContainerRef.current) return;

      const L = (await import('leaflet')).default;

      if (!isMounted) return;

      if (!mapInstanceRef.current && mapContainerRef.current) {
        const map = L.map(mapContainerRef.current, {
          zoomControl: false,
          attributionControl: false,
        }).setView([13.6, 75.9], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18,
        }).addTo(map);

        layerGroupRef.current = L.layerGroup().addTo(map);
        mapInstanceRef.current = map;
      }

      const map = mapInstanceRef.current;
      const layerGroup = layerGroupRef.current;
      if (!map || !layerGroup) return;

      layerGroup.clearLayers();

      const pinIcon = (bg: string, glyph: string, shape: 'circle' | 'diamond' | 'badge' = 'circle', label?: string) => {
        if (shape === 'badge') {
          return L.divIcon({
            html: `<div style="display:flex; align-items:center; background:#FAF9F5; border:2px solid ${bg}; border-radius:20px; padding:2px 8px 2px 4px; box-shadow:0 3px 10px rgba(0,0,0,0.25); gap:4px; font-family:'IBM Plex Sans',sans-serif; cursor:pointer;">
              <div style="width:20px; height:20px; border-radius:50%; background:${bg}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:bold;">⚡</div>
              <span style="font-size:11px; font-weight:700; color:#16221D; white-space:nowrap;">${label || ''}</span>
            </div>`,
            className: 'custom-div-icon',
            iconSize: [80, 26],
            iconAnchor: [40, 13],
          });
        }

        const base =
          shape === 'diamond'
            ? 'width:18px;height:18px;transform:rotate(45deg);border-radius:4px;'
            : 'width:24px;height:24px;border-radius:50%;';
        return L.divIcon({
          html: `<div style="${base} background:${bg}; border:2.5px solid #fff; box-shadow:0 2px 8px rgba(0,0,0,0.35); display:flex; align-items:center; justify-content:center; font-size:11px; color:#fff; font-weight:bold;">${
            shape === 'diamond' ? '' : glyph
          }</div>`,
          className: 'custom-div-icon',
          iconSize: [24, 24],
          iconAnchor: [12, 12],
        });
      };

      // Polyline coordinates
      const polylineCoords: [number, number][] =
        itinerary?.polyline_coords && itinerary.polyline_coords.length > 0
          ? itinerary.polyline_coords
          : [
              [12.9716, 77.5946],
              [13.1004, 76.9791],
              [13.0072, 76.1004],
              [13.1642, 75.7674],
              [13.42, 75.25],
              [14.25, 74.7],
              [15.2993, 74.124],
            ];

      // Route Outer Glow / Shadow
      L.polyline(polylineCoords, {
        color: '#16221D',
        weight: 7,
        opacity: 0.35,
        lineCap: 'round',
      }).addTo(layerGroup);

      // Route Main Line (Deep Pine Green with vibrant contrast)
      const routeLine = L.polyline(polylineCoords, {
        color: '#2F5C50',
        weight: 4.5,
        opacity: 0.95,
        lineCap: 'round',
      }).addTo(layerGroup);

      // Start Marker
      const startCoord = originCoords ? [originCoords.lat, originCoords.lng] : polylineCoords[0];
      L.marker(startCoord as [number, number], {
        icon: pinIcon('#2F5C50', '●'),
      })
        .addTo(layerGroup)
        .bindPopup(`<b>${originName}</b><br/>Departure Point`);

      // End Marker
      const endCoord = destCoords
        ? [destCoords.lat, destCoords.lng]
        : polylineCoords[polylineCoords.length - 1];
      L.marker(endCoord as [number, number], {
        icon: pinIcon('#16221D', '', 'diamond'),
      })
        .addTo(layerGroup)
        .bindPopup(`<b>${destName}</b><br/>Destination`);

      // Collect IDs of designated itinerary stops
      const plannedStopChargerIds = new Set<string>();
      if (itinerary) {
        itinerary.legs.forEach((leg, idx) => {
          if (leg.stop) {
            plannedStopChargerIds.add(leg.stop.charger_id);
            const stop = leg.stop;
            const lat = stop.latitude || 13.0072;
            const lng = stop.longitude || 76.1004;

            const marker = L.marker([lat, lng], {
              icon: pinIcon('#B8863F', `${idx + 1}`, 'badge', `${stop.charger_name.split('-')[0].trim()} · ${Math.round(stop.estimated_charge_time_min)}m`),
            }).addTo(layerGroup);

            marker.bindPopup(
              `<div style="font-family:'IBM Plex Sans',sans-serif; min-width:160px;">
                <b style="color:#16221D; font-size:13px;">${stop.charger_name}</b><br/>
                <span style="color:#96692A; font-weight:600; font-size:11px;">Stop #${idx + 1} · km ${stop.km_marker.toFixed(0)}</span><br/>
                <span style="color:#2F5C50; font-size:11px;">Charge: ${stop.arrival_battery_pct.toFixed(0)}% → ${stop.charge_to_pct.toFixed(0)}% (${stop.estimated_charge_time_min.toFixed(0)} min)</span><br/>
                <span style="color:#8C8778; font-size:10px;">${stop.power_kw} kW DC · ${stop.connector_types || 'CCS2'}</span>
              </div>`
            );

            marker.on('click', () => {
              if (onSelectCharger) {
                onSelectCharger(stop);
              }
            });
          }
        });
      }

      // Display other Corridor & Nearby Chargers (Bolt.Earth, Statiq, Tata Power, etc.)
      const shouldShowAll = activeFilter === 'chargers' || activeFilter === 'dc_fast' || activeFilter === 'nh48';

      allChargers.forEach((charger) => {
        // Don't duplicate planned stop
        if (plannedStopChargerIds.has(charger.id)) return;

        // Filter based on DC fast only
        if (activeFilter === 'dc_fast' && charger.power_kw < 30) return;

        const slug = charger.network?.slug || 'bolt-earth';
        const netInfo = NETWORK_COLORS[slug] || { bg: '#00D26A', text: '#fff', label: charger.network?.name || 'Bolt.Earth' };

        const marker = L.marker([charger.latitude, charger.longitude], {
          icon: pinIcon(netInfo.bg, '⚡', 'circle'),
          opacity: shouldShowAll ? 0.95 : 0.65,
        }).addTo(layerGroup);

        marker.bindPopup(
          `<div style="font-family:'IBM Plex Sans',sans-serif; min-width:150px;">
            <b style="color:#16221D;">${charger.name}</b><br/>
            <span style="color:${netInfo.bg}; font-weight:700; font-size:11px;">${netInfo.label} · ${charger.power_kw} kW</span><br/>
            <span style="color:#8C8778; font-size:10px;">${charger.address || ''}</span>
          </div>`
        );

        marker.on('click', () => {
          if (onSelectCharger) {
            onSelectCharger({
              charger_id: charger.id,
              charger_name: charger.name,
              charger_address: charger.address,
              network_name: charger.network?.name,
              network_slug: charger.network?.slug,
              power_kw: charger.power_kw,
              latitude: charger.latitude,
              longitude: charger.longitude,
              connector_types: charger.connector_types,
              km_marker: 0,
              arrival_battery_pct: 35,
              charge_to_pct: 80,
              estimated_charge_time_min: Math.round((45 / (charger.power_kw || 50)) * 30),
            });
          }
        });
      });

      // Fit bounds
      try {
        map.fitBounds(routeLine.getBounds(), { padding: [60, 40] });
      } catch (e) {
        console.error('Fit bounds error:', e);
      }
    }

    initMap();

    return () => {
      isMounted = false;
    };
  }, [itinerary, originCoords, destCoords, originName, destName, allChargers, activeFilter, onSelectCharger]);

  const handleLocateUser = async () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    const L = (await import('leaflet')).default;
    const map = mapInstanceRef.current;
    if (!map) return;

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        if (userMarkerRef.current) {
          map.removeLayer(userMarkerRef.current);
        }
        userMarkerRef.current = L.circleMarker([latitude, longitude], {
          radius: 8,
          color: '#fff',
          weight: 3,
          fillColor: '#1A73E8',
          fillOpacity: 1,
        })
          .addTo(map)
          .bindPopup('You are here')
          .openPopup();
        map.setView([latitude, longitude], 12);
      },
      () => {
        alert('Location permission was denied or unavailable.');
      }
    );
  };

  const handleZoomIn = () => {
    mapInstanceRef.current?.zoomIn();
  };

  const handleZoomOut = () => {
    mapInstanceRef.current?.zoomOut();
  };

  const handleRecenter = () => {
    if (layerGroupRef.current && mapInstanceRef.current) {
      const layers = layerGroupRef.current.getLayers();
      const polyline = layers.find((l: any) => l instanceof (window as any).L?.Polyline || l.getBounds);
      if (polyline && polyline.getBounds) {
        mapInstanceRef.current.fitBounds(polyline.getBounds(), { padding: [60, 40] });
      } else {
        mapInstanceRef.current.setView([13.6, 75.9], 7);
      }
    }
  };

  return (
    <div className="absolute inset-0 z-0">
      {/* Leaflet container */}
      <div ref={mapContainerRef} className="w-full h-full filter saturate-80 contrast-105" />

      {/* Floating Action Buttons (FABs) */}
      <div className="absolute right-4 bottom-72 md:bottom-28 z-20 flex flex-col gap-2.5">
        <button
          onClick={handleLocateUser}
          className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-blue-600 hover:bg-gray-50 active:scale-95 transition-all text-base border border-gray-100"
          title="Current location"
        >
          📍
        </button>
        <button
          onClick={handleRecenter}
          className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-gray-700 hover:bg-gray-50 active:scale-95 transition-all text-base border border-gray-100"
          title="Re-center route"
        >
          🧭
        </button>
        <button
          onClick={handleZoomIn}
          className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-gray-700 hover:bg-gray-50 active:scale-95 transition-all text-base border border-gray-100 font-bold"
          title="Zoom In"
        >
          ＋
        </button>
        <button
          onClick={handleZoomOut}
          className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-gray-700 hover:bg-gray-50 active:scale-95 transition-all text-base border border-gray-100 font-bold"
          title="Zoom Out"
        >
          －
        </button>
      </div>
    </div>
  );
}
