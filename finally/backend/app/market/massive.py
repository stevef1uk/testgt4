"""Massive market-data client for latest ticker prices. Network access only; no database access."""

import json
import urllib.parse
import urllib.request


class MassiveClient:
    """Fetches the latest trade price for a ticker from the Massive REST API."""

    def __init__(self, api_key: str, base_url: str = "https://api.massive.com", timeout: float = 5.0) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_latest_price(self, ticker: str) -> float:
        query = urllib.parse.urlencode({"apiKey": self._api_key})
        url = f"{self._base_url}/v2/last/trade/{urllib.parse.quote(ticker)}?{query}"
        with urllib.request.urlopen(url, timeout=self._timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return float(payload["results"]["p"])