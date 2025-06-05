from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class BitgetAPIError(Exception):
    """Custom exception for Bitget API errors."""
    pass


class BitgetExchange(BaseExchange):
    """Bitget exchange implementation using requests."""

    BASE_URL = "https://api.bitget.com/api/v2"

    def __init__(self):
        """Initialize Bitget client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1day",
            "1w": "1week",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Bitget API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            BitgetAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise BitgetAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to Bitget format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to Bitget format."""
        # Convert from BTC-BRL to BTCBRL
        return symbol.replace("-", "").upper()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Bitget."""
        try:
            # Convert timeframe to Bitget format
            bitget_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Bitget format
            bitget_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to Bitget API
            response = self._make_request(
                "GET",
                "spot/market/candles",
                params={
                    "symbol": bitget_symbol,
                    "granularity": bitget_timeframe,
                    "startTime": start_ms,
                    "endTime": end_ms,
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
                    exchange="bitget",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise BitgetAPIError(f"Error getting candles from Bitget: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs with BRL as quote currency."""
        try:
            response = self._make_request("GET", "spot/public/symbols")
            pairs = []
            for symbol_data in response["data"]:
                # Only include pairs where quote currency is BRL
                if symbol_data['quoteCoin'] == 'BRL':
                    # Convert from BTCBRL to BTC-BRL format
                    symbol = f"{symbol_data['baseCoin']}-{symbol_data['quoteCoin']}"
                    pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise BitgetAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 