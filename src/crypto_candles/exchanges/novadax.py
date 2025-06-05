from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class NovadaxAPIError(Exception):
    """Custom exception for Novadax API errors."""
    pass


class NovadaxExchange(BaseExchange):
    """Novadax exchange implementation using requests."""

    BASE_URL = "https://api.novadax.com/v1"

    def __init__(self):
        """Initialize Novadax client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "ONE_MIN",
            "5m": "FIVE_MIN",
            "15m": "FIFTEEN_MIN",
            "30m": "HALF_HOU",
            "1h": "ONE_HOU",
            "1d": "ONE_DAY",
            "1w": "ONE_WEE",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Novadax API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            NovadaxAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NovadaxAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to Novadax format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to Novadax format."""
        # Convert from BTC-BRL to BTC_BRL
        return symbol.replace("-", "_")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Novadax."""
        try:
            # Convert timeframe to Novadax format
            novadax_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Novadax format
            novadax_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp())
            end_ms = int(end_date.timestamp())
            
            # Make request to Novadax API
            response = self._make_request(
                "GET",
                f"market/kline/history",
                params={
                    "symbol": novadax_symbol,
                    "from": start_ms,
                    "to": end_ms,
                    "unit": novadax_timeframe,
                },
            )
            
            # Parse response
            candles = []
            for candle_data in response["data"]:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data["score"])),
                    open=float(candle_data["openPrice"]),
                    high=float(candle_data["highPrice"]),
                    low=float(candle_data["lowPrice"]),
                    close=float(candle_data["closePrice"]),
                    volume=float(candle_data["amount"]),
                    quote_volume=float(candle_data["vol"]),  # amount is quote volume
                    symbol=symbol,
                    exchange="novadax",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise NovadaxAPIError(f"Error getting candles from Novadax: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs."""
        try:
            response = self._make_request("GET", "common/symbols")
            pairs = []
            for symbol_data in response["data"]:
                # Convert from BTC_BRL to BTC-BRL format
                symbol = symbol_data["symbol"].replace("_", "-")
                pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise NovadaxAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 