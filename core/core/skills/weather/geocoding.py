import aiohttp
from typing import Dict, Any, Optional, List, Tuple


class GeocodingService:
    """Geocoding service using OpenStreetMap (Nominatim)"""

    def __init__(self, base_url: str, user_agent: str):
        self.base_url = base_url
        self.user_agent = user_agent

    async def geocode(self, location: str) -> Optional[Dict[str, Any]]:
        params = {"q": location, "format": "json", "limit": 1}

        headers = {"User-Agent": self.user_agent}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}search", params=params, headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(
                            f"Geocoding API error: {response.status} - {error_text}"
                        )

                    data = await response.json()

                    if not data:
                        return None

                    location_data = data[0]
                    return {
                        "name": location_data.get("display_name", location),
                        "lat": float(location_data.get("lat")),
                        "lon": float(location_data.get("lon")),
                        "country": location_data.get("address", {}).get("country"),
                        "city": location_data.get("address", {}).get("city")
                        or location_data.get("address", {}).get("town"),
                    }
        except Exception as e:
            print(f"Error geocoding location: {e}")
            return None

    async def get_location_from_ip(self) -> Optional[Dict[str, Any]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://ip-api.com/json/") as response:
                    if response.status != 200:
                        return None

                    data = await response.json()

                    if data.get("status") != "success":
                        return None

                    return {
                        "name": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "country": data.get("country"),
                        "city": data.get("city"),
                    }
        except Exception as e:
            print(f"Error getting location from IP: {e}")
            return None
