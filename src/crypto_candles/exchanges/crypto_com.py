from datetime import datetime
from typing import List, Optional

import pandas as pd
import requests

from .base import BaseExchange
from ..models.candle import Candle


class CryptoComAPIError(Exception):
    """Exception raised for Crypto.com API errors."""

    pass


class CryptoComExchange(BaseExchange):
    """Crypto.com exchange implementation using requests."""

    BASE_URL = "https://api.crypto.com/v2"

    def __init__(self):
        """Initialize Crypto.com client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w",
            "1M": "1M",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Crypto.com API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            CryptoComAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise CryptoComAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to Crypto.com format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to Crypto.com format."""
        # Convert from BTC-BRL to BTC_BRL
        return symbol.replace("-", "_")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """
        Get candles from Crypto.com.

        Args:
            symbol: Trading pair symbol (e.g., "BTC-BRL")
            timeframe: Candle timeframe (e.g., "1h", "1d")
            start_date: Start date for fetching candles
            end_date: End date for fetching candles

        Returns:
            List of Candle objects

        Raises:
            CryptoComAPIError: If API request fails
        """
        try:
            # Convert timeframe to Crypto.com format
            cc_timeframe = self._convert_timeframe(timeframe)

            # Convert symbol to Crypto.com format
            cc_symbol = self._convert_symbol(symbol)

            # Convert dates to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)

            # Make API request
            response = self._make_request(
                "GET",
                "public/get-candlestick",
                params={
                    "instrument_name": cc_symbol,
                    "timeframe": cc_timeframe,
                    "start_ts": start_ms,
                    "end_ts": end_ms,
                },
            )

            # Convert response to candles
            candles = []
            for candle_data in response["result"]["data"]:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(candle_data["t"] / 1000),
                    open=float(candle_data["o"]),
                    high=float(candle_data["h"]),
                    low=float(candle_data["l"]),
                    close=float(candle_data["c"]),
                    volume=float(candle_data["v"]),
                    quote_volume=float(candle_data["v"]) * float(candle_data["c"]),
                    symbol=symbol,
                    exchange="crypto_com",
                    timeframe=timeframe,
                )
                candles.append(candle)

            return candles

        except Exception as e:
            raise CryptoComAPIError(f"Failed to fetch candles: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs with BRL as quote currency."""
        try:
            response = self._make_request("GET", "public/get-ticker")
            pairs = []
            for ticker in response["result"]["data"]:
                # Only include pairs where quote currency is BRL
                if ticker["i"].endswith("_BRL"):
                    # Convert from BTC_BRL to BTC-BRL format
                    base = ticker["i"].replace("_BRL", "")
                    symbol = f"{base}-BRL"
                    pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise CryptoComAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 