import os
import googlemaps
from typing import Optional, Tuple, Dict, Any
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


class GoogleMapsRouter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key not configured")
        self.client = googlemaps.Client(key=self.api_key)

    def get_route(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        alternatives: bool = False
    ) -> RouteResult:
        """Get route from origin to destination."""
        result = self.client.directions(
            origin=origin,
            destination=destination,
            mode=mode,
            alternatives=alternatives,
            units="metric"
        )

        if not result:
            raise ValueError("No route found")

        route = result[0]
        leg = route["legs"][0]

        distance_km = leg["distance"]["value"] / 1000.0
        duration_min = leg["duration"]["value"] / 60.0
        polyline = route["overview_polyline"]["points"]

        start_loc = leg["start_location"]
        end_loc = leg["end_location"]

        return RouteResult(
            distance_km=distance_km,
            duration_min=duration_min,
            polyline=polyline,
            start_lat=start_loc["lat"],
            start_lng=start_loc["lng"],
            end_lat=end_loc["lat"],
            end_lng=end_loc["lng"]
        )

    def get_route_from_coords(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving"
    ) -> RouteResult:
        """Get route from coordinates."""
        origin = f"{origin_lat},{origin_lng}"
        destination = f"{dest_lat},{dest_lng}"
        return self.get_route(origin, destination, mode=mode)

    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address to lat/lng."""
        result = self.client.geocode(address)
        if not result:
            return None
        loc = result[0]["geometry"]["location"]
        return (loc["lat"], loc["lng"])

    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Reverse geocode lat/lng to address."""
        result = self.client.reverse_geocode((lat, lng))
        if not result:
            return None
        return result[0]["formatted_address"]


# Singleton instance
_router: Optional[GoogleMapsRouter] = None


def get_router() -> GoogleMapsRouter:
    global _router
    if _router is None:
        _router = GoogleMapsRouter()
    return _router