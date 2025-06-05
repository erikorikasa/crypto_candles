from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class FoxbitAPIError(Exception):
    """Custom exception for Foxbit API errors."""
    pass


class FoxbitExchange(BaseExchange):
    """Foxbit exchange implementation using requests."""

    BASE_URL = "https://api.foxbit.com.br"
    API_VERSION = "v3"

    def __init__(self):
        """Initialize Foxbit client."""
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
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Foxbit API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            FoxbitAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FoxbitAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert timeframe to Foxbit format."""
        # Foxbit uses the same timeframe format as our standard
        return timeframe

    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol to Foxbit format."""
        # Convert from BTC-BRL to BTCBRL
        return symbol.replace("-", "").lower()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Foxbit."""
        try:
            # Convert timeframe to Foxbit format
            foxbit_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Foxbit format
            foxbit_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to Foxbit API
            response = self._make_request(
                "GET",
                f"markets/{foxbit_symbol}/candlesticks",
                params={
                    "interval": foxbit_timeframe,
                    "start_time": start_ms,
                    "end_time": end_ms,
                    "limit": 500,
                },
            )
            
            # Parse response
            candles = []
            for candle_data in response:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data[0]) / 1000),  # open datetime
                    open=float(candle_data[1]),  # open price
                    high=float(candle_data[2]),  # high
                    low=float(candle_data[3]),   # low
                    close=float(candle_data[4]), # close
                    volume=float(candle_data[6]), # base volume
                    quote_volume=float(candle_data[7]), # quote volume
                    symbol=symbol,
                    exchange="foxbit",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise FoxbitAPIError(f"Error getting candles from Foxbit: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs"""
        try:
            response = self._make_request("GET", "markets")['data']
            pairs = []
            for market in response:
                symbol = market['symbol']
                pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise FoxbitAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 