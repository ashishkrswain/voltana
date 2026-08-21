import os
import httpx
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class RouteResult:
    distance_km: float
    duration_min: float
    polyline: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    polyline_coords: list[tuple[float, float]] = None


class ORSRouter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ORS_API_KEY")
        self.base_url = "https://api.openrouteservice.org/v2"
        self.osrm_url = "https://router.project-osrm.org/route/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        profile: str = "driving-car"
    ) -> RouteResult:
        """Get route from origin to destination using ORS or public OSRM."""
        if self.api_key:
            try:
                url = f"{self.base_url}/directions/{profile}/geojson"
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                }
                body = {
                    "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
                    "format": "geojson",
                }
                response = await self.client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()

                feature = data["features"][0]
                geometry = feature["geometry"]
                summary = feature["properties"]["summary"]
                coords = [(c[1], c[0]) for c in geometry["coordinates"]]
                polyline = self._encode_polyline(coords)

                return RouteResult(
                    distance_km=summary["distance"] / 1000.0,
                    duration_min=summary["duration"] / 60.0,
                    polyline=polyline,
                    start_lat=origin_lat,
                    start_lng=origin_lng,
                    end_lat=dest_lat,
                    end_lng=dest_lng,
                    polyline_coords=coords,
                )
            except Exception as e:
                print(f"ORS routing failed, falling back to OSRM: {e}")

        # OSRM Public Routing Fallback (Keyless, covers all Indian roads)
        url = f"{self.osrm_url}/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError("No route found by OSRM")

        route_data = data["routes"][0]
        # OSRM returns coordinates as [lng, lat]
        coords = [(c[1], c[0]) for c in route_data["geometry"]["coordinates"]]
        polyline = self._encode_polyline(coords)

        return RouteResult(
            distance_km=route_data["distance"] / 1000.0,
            duration_min=route_data["duration"] / 60.0,
            polyline=polyline,
            start_lat=origin_lat,
            start_lng=origin_lng,
            end_lat=dest_lat,
            end_lng=dest_lng,
            polyline_coords=coords,
        )

    def _encode_polyline(self, coords: list[tuple[float, float]]) -> str:
        """Encode list of (lat, lng) to Google polyline format."""
        # Simple polyline encoding algorithm
        result = []
        prev_lat = 0
        prev_lng = 0

        for lat, lng in coords:
            # Scale by 1e5 and round
            lat_e5 = int(round(lat * 1e5))
            lng_e5 = int(round(lng * 1e5))

            # Delta encoding
            dlat = lat_e5 - prev_lat
            dlng = lng_e5 - prev_lng

            prev_lat = lat_e5
            prev_lng = lng_e5

            # Encode each delta
            for diff in (dlat, dlng):
                diff <<= 1
                if diff < 0:
                    diff = ~diff
                while diff >= 0x20:
                    result.append(chr((0x20 | (diff & 0x1f)) + 63))
                    diff >>= 5
                result.append(chr(diff + 63))

        return "".join(result)

    async def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address to lat/lng using ORS Pelias."""
        url = f"{self.base_url}/geocode/search"
        headers = {"Authorization": self.api_key}
        params = {"text": address, "size": 1}

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            return (coords[1], coords[0])  # lat, lng
        return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Reverse geocode lat/lng to address."""
        url = f"{self.base_url}/geocode/reverse"
        headers = {"Authorization": self.api_key}
        params = {"point.lat": lat, "point.lon": lng, "size": 1}

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data["features"]:
            return data["features"][0]["properties"].get("label")
        return None

    async def close(self):
        await self.client.aclose()


# Singleton instance
_router: Optional[ORSRouter] = None


def get_ors_router() -> ORSRouter:
    global _router
    if _router is None:
        _router = ORSRouter()
    return _router