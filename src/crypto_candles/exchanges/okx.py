from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class OKXAPIError(Exception):
    """Custom exception for OKX API errors."""
    pass


class OKXExchange(BaseExchange):
    """OKX exchange implementation using requests."""

    BASE_URL = "https://www.okx.com"
    API_VERSION = "v5"

    def __init__(self):
        """Initialize OKX client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to OKX API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            OKXAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/api/{self.API_VERSION}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise OKXAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to OKX format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to OKX format."""
        # OKX uses the same format (e.g., BTC-BRL)
        return symbol

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from OKX."""
        try:
            # Convert timeframe to OKX format
            okx_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to OKX format
            okx_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to OKX API
            response = self._make_request(
                "GET",
                "market/history-candles",
                params={
                    "instId": okx_symbol,
                    "bar": okx_timeframe,
                    "after": end_ms,
                    "before": start_ms
                },
            )
            # Parse response
            candles = []
            for candle_data in response["data"]:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data[0]) / 1000),
                    open=float(candle_data[1]),
                    high=float(candle_data[2]),
                    low=float(candle_data[3]),
                    close=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    quote_volume=float(candle_data[6]),
                    symbol=symbol,
                    exchange="okx",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise OKXAPIError(f"Error getting candles from OKX: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs with BRL as quote currency."""
        try:
            response = self._make_request("GET", "public/instruments", params={"instType": "SPOT"})
            pairs = []
            for instrument in response["data"]:
                # Only include pairs where quote currency is BRL
                if instrument["quoteCcy"] == "BRL":
                    # Convert from BTC-BRL to BTC-BRL format (already in correct format)
                    symbol = f"{instrument['baseCcy']}-{instrument['quoteCcy']}"
                    pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise OKXAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 