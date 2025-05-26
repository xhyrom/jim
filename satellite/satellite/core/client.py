import logging
from typing import Dict, Any, Optional
import aiohttp

logger = logging.getLogger(__name__)


class CoreClient:
    """Client for communicating with the jim Core API"""

    def __init__(
        self, base_url: str = "http://localhost:31415", api_key: Optional[str] = None
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def ask(
        self, text: str, user_id: str = "default", device_id: str = "satellite"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/v0/ask"

        payload = {"text": text, "user_id": user_id, "device_id": device_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Error from Core API: {response.status}")
                        return {"error": f"API returned status {response.status}"}

                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            logger.exception(f"Failed to communicate with Core API: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}
